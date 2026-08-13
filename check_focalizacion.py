import os
import sys
import json
import time
import requests
from playwright.sync_api import sync_playwright

# Listado oficial de estados según códigos de INEGI (01-32)
ESTADOS = {
    "01": "Aguascalientes",
    "02": "Baja California",
    "03": "Baja California Sur",
    "04": "Campeche",
    "05": "Coahuila",
    "06": "Colima",
    "07": "Chiapas",
    "08": "Chihuahua",
    "09": "Ciudad de México",
    "10": "Durango",
    "11": "Guanajuato",
    "12": "Guerrero",
    "13": "Hidalgo",
    "14": "Jalisco",
    "15": "Estado de México",
    "16": "Michoacán",
    "17": "Morelos",
    "18": "Nayarit",
    "19": "Nuevo León",
    "20": "Oaxaca",
    "21": "Puebla",
    "22": "Querétaro",
    "23": "Quintana Roo",
    "24": "San Luis Potosí",
    "25": "Sinaloa",
    "26": "Sonora",
    "27": "Tabasco",
    "28": "Tamaulipas",
    "29": "Tlaxcala",
    "30": "Veracruz",
    "31": "Yucatán",
    "32": "Zacatecas"
}

URL = "https://jovenesconstruyendoelfuturo.stps.gob.mx/focalizacion/"
HEADLESS = os.environ.get("HEADLESS", "true").lower() == "true"

# Credenciales leídas EXCLUSIVAMENTE de variables de entorno (sin defaults reales)
ONESIGNAL_APP_ID = os.environ.get("ONESIGNAL_APP_ID", "")
ONESIGNAL_REST_API_KEY = os.environ.get("ONESIGNAL_REST_API_KEY", "")
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "")

def load_health():
    """Carga el contador de fallas consecutivas y el estado de notificación de salud"""
    health_path = "data/salud_checker.json"
    if os.path.exists(health_path):
        try:
            with open(health_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "consecutive_failures": 0,
        "already_notified": False,
        "last_failure_type": ""
    }

def save_health(health):
    """Guarda el log de salud actual en disco"""
    health_path = "data/salud_checker.json"
    try:
        os.makedirs("data", exist_ok=True)
        with open(health_path, "w", encoding="utf-8") as f:
            json.dump(health, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error al escribir salud_checker.json: {e}")

def send_health_alert(topic, title, message):
    """Envía alerta de salud personal silenciosa mediante ntfy.sh"""
    if not topic:
        print("Advertencia: NTFY_TOPIC no configurada. Alerta de salud omitida.")
        return
    url = f"https://ntfy.sh/{topic}"
    headers = {
        "Title": title.encode("utf-8"),
        "Priority": "4",  # Prioridad alta para alertar, pero no molesta innecesariamente
        "Tags": "warning,skull"
    }
    try:
        response = requests.post(url, data=message.encode("utf-8"), headers=headers, timeout=10)
        if response.status_code == 200:
            print("Alerta de salud enviada con éxito a ntfy.sh.")
        else:
            print(f"Error al enviar a ntfy.sh (Código {response.status_code}): {response.text}")
    except Exception as e:
        print(f"Excepción al enviar alerta a ntfy.sh: {e}")

def send_onesignal_push(app_id, api_key, state_name, mun_name, old_status, new_status):
    """Envía una notificación web push usando OneSignal REST API con tags combinados (AND)"""
    if not app_id or not api_key:
        print("Error: Credenciales de OneSignal no configuradas. Saltando notificación.")
        return False
        
    url = "https://onesignal.com/api/v1/notifications"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {api_key}"
    }
    
    # Estatus amigable para el usuario
    estatus_es = "Abierto" if new_status == "abierto" else ("Meta Alcanzada" if new_status == "meta_alcanzada" else "Cerrado")
    msg = f"El municipio {mun_name} en {state_name} ahora está en estatus: {estatus_es}."
    
    body = {
        "app_id": app_id,
        "contents": {
            "es": msg
        },
        "headings": {
            "es": "Cambio de focalización JCF 🇲🇽"
        },
        "filters": [
            {"field": "tag", "key": "estado", "relation": "=", "value": state_name},
            {"field": "tag", "key": "municipio", "relation": "=", "value": mun_name}
        ]
    }
    
    try:
        response = requests.post(url, json=body, headers=headers, timeout=15)
        if response.status_code == 200:
            print(f"Push enviado con éxito para {mun_name}, {state_name}.")
            return True
        else:
            print(f"Error OneSignal API (Código {response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"Excepción al llamar a OneSignal API: {e}")
        return False

def parse_municipios(container_text):
    """Parsea el texto de la tabla y extrae nombres y estatus de los municipios"""
    municipios = {}
    lines = [line.strip() for line in container_text.split("\n") if line.strip()]
    
    for idx, line in enumerate(lines):
        status_key = None
        if "abierto" in line.lower():
            status_key = "abierto"
        elif "cerrado" in line.lower():
            status_key = "cerrado"
        elif "meta" in line.lower() or "alcanzada" in line.lower():
            status_key = "meta_alcanzada"
            
        if status_key and idx > 0:
            mun_name = lines[idx - 1]
            if not any(k in mun_name.lower() for k in ["abierto", "cerrado", "meta", "alcanzada"]):
                municipios[mun_name] = status_key
                
    return municipios

def run():
    print("=== Iniciando Checker de Focalización JCF ===")
    
    snap_path = "data/estados_municipios.json"
    if not os.path.exists(snap_path):
        print(f"[ERROR] Archivo {snap_path} no encontrado. Ejecuta primero descubrir_estados_municipios.py.")
        sys.exit(1)
        
    try:
        with open(snap_path, "r", encoding="utf-8") as f:
            snapshot_data = json.load(f)
    except Exception as e:
        print(f"[ERROR] No se pudo leer {snap_path}: {e}")
        sys.exit(1)
        
    health = load_health()
    error_occurred = False
    error_reasons = []
    
    successfully_scraped = {}
    onesignal_failures = []
    
    # Iniciar Playwright
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=HEADLESS)
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            for state_code, state_info in sorted(snapshot_data.items()):
                state_name = state_info["nombre"]
                print(f"\nConsultando {state_name} ({state_code})...")
                page = context.new_page()
                
                try:
                    # 1. Navegar al portal
                    response = page.goto(URL, wait_until="domcontentloaded", timeout=45000)
                    
                    # Verificar si hay bloqueo HTTP (403, 429, etc.)
                    if response and response.status in [403, 429]:
                        raise Exception(f"HTTP {response.status} - Bloqueo/Filtro del servidor JCF detectado.")
                    
                    # 2. Localizar y dar clic en el botón del Estado
                    state_val = int(state_code)
                    selector = f"button#edo_{state_val}, button#edo_{state_code}"
                    
                    page.wait_for_selector(selector, timeout=15000)
                    state_btn = page.locator(selector).first
                    state_btn.scroll_into_view_if_needed()
                    state_btn.click()
                    
                    # 3. Esperar la tabla
                    container_selector = "div.barridoTabla"
                    page.wait_for_selector(container_selector, timeout=15000)
                    
                    # 4. Scroll en la tabla
                    for scroll_step in range(6):
                        page.evaluate("document.querySelector('div.barridoTabla').scrollTop = document.querySelector('div.barridoTabla').scrollHeight")
                        page.wait_for_timeout(300)
                    
                    container = page.locator(container_selector)
                    container_text = container.inner_text().strip()
                    
                    # 5. Parsear municipios
                    municipios = parse_municipios(container_text)
                    if not municipios:
                        raise Exception("No se extrajeron municipios del contenedor.")
                        
                    successfully_scraped[state_code] = municipios
                    print(f"-> {len(municipios)} municipios leídos.")
                    
                except Exception as e:
                    print(f"Error procesando {state_name} ({state_code}): {e}")
                    error_reasons.append(f"{state_name}: {e}")
                finally:
                    page.close()
                    
            browser.close()
            
    except Exception as p_err:
        error_occurred = True
        error_reasons.append(f"Excepción Playwright: {p_err}")

    # --- VALIDACIÓN DE UMBRALES DE FALLA ---
    total_states = len(snapshot_data)
    failed_states_count = total_states - len(successfully_scraped)
    
    # 1. ¿Falla del 30% o más de los estados?
    if total_states > 0 and (failed_states_count / total_states) >= 0.30:
        error_occurred = True
        error_reasons.append(f"Falla crítica: {failed_states_count}/{total_states} estados no pudieron ser consultados (>= 30%).")
        
    # 2. ¿Hubo algún bloqueo HTTP?
    for reason in error_reasons:
        if "HTTP 403" in reason or "HTTP 429" in reason:
            error_occurred = True
            
    # --- COMPARACIÓN DE CAMBIOS Y ENVÍO DE NOTIFICACIONES ---
    # Procesamos solo los estados que se leyeron con éxito
    if not error_occurred or len(successfully_scraped) > 0:
        for state_code, current_muns in successfully_scraped.items():
            state_name = snapshot_data[state_code]["nombre"]
            cached_muns = snapshot_data[state_code]["municipios"]
            
            for mun_name, current_status in current_muns.items():
                old_status = cached_muns.get(mun_name)
                
                # Si existía estatus anterior y es diferente al actual, notificamos
                if old_status and old_status != current_status:
                    print(f"\n[ALERTA] ¡Cambio de estatus para {mun_name}, {state_name}! De '{old_status}' a '{current_status}'")
                    # Llamada a OneSignal API
                    success = send_onesignal_push(ONESIGNAL_APP_ID, ONESIGNAL_REST_API_KEY, state_name, mun_name, old_status, current_status)
                    if not success:
                        onesignal_failures.append(f"{mun_name} ({state_name})")
                
                # Actualizar el snapshot en memoria
                cached_muns[mun_name] = current_status

        # Escribir el nuevo estatus en disco si no hay una falla crítica total
        if len(successfully_scraped) > (total_states * 0.5): # Guardar solo si logramos leer más del 50%
            try:
                with open(snap_path, "w", encoding="utf-8") as f:
                    json.dump(snapshot_data, f, ensure_ascii=False, indent=2)
                print(f"\nEstatus actualizado guardado en '{snap_path}'.")
            except Exception as e:
                print(f"Error al escribir {snap_path}: {e}")

    # 3. ¿Errores al llamar la API de OneSignal?
    if onesignal_failures:
        error_occurred = True
        error_reasons.append(f"Error al enviar notificaciones de OneSignal para: {', '.join(onesignal_failures)}")

    # --- GESTIÓN DE ALERTAS DE SALUD OPERATIVAS (ntfy.sh) ---
    if error_occurred or len(error_reasons) > 0:
        # Hubo fallas
        health["consecutive_failures"] += 1
        failures_summary = " | ".join(error_reasons[:3]) # Resumen de los primeros 3 errores
        
        print(f"\n[SALUD] Falla operativa detectada. Consecutivas: {health['consecutive_failures']}")
        
        # Enviar alerta en la tercera falla consecutiva
        if health["consecutive_failures"] >= 3 and not health["already_notified"]:
            title = "CRÍTICO: Checker JCF reporta fallas consecutivas"
            msg = (
                f"El checker de focalización de JCF ha fallado {health['consecutive_failures']} veces seguidas.\n\n"
                f"Errores detectados:\n" + "\n".join(error_reasons)
            )
            send_health_alert(NTFY_TOPIC, title, msg)
            health["already_notified"] = True
            
        save_health(health)
        # Detener la ejecución con código de error para notificar en la Actions UI
        sys.exit(1)
    else:
        # Éxito completo
        print("\n=== Corrida del Checker Finalizada de Manera Exitosa ===")
        
        # Si estaba notificado de falla, avisar recuperación
        if health["already_notified"]:
            title = "RECUPERACIÓN: Checker JCF Funcionando"
            msg = "El sistema de monitoreo de JCF ha vuelto a completarse de forma normal y exitosa."
            send_health_alert(NTFY_TOPIC, title, msg)
            
        health["consecutive_failures"] = 0
        health["already_notified"] = False
        health["last_failure_type"] = ""
        save_health(health)

if __name__ == "__main__":
    run()
