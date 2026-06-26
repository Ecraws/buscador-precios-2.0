import streamlit as st
import pandas as pd

# Configuración de página optimizada para rendimiento móvil
st.set_page_config(
    page_title="Buscador de Precios Flash Pro", 
    page_icon="⚡", 
    layout="centered"
)

# Estilos CSS Avanzados (Cartas estilizadas, precios corregidos y limpios)
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
        padding: 22px;
        border-radius: 18px;
        box-shadow: 0px 5px 20px rgba(0,0,0,0.04);
        margin-top: 12px;
        margin-bottom: 12px;
        border-left: 12px solid #2ecc71;
    }
    .precio-enorme {
        color: #2ecc71;
        font-size: 65px;
        font-weight: 900;
        line-height: 1.0;
        margin: 10px 0;
        letter-spacing: -2px;
        font-family: 'Arial Black', sans-serif;
    }
    .historial-item {
        background-color: #ffffff;
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 6px;
        border-left: 5px solid #34495e;
        font-size: 14px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.02);
    }
    div[data-testid="stForm"] {
        padding: 12px !important;
        border-radius: 14px !important;
        background-color: white !important;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.01) !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Buscador Flash Ultra")

# Función optimizada para formatear precios sin centavos rotos y con puntos de miles locales
def formatear_precio(valor):
    try:
        # Redondeamos a entero para eliminar centavos raros (.043, .81)
        entero = round(float(valor))
        return f"${entero:,.0f}".replace(",", ".")
    except:
        return f"${valor}"

# Motor de indexación instantánea en memoria
@st.cache_data(show_spinner=False)
def cargar_y_mapear_datos():
    try:
        df = pd.read_excel("productos.xlsx")
        
        # Limpieza base de campos
        df['Descripcion_Clean'] = df['Descripcion'].astype(str).str.strip()
        df['Precio_Clean'] = df['Precio'].fillna(0)
        
        # Formateo de códigos evitando flotantes (.0)
        df['cod_interno_clean'] = df['Codigo Interno'].astype(str).apply(
            lambda x: x.split('.')[0] if '.' in x and x.split('.')[1] == '0' else x
        ).str.strip().str.lower()
        
        df['cod_scanner_clean'] = df['codigoscanner'].astype(str).apply(
            lambda x: x.split('.')[0] if '.' in x else x
        ).str.strip().str.lower()
        
        # Diccionario para búsquedas O(1) de códigos exactos
        mapa_codigos = {}
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
        st.error("⚠️ Error crítico: Verifica 'productos.xlsx' en la raíz de tu GitHub.")
        return None, None

df, mapa_rapido = cargar_y_mapear_datos()

if df is not None:
    # Gestión del historial en sesión
    if 'historial' not in st.session_state:
        st.session_state.historial = []

    # --- FORMULARIO DE ENTRADA DIGITAL ---
    with st.form(key="formulario_busqueda", clear_on_submit=False):
        busqueda = st.text_input(
            "🔍 Ingresá Código o Nombre del Producto:", 
            placeholder="Escribí aquí y presioná Enter o Buscar...",
            key="input_text"
        ).strip().lower()
        
        bot_buscar = st.form_submit_button("🚀 BUSCAR PRECIO YA", use_container_width=True)

    if busqueda:
        if st.button("❌ LIMPIAR PANTALLA", use_container_width=True):
            st.rerun()

    # --- PROCESAMIENTO LOGÍSTICO DE BÚSQUEDA ---
    if busqueda:
        resultados_lista = []
        
        # Intento 1: Mapeo directo por código de barra o interno
        if busqueda in mapa_rapido:
            resultados_lista.append(mapa_rapido[busqueda])
        else:
            # Intento 2: Filtrado por texto si no es un código numérico exacto
            res_df = df[df['Descripcion_Clean'].str.lower().str.contains(busqueda, na=False)]
            if not res_df.empty:
                for _, fila in res_df.iterrows():
                    resultados_lista.append({
                        'desc': fila['Descripcion_Clean'],
                        'precio': fila['Precio_Clean'],
                        'interno': fila['cod_interno_clean'],
                        'sector': str(fila['Descrip Sector']).strip() if pd.notna(fila['Descrip Sector']) else 'N/A',
                        'scanner': fila['cod_scanner_clean']
                    })

        # --- DESPLIEGUE DE RESULTADOS Y CARTAS ---
        if resultados_lista:
            
            # CONTROL INTERACTIVO DE HISTORIAL: Si hay múltiples resultados, dejamos que el usuario elija
            st.markdown("### 📥 Guardar en Recientes:")
            opciones_historial = [f"{p['desc']} ({formatear_precio(p['precio'])})" for p in resultados_lista]
            
            # Selector inteligente para decidir qué mandar al historial
            seleccion_prod = st.selectbox(
                "Seleccioná qué producto agregar a tus últimas búsquedas:",
                options=opciones_historial,
                key="selector_historial"
            )
            
            # Botón de confirmación manual para agregar al historial
            if st.button("📌 AGREGAR A RECIENTES", use_container_width=True):
                if seleccion_prod:
                    # Buscamos el elemento correspondiente en la lista
                    idx = opciones_historial.index(seleccion_prod)
                    prod_elegido = resultados_lista[idx]
                    item_historial = f"{prod_elegido['desc']} - **{formatear_precio(prod_elegido['precio'])}**"
                    
                    if not st.session_state.historial or st.session_state.historial[0] != item_historial:
                        st.session_state.historial.insert(0, item_historial)
                        if len(st.session_state.historial) > 5:
                            st.session_state.historial.pop()
                    st.success("¡Producto guardado en la lista de abajo!")
            
            st.write("---")
            st.markdown(f"### 📦 Productos Encontrados ({len(resultados_lista)}):")
            
            # Renderizado individual de las cartas mejoradas
            for prod in resultados_lista:
                precio_visual = formatear_precio(prod['precio'])
                
                st.markdown(f"""
                <div class="producto-card">
                    <h2 style='margin:0; color:#2c3e50; font-size:22px; font-weight:700;'>{prod['desc']}</h2>
                    <p class="precio-enorme">💰 {precio_visual}</p>
                    <p style='margin:0; color:#7f8c8d; font-size:14px; line-height: 1.6; border-top: 1px solid #eee; padding-top: 10px; margin-top: 5px;'>
                        🔢 <b>Cód. Interno:</b> <span style="color:#2c3e50;">{prod['interno'] if prod['interno'] != 'nan' else 'N/A'}</span><br>
                        📁 <b>Sector:</b> <span style="color:#2c3e50;">{prod['sector']}</span><br>
                        🏷️ <b>Scanner / EAN:</b> <span style="color:#2c3e50;">{prod['scanner'] if prod['scanner'] != 'nan' else 'N/A'}</span>
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning(f"🔍 No se encontró ningún artículo para: '{busqueda}'.")

    # --- HISTORIAL DE ÚLTIMAS BÚSQUEDAS ---
    if st.session_state.historial:
        st.write("---")
        st.subheader("📋 Últimas búsquedas guardadas:")
        for item in st.session_state.historial:
            st.markdown(f'<div class="historial-item">🔹 {item}</div>', unsafe_allow_html=True)
