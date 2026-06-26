import streamlit as st
import pandas as pd

# Configuración de página optimizada para rendimiento móvil
st.set_page_config(
    page_title="Buscador de Precios Flash", 
    page_icon="⚡", 
    layout="centered"
)

# Estilos CSS optimizados (Diseño ultraliviano, sin animaciones pesadas)
st.markdown("""
    <style>
    .main, .block-container {
        max-width: 100% !important;
        padding: 10px !important;
        overflow-x: hidden !important;
        background-color: #f8f9fa;
    }
    .producto-card {
        background-color: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.04);
        margin-top: 15px;
        margin-bottom: 15px;
        border-left: 12px solid #2ecc71;
    }
    .precio-enorme {
        color: #2ecc71;
        font-size: 95px;
        font-weight: 900;
        line-height: 0.85;
        margin: 15px 0 10px 0;
        letter-spacing: -3px;
        font-family: Arial, sans-serif;
    }
    .historial-item {
        background-color: #ffffff;
        padding: 10px 14px;
        border-radius: 8px;
        margin-bottom: 6px;
        border-left: 5px solid #34495e;
        font-size: 13px;
    }
    /* Estilo compacto para el formulario de entrada */
    div[data-testid="stForm"] {
        padding: 12px !important;
        border-radius: 14px !important;
        background-color: white !important;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.02) !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Buscador Flash Ultra")

# Motor de indexación instantánea (Carga una sola vez y crea mapas de búsqueda rápidos)
@st.cache_data(show_spinner=False)
def cargar_y_mapear_datos():
    try:
        df = pd.read_excel("productos.xlsx")
        
        # Limpieza estricta de datos básios
        df['Descripcion_Clean'] = df['Descripcion'].astype(str).str.strip()
        df['Precio_Clean'] = df['Precio'].fillna(0)
        
        # Formateo rápido de códigos para evitar decimales ocultos (.0)
        df['cod_interno_clean'] = df['Codigo Interno'].astype(str).apply(
            lambda x: x.split('.')[0] if '.' in x and x.split('.')[1] == '0' else x
        ).str.strip().str.lower()
        
        df['cod_scanner_clean'] = df['codigoscanner'].astype(str).apply(
            lambda x: x.split('.')[0] if '.' in x else x
        ).str.strip().str.lower()
        
        # Creamos mapas de búsqueda directa (Indices en memoria O(1))
        mapa_codigos = {}
        
        # Mapeamos primero por código interno
        for _, fila in df.iterrows():
            int_code = fila['cod_interno_clean']
            scan_code = fila['cod_scanner_clean']
            
            prod_info = {
                'desc': fila['Descripcion_Clean'],
                'precio': fila['Precio_Clean'],
                'interno': int_code,
                'sector': str(fila['Descrip Sector']).strip() if pd.notna(fila['Descrip Sector']) else 'N/A',
                'scanner': scan_code
            }
            
            if int_code and int_code != 'nan':
                mapa_codigos[int_code] = prod_info
            if scan_code and scan_code != 'nan':
                mapa_codigos[scan_code] = prod_info
                
        return df, mapa_codigos
    except Exception as e:
        st.error("⚠️ Error al procesar 'productos.xlsx'. Asegúrate de que esté en la raíz de tu GitHub.")
        return None, None

df, mapa_rapido = cargar_y_mapear_datos()

if df is not None:
    # Inicialización del historial
    if 'historial' not in st.session_state:
        st.session_state.historial = []

    # --- FORMULARIO DE CONSULTA INSTANTÁNEA ---
    with st.form(key="formulario_busqueda", clear_on_submit=False):
        busqueda = st.text_input(
            "🔍 Ingresá Código (Scanner o Interno) o Texto:", 
            placeholder="Escribí y presioná Ir / Enter...",
            key="input_text"
        ).strip().lower()
        
        # Botón de ejecución optimizado de ancho completo
        bot_buscar = st.form_submit_button("🚀 BUSCAR PRECIO YA", use_container_width=True)

    # Botón secundario para limpiar rápido si ya hay algo en pantalla
    if busqueda:
        if st.button("❌ LIMPIAR PANTALLA", use_container_width=True):
            st.rerun()

    # --- PROCESADOR ULTRA VELOZ ---
    if busqueda:
        producto_encontrado = None
        
        # INTENTO 1: Búsqueda exacta y directa en el mapa de memoria (Cero milisegundos)
        if busqueda in mapa_rapido:
            producto_encontrado = mapa_rapido[busqueda]
            resultados_lista = [producto_encontrado]
        else:
            # INTENTO 2: Si no es un código exacto, busca por texto en las descripciones (Plan B)
            res_df = df[df['Descripcion_Clean'].str.lower().str.contains(busqueda, na=False)]
            if not res_df.empty:
                resultados_lista = []
                for _, fila in res_df.head(3).iterrows(): # Limitamos a los 3 mejores para no congelar el celular
                    resultados_lista.append({
                        'desc': fila['Descripcion_Clean'],
                        'precio': fila['Precio_Clean'],
                        'interno': fila['cod_interno_clean'],
                        'sector': str(fila['Descrip Sector']).strip() if pd.notna(fila['Descrip Sector']) else 'N/A',
                        'scanner': fila['cod_scanner_clean']
                    })
            else:
                resultados_lista = []

        # --- MOSTRAR RESULTADOS ---
        if resultados_lista:
            # Historial ultra rápido
            primer_item = resultados_lista[0]
            item_historial = f"{primer_item['desc']} - **${primer_item['precio']:,}**"
            if not st.session_state.historial or st.session_state.historial[0] != item_historial:
                st.session_state.historial.insert(0, item_historial)
                if len(st.session_state.historial) > 4:
                    st.session_state.historial.pop()

            st.markdown("### 📦 Producto Encontrado:")
            
            for prod in resultados_lista:
                st.markdown(f"""
                <div class="producto-card">
                    <h2 style='margin:0; color:#2c3e50; font-size:24px; font-weight:700;'>{prod['desc']}</h2>
                    <p class="precio-enorme">💰 ${prod['precio']:,}</p>
                    <p style='margin:0; color:#7f8c8d; font-size:15px; line-height: 1.6; border-top: 1px solid #eee; padding-top: 12px; margin-top: 5px;'>
                        🔢 <b>Cód. Interno:</b> <span style="color:#2c3e50;">{prod['interno'] if prod['interno'] != 'nan' else 'N/A'}</span><br>
                        📁 <b>Sector:</b> <span style="color:#2c3e50;">{prod['sector']}</span><br>
                        🏷️ <b>Scanner / EAN:</b> <span style="color:#2c3e50;">{prod['scanner'] if prod['scanner'] != 'nan' else 'N/A'}</span>
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning(f"🔍 No se encontró nada para: '{busqueda}'.")

    # --- HISTORIAL RECIENTE ---
    if st.session_state.historial:
        st.write("---")
        st.subheader("📋 Últimas búsquedas:")
        for item in st.session_state.historial:
            st.markdown(f'<div class="historial-item">🔹 {item}</div>', unsafe_allow_html=True)
