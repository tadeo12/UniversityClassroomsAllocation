# Manual de Usuario y Despliegue
## Sistema de Optimización de Distribución de Aulas

Este documento detalla los pasos necesarios para obtener el código, instalar las dependencias, ejecutar la aplicación y preparar los datos de entrada.

### 1. Requisitos Previos

Asegúrate de tener instalado el siguiente software en tu sistema:

* **Python 3.11** (o superior).
* **Git** (opcional, si decides clonar el repositorio).

Puedes verificar las instalaciones ejecutando:

```bash
python --version
git --version
```

### 2. Obtención del Código Fuente

Antes de comenzar, necesitas descargar el proyecto en tu equipo.

**Opción A: Clonar el repositorio (Recomendado)**

Abre tu terminal y ejecuta el siguiente comando:

```bash
git clone [https://github.com/tadeo12/UniversityClassroomsAllocation.git](https://github.com/tadeo12/UniversityClassroomsAllocation.git)
cd UniversityClassroomsAllocation
```

**Opción B: Descargar como ZIP**

1. Descarga el archivo `.zip` con el código fuente desde el repositorio.
2. Descomprímelo en una carpeta de tu elección.
3. Abre la terminal y navega hasta esa carpeta:
    ```bash
    cd ruta/a/la/carpeta/descomprimida
    ```

### 3. Instalación de Dependencias

Se recomienda utilizar un entorno virtual para no afectar tu instalación global de Python.

#### Paso 3.1: Crear y activar entorno virtual

**En Windows:**

```powershell
python -m venv venv
.\venv\Scripts\activate
```

**En Linux/Mac:**

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Paso 3.2: Instalar librerías

Una vez dentro del entorno virtual (verás `(venv)` en tu terminal), instala las dependencias ejecutando:

```bash
pip install streamlit reportlab pandas matplotlib
```

Si tienes un archivo `requirements.txt`, puedes usar `pip install -r requirements.txt`. Si no, el comando anterior instalará todo lo necesario.

### 4. Ejecución del Servicio

Para levantar la interfaz gráfica con la configuración específica de desarrollo, ejecuta el siguiente comando desde la raíz del proyecto:

```bash
streamlit run app/main.py --server.port 80 --server.enableCORS false --server.enableXsrfProtection false
```

**Desglose del comando:**

* **`app/main.py`**: Es el punto de entrada de la aplicación. Asegúrate de estar en la carpeta correcta.
* **`--server.port 80`**: Levanta el servicio en el puerto HTTP estándar (80).
    > **Nota:** En sistemas Linux/Mac, usar el puerto 80 puede requerir permisos de superusuario (`sudo`). Si tienes problemas, quita esta bandera para usar el puerto por defecto (8501).
* **`--server.enableCORS false`**: Deshabilita la política de origen cruzado.
* **`--server.enableXsrfProtection false`**: Deshabilita la protección XSRF.

Una vez ejecutado, el sistema debería estar accesible en [http://localhost](http://localhost) (o `http://localhost:8501` si no usaste el puerto 80).

### 5. Recomendaciones de Uso y Limitaciones

Antes de operar el sistema, ten en cuenta las siguientes consideraciones de seguridad y funcionamiento:

#### Seguridad y Entorno
* **Uso Local Exclusivo:** Esta aplicación está diseñada como un prototipo para ejecución local o en una red controlada. No debe exponerse directamente a internet público, ya que las protecciones CORS y XSRF están deshabilitadas y la gestión de archivos no es segura para entornos multiusuario.
* **Un Solo Usuario:** El sistema no gestiona sesiones concurrentes de escritura. Se recomienda que sea utilizado por un único usuario a la vez para evitar conflictos en los archivos de configuración y datos.

#### Errores Conocidos (Workarounds)
* **Menú de Resultados:** Existe un error de refresco en la interfaz donde la opción "Resultados" no aparece automáticamente tras finalizar el algoritmo.
    * **Solución:** Haga clic en el menú "Opciones Avanzadas" para forzar la actualización de la barra lateral y ver la pestaña de resultados.
    
    Ademas, en caso de que se haya ejecutado el algoritmo a partir de una distribucion predeterminada, puede que el json de la vista detallada no funcione correctamente (aparece con valores none o null). Esto sin embargo no evita que se pueda descargar el pdf con la distribucion correcta. Ademas la vista no detallada (para copiar y pegar) funciona corractamente
    
* **Cambios de Configuración:** Modificar la configuración (archivo `config.json` o vía GUI) después de haber ejecutado el algoritmo una vez puede generar inconsistencias.
    
    * **Solución:** Reinicie el servicio si necesita cambiar parámetros estructurales luego de ya haber ejecutado una vez el algoritmo
    
* **Mientras el algoritmo ejecuta**:

    * No ir a opciones avanzadas, ya que al volver a la pagina principal ocurre un bug con los graficos y no se indexan correctamente.
    * Para scrollear y ver los graficos de mas abajo, usar la flecha de abajo del teclado (la rueda del mouse puede no funcionar).


#### Limitación de Datos
* **Atomicidad de Horarios:** La definición de `availableTimeSlots` en las aulas depende estrictamente de la configuración de duración del bloque horario (`hours_per_resource`). Si cambia la configuración (ej. de 1 hora a 30 min), debe actualizar manualmente los índices en el JSON de entrada, ya que estos valores no se recalculan automáticamente.

### 6. Formato de Datos de Entrada

El sistema se alimenta de archivos JSON. A continuación se detallan las estructuras esperadas.

#### A. Archivo de Entidades (`data.json`)

Este archivo define los recursos, profesores, materias y grupos.

**Estructura General:**

```json
{
    "places": [...],
    "teachers": [...],
    "subjects": [...],
    "classrooms": [...],
    "commissions": [...],
    "groups": [...],
    "commissions_groups": [...]
}
```

**Detalle importante sobre classrooms (Aulas):** Las aulas pueden tener disponibilidad limitada usando la propiedad `availableTimeSlots`.

* El formato es `[día, hora]`.
* **Día:** 0 (Lunes) a 4 (Viernes).
* **Hora:** Índice del bloque horario (depende de tu configuración, ej: 0 para las 8:00hs).

**Ejemplo de Aula:**

```json
{
    "name": "Aula 6",
    "capacity": 233,
    "place": "Palihue",
    "availableTimeSlots": [
        [1, 0], [1, 1]  // Disponible Martes en los primeros dos bloques
    ]
}
```

#### B. Archivo de Distribución Inicial 

Si deseas cargar una distribución predefinida (o guardar una generada), el sistema utiliza un formato de mapa donde la clave es una cadena de texto que representa una tupla de recurso, y el valor es el nombre de la comisión.

* **Formato de la Clave (String):** `"(día, hora, 'Nombre del Aula')"`
* **día:** Entero (0-4).
* **hora:** Entero (índice del bloque horario).
* **Nombre del Aula:** String exacto coincidente con `data.json`.

**Ejemplo:**

```json
{
    "(3, 10, 'LP004')": "RPA G-N",
    "(0, 10, 'LP001')": "AyC",
    "(4, 4, 'LP005')": "ED A-K"
}
```

> **Nota:** Es fundamental respetar las comillas simples internas `'` para el nombre del aula y los paréntesis, ya que el sistema parsea este string para convertirlo en objeto.