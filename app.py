import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# Configuración de la página para celulares
st.set_page_config(
    page_title="Buscador de Precios Pro", 
    page_icon="📱", 
    layout="centered"
)

# Estilos visuales de la aplicación (Tarjetas de productos modernas)
st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    .producto-card {
        background-color: white;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border-left: 6px solid #00b4d8;
    }
    .precio-destacado {
        color: #2ecc71;
        font-size: 28px;
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
    # Navegación por pestañas
    tab1, tab2 = st.tabs(["🔍 Buscar Tipeando", "📷 Escáner en Vivo"])
    
    codigo_escaneado = ""
    
    # --- PESTAÑA 1: BÚSQUEDA MANUAL ---
    with tab1:
        busqueda_texto = st.text_input("Escribí Descripción, Scanner o Cód. Interno:", key="manual_search").strip().lower()
        if busqueda_texto:
            codigo_escaneado = busqueda_texto

    # --- PESTAÑA 2: CÁMARA ESCÁNER EN VIVO ---
    with tab2:
        st.subheader("Escáner de Código de Barras")
        st.write("Apunta la cámara hacia el código de barras del producto.")
        
        # Usamos un componente HTML5/JavaScript para activar la cámara en modo video continuo
        # Este script utiliza la API nativa BarcodeDetector admitida por la mayoría de celulares modernos
        html_code = """
        <div style="text-align: center;">
            <video id="video" width="100%" height="auto" style="border: 2px solid #00b4d8; border-radius: 10px; max-width: 400px;" autoplay playsinline></video>
            <p id="resultado" style="font-weight: bold; color: #00b4d8; margin-top: 10px;">Buscando código de barras...</p>
        </div>
        
        <script>
        const video = document.getElementById('video');
        const resultadoText = document.getElementById('resultado');
        
        // Activar la cámara trasera del celular
        navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
            .then(stream => {
                video.srcObject = stream;
            })
            .catch(err => {
                resultadoText.innerText = "Error al acceder a la cámara trasera.";
                console.error(err);
            });

        // Verificar si el navegador soporta el detector de códigos de barras nativo
        if ('BarcodeDetector' in window) {
            const barcodeDetector = new BarcodeDetector({ formats: ['ean_13', 'ean_8', 'code_128', 'code_39', 'upc_a'] });
            
            async function detectar() {
                try {
                    const barcodes = await barcodeDetector.detect(video);
                    if (barcodes.length > 0) {
                        const rawCode = barcodes[0].rawValue;
                        resultadoText.innerText = "¡Código Detectado!: " + rawCode;
                        
                        // Enviamos el código detectado de vuelta a Streamlit
                        window.parent.postMessage({
                            type: 'streamlit:set_widget_value',
                            key: 'barcode_detected',
                            value: rawCode
                        }, '*');
                        
                        // Pequeña vibración de éxito (si el dispositivo lo soporta)
                        if (navigator.vibrate) navigator.vibrate(200);
                    }
                } catch (error) {
                    console.error(error);
                }
                requestAnimationFrame(detectar);
            }
            
            video.addEventListener('play', () => {
                requestAnimationFrame(detectar);
            });
        } else {
            resultadoText.innerHTML = "⚠️ Tu navegador no soporta el escáner continuo directo.<br><small>Usa la pestaña 'Buscar Tipeando' e inicia el escáner integrado de tu teclado.</small>";
        }
        </script>
        """
        
        # Renderizamos el escáner de video en la pantalla del celular
        components.html(html_code, height=320)
        
        # Capturamos el valor que el JavaScript nos envía cuando detecta un código
        if 'barcode_detected' in st.session_state and st.session_state.barcode_detected:
            codigo_escaneado = str(st.session_state.barcode_detected).strip().lower()
            st.success(f"Buscando automáticamente: {codigo_escaneado}")

    # --- PROCESAMIENTO DE RESULTADOS ---
    if codigo_escaneado:
        resultados = df[
            df['desc_busqueda'].str.contains(codigo_escaneado, na=False) | 
            df['scan_busqueda'].str.contains(codigo_escaneado, na=False) |
            df['interno_busqueda'].str.contains(codigo_escaneado, na=False)
        ]
        
        if not resultados.empty:
            st.markdown(f"### 📦 Resultados para: '{codigo_escaneado}'")
            
            for index, fila in resultados.iterrows():
                cod_int_texto = str(fila['Codigo Interno']).split('.')[0] if '.' in str(fila['Codigo Interno']) and str(fila['Codigo Interno']).split('.')[1] == '0' else str(fila['Codigo Interno'])
                scanner_texto = str(fila['codigoscanner']).split('.')[0] if '.' in str(fila['codigoscanner']) else str(fila['codigoscanner'])
                
                st.markdown(f"""
                <div class="producto-card">
                    <h2 style='margin:0; color:#2c3e50; font-size:20px;'>{fila['Descripcion']}</h2>
                    <p class="precio-destacado">💰 ${fila['Precio']:,}</p>
                    <p style='margin:0; color:#7f8c8d; font-size:14px; line-height: 1.6;'>
                        🔢 <b>Cód. Interno:</b> {cod_int_texto if pd.notna(fila['Codigo Interno']) else 'N/A'}<br>
                        📁 <b>Sector:</b> {fila['Descrip Sector'] if pd.notna(fila['Descrip Sector']) else 'N/A'}<br>
                        🏷️ <b>Scanner/EAN:</b> {scanner_texto if pd.notna(fila['codigoscanner']) else 'N/A'}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning(f"🔍 No se encontró ningún producto que coincida con '{codigo_escaneado}'.")
