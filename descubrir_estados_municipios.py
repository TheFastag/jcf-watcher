import os
import sys
import json
import time
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
            # Evitar capturar palabras de estatus como nombres de municipio por error
            if not any(k in mun_name.lower() for k in ["abierto", "cerrado", "meta", "alcanzada"]):
                municipios[mun_name] = status_key
                
    return municipios

def run():
    print("=== Iniciando Script de Descubrimiento de Municipios ===")
    
    # Crear carpetas de datos si no existen
    os.makedirs("data", exist_ok=True)
    os.makedirs("site", exist_ok=True)
    
    # Permitir filtrar estados por argumento en consola para acelerar pruebas locales
    target_states = sys.argv[1:] if len(sys.argv) > 1 else sorted(list(ESTADOS.keys()))
    print(f"Estados a escanear ({len(target_states)}): {', '.join(target_states)}")
    
    # Cargar snapshots anteriores si existen para no perder datos si hay fallas parciales
    snap_path = "data/estados_municipios.json"
    full_data = {}
    if os.path.exists(snap_path):
        try:
            with open(snap_path, "r", encoding="utf-8") as f:
                full_data = json.load(f)
        except Exception as e:
            print(f"No se pudo cargar el archivo actual {snap_path}: {e}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        for state_code in target_states:
            state_name = ESTADOS.get(state_code)
            if not state_name:
                print(f"Código de estado desconocido: {state_code}. Saltando.")
                continue
                
            print(f"\n---> Escaneando Estado: {state_name} ({state_code})")
            page = context.new_page()
            
            try:
                # 1. Navegar a la página
                page.goto(URL, wait_until="domcontentloaded", timeout=45000)
                
                state_val = int(state_code)
                selector = f"button#edo_{state_val}, button#edo_{state_code}"
                
                page.wait_for_selector(selector, timeout=15000)
                state_btn = page.locator(selector).first
                state_btn.scroll_into_view_if_needed()
                state_btn.click()
                
                # 3. Esperar a que cargue la lista
                container_selector = "div.barridoTabla"
                page.wait_for_selector(container_selector, timeout=15000)
                
                # 4. Desplazar hacia abajo en la tabla/contenedor para lazy loading
                # Algunos estados tienen muchísimos municipios (ej. Oaxaca)
                print(f"[{state_name}] Desplazando contenedor para cargar elementos...")
                for scroll_step in range(6):
                    page.evaluate("document.querySelector('div.barridoTabla').scrollTop = document.querySelector('div.barridoTabla').scrollHeight")
                    page.wait_for_timeout(300)
                
                # Obtener el contenido final de la lista
                container = page.locator(container_selector)
                container_text = container.inner_text().strip()
                
                # 5. Parsea la lista
                municipios = parse_municipios(container_text)
                print(f"[{state_name}] ¡Éxito! Se encontraron {len(municipios)} municipios.")
                
                # Guardar en nuestro diccionario temporal
                full_data[state_code] = {
                    "nombre": state_name,
                    "municipios": municipios
                }
                
            except Exception as e:
                print(f"[ERROR] Error al procesar {state_name} ({state_code}): {e}")
                # Mantener datos anteriores si la consulta de este estado falló
                if state_code not in full_data:
                    full_data[state_code] = {
                        "nombre": state_name,
                        "municipios": {}
                    }
            finally:
                page.close()
                
        browser.close()
        
    # Guardar archivo de estatus interno (estados_municipios.json)
    with open(snap_path, "w", encoding="utf-8") as f:
        json.dump(full_data, f, ensure_ascii=False, indent=2)
    print(f"\nArchivo guardado: {snap_path}")
    
    # Generar catálogo público para el frontend (site/data.json - solo nombres sin estatus)
    catalog = {}
    for code, info in sorted(full_data.items()):
        catalog[code] = {
            "nombre": info["nombre"],
            "municipios": sorted(list(info["municipios"].keys()))
        }
        
    catalog_path = "site/data.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
    print(f"Catálogo público guardado: {catalog_path}")
    
    print("\n=== Escaneo de Descubrimiento Completado ===")

if __name__ == "__main__":
    run()
