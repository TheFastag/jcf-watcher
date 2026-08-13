# Alertas de Focalización JCF 🇲🇽

Este es un servicio gratuito y anónimo de notificaciones web push en tiempo real para recibir alertas en cuanto se abran las vacantes del programa **Jóvenes Construyendo el Futuro (JCF)** en tu municipio.

El sistema monitorea en segundo plano el portal oficial de focalización de la STPS y te avisa al instante para que seas de los primeros en solicitar tu registro cuando la plataforma abra.

---

## ✨ Características

- 📱 **Notificaciones en tiempo real:** Recibe avisos directo en tu celular, tablet o computadora (Chrome, Edge, Firefox, Brave, etc.).
- 🔒 **100% Anónimo:** No requerimos tu nombre, correo, CURP, teléfono ni ningún dato personal. Tu privacidad está completamente protegida.
- ⚡ **Sin registros:** No necesitas crear una cuenta, configurar contraseñas ni instalar aplicaciones externas en tu teléfono.
- 💸 **Totalmente gratis:** Servicio sin costo, libre de publicidad molesta o tarifas de suscripción.

---

## 🚀 Cómo activar tus avisos

1. **Visita la página web oficial de este proyecto:**
   *(Ingresa a la URL asignada a tu sitio web, por ejemplo: `https://tu-sitio.netlify.app`)*
2. **Selecciona tu localidad:**
   - En el paso 1, elige tu **Estado** de la lista.
   - En el paso 2, selecciona tu **Municipio**.
3. **Activa las notificaciones:**
   - Haz clic en el botón **"Activar Avisos Push"**.
   - Cuando tu navegador te muestre una pequeña ventana flotante preguntando si deseas permitir las notificaciones de esta página, haz clic en **"Permitir"** (o *Allow*).
4. **¡Listo!** Ya estás suscrito. Puedes cerrar la página y seguir usando tu teléfono con normalidad; la alerta te sonará en pantalla en cuanto el estatus de tu municipio pase a estar **Abierto**.

> [!TIP]
> Si en el futuro deseas recibir alertas de otro municipio diferente, simplemente vuelve a ingresar a la página, selecciona tu nuevo estado y municipio, y presiona el botón nuevamente para actualizar tu suscripción.

---

## 🔍 ¿Cómo funciona el sistema?

1. Un bot automatizado revisa de forma periódica el mapa de focalización de la plataforma oficial de JCF.
2. Compara el estatus de los 32 estados de México contra el último registro guardado.
3. Si el estatus de tu municipio cambia (por ejemplo, pasa de **"Municipio Cerrado"** a **"Municipio Abierto"**), el sistema envía instantáneamente un aviso a través del servicio de OneSignal que se distribuye a todos los navegadores suscritos a ese municipio.

---

## 🚫 Exención de Responsabilidad
Este es un proyecto de código abierto no oficial y de carácter únicamente informativo. No estamos afiliados, asociados, autorizados ni respaldados por la Secretaría del Trabajo y Previsión Social (STPS) ni por el programa oficial gubernamental de Jóvenes Construyendo el Futuro. 

El sistema **nunca** realiza el trámite ni el llenado de solicitudes por ti; su único propósito es avisarte para que tú ingreses manualmente al portal oficial a realizar tu solicitud con tus datos reales.
