import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# Configuración de la página para celulares
st.set_page_config(
    page_title="Buscador de Precios Premium", 
    page_icon="📱", 
    layout="centered"
)

# Estilos visuales avanzados con PRECIO MÁS GRANDE y llamativo
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .producto-card {
        background-color: white;
        padding: 22px;
        border-radius: 14px;
        box-shadow: 0px 4px 14px rgba(0,0,0,0.07);
        margin-bottom: 20px;
        border-left: 8px solid #2ecc71;
    }
    .precio-destacado {
        color: #2ecc71;
        font-size: 46px; /* <-- PRECIO CONSIDERABLEMENTE MÁS GRANDE */
        font-weight: 900;
        margin: 10px 0;
        letter-spacing: -1px;
    }
    .historial-item {
        background-color: #ffffff;
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 8px;
        border-left: 4px solid #bdc3c7;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📱 Buscador de Productos Pro")

# Carga inteligente de datos desde el Excel
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
    # Inicializamos la memoria de la aplicación
    if 'buscar_este_codigo' not in st.session_state:
        st.session_state.buscar_este_codigo = ""
    if 'historial' not in st.session_state:
        st.session_state.historial = []

    # Capturamos lo que envíe el JavaScript de la cámara
    if 'barcode_detected' in st.session_state and st.session_state.barcode_detected:
        nuevo_codigo = str(st.session_state.barcode_detected).strip()
        if nuevo_codigo and nuevo_codigo != st.session_state.buscar_este_codigo:
            st.session_state.buscar_este_codigo = nuevo_codigo
            st.session_state.barcode_detected = "" 
            st.rerun()

    # Pestañas de navegación superiores
    tab1, tab2 = st.tabs(["🔍 Buscar Tipeando", "📷 Lector Multidireccional"])
    
    # --- PESTAÑA 1: BÚSQUEDA MANUAL ---
    with tab1:
        busqueda_texto = st.text_input("Escribí Descripción, Scanner o Cód. Interno:", key="manual_search").strip().lower()
        if busqueda_texto:
            st.session_state.buscar_este_codigo = busqueda_texto

    # --- PESTAÑA 2: CÁMARA ESCÁNER 360° ---
    with tab2:
        if st.session_state.buscar_este_codigo:
            st.write("✨ ¡Escaneo realizado con éxito!")
            if st.button("📷 Escanear otro producto", type="primary"):
                st.session_state.buscar_este_codigo = ""
                st.rerun()
        else:
            st.subheader("Escáner en Cualquier Dirección")
            st.write("Apunta al código de barras. Ahora puedes leerlo de costado, vertical o inclinado.")
            
            html_code = """
            <div style="text-align: center; position: relative;">
                <div id="interactive" class="viewport" style="width: 100%; max-width: 400px; height: 230px; border: 3px solid #2ecc71; border-radius: 12px; overflow: hidden; margin: 0 auto; background-color: #000; position: relative;">
                    <video autoplay playsinline style="width: 100%; height: 100%; object-fit: cover;"></video>
                    <div style="position: absolute; top: 50%; left: 10%; width: 80%; height: 2px; background-color: #2ecc71; opacity: 0.4; pointer-events: none;"></div>
                    <div style="position: absolute; top: 10%; left: 50%; width: 2px; height: 80%; background-color: #2ecc71; opacity: 0.4; pointer-events: none;"></div>
                </div>
                <p id="resultado" style="font-weight: bold; color: #2ecc71; margin-top: 10px; font-size: 16px;">Escáner 360° activado...</p>
            </div>
            
            <script src="https://cdnjs.cloudflare.com/ajax/libs/quagga/0.12.1/quagga.min.js"></script>
            
            <script>
            function reproducirBeep() {
                try {
                    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    const oscillator = audioCtx.createOscillator();
                    const gainNode = audioCtx.createGain();
                    
                    oscillator.type = 'sine';
                    oscillator.frequency.setValueAtTime(1200, audioCtx.currentTime);
                    gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
                    
                    oscillator.connect(gainNode);
                    gainNode.connect(audioCtx.destination);
                    
                    oscillator.start();
                    oscillator.stop(audioCtx.currentTime + 0.12);
                } catch(e) { console.log("Audio bloqueado"); }
            }

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
                locator: { 
                    patchSize: "medium", 
                    halfSample: false 
                },
                decoder: { 
                    readers: ["ean_reader", "ean_8_reader", "code_128_reader"],
                    // TRUCO CLAVE: Fuerza al lector a buscar patrones verticales, diagonales y alternativos
                    multiple: false,
                    tryPatterns: true
                },
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
                        
                        reproducirBeep();
                        
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

    # --- MOSTRAR RESULTADOS DE BÚSQUEDA ---
    codigo_a_buscar = st.session_state.buscar_este_codigo.lower().strip()
    
    if codigo_a_buscar:
        resultados = df[
            df['desc_busqueda'].str.contains(codigo_a_buscar, na=False) | 
            df['scan_busqueda'].str.contains(codigo_a_buscar, na=False) |
            df['interno_busqueda'].str.contains(codigo_a_buscar, na=False)
        ]
        
        if not resultados.empty:
            primer_resultado = resultados.iloc[0]
            desc = primer_resultado['Descripcion']
            precio = primer_resultado['Precio']
            
            # Historial de consultas
            registro_historial = f"{desc} - **${precio:,}**"
            if not st.session_state.historial or st.session_state.historial[0] != registro_historial:
                st.session_state.historial.insert(0, registro_historial)
                if len(st.session_state.historial) > 3:
                    st.session_state.historial.pop()

            st.markdown(f"### 📦 Producto Encontrado:")
            
            for index, fila in resultados.iterrows():
                cod_int_texto = str(fila['Codigo Interno']).split('.')[0] if '.' in str(fila['Codigo Interno']) and str(fila['Codigo Interno']).split('.')[1] == '0' else str(fila['Codigo Interno'])
                scanner_texto = str(fila['codigoscanner']).split('.')[0] if '.' in str(fila['codigoscanner']) else str(fila['codigoscanner'])
                
                # Renderizado con el precio gigante rediseñado
                st.markdown(f"""
                <div class="producto-card">
                    <h2 style='margin:0; color:#2c3e50; font-size:24px;'>{fila['Descripcion']}</h2>
                    <p class="precio-destacado">💰 ${fila['Precio']:,}</p>
                    <p style='margin:0; color:#7f8c8d; font-size:15px; line-height: 1.6;'>
                        🔢 <b>Cód. Interno:</b> {cod_int_texto if pd.notna(fila['Codigo Interno']) else 'N/A'}<br>
                        📁 <b>Sector:</b> {fila['Descrip Sector'] if pd.notna(fila['Descrip Sector']) else 'N/A'}<br>
                        🏷️ <b>Scanner/EAN:</b> {scanner_texto if pd.notna(fila['codigoscanner']) else 'N/A'}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("❌ Limpiar consulta actual"):
                st.session_state.buscar_este_codigo = ""
                st.rerun()
        else:
            st.warning(f"🔍 El código '{st.session_state.buscar_este_codigo}' no está en el Excel.")
            if st.button("🔄 Volver a intentar"):
                st.session_state.buscar_este_codigo = ""
                st.rerun()

    # --- SECCIÓN DE HISTORIAL RECIENTE ---
    if st.session_state.historial:
        st.write("---")
        st.subheader("📋 Últimas consultas:")
        for item in st.session_state.historial:
            st.markdown(f'<div class="historial-item">🔹 {item}</div>', unsafe_allow_html=True)
