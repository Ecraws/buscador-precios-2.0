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
    tab1, tab2 = st.tabs(["🔍 Buscar Tipeando", "📷 Lector de Barras"])
    
    codigo_escaneado = ""
    
    # --- PESTAÑA 1: BÚSQUEDA MANUAL ---
    with tab1:
        busqueda_texto = st.text_input("Escribí Descripción, Scanner o Cód. Interno:", key="manual_search").strip().lower()
        if busqueda_texto:
            codigo_escaneado = busqueda_texto

    # --- PESTAÑA 2: CÁMARA ESCÁNER EN VIVO (QUAGGA JS) ---
    with tab2:
        st.subheader("Escáner en Vivo")
        st.write("Centrá el código de barras en la cámara trasera. Asegurá buena luz y que no esté borroso.")
        
        # Insertamos el escáner basado en QuaggaJS
        html_code = """
        <div style="text-align: center; position: relative;">
            <div id="interactive" class="viewport" style="width: 100%; max-width: 400px; height: 250px; border: 2px solid #00b4d8; border-radius: 10px; overflow: hidden; margin: 0 auto; background-color: #000;">
                <video autoplay playsinline style="width: 100%; height: 100%; object-fit: cover;"></video>
            </div>
            <p id="resultado" style="font-weight: bold; color: #00b4d8; margin-top: 10px;">Escaneando activamente...</p>
        </div>
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/quagga/0.12.1/quagga.min.js"></script>
        
        <script>
        // Configuración e inicio de QuaggaJS
        Quagga.init({
            inputStream: {
                name: "Live",
                type: "LiveStream",
                target: document.querySelector('#interactive'),
                constraints: {
                    width: 640,
                    height: 480,
                    facingMode: "environment" // Fuerza el uso de la cámara trasera
                },
            },
            decoder: {
                // Tipos de códigos de barra comerciales más comunes (EAN, Code 128, etc)
                readers: ["ean_reader", "ean_8_reader", "code_128_reader", "code_39_reader", "upc_reader"]
            },
            locate: true // Ayuda a localizar las líneas del código en la imagen
        }, function(err) {
            if (err) {
                document.getElementById('resultado').innerText = "Error al iniciar la cámara trasera.";
                console.error(err);
                return;
            }
            Quagga.start();
        });

        // Escucha cuando detecta un código con éxito
        Quagga.onDetected(function(data) {
            if (data.codeResult && data.codeResult.code) {
                const codigo = data.codeResult.code;
                document.getElementById('resultado').innerText = "¡Código Detectado!: " + codigo;
                
                // Enviamos el código de barras de vuelta a Streamlit
                window.parent.postMessage({
                    type: 'streamlit:set_widget_value',
                    key: 'barcode_detected',
                    value: codigo
                }, '*');
                
                // Feedback táctil (vibración) si el celular lo permite
                if (navigator.vibrate) navigator.vibrate(150);
                
                // Frenamos el escáner un segundo para evitar lecturas repetidas en bucle
                Quagga.stop();
                setTimeout(function(){ Quagga.start(); }, 2000);
            }
        });
        </script>
        """
        
        # Renderizamos el componente en la app
        components.html(html_code, height=310)
        
        # Recibimos el código que descubrió QuaggaJS
        if 'barcode_detected' in st.session_state and st.session_state.barcode_detected:
            codigo_escaneado = str(st.session_state.barcode_detected).strip().lower()
            st.success(f"Código detectado: {codigo_escaneado}")

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
