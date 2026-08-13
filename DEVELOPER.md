# Guía del Desarrollador - JCF Focalización Watcher 🛠️

Este documento contiene la información técnica para el administrador de la plataforma. **Mantén esta información privada o separada** si no quieres exponer la arquitectura interna o tus endpoints de mantenimiento.

---

## 📁 Estructura del Repositorio
- `site/index.html` — La página pública de suscripción para los usuarios.
- `site/data.json` — Catálogo estático de nombres de estados y municipios.
- `data/estados_municipios.json` — Base de datos interna del estatus de focalización actual.
- `data/salud_checker.json` — Archivo de control para evitar saturación de alarmas de salud.
- `check_focalizacion.py` — El checker principal de 32 estados.
- `descubrir_estados_municipios.py` — Script inicial para poblar el catálogo de municipios.
- `netlify.toml` — Configuración que evita el consumo de créditos en Netlify.

---

## 🚀 Despliegue en la Nube (Auto-Deploy Gratis)

### 1. Alojar la página web en Netlify
1. Crea una cuenta gratuita en [Netlify](https://netlify.com) conectando tu cuenta de GitHub.
2. Añade un nuevo sitio seleccionando **Import from Git** y elige tu repositorio `jcf-watcher`.
3. Netlify detectará automáticamente el archivo [netlify.toml](file:///c:/Users/sams_/Downloads/JCF_SCRIPT/netlify.toml). Este archivo contiene una regla de ignorado inteligente:
   ```toml
   [build]
     publish = "site"
     ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- site/"
   ```
   **Esta regla es crucial.** Le dice a Netlify que **no reconstruya ni despliegue el sitio** si los cambios ocurren fuera de la carpeta `site/`. Como el checker hace commits continuos en la carpeta `data/` para actualizar el estatus de los municipios, esto previene que gastes tus minutos de despliegue de Netlify de forma innecesaria. No borres ni edites este archivo.

### 2. Configurar OneSignal (Web Push para Usuarios)
1. Crea una cuenta gratuita en [OneSignal](https://onesignal.com).
2. Crea una nueva aplicación de tipo **Web Push**.
3. En la configuración de Web Push, ingresa la URL que te asignó Netlify para tu sitio web.
4. **App ID Público:** Abre el archivo [site/index.html](file:///c:/Users/sams_/Downloads/JCF_SCRIPT/site/index.html) y reemplaza la cadena `TU_ONESIGNAL_APP_ID_AQUI` con tu App ID real de OneSignal. *(Nota: Este ID es público y está diseñado para estar en el navegador del usuario final).*
5. **REST API Key Secreta:** Obtén tu clave API en Settings > API Keys de OneSignal. Esta clave es **secreta** y nunca debe quedar escrita en tu código.

### 3. Configurar GitHub Secrets y Permisos
Ve a tu repositorio en GitHub y configura los siguientes valores:
1. **GitHub Secrets:** En Settings > Secrets and variables > Actions, haz clic en **New repository secret** y agrega:
   - `ONESIGNAL_APP_ID` - Tu App ID público de OneSignal.
   - `ONESIGNAL_REST_API_KEY` - Tu API Key de OneSignal (empieza con `Basic...` o tu clave directa).
   - `NTFY_TOPIC` - Tu tema de notificaciones personales de ntfy.sh (para alertas de fallas).
2. **Permisos de Escritura:** En Settings > Actions > General, navega hasta el final y en **Workflow permissions** selecciona **Read and write permissions** y guarda.

---

## 🛠️ Lógica de Alertas de Salud (ntfy.sh)

Para evitar que tu celular se sature con mensajes innecesarios, el script implementa una lógica anti-saturación:
1. **Detección de Error:** Si la consulta de JCF falla (bloqueo HTTP 403/429, error en el script, fallo del API de OneSignal, o si no se pueden leer el 30% o más de los estados), se suma 1 al contador de fallas consecutivas en `data/salud_checker.json`.
2. **Umbral de Alerta:** Solo te llegará un mensaje push a tu tema de ntfy (ej. `mi-alerta-jcf-solidaridad`) si el checker falla **3 veces consecutivas**. *(Puedes ajustar este valor editando `check_focalizacion.py` en la línea 324).*
3. **Silenciamiento:** Una vez enviado el mensaje de alerta, no se enviarán más notificaciones en las siguientes ejecuciones fallidas.
4. **Recuperación:** Cuando la página de JCF responda con éxito nuevamente, se te enviará un **único mensaje de recuperación** y el contador se reseteará a cero.

---

## 📅 Calendario de Ejecución y Concurrencia
El workflow [.github/workflows/check.yml](file:///c:/Users/sams_/Downloads/JCF_SCRIPT/.github/workflows/check.yml) corre con frecuencia variable:
- **Periodo Frecuente (Cada 10 minutos):** Del día 1 al 15 de meses pares (Feb, Abr, Jun, Ago, Oct, Dic), que es la ventana histórica donde suelen ocurrir las aperturas.
- **Periodo Espaciado (Cada 30 minutos):** El resto del año.
*(Nota: Este calendario es una observación empírica de la comunidad, no una programación oficial de la STPS).*

Para evitar que los trabajos de 2.5 minutos se empalmen si el portal de JCF tarda demasiado en responder, el workflow tiene activa la concurrencia:
```yaml
concurrency:
  group: jcf-checker
  cancel-in-progress: false
```

---

## 🔐 Seguridad
Dado que tu repositorio debe ser público para obtener minutos gratuitos ilimitados de GitHub Actions:
- **Cero claves en el código:** `ONESIGNAL_REST_API_KEY` y `NTFY_TOPIC` se leen exclusivamente a través de variables de entorno y se configuran de forma segura en los Secrets de tu repositorio en GitHub.
- **Exclusiones:** El archivo [.gitignore](file:///c:/Users/sams_/Downloads/JCF_SCRIPT/.gitignore) se encuentra configurado para excluir archivos locales `.env` o capturas de depuración.
- **Secret Scanning:** Te recomendamos activar la opción gratuita en tu repositorio: **Settings** > **Security** > **Secret scanning** > clic en **Enable**. Esto escaneará tus commits automáticamente y te alertará si subes un token por accidente.

---

## 🔧 Mantenimiento
Las páginas gubernamentales cambian de diseño ocasionalmente. Si el checker comienza a fallar de forma continua, el sistema te avisará a ntfy. El único mantenimiento requerido es revisar la pestaña **Actions** de tu repositorio para examinar los logs de error y actualizar los selectores de búsqueda en `check_focalizacion.py` si la estructura del sitio oficial cambia.
