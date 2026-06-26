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
        font-size: 32px;
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
    tab1, tab2 = st.tabs(["🔍 Buscar Tipeando", "📷 Lector de Barras HD"])
    
    codigo_escaneado = ""
    
    # --- PESTAÑA 1: BÚSQUEDA MANUAL ---
    with tab1:
        busqueda_texto = st.text_input("Escribí Descripción, Scanner o Cód. Interno:", key="manual_search").strip().lower()
        if busqueda_texto:
            codigo_escaneado = busqueda_texto

    # --- PESTAÑA 2: CÁMARA ESCÁNER EN VIVO OPTIMIZADO ---
    with tab2:
        st.subheader("Escáner de Alta Precisión")
        st.write("Coloca el código horizontalmente en el centro del recuadro. Acerca o aleja lentamente para hacer foco.")
        
        html_code = """
        <div style="text-align: center; position: relative;">
            <div id="interactive" class="viewport" style="width: 100%; max-width: 400px; height: 250px; border: 3px solid #2ecc71; border-radius: 12px; overflow: hidden; margin: 0 auto; background-color: #000; position: relative;">
                <video autoplay playsinline style="width: 100%; height: 100%; object-fit: cover;"></video>
                <div style="position: absolute; top: 50%; left: 5%; width: 90%; height: 2px; background-color: red; opacity: 0.6; pointer-events: none;"></div>
            </div>
            <p id="resultado" style="font-weight: bold; color: #2ecc71; margin-top: 10px; font-size: 16px;">Cámara lista. Escaneando...</p>
        </div>
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/quagga/0.12.1/quagga.min.js"></script>
        
        <script>
        let ultimoCodigo = "";
        let tiempoBloqueo = 0;

        Quagga.init({
            inputStream: {
                name: "Live",
                type: "LiveStream",
                target: document.querySelector('#interactive'),
                constraints: {
                    // Maximizamos la resolución a HD para que distinga líneas finas de EAN-13 y EAN-8
                    width: { min: 1280, ideal: 1280 },
                    height: { min: 720, ideal: 720 },
                    facingMode: "environment",
                    focusMode: "continuous" // Fuerza el autofoco continuo en celulares compatibles
                },
            },
            locator: {
                patchSize: "medium", // Tamaño de parche optimizado para EAN comerciales
                halfSample: false     // No reduce la imagen a la mitad para no perder nitidez
            },
            decoder: {
                // Enfocado estrictamente en tus formatos solicitados para no saturar la memoria
                readers: ["ean_reader", "ean_8_reader", "code_128_reader"]
            },
            locate: true
        }, function(err) {
            if (err) {
                document.getElementById('resultado').innerText = "Error: Permite el acceso a la cámara trasera.";
                document.getElementById('resultado').style.color = "red";
                console.error(err);
                return;
            }
            Quagga.start();
        });

        Quagga.onDetected(function(data) {
            const ahora = Date.now();
            
            // FILTRO DE SEGURIDAD ANTIBUCLE: 
            // Si leyó un código hace menos de 3 segundos, ignora la lectura para que no se tilde la app
            if (ahora < tiempoBloqueo) {
                return; 
            }

            if (data.codeResult && data.codeResult.code) {
                const codigo = data.codeResult.code;
                
                // Validación básica de códigos de barras comerciales (mínimo 5 dígitos)
                if(codigo.length >= 5) {
                    tiempoBloqueo = ahora + 3000; // Bloquea nuevas lecturas por 3 segundos
                    
                    document.getElementById('resultado').innerText = "¡Código Detectado!: " + codigo;
                    
                    // Envía el código de forma limpia a Streamlit una única vez
                    window.parent.postMessage({
                        type: 'streamlit:set_widget_value',
                        key: 'barcode_detected',
                        value: codigo
                    }, '*');
                    
                    if (navigator.vibrate) navigator.vibrate(200);
                }
            }
        });
        </script>
        """
        
        # Renderizamos el componente en la app
        components.html(html_code, height=310)
        
        # Recibimos el código desde JavaScript sin saturar el estado de Streamlit
        if 'barcode_detected' in st.session_state and st.session_state.barcode_detected:
            codigo_escaneado = str(st.session_state.barcode_detected).strip().lower()
            # Mostramos un botón para limpiar el escáner si queremos buscar otra cosa
            if st.button("🔄 Limpiar / Escanear otro"):
                st.session_state.barcode_detected = ""
                st.rerun()

    # --- PROCESAMIENTO Y MUESTRA DE RESULTADOS ---
    if codigo_escaneado:
        resultados = df[
            df['desc_busqueda'].str.contains(codigo_escaneado, na=False) | 
            df['scan_busqueda'].str.contains(codigo_escaneado, na=False) |
            df['interno_busqueda'].str.contains(codigo_escaneado, na=False)
        ]
        
        if not resultados.empty:
            st.markdown(f"### 📦 Producto Encontrado:")
            
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
        else:
            st.warning(f"🔍 El código '{codigo_escaneado}' no está registrado en el Excel.")
