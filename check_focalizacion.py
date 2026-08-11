import os
import sys
import time
import requests
from playwright.sync_api import sync_playwright

# Configuración mediante variables de entorno o valores por defecto
STATE_ID = os.environ.get("STATE_ID", "23")  # 23 es Quintana Roo
MUNICIPALITY_NAME = os.environ.get("MUNICIPALITY_NAME", "Solidaridad")
STATUS_FILE = os.environ.get("STATUS_FILE", "status.txt")
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "")
HEADLESS = os.environ.get("HEADLESS", "true").lower() == "true"

def send_notification(topic, title, message):
    """Envía una notificación push gratuita usando ntfy.sh"""
    url = f"https://ntfy.sh/{topic}"
    headers = {
        "Title": title.encode("utf-8"),
        "Priority": "5",
        "Tags": "bell,loudspeaker,mexico"
    }
    try:
        response = requests.post(url, data=message.encode("utf-8"), headers=headers, timeout=10)
        if response.status_code == 200:
            print("Notificación push enviada con éxito a ntfy.sh")
        else:
            print(f"Error al enviar a ntfy.sh (Código {response.status_code}): {response.text}")
    except Exception as e:
        print(f"Excepción al enviar notificación push: {e}")

def run():
    print("=== Iniciando consulta de focalización JCF ===")
    print(f"Estado ID: {STATE_ID}")
    print(f"Municipio objetivo: {MUNICIPALITY_NAME}")
    print(f"Modo Headless: {HEADLESS}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        url = "https://jovenesconstruyendoelfuturo.stps.gob.mx/focalizacion/"
        print(f"Navegando a: {url}")
        page.goto(url, wait_until="networkidle")

        # Paso 1: Localizar y hacer clic en el botón del Estado
        button_selector = f"button#edo_{STATE_ID}"
        try:
            print(f"Esperando el botón del estado con selector: {button_selector}")
            page.wait_for_selector(button_selector, timeout=15000)
            state_btn = page.locator(button_selector)
            state_btn.scroll_into_view_if_needed()
            state_btn.click()
            print("Botón del estado clickeado exitosamente.")
        except Exception as e:
            print(f"[Fallback] No se pudo hacer clic con '{button_selector}': {e}")
            print("Intentando localizar el botón del estado buscando 'QUINTANA ROO' en el texto de la página...")
            
            # Buscar elementos interactivos que tengan texto del estado
            buttons = page.locator("button, a, div").all()
            clicked_fallback = False
            for btn in buttons:
                try:
                    text = btn.inner_text().strip().upper()
                    if "QUINTANA ROO" in text and ("MUNICIPIO" in text or "VER" in text or btn.get_attribute("id") == f"edo_{STATE_ID}"):
                        print(f"Encontrado botón alternativo con texto: '{text}'. Clickeando...")
                        btn.scroll_into_view_if_needed()
                        btn.click()
                        clicked_fallback = True
                        break
                except Exception:
                    continue
            
            if not clicked_fallback:
                # Si falló, tomemos una captura si es posible para depurar
                try:
                    page.screenshot(path="debug_state_error.png")
                    print("Captura de pantalla de depuración guardada como 'debug_state_error.png'")
                except Exception:
                    pass
                raise Exception("No se pudo encontrar ni hacer clic en el botón del estado objetivo.")

        # Paso 2: Buscar el input de búsqueda de municipios
        input_selector = "input#myInput"
        try:
            print(f"Esperando el buscador de municipios con selector: {input_selector}")
            page.wait_for_selector(input_selector, timeout=10000)
            search_input = page.locator(input_selector)
            search_input.fill(MUNICIPALITY_NAME)
            print(f"Texto '{MUNICIPALITY_NAME}' ingresado en el buscador.")
        except Exception as e:
            print(f"[Fallback] No se pudo encontrar el buscador con '{input_selector}': {e}")
            print("Buscando input alternativo con placeholder que contenga 'Municipio'...")
            search_input = page.locator("input[placeholder*='Municipio']").first
            if search_input.count() > 0:
                search_input.fill(MUNICIPALITY_NAME)
                print(f"Texto '{MUNICIPALITY_NAME}' ingresado en el buscador alternativo.")
            else:
                try:
                    page.screenshot(path="debug_search_error.png")
                    print("Captura de pantalla de depuración guardada como 'debug_search_error.png'")
                except Exception:
                    pass
                raise Exception("No se pudo localizar el campo de búsqueda de municipios.")

        # Esperar a que se aplique el filtro en la tabla
        time.sleep(3)

        # Paso 3: Extraer el estatus del municipio objetivo
        container_selector = "div.barridoTabla"
        try:
            page.wait_for_selector(container_selector, timeout=10000)
            container = page.locator(container_selector)
            container_text = container.inner_text().strip()
            print("\n--- Contenido de texto extraído del contenedor de municipios ---")
            print(container_text)
            print("----------------------------------------------------------------\n")
        except Exception as e:
            raise Exception(f"No se pudo encontrar el contenedor de municipios '{container_selector}': {e}")

        # Buscar el estatus analizando las filas de la tabla
        rows = page.locator(f"{container_selector} tr").all()
        if not rows:
            # Fallback a elementos de lista o divs
            rows = page.locator(f"{container_selector} li").all()
        if not rows:
            rows = page.locator(f"{container_selector} div.row").all()

        found_status = None
        if rows:
            print(f"Se encontraron {len(rows)} filas/elementos en el contenedor.")
            for row in rows:
                try:
                    text = row.inner_text().strip()
                    if MUNICIPALITY_NAME.lower() in text.lower():
                        # Buscar palabras clave de estatus
                        for status_candidate in ["Municipio Abierto", "Meta Alcanzada", "Municipio Cerrado"]:
                            if status_candidate.lower() in text.lower():
                                found_status = status_candidate
                                print(f"-> Fila coincidente encontrada: '{text}' => Estatus: '{found_status}'")
                                break
                        if found_status:
                            break
                except Exception:
                    continue

        # Fallback de parseo de texto plano por líneas si fallaron las filas estructuradas
        if not found_status:
            print("[Fallback] Intentando buscar el estatus línea por línea en el bloque de texto...")
            lines = [line.strip() for line in container_text.split("\n") if line.strip()]
            for idx, line in enumerate(lines):
                if MUNICIPALITY_NAME.lower() in line.lower():
                    # Buscar en la misma línea o en las siguientes 2 líneas
                    for offset in [0, 1, 2]:
                        if idx + offset < len(lines):
                            candidate_line = lines[idx + offset]
                            for status_candidate in ["Municipio Abierto", "Meta Alcanzada", "Municipio Cerrado"]:
                                if status_candidate.lower() in candidate_line.lower():
                                    found_status = status_candidate
                                    print(f"-> Estatus '{found_status}' encontrado mediante fallback de líneas (línea original: '{line}')")
                                    break
                        if found_status:
                            break
                if found_status:
                    break

        if not found_status:
            # Depuración: imprimir el HTML completo si falló el parseo
            html_debug = container.inner_html()
            print("\n[ERROR] No se pudo encontrar el estatus. Mostrando HTML del contenedor para depuración:")
            print(html_debug)
            print("----------------------------------------------------------------\n")
            try:
                page.screenshot(path="debug_status_not_found.png")
                print("Captura de pantalla de depuración guardada como 'debug_status_not_found.png'")
            except Exception:
                pass
            raise Exception(f"No se pudo determinar el estatus para el municipio '{MUNICIPALITY_NAME}'.")

        # Paso 4: Comparar y Guardar Estado
        old_status = "Desconocido"
        if os.path.exists(STATUS_FILE):
            try:
                with open(STATUS_FILE, "r", encoding="utf-8") as f:
                    old_status = f.read().strip()
            except Exception as e:
                print(f"Advertencia: No se pudo leer el archivo de estatus anterior: {e}")

        print(f"Estatus Anterior: '{old_status}'")
        print(f"Estatus Actual: '{found_status}'")

        if found_status != old_status:
            print("¡Cambio de estatus detectado!")
            
            # Formatear el mensaje de notificación
            if old_status == "Desconocido":
                msg = f"Sistema inicializado. Estatus actual de {MUNICIPALITY_NAME}: {found_status}"
            else:
                msg = f"¡Alerta JCF! El municipio {MUNICIPALITY_NAME} cambió de '{old_status}' a '{found_status}'."

            if NTFY_TOPIC:
                title_notification = f"JCF: Cambio de Estatus en {MUNICIPALITY_NAME}"
                send_notification(NTFY_TOPIC, title_notification, msg)
            else:
                print("Advertencia: No se envió notificación push porque NTFY_TOPIC no está definida.")

            # Guardar el nuevo estatus en el archivo
            try:
                with open(STATUS_FILE, "w", encoding="utf-8") as f:
                    f.write(found_status)
                print(f"Nuevo estatus '{found_status}' guardado en '{STATUS_FILE}'.")
            except Exception as e:
                print(f"Error al escribir en el archivo de estatus: {e}")
        else:
            print("El estatus no ha cambiado. No se requiere notificación.")

        browser.close()

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print(f"\n[FATAL] Ocurrió un error al ejecutar el script: {e}")
        sys.exit(1)
