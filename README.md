# ACTIVIDAD-7-EMJAMBRE-DE-3-ROBOTS-
# 📡 Sistema de Comunicación Híbrido Bidireccional RS485 & UART (ESP32 - PC)

Este proyecto implementa un sistema de comunicación híbrido, bidireccional y en tiempo real diseñado para entornos de **Monitoreo y Control en Líneas de Producción Industrial**. La solución integra la adquisición de datos multisensor, el control de actuadores, un enlace de comunicación industrial mediante **RS485** y una interfaz gráfica de supervisión en tiempo real (**GUI en Python**).

---

## 📌 Visión General del Sistema

El sistema combina dos tecnologías principales de transmisión para garantizar la flexibilidad local y la robustez a larga distancia:

1. **ESP32 ↔ PC (UART / USB Local):**
   * Transmisión de lecturas de sensores locales desde el ESP32 principal hacia la PC.
   * Recepción de comandos desde la PC hacia el ESP32 para el control de actuadores (LEDs indicadores).
   
2. **ESP32 Principal ↔ ESP32 Remoto (RS485 Industrial):**
   * Conexión punto a punto utilizando transceptores **RS485**.
   * Transmisión de señales diferenciales a través de un par trenzado (Líneas A y B) en modo **Half-Duplex**.
   * Control de flujo de dirección mediante un pin habilitador (`DE/RE`).

## 🏗️ Arquitectura y Comunicaciones

### 🌐 Conexión Industrial RS485
* **Inmunidad al Ruido:** Utiliza transmisión de voltaje diferencial para soportar entornos industriales con alta interferencia electromagnética.
* **Alcance:** Soporta distancias físicas de enlace de hasta **$1200\text{ metros}$**.
* **Modo Half-Duplex:** El ESP32 conmuta dinámicamente el pin de habilitación para alternar entre el estado de emisión y recepción de paquetes de datos.

### 💻 Supervisión y Control (Interfaz Python GUI)
En el extremo de la PC se ejecutó una aplicación desarrollada con `pyserial`, `tkinter` y `matplotlib`:
* **Tasa de refresco:** Procesamiento y renderizado continuo a frecuencias superiores a los **$20\text{ Hz}$**.
* **Visualización:** Selección dinámica de variables (locales y remotas) con graficación de curvas en tiempo real.
* **Mando y Control:** Envío de comandos de activación hacia los microcontroladores para accionar salidas discretas (LEDs simuladores de carga/actuadores).

---

## 🧪 Pruebas y Validación del Sistema

Tras el diseño e implementación, se realizó una fase intensiva de pruebas en un entorno controlado replicando escenarios reales de aplicación:

### 1. Enlace de Comunicación y Estabilidad
* **RS485:** Se verificó la transmisión sin pérdida de paquetes entre los nodos ESP32 bajo diferentes tasas de transferencia.
* **USB/UART:** Se comprobó la fluidez de la comunicación bidireccional con la interfaz gráfica sin saturación del puerto serial.

### 2. Adquisición de Sensores y Actuación
* **Sensórica:** Muestreo y verificación de precisión ante perturbaciones ambientales, incluyendo cambios de iluminación, variaciones de distancia y aceleración/orientación mediante giroscopio.
* **Actuadores:** Respuesta inmediata de encendido/apagado de los LEDs ante los comandos enviados desde la GUI.

### 3. Interfaz Gráfica (Python GUI)
* Renderizado estable a $20\text{ Hz}$ sin latencia perceptible.
* Conmutación correcta entre la visualización de datos provenientes del nodo local y del nodo remoto.

---

## 🚀 Conclusiones

El desarrollo permitió validar el alto grado de confiabilidad y robustez del estándar **RS485** combinado con arquitecturas **IoT/Embedded** basadas en el ESP32. Esta solución proporciona una base modular, económica y escalable para proyectos de telemetría industrial y automatización de líneas de producción.
