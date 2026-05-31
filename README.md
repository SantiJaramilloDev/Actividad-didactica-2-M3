# Simulación de un problema bancario

Este repositorio contiene la solución e implementación de la Actividad Didáctica 2 - Módulo 3, consistente en una simulación de eventos discretos desarrollada en Python mediante la biblioteca SimPy. El propósito fundamental es modelar, analizar y evaluar el desempeño de los cajeros del Banco de Colombia bajo distintos escenarios de atención para sustentar decisiones operativas estratégicas.

---

## Contexto del Problema

El Banco de Colombia requiere medir y optimizar el rendimiento de sus cajeros físicos durante las operaciones de pago y retiro, al no contar con canales electrónicos de autoservicio. La gerencia busca determinar la configuración de cajas más eficiente a partir de las siguientes opciones:
*   Asignar una caja exclusiva para retiros y dos para pagos (Opción A).
*   Asignar dos cajas exclusivas para retiros y una para pagos (Opción B).
*   Mantener la configuración actual de tres cajeros mixtos que atienden cualquier tipo de transacción (Escenario Base).

### Parámetros del Sistema
*   **Duración de la jornada:** 8 horas diarias (equivalentes a 480 minutos).
*   **Distribución de transacciones:**
    *   El 70% de los usuarios realiza operaciones de retiro.
    *   El 30% restante efectúa consignaciones o pagos.
*   **Naturaleza de los Cajeros:** Modelados como servidores independientes M/M/1 (procesos de llegada de Poisson y tiempos de servicio con distribución exponencial). Se asume una velocidad de atención inmediata y un tiempo de desplazamiento despreciable entre la fila y la caja.
*   **Número de Réplicas:** La evaluación se sustenta en 10 réplicas del día de operación para garantizar robustez estadística.

---

## Especificación de Datos del Modelo

A continuación se presentan los parámetros definidos para modelar el comportamiento de los clientes y los tiempos de atención en el sistema.

### Tabla 1. Tiempos Estimados de Servicio y Llegada (Distribuciones Exponenciales)

| Tipo de Acción | Tipo de Usuario | Media de Uso del Servicio ($\mu^{-1}$) | Media de Tiempo entre Llegadas ($\lambda^{-1}$) |
| :--- | :--- | :---: | :---: |
| **Retiro (70%)** | Rápido | 1 min | 1 min |
| | Normal | 2 min | 2 min |
| | Lento | 3 min | 3 min |
| | Muy lento | 4 min | 3 min |
| **Pago / Consignación (30%)** | Rápido | 3 min | 1 min |
| | Normal | 3 min | 2 min |
| | Lento | 5 min | 3 min |
| | Muy lento | 7 min | 4 min |

### Tabla 2. Probabilidades por Tipo de Usuario

| Tipo de Acción | Tipo de Usuario | Probabilidad Asociada |
| :--- | :--- | :---: |
| **Retiro** | Rápido | 0.23 |
| | Normal | 0.40 |
| | Lento | 0.17 |
| | Muy lento | 0.20 |
| **Pago / Consignación** | Rápido | 0.10 |
| | Normal | 0.20 |
| | Lento | 0.30 |
| | Muy lento | 0.40 |

---

## Estructura del Código de Simulación

El desarrollo de la simulación se estructuró en Python empleando las siguientes bibliotecas especializadas:
*   `simpy`: Para la gestión del motor de simulación de eventos discretos y modelación de colas.
*   `numpy`: Para la consolidación estadística y generación de tiempos mediante variables aleatorias.
*   `pandas`: Para el procesamiento y estructuración tabular de los datos obtenidos en cada réplica.
*   `matplotlib`: Para la visualización gráfica de los tiempos de espera promedio en los escenarios evaluados.

El script principal [`simulacion_problema_bancario.py`](file:///e:/IUDigital/Simulaci%C3%B3n/Actividad%20did%C3%A1ctica%202-M3/simulacion_problema_bancario.py) se compone de las siguientes secciones:

1.  **Configuración de Parámetros:** Definición de diccionarios de entrada con las probabilidades y medias exponenciales de llegada y servicio establecidas por el enunciado.
2.  **Clase `BancoSimulacion`:** 
    *   `__init__`: Crea las colas de espera independientes representadas mediante objetos `simpy.Resource`.
    *   `elegir_cajero`: Implementa la lógica de selección de cola, donde el usuario ingresa a la fila más corta en cajas multifuncionales o se dirige a la caja exclusiva de su tipo de transacción.
    *   `llegadas`: Genera las entidades clientes de forma dinámica basándose en la tasa exponencial de llegada de cada perfil.
    *   `atender_cliente`: Modela el tiempo en fila, la asignación del recurso y el consumo del tiempo de servicio según el perfil del usuario.
3.  **Módulo de Ejecución y Visualización:** Controla el ciclo de las 10 réplicas por cada escenario, genera el reporte en consola y grafica los resultados comparativos.

---

## Resultados de la Simulación

A partir de las corridas del modelo, se obtuvieron las siguientes estadísticas para cada uno de los criterios evaluados.

### 1. Tiempos de Atención por Cajero (Escenario Base)
Los tiempos promedio medidos por cajero para todas las transacciones atendidas en el escenario base fueron:
*   **Cajero 0:** 3.12 minutos
*   **Cajero 1:** 3.03 minutos
*   **Cajero 2:** 3.10 minutos
*   **Menor tiempo promedio de atención:** Cajero 1 (3.03 minutos)
*   **Mayor tiempo promedio de atención:** Cajero 0 (3.12 minutos)

> [!NOTE]
> Las variaciones entre los cajeros se deben a la aleatoriedad de las distribuciones exponenciales de servicio y llegada en cada corrida. Teóricamente, al ser servidores con capacidades idénticas y asignación basada en la cola más corta, los tiempos convergen hacia valores muy similares.

### 2. Total de Usuarios por Tipo en cada Réplica (Escenario Base)

La distribución diaria del volumen de clientes que ingresaron al banco por tipo de transacción se detalla en la siguiente tabla:

| Réplica | Retiro-Rápido | Retiro-Normal | Retiro-Lento | Retiro-Muy lento | Pago-Rápido | Pago-Normal | Pago-Lento | Pago-Muy lento |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | 36 | 55 | 21 | 31 | 4 | 12 | 22 | 24 |
| **2** | 44 | 63 | 21 | 32 | 10 | 12 | 19 | 30 |
| **3** | 38 | 45 | 22 | 27 | 4 | 9 | 25 | 19 |
| **4** | 38 | 68 | 29 | 24 | 5 | 9 | 19 | 24 |
| **5** | 39 | 77 | 19 | 38 | 9 | 12 | 26 | 26 |
| **6** | 42 | 65 | 31 | 40 | 5 | 14 | 18 | 17 |
| **7** | 30 | 65 | 24 | 35 | 3 | 12 | 19 | 25 |
| **8** | 44 | 73 | 24 | 28 | 3 | 8 | 15 | 19 |
| **9** | 32 | 56 | 21 | 32 | 12 | 13 | 19 | 24 |
| **10** | 34 | 51 | 21 | 25 | 3 | 14 | 23 | 22 |

### 3. Modelo con Menor Cantidad de Usuarios por Tipo
Se identificó la cantidad mínima de clientes registrada en las réplicas para cada tipología:
*   **Retiro-Rápido:** Mínimo de 30 usuarios (Réplica 7)
*   **Retiro-Normal:** Mínimo de 45 usuarios (Réplica 3)
*   **Retiro-Lento:** Mínimo de 19 usuarios (Réplica 5)
*   **Retiro-Muy lento:** Mínimo de 24 usuarios (Réplica 4)
*   **Pago-Rápido:** Mínimo de 3 usuarios (Réplicas 7, 8 y 10)
*   **Pago-Normal:** Mínimo de 8 usuarios (Réplica 8)
*   **Pago-Lento:** Mínimo de 15 usuarios (Réplica 8)
*   **Pago-Muy lento:** Mínimo de 17 usuarios (Réplica 6)

### 4. Promedio de Usuarios por Tipo (Consolidado de 10 Réplicas)
El flujo medio diario de clientes en el sistema según su perfil es:
*   **Retiro - Rápido:** 37.7 usuarios/día
*   **Retiro - Normal:** 61.8 usuarios/día
*   **Retiro - Lento:** 23.3 usuarios/día
*   **Retiro - Muy lento:** 31.2 usuarios/día
*   **Pago - Rápido:** 5.8 usuarios/día
*   **Pago - Normal:** 11.5 usuarios/día
*   **Pago - Lento:** 20.5 usuarios/día
*   **Pago - Muy lento:** 23.0 usuarios/día

---

## Análisis y Respuestas a los Puntos de la Tarea

Con base en los datos estructurados, se desarrollan las respuestas técnicas a los cuestionamientos del problema:

### 1. Cajero con menor y mayor tiempo promedio de atención
El cajero con el mejor rendimiento fue el **Cajero 1**, registrando un tiempo promedio de atención de **3.03 minutos**. Por el contrario, el **Cajero 0** obtuvo el tiempo promedio más alto con **3.12 minutos**. La diferencia entre ambos es de apenas 0.09 minutos, lo que ratifica una distribución equitativa de la carga de trabajo en el esquema de cajas mixtas.

### 2. Promedio de usuarios de cada tipo en la totalidad de cajeros
Las medias diarias demuestran que el perfil **Retiro-Normal** es, por un amplio margen, el más representativo con **61.8 usuarios diarios en promedio**. En contraste, los usuarios de **Pago-Rápido** son los de menor presencia en el banco con una media de **5.8 usuarios por jornada**.

### 3. Total de usuarios por tipo en réplicas y modelo con menor cantidad
Los valores individuales y globales correspondientes a cada réplica se especifican en la tabla del apartado anterior. Los registros mínimos absolutos por categoría evidencian variaciones notables entre jornadas de simulación, ocurriendo, por ejemplo, que la réplica 8 albergó la menor cantidad de clientes para tres perfiles diferentes de pago.

### 4. Justificación técnica sobre la creación de un nuevo cajero
> [!IMPORTANT]
> **No se justifica la inversión para la creación de un cuarto cajero en el escenario base.**
> Bajo el esquema de tres cajeros mixtos, el tiempo promedio de espera en fila es de **1.82 minutos**. Esta cifra indica un nivel de servicio sobresaliente con tiempos de espera mínimos para los usuarios. Instalar una caja adicional incrementaría los costos fijos de nómina e infraestructura del banco sin aportar un beneficio de cara al cliente, derivando principalmente en tiempos de ocio para los servidores.
> 
> Únicamente bajo los esquemas de exclusividad de cajas, donde el tiempo de espera promedio asciende drásticamente a 3.85 o 3.88 minutos, y si se definiera un estándar rígido de servicio que obligara a tiempos de espera menores a 2 minutos, se podría considerar una nueva caja para subsanar la ineficiencia introducida por la segmentación de colas.

### 5. Configuración óptima de cajeros exclusivos (Decisión de Asignación)
Al confrontar los tiempos de espera promedio consolidados entre los tres esquemas de servicio se observa lo siguiente:

```
Tiempos Promedio de Espera por Configuración:
+------------------------------------+------------------+
| Configuración de Cajeros           | Espera Promedio  |
+------------------------------------+------------------+
| Escenario Base (3 Mixtos)          | 1.82 minutos     |
| Opción A (1 Retiro / 2 Pagos)      | 3.88 minutos     |
| Opción B (2 Retiros / 1 Pago)      | 3.85 minutos     |
+------------------------------------+------------------+
```

*   **Recomendación de Diseño:** La gerencia **no debe implementar atención exclusiva**. La configuración mixta del Escenario Base es la más eficiente, alcanzando una espera de **1.82 minutos** (una reducción superior al 52% respecto a las configuraciones con segmentación). De acuerdo con la teoría de colas, al unificar los recursos se flexibiliza la atención de la demanda fluctuante, impidiendo que un servidor quede libre mientras la cola de otra tipología está congestionada.
*   **Decisión en caso de Segmentación Obligatoria:** Si el banco debe implementar cajas exclusivas por políticas internas irrevocables, la decisión correcta es elegir la **Opción B (2 cajeros para Retiro y 1 cajero para Pago)**.
*   **Fundamento Técnico:** La Opción B reporta una espera de **3.85 minutos**, ligeramente menor a los **3.88 minutos** de la Opción A. Esto se fundamenta plenamente en el hecho de que el **70% de los clientes solicita operaciones de Retiro**. Al destinar el 66% de la capacidad de servicio (2 de los 3 cajeros) al flujo mayoritario, se logra un balance de colas un poco más tolerable que al limitar los retiros a un solo cajero ocioso y saturar las cajas de pago.

---

## Instrucciones de Instalación y Ejecución

### Requisitos del Entorno
Para el correcto funcionamiento del modelo es necesario contar con Python 3.8 o superior y las dependencias requeridas instaladas. Esto se puede lograr ejecutando en consola:

```bash
pip install simpy numpy pandas matplotlib
```

### Ejecución de la Simulación
Para iniciar las corridas de simulación y visualizar el reporte textual integrado junto a la representación gráfica del comportamiento de los escenarios, ejecute el siguiente comando:

```bash
python simulacion_problema_bancario.py
```

El script imprimirá en la consola los reportes tabulados y desplegará la interfaz gráfica correspondiente al diagrama de barras comparativo elaborado en Matplotlib.

---

## Información del Proyecto
*   **Asignatura:** Simulación
*   **Institución:** IU Digital de Antioquia
*   **Autor:** Brayan Santiago Jaramillo Amézquita
*   **Año:** 2026
