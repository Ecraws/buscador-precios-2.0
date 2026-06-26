import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# Configuración de la página para celulares
st.set_page_config(
    page_title="Buscador de Precios Pro", 
    page_icon="📱", 
    layout="centered"
)

# Estilos visuales de la aplicación
st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    .producto-card {
        background-color: white;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border-left: 6px solid #2ecc71;
    }
    .precio-destacado {
        color: #2ecc71;
        font-size: 36px;
        font-weight: bold;
        margin: 5px 0;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📱 Buscador de Productos")

# Carga de datos desde el Excel
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_excel("productos.xlsx")
        df['desc_busqueda'] = df['Descripcion'].astype(str).str.lower().str.strip()
        df['scan_busqueda'] = df['codigoscanner'].astype(str).str.strip()
        df['interno_busqueda'] = df['Codigo Interno'].astype(str).apply(
            lambda x: x.split('.')[0] if '.' in x and x.split('.')[1] == '0' else x
        ).str.strip().str.lower()
        return df
    except Exception as e:
        st.error("⚠️ No se pudo cargar 'productos.xlsx'. Verifica los nombres de tus columnas en la fila 1.")
        return None

df = cargar_datos()

if df is not None:
    # LÍNEA 54 CORREGIDA: Inicializamos las variables en la memoria si no existen
    if 'buscar_este_codigo' not in st.session_state:
        st.session_state.buscar_este_codigo = ""

    # Capturamos de forma oculta e inmediata lo que envíe el JavaScript de la cámara
    if 'barcode_detected' in st.session_state and st.session_state.barcode_detected:
        nuevo_codigo = str(st.session_state.barcode_detected).strip()
        if nuevo_codigo and nuevo_codigo != st.session_state.buscar_este_codigo:
            st.session_state.buscar_este_codigo = nuevo_codigo
            st.session_state.barcode_detected = "" # Limpiamos el puente para la próxima
            st.rerun() # Fuerza a la app a buscar YA el producto

    # Pestañas de navegación
    tab1, tab2 = st.tabs(["🔍 Buscar Tipeando", "📷 Lector de Barras HD"])
    
    # --- PESTAÑA 1: BÚSQUEDA MANUAL ---
    with tab1:
        busqueda_texto = st.text_input("Escribí Descripción, Scanner o Cód. Interno:", key="manual_search").strip().lower()
        if busqueda_texto:
            st.session_state.buscar_este_codigo = busqueda_texto

    # --- PESTAÑA 2: CÁMARA ESCÁNER AUTOMÁTICO ---
    with tab2:
        # Si ya hay un producto buscado, apagamos la cámara temporalmente
        if st.session_state.buscar_este_codigo:
            st.write("✨ ¡Escaneo realizado con éxito!")
            if st.button("📷 Escanear otro producto", type="primary"):
                st.session_state.buscar_este_codigo = ""
                st.rerun()
        else:
            st.subheader("Escáner de Alta Precisión")
            st.write("Coloca el código horizontalmente sobre la línea roja.")
            
            html_code = """
            <div style="text-align: center; position: relative;">
                <div id="interactive" class="viewport" style="width: 100%; max-width: 400px; height: 230px; border: 3px solid #2ecc71; border-radius: 12px; overflow: hidden; margin: 0 auto; background-color: #000; position: relative;">
                    <video autoplay playsinline style="width: 100%; height: 100%; object-fit: cover;"></video>
                    <div style="position: absolute; top: 50%; left: 5%; width: 90%; height: 2px; background-color: red; opacity: 0.7; pointer-events: none;"></div>
                </div>
                <p id="resultado" style="font-weight: bold; color: #2ecc71; margin-top: 10px; font-size: 16px;">Escaneando activamente...</p>
            </div>
            
            <script src="https://cdnjs.cloudflare.com/ajax/libs/quagga/0.12.1/quagga.min.js"></script>
            
            <script>
            Quagga.init({
                inputStream: {
                    name: "Live",
                    type: "LiveStream",
                    target: document.querySelector('#interactive'),
                    constraints: {
                        width: { min: 1280, ideal: 1280 },
                        height: { min: 720, ideal: 720 },
                        facingMode: "environment",
                        focusMode: "continuous"
                    },
                },
                locator: { patchSize: "medium", halfSample: false },
                decoder: { readers: ["ean_reader", "ean_8_reader", "code_128_reader"] },
                locate: true
            }, function(err) {
                if (err) {
                    document.getElementById('resultado').innerText = "Error: Activa los permisos de cámara.";
                    document.getElementById('resultado').style.color = "red";
                    return;
                }
                Quagga.start();
            });

            Quagga.onDetected(function(data) {
                if (data.codeResult && data.codeResult.code) {
                    const codigo = data.codeResult.code;
                    if(codigo.length >= 5) {
                        document.getElementById('resultado').innerText = "¡Código detectado!: " + codigo;
                        
                        // Enviamos el dato a Streamlit de inmediato
                        window.parent.postMessage({
                            type: 'streamlit:set_widget_value',
                            key: 'barcode_detected',
                            value: codigo
                        }, '*');
                        
                        if (navigator.vibrate) navigator.vibrate(200);
                        Quagga.stop(); 
                    }
                }
            });
            </script>
            """
            components.html(html_code, height=290)

    # --- MOSTRAR RESULTADOS DE BÚSQUEDA AUTOMÁTICA ---
    codigo_a_buscar = st.session_state.buscar_este_codigo.lower().strip()
    
    if codigo_a_buscar:
        resultados = df[
            df['desc_busqueda'].str.contains(codigo_a_buscar, na=False) | 
            df['scan_busqueda'].str.contains(codigo_a_buscar, na=False) |
            df['interno_busqueda'].str.contains(codigo_a_buscar, na=False)
        ]
        
        if not resultados.empty:
            st.markdown(f"### 📦 Resultado de búsqueda para: **{st.session_state.buscar_este_codigo}**")
            
            for index, fila in resultados.iterrows():
                cod_int_texto = str(fila['Codigo Interno']).split('.')[0] if '.' in str(fila['Codigo Interno']) and str(fila['Codigo Interno']).split('.')[1] == '0' else str(fila['Codigo Interno'])
                scanner_texto = str(fila['codigoscanner']).split('.')[0] if '.' in str(fila['codigoscanner']) else str(fila['codigoscanner'])
                
                st.markdown(f"""
                <div class="producto-card">
                    <h2 style='margin:0; color:#2c3e50; font-size:22px;'>{fila['Descripcion']}</h2>
                    <p class="precio-destacado">💰 ${fila['Precio']:,}</p>
                    <p style='margin:0; color:#7f8c8d; font-size:14px; line-height: 1.6;'>
                        🔢 <b>Cód. Interno:</b> {cod_int_texto if pd.notna(fila['Codigo Interno']) else 'N/A'}<br>
                        📁 <b>Sector:</b> {fila['Descrip Sector'] if pd.notna(fila['Descrip Sector']) else 'N/A'}<br>
                        🏷️ <b>Scanner/EAN:</b> {scanner_texto if pd.notna(fila['codigoscanner']) else 'N/A'}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("❌ Limpiar búsqueda actual"):
                st.session_state.buscar_este_codigo = ""
                st.rerun()
        else:
            st.warning(f"🔍 El código '{st.session_state.buscar_este_codigo}' no se encuentra en el archivo Excel.")
            if st.button("🔄 Intentar con otro código"):
                st.session_state.buscar_este_codigo = ""
                st.rerun()
