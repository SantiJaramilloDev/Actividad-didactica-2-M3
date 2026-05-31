import simpy
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 1. CONFIGURACIÓN Y DATOS DEL MODELO

# Probabilidades generales
PROB_ACCION = {'Retiro': 0.70, 'Pago': 0.30}

# Probabilidades del tipo de usuario según su acción (Tabla 2)
PROB_TIPO = {
    'Retiro': {'Rápido': 0.23, 'Normal': 0.40, 'Lento': 0.17, 'Muy lento': 0.20},
    'Pago': {'Rápido': 0.10, 'Normal': 0.20, 'Lento': 0.30, 'Muy lento': 0.40}
}

# Tiempos promedio de servicio en minutos (Tabla 1)
MEDIA_SERVICIO = {
    'Retiro': {'Rápido': 1, 'Normal': 2, 'Lento': 3, 'Muy lento': 4},
    'Pago': {'Rápido': 3, 'Normal': 3, 'Lento': 5, 'Muy lento': 7}
}

# Tiempos promedio entre llegadas en minutos (Tabla 1)
MEDIA_LLEGADA = {
    'Retiro': {'Rápido': 1, 'Normal': 2, 'Lento': 3, 'Muy lento': 3},
    'Pago': {'Rápido': 1, 'Normal': 2, 'Lento': 3, 'Muy lento': 4}
}

TIEMPO_SIMULACION = 480  # 8 horas al día en minutos
NUM_REPLICAS = 10

# 2. LÓGICA DEL SIMULADOR

class BancoSimulacion:
    def __init__(self, env, escenario="base"):
        self.env = env
        self.escenario = escenario
        
        # Creación de cajeros (Servidores M/M/1 independientes)
        if escenario == "base":
            # 3 cajeros que atienden todo
            self.cajeros = [{'id': i, 'res': simpy.Resource(env, capacity=1)} for i in range(3)]
        elif escenario == "1_retiro_2_pagos":
            self.cajeros_retiro = [{'id': 'R1', 'res': simpy.Resource(env, capacity=1)}]
            self.cajeros_pago = [{'id': 'P1', 'res': simpy.Resource(env, capacity=1)}, 
                                 {'id': 'P2', 'res': simpy.Resource(env, capacity=1)}]
        elif escenario == "2_retiros_1_pago":
            self.cajeros_retiro = [{'id': 'R1', 'res': simpy.Resource(env, capacity=1)}, 
                                   {'id': 'R2', 'res': simpy.Resource(env, capacity=1)}]
            self.cajeros_pago = [{'id': 'P1', 'res': simpy.Resource(env, capacity=1)}]
            
        # Variables estadísticas
        self.tiempos_espera = []
        self.tiempos_servicio_por_cajero = {}
        self.usuarios_por_tipo = {
            'Retiro': {'Rápido': 0, 'Normal': 0, 'Lento': 0, 'Muy lento': 0},
            'Pago': {'Rápido': 0, 'Normal': 0, 'Lento': 0, 'Muy lento': 0}
        }

    def elegir_cajero(self, accion):
        # Lógica de elegir la fila más corta (M/M/1 independientes)
        if self.escenario == "base":
            return min(self.cajeros, key=lambda c: len(c['res'].queue))
        
        elif self.escenario == "1_retiro_2_pagos":
            if accion == 'Retiro':
                return self.cajeros_retiro[0]
            else:
                return min(self.cajeros_pago, key=lambda c: len(c['res'].queue))
                
        elif self.escenario == "2_retiros_1_pago":
            if accion == 'Retiro':
                return min(self.cajeros_retiro, key=lambda c: len(c['res'].queue))
            else:
                return self.cajeros_pago[0]

    def llegadas(self):
        while True:
            # 1. Determinar Acción (70% Retiro, 30% Pago)
            accion = random.choices(list(PROB_ACCION.keys()), weights=list(PROB_ACCION.values()))[0]
            
            # 2. Determinar Tipo de Usuario
            tipos = list(PROB_TIPO[accion].keys())
            probs = list(PROB_TIPO[accion].values())
            tipo = random.choices(tipos, weights=probs)[0]
            
            self.usuarios_por_tipo[accion][tipo] += 1
            
            # 3. Iniciar el proceso de atención
            self.env.process(self.atender_cliente(accion, tipo))
            
            # 4. Determinar tiempo hasta la próxima llegada
            t_llegada = random.expovariate(1.0 / MEDIA_LLEGADA[accion][tipo])
            yield self.env.timeout(t_llegada)

    def atender_cliente(self, accion, tipo):
        llegada = self.env.now
        cajero_elegido = self.elegir_cajero(accion)
        id_cajero = cajero_elegido['id']
        recurso = cajero_elegido['res']
        
        # Iniciar registro del cajero si no existe
        if id_cajero not in self.tiempos_servicio_por_cajero:
            self.tiempos_servicio_por_cajero[id_cajero] = []
            
        with recurso.request() as request:
            yield request # Esperar en la fila
            espera = self.env.now - llegada
            self.tiempos_espera.append(espera)
            
            # Tiempo de servicio
            t_servicio = random.expovariate(1.0 / MEDIA_SERVICIO[accion][tipo])
            yield self.env.timeout(t_servicio)
            self.tiempos_servicio_por_cajero[id_cajero].append(t_servicio)

# 3. EJECUCIÓN DE RÉPLICAS Y ANÁLISIS

def ejecutar_simulacion():
    escenarios = ["base", "1_retiro_2_pagos", "2_retiros_1_pago"]
    resultados_globales = {}
    
    # Variables para almacenar datos requeridos por la rúbrica
    datos_replica_base = []
    tiempos_servicio_base_global = {0: [], 1: [], 2: []}
    
    for escenario in escenarios:
        esperas_replicas = []
        
        for replica in range(NUM_REPLICAS):
            env = simpy.Environment()
            banco = BancoSimulacion(env, escenario)
            env.process(banco.llegadas())
            env.run(until=TIEMPO_SIMULACION)
            
            # Guardar promedio de espera de la réplica
            espera_promedio = np.mean(banco.tiempos_espera) if banco.tiempos_espera else 0
            esperas_replicas.append(espera_promedio)
            
            # Recolectar datos específicos solo del escenario base para la rúbrica
            if escenario == "base":
                # Guardar usuarios por tipo en esta réplica
                fila_usuarios = {'Réplica': replica + 1}
                for accion in banco.usuarios_por_tipo:
                    for tipo, cant in banco.usuarios_por_tipo[accion].items():
                        fila_usuarios[f"{accion}-{tipo}"] = cant
                datos_replica_base.append(fila_usuarios)
                
                # Acumular tiempos de servicio por cajero
                for c_id, tiempos in banco.tiempos_servicio_por_cajero.items():
                    tiempos_servicio_base_global[c_id].extend(tiempos)
                    
        resultados_globales[escenario] = esperas_replicas

    # IMPRESIÓN DE RESULTADOS
    print(" RESULTADOS DE LA SIMULACIÓN")

    # 1. Cajero con menor y mayor tiempo promedio de atención (Escenario Base)
    promedios_servicio = {c_id: np.mean(tiempos) for c_id, tiempos in tiempos_servicio_base_global.items()}
    cajero_min = min(promedios_servicio, key=promedios_servicio.get)
    cajero_max = max(promedios_servicio, key=promedios_servicio.get)
    print("\n1. TIEMPOS DE ATENCIÓN POR CAJERO (Escenario Base):")
    for c_id, prom in promedios_servicio.items():
        print(f"   Cajero {c_id}: {prom:.2f} minutos")
    print(f"   -> Menor tiempo promedio: Cajero {cajero_min} ({promedios_servicio[cajero_min]:.2f} min)")
    print(f"   -> Mayor tiempo promedio: Cajero {cajero_max} ({promedios_servicio[cajero_max]:.2f} min)")

    # 2. Total de usuarios por tipo en cada réplica y menor cantidad (Escenario Base)
    df_usuarios = pd.DataFrame(datos_replica_base).set_index('Réplica')
    print("\n2. TOTAL DE USUARIOS POR TIPO EN CADA RÉPLICA (Escenario Base):")
    print(df_usuarios.to_string())
    
    print("\n3. MODELO CON MENOR CANTIDAD DE USUARIOS POR TIPO (Mínimos por columna):")
    minimos = df_usuarios.min()
    for col, val in minimos.items():
        replica_min = df_usuarios[df_usuarios[col] == val].index.tolist()
        print(f"   {col}: {val} usuarios (Ocurrió en la(s) réplica(s) {replica_min})")

    # 4. Promedio de usuarios de cada tipo en la totalidad de cajeros (Escenario Base)
    promedios_usuarios = df_usuarios.mean()
    print("\n4. PROMEDIO DE USUARIOS POR TIPO (10 Réplicas):")
    for col, val in promedios_usuarios.items():
        print(f"   {col}: {val:.1f} usuarios")

    # 5 & 6. Análisis de Espera y Asignación de Cajeros
    print("\n5 & 6. ANÁLISIS DE TIEMPOS DE ESPERA Y ASIGNACIÓN EXCLUSIVA:")
    for esc, esperas in resultados_globales.items():
        print(f"   Escenario [{esc}]: Espera promedio = {np.mean(esperas):.2f} minutos")
    
  
    # 4. GRÁFICA DE RESULTADOS
  
    graficar_resultados(
        resultados_globales["base"], 
        resultados_globales["1_retiro_2_pagos"], 
        resultados_globales["2_retiros_1_pago"]
    )

def graficar_resultados(res_base, res_1r2p, res_2r1p):
    escenarios = ['Base\n(3 Mixtos)', 'Opción A\n(1 Retiro / 2 Pagos)', 'Opción B\n(2 Retiros / 1 Pago)']
    promedios = [np.mean(res_base), np.mean(res_1r2p), np.mean(res_2r1p)]
    
    plt.figure(figsize=(10, 6))
    barras = plt.bar(escenarios, promedios, color=['#4C72B0', '#DD8452', '#55A868'])
    
    plt.title('Tiempo Promedio de Espera por Configuración de Cajeros\n(10 Réplicas, 8 Horas/Día)', fontsize=14, fontweight='bold')
    plt.ylabel('Tiempo de Espera Promedio (Minutos)', fontsize=12)
    plt.xlabel('Configuración de Cajeros', fontsize=12)
    
    # Agregar valores numéricos sobre las barras
    for barra in barras:
        yval = barra.get_height()
        plt.text(barra.get_x() + barra.get_width()/2, yval + (max(promedios)*0.02), 
                 f'{yval:.2f} min', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

# Ejecutar el script
if __name__ == "__main__":
    ejecutar_simulacion()