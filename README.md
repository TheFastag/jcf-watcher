# JCF Focalización Watcher 🇲🇽

Este sistema monitorea automáticamente el estatus del municipio **Solidaridad, Quintana Roo** (o cualquier otro que configures) en el portal de focalización de **Jóvenes Construyendo el Futuro (JCF)**. 

Cuando el estatus cambia (por ejemplo, de **"Municipio Cerrado"** a **"Municipio Abierto"**), el sistema te envía inmediatamente una **notificación push gratuita** a tu celular utilizando el servicio gratuito y libre de **ntfy.sh**.

> [!IMPORTANT]
> **Este script solo te avisa.** No realiza de forma automatizada el llenado o envío de tu solicitud. Esto respeta las reglas del portal y te garantiza que tú mismo ingreses tus datos manualmente una vez notificado. Todo el flujo es 100% gratuito y no requiere tarjetas ni cuentas de pago.

---

## 📱 Configuración de Notificaciones (ntfy.sh)

1. Descarga la aplicación **ntfy** en tu teléfono:
   - [Google Play Store (Android)](https://play-store-link) o F-Droid.
   - [App Store (iOS)](https://apps.apple.com/app/ntfy/id1625396389).
   - *O bien puedes usar la versión web: abre [https://ntfy.sh/](https://ntfy.sh/) en tu navegador de preferencia.*
2. En la app, presiona el botón **"+"** o **"Subscribe to topic"**.
3. Elige un nombre de tema único y aleatorio (por ejemplo: `jcf-alerta-solidaridad-789`). **No uses espacios ni caracteres especiales**.
4. ¡Listo! Ya estás suscrito al canal. Cualquier mensaje que se envíe a `https://ntfy.sh/tu-tema-secreto` llegará al instante como notificación push.

---

## 🛠️ Instalación y Uso Local

Sigue estos pasos para validar que el script funciona y ver cómo interactúa con el sitio web de manera visual.

### 1. Requisitos Previos
Asegúrate de tener instalado Python 3.8 o superior en tu equipo.

### 2. Instalar dependencias
Abre una terminal en esta carpeta y ejecuta:
```bash
pip install -r requirements.txt
```

### 3. Instalar navegadores de Playwright
Playwright requiere descargar su versión de Chromium para funcionar:
```bash
playwright install chromium
```

### 4. Probar en modo visible (Visual / Headless = false)
Por defecto, el script corre en modo oculto (headless). Para probarlo de forma visible y verificar cómo da clic y busca la información:

**En Windows (PowerShell):**
```powershell
$env:HEADLESS="false"
$env:NTFY_TOPIC="tu-tema-creado" # Reemplaza con tu tema de ntfy
python check_focalizacion.py
```

**En Linux / macOS:**
```bash
HEADLESS=false NTFY_TOPIC="tu-tema-creado" python check_focalizacion.py
```

Al correrlo, verás cómo se abre el navegador Chrome, entra a la página, hace clic en el estado de Quintana Roo, ingresa "Solidaridad" en la búsqueda, extrae el estado y crea un archivo llamado `status.txt` con el valor actual. Si es la primera vez que corre, te llegará la notificación push de inicialización.

---

## 🚀 Despliegue Automático Gratis (GitHub Actions)

Para que el script corra de manera continua cada 6 horas y guarde el estatus sin necesidad de tener tu computadora encendida:

1. **Crea un repositorio en GitHub:** Crea un nuevo repositorio (puede ser privado o público) y sube todos los archivos de este proyecto (`check_focalizacion.py`, `.github/`, `requirements.txt`, etc.).
2. **Configura el Secret de Notificación:**
   - En tu repositorio de GitHub, ve a **Settings** > **Secrets and variables** > **Actions**.
   - Haz clic en **New repository secret**.
   - Nombre: `NTFY_TOPIC`
   - Valor: El nombre de tu tema único creado en el paso 1 (por ejemplo: `jcf-alerta-solidaridad-789`).
3. **Otorga permisos de escritura al Workflow:**
   - Como el script necesita guardar el archivo `status.txt` dentro de tu repositorio entre corridas para recordar el estatus anterior, GitHub Actions requiere permisos de escritura.
   - Ve a **Settings** > **Actions** > **General**.
   - Ve al final de la página hasta la sección **Workflow permissions**.
   - Selecciona **Read and write permissions** y haz clic en **Save**.
4. **Prueba el Workflow manualmente:**
   - Ve a la pestaña **Actions** en tu repositorio.
   - Selecciona el flujo **Check JCF Focalizacion** en la barra lateral izquierda.
   - Haz clic en el botón desplegable **Run workflow** y luego en **Run workflow**.
   - Espera unos minutos a que finalice. Deberías recibir tu primera notificación y ver aparecer el archivo `status.txt` en la raíz de tu repositorio en GitHub.

---

## 🔍 Depuración y Resolución de Fallas (Selectores)

Dado que las páginas gubernamentales cambian su diseño sin previo aviso, el script está preparado para ser fácil de depurar:

1. **Mensajes Detallados:** El script imprime por consola el texto íntegro capturado del contenedor de la tabla (`div.barridoTabla`) en cada corrida.
2. **Capturas de Pantalla en Errores:** Si el script no logra encontrar el botón del estado o el campo de búsqueda, guardará automáticamente archivos de imagen en la raíz del proyecto:
   - `debug_state_error.png`: Si no encuentra el botón de Quintana Roo.
   - `debug_search_error.png`: Si no encuentra el buscador.
   - `debug_status_not_found.png`: Si encontró el buscador pero no pudo interpretar el estatus de la tabla.
3. **Ajuste de Selectores en el código:**
   - Abre [check_focalizacion.py](file:///c:/Users/sams_/Downloads/JCF_SCRIPT/check_focalizacion.py).
   - Para cambiar el estado, ajusta la variable `STATE_ID` o la variable de entorno correspondiente.
   - Si cambia la clase del contenedor de la tabla, modifica `container_selector = "div.barridoTabla"` en la línea 110.
   - Si cambia el buscador de texto, modifica `input_selector = "input#myInput"` en la línea 79.
