# Personal Web Monitor (PoC - JCF) 📢

Este proyecto es un sistema personal de notificaciones web push en tiempo real que desarrollé para recibir alertas sobre cambios o actualizaciones en portales de mi interés. 

Como caso de estudio y prueba de concepto (PoC), el código se encuentra configurado para monitorear el estatus de focalización en el portal de Jóvenes Construyendo el Futuro (JCF) a nivel municipal en los 32 estados de México. Comparto este repositorio de manera abierta y sin ánimo de lucro como referencia de desarrollo o por si el concepto resulta útil para fines de prueba.

---

## 💡 Cómo funciona

1. Un bot automatizado en segundo plano consulta de forma periódica el portal de interés.
2. Compara el estado actual de los municipios contra un historial local.
3. Si el estatus de un municipio cambia (por ejemplo, de `"cerrado"` a `"abierto"`), el bot realiza una llamada a la API de OneSignal.
4. OneSignal distribuye un aviso Web Push al instante a todos los navegadores que hayan elegido suscribirse a ese estado y municipio.

---

## 🛠️ Cómo utilizar la prueba de concepto

Si deseas probar el funcionamiento del notificador para tu localidad:

1. **Visita la página web de prueba:**
   *(Ingresa a la URL pública donde se haya alojado la carpeta `site/`)*
2. **Selecciona tu localidad:**
   - Selecciona tu **Estado** de la lista desplegable.
   - Selecciona tu **Municipio** de la segunda lista desplegable.
3. **Activa las alertas:**
   - Haz clic en **"Activar Avisos Push"**.
   - Concede el permiso para recibir notificaciones cuando tu navegador de internet te lo solicite.
4. **¡Listo!** El navegador quedará registrado para recibir las alertas push automáticas de ese municipio en específico en caso de que ocurran cambios.

---

## ⚙️ Características técnicas

- **100% Anónimo:** No requiere CURP, correos, nombres ni ningún dato personal del usuario. Solo se almacena una etiqueta de suscripción anónima en los servidores de mensajería de OneSignal.
- **Sin cuentas:** No necesitas registrarte ni iniciar sesión.
- **Multiplataforma:** Las alertas llegan directo a tu pantalla tanto en móviles como en computadoras de escritorio a través de navegadores compatibles (Chrome, Firefox, Safari, Edge, Brave, etc.).

---

## 🚫 Exención de Responsabilidad
Este es un proyecto personal, de código abierto y con fines exclusivamente didácticos y de referencia. No tiene relación alguna, ni está avalado, afiliado o patrocinado por la Secretaría del Trabajo y Previsión Social (STPS), ni por el programa gubernamental de Jóvenes Construyendo el Futuro. 

Este software **no realiza trámites, registros ni llenado de formularios** de forma automática; su única función es servir como canal de avisos informativos para que el usuario sea quien realice cualquier trámite de manera manual y directa en los canales oficiales.
