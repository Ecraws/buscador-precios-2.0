import streamlit as st
import pandas as pd
from PIL import Image
from pyzbar.pyzbar import decode

# Configuración de la página optimizada para celulares
st.set_page_config(
    page_title="Buscador de Precios", 
    page_icon="📱", 
    layout="centered"
)

# Estilos visuales para mejorar la interfaz en el celular
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #1f77b4; }
    .producto-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border-left: 5px solid #2ecc71;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📱 Buscador de Productos")

# Función optimizada para cargar los datos del Excel
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_excel("productos.xlsx")
        
        # Limpieza de datos para búsquedas efectivas
        df['desc_busqueda'] = df['Descripcion'].astype(str).str.lower().str.strip()
        df['scan_busqueda'] = df['codigoscanner'].astype(str).str.strip()
        
        # Limpiamos el Código Interno quitando decimales (.0) si existen
        df['interno_busqueda'] = df['Codigo Interno'].astype(str).apply(
            lambda x: x.split('.')[0] if '.' in x and x.split('.')[1] == '0' else x
        ).str.strip().str.lower()
        
        return df
    except Exception as e:
        st.error("⚠️ Error: Asegúrate de que el archivo se llame 'productos.xlsx' y tenga las columnas correctas en la fila 1.")
        return None

df = cargar_datos()

# Función para escanear el código de barras de la foto
def decodificar_codigo(imagen_capturada):
    try:
        img = Image.open(imagen_capturada)
        codigos = decode(img)
        if codigos:
            # Retorna el primer código de barras encontrado convertido en texto
            return codigos[0].data.decode('utf-8').strip()
    except Exception as e:
        pass
    return None

if df is not None:
    # Pestañas de navegación modernas
    tab1, tab2 = st.tabs(["🔍 Buscar Tipeando", "📷 Usar Cámara"])
    
    busqueda = ""
    
    # --- PESTAÑA 1: BÚSQUEDA MANUAL ---
    with tab1:
        busqueda_texto = st.text_input("Escribí Descripción, Scanner o Cód. Interno:", "").strip().lower()
        if busqueda_texto:
            busqueda = busqueda_texto

    # --- PESTAÑA 2: ESCÁNER AUTOMÁTICO ---
    with tab2:
        st.subheader("Escáner de Código de Barras")
        foto_codigo = st.camera_input("Apuntá al código de barras de cerca y con buena luz")
        
        if foto_codigo:
            with st.spinner("🔍 Leyendo código de barras..."):
                codigo_detectado = decodificar_codigo(foto_codigo)
                
                if codigo_detectado:
                    st.success(f"✅ Código detectado: {codigo_detectado}")
                    busqueda = codigo_detectado.lower()
                else:
                    st.error("❌ No se pudo leer el código. Intenta sacar la foto más de cerca, más quieto o con mejor iluminación.")
                    st.info("💡 Tip: Si el código es muy chico, recuerda que puedes usar la pestaña 'Buscar Tipeando' con el escáner del teclado de tu celular.")

    # --- LÓGICA DE BÚSQUEDA Y RESULTADOS ---
    if busqueda:
        # Buscamos coincidencias en las 3 columnas configuradas
        resultados = df[
            df['desc_busqueda'].str.contains(busqueda, na=False) | 
            df['scan_busqueda'].str.contains(busqueda, na=False) |
            df['interno_busqueda'].str.contains(busqueda, na=False)
        ]
        
        if not resultados.empty:
            st.markdown(f"### 📦 Se encontraron {len(resultados)} productos:")
            
            for index, fila in resultados.iterrows():
                # Formateo limpio de textos para evitar decimales molestos
                cod_int_texto = str(fila['Codigo Interno']).split('.')[0] if '.' in str(fila['Codigo Interno']) and str(fila['Codigo Interno']).split('.')[1] == '0' else str(fila['Codigo Interno'])
                scanner_texto = str(fila['codigoscanner']).split('.')[0] if '.' in str(fila['codigoscanner']) else str(fila['codigoscanner'])
                
                # Diseño de tarjeta para cada producto
                st.markdown(f"""
                <div class="producto-card">
                    <h2 style='margin:0; color:#2c3e50; font-size:22px;'>{fila['Descripcion']}</h2>
                    <h3 style='margin:5px 0; color:#2ecc71; font-size:26px;'>💰 ${fila['Precio']:,}</h3>
                    <p style='margin:0; color:#7f8c8d; font-size:14px;'>
                        🔢 <b>Cód. Interno:</b> {cod_int_texto if pd.notna(fila['Codigo Interno']) else 'N/A'} | 
                        📁 <b>Sector:</b> {fila['Descrip Sector'] if pd.notna(fila['Descrip Sector']) else 'N/A'}<br>
                        🏷️ <b>Scanner/EAN:</b> {scanner_texto if pd.notna(fila['codigoscanner']) else 'N/A'}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("🔍 No se encontraron productos con esos datos. Intenta con otra palabra.")
