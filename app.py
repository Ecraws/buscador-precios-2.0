import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# Configuración de rendimiento de la página
st.set_page_config(
    page_title="Buscador de Precios Industrial", 
    page_icon="📱", 
    layout="centered"
)

# Estilos CSS de Nivel Aplicación Nativa (UI/UX Ultra Premium)
st.markdown("""
    <style>
    .main, .block-container {
        max-width: 100% !important;
        padding-left: 10px !important;
        padding-right: 10px !important;
        overflow-x: hidden !important;
        background-color: #f4f6f9;
    }
    .producto-card {
        background-color: white;
        padding: 24px;
        border-radius: 20px;
        box-shadow: 0px 10px 25px rgba(0,0,0,0.05);
        margin-top: 15px;
        margin-bottom: 15px;
        border-left: 12px solid #2ecc71;
        transition: all 0.3s ease;
    }
    .precio-enorme {
        color: #2ecc71;
        font-size: 95px;
        font-weight: 900;
        line-height: 0.85;
        margin: 20px 0 10px 0;
        letter-spacing: -3px;
        font-family: 'Helvetica Neue', Arial, sans-serif;
    }
    .historial-item {
        background-color: #ffffff;
        padding: 12px 18px;
        border-radius: 10px;
        margin-bottom: 8px;
        border-left: 5px solid #34495e;
        font-size: 14px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.02);
    }
    /* Estilización de las pestañas superiores */
    .stTabs [data-baseweb="tab"] {
        font-size: 16px;
        font-weight: bold;
        padding: 12px 20px;
    }
    div[data-testid="stVerticalBlock"] {
        max-width: 100% !important;
        overflow-x: hidden !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📱 Buscador de Productos Ultra")

# Motor de carga indexada y caché persistente
@st.cache_data(show_spinner=False)
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
        st.error("⚠️ Error crítico: Verifica que 'productos.xlsx' esté en la raíz de GitHub.")
        return None

df = cargar_datos()

if df is not None:
    # Arquitectura de Estados Limpia
    if 'buscar_este_codigo' not in st.session_state:
        st.session_state.buscar_este_codigo = ""
    if 'historial' not in st.session_state:
        st.session_state.historial = []
    if 'camara_activa' not in st.session_state:
        st.session_state.camara_activa = False

    # Tabs de interacción fluida
    tab1, tab2 = st.tabs(["🔍 Búsqueda Manual", "📷 Escáner Industrial 360°"])
    
    # --- PESTAÑA 1: BÚSQUEDA MANUAL ---
    with tab1:
        busqueda_texto = st.text_input("Ingresa Descripción, Scanner o Código Interno:", key="manual_search").strip().lower()
        if busqueda_texto:
            st.session_state.buscar_este_codigo = busqueda_texto

    # --- PESTAÑA 2: ESCÁNER CON TECNOLOGÍA DE RÁFAGA ---
    with tab2:
        st.subheader("Control Remoto de Cámara")
        
        # Botonera ergonómica de control principal
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.session_state.camara_activa:
                if st.button("🔴 APAGAR CÁMARA", use_container_width=True):
                    st.session_state.camara_activa = False
                    st.rerun()
            else:
                if st.button("🟢 ENCENDER CÁMARA", type="primary", use_container_width=True):
                    st.session_state.camara_activa = True
                    st.rerun()
        with col_btn2:
            if st.button("❌ LIMPIAR PANTALLA", use_container_width=True):
                st.session_state.buscar_este_codigo = ""
                st.rerun()

        # Inyección del componente de escaneo optimizado a nivel de hardware
        if st.session_state.camara_activa:
            st.write("Alineá el código dentro del visor y presioná el disparador:")
            
            html_code = """
            <div style="width: 100%; max-width: 100%; box-sizing: border-box; text-align: center; overflow: hidden;">
                
                <div id="interactive" class="viewport" style="width: 100%; max-width: 360px; height: 210px; border: 4px solid #3498db; border-radius: 16px; overflow: hidden; margin: 0 auto; background-color: #000; position: relative; box-sizing: border-box; box-shadow: inset 0 0 20px rgba(0,0,0,0.6);">
                    <video autoplay playsinline style="width: 100%; height: 100%; object-fit: cover; position: absolute; top:0; left:0; filter: contrast(1.1) brightness(1.05);"></video>
                    
                    <div style="position: absolute; top: 50%; left: 8%; width: 84%; height: 2px; background-color: #3498db; opacity: 0.7; pointer-events: none;"></div>
                    <div style="position: absolute; top: 8%; left: 50%; width: 2px; height: 84%; background-color: #3498db; opacity: 0.7; pointer-events: none;"></div>
                    <div style="position: absolute; top: 40%; left: 40%; width: 20%; height: 20%; border: 2px dashed rgba(52, 152, 219, 0.4); pointer-events: none;"></div>
                </div>
                
                <button id="disparador" style="margin-top: 15px; padding: 16px 0; font-size: 18px; font-weight: 800; color: white; background-color: #e74c3c; border: none; border-radius: 35px; box-shadow: 0px 6px 20px rgba(231,76,60,0.5); cursor: pointer; width: 100%; max-width: 360px; box-sizing: border-box; -webkit-tap-highlight-color: transparent; letter-spacing: 0.5px;">
                    📸 GATILLAR ESCÁNER
                </button>
                
                <p id="resultado" style="font-weight: bold; color: #3498db; margin-top: 12px; font-size: 14px; letter-spacing: 0.2px;">Hardware listo. Sostén firme y gatilla.</p>
            </div>
            
            <script src="https://cdnjs.cloudflare.com/ajax/libs/quagga/0.12.1/quagga.min.js"></script>
            
            <script>
            let quaggaInicializado = false;
            let analizandoRafaga = false;

            function playBeep() {
                try {
                    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    const oscillator = audioCtx.createOscillator();
                    const gainNode = audioCtx.createGain();
                    oscillator.type = 'sine';
                    oscillator.frequency.setValueAtTime(1400, audioCtx.currentTime); // Tono más limpio y profesional
                    gainNode.gain.setValueAtTime(0.15, audioCtx.currentTime);
                    oscillator.connect(gainNode);
                    gainNode.connect(audioCtx.destination);
                    oscillator.start();
                    oscillator.stop(audioCtx.currentTime + 0.09); // Bip ultra-corto de alta gama
                } catch(e) {}
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
                    halfSample: false // Mantiene nitidez pura de la lente
                },
                decoder: { 
                    readers: ["ean_reader", "ean_8_reader", "code_128_reader"],
                    tryPatterns: true // Fuerza decodificación 360 grados (Vertical/Diagonal)
                },
                locate: true
            }, function(err) {
                if (err) {
                    document.getElementById('resultado').innerText = "Acceso a cámara denegado o bloqueado.";
                    document.getElementById('resultado').style.color = "#e74c3c";
                    return;
                }
                Quagga.start();
                quaggaInicializado = true;
            });

            // DISPARADOR LOGIC: Abre una ventana de ráfaga matemática interactiva
            document.getElementById('disparador').addEventListener('click', function() {
                if (!quaggaInicializado || analizandoRafaga) return;
                
                analizandoRafaga = true;
                document.getElementById('resultado').innerText = "⚡ PROCESANDO RÁFAGA (30 FPS)...";
                document.getElementById('resultado').style.color = "#e67e22";
                document.getElementById('disparador').style.backgroundColor = "#7f8c8d";
                document.getElementById('disparador').style.boxShadow = "none";
                
                // Definimos la función recolectora
                const interceptorLectura = function(data) {
                    if (data && data.codeResult && data.codeResult.code) {
                        const codigoFinal = data.codeResult.code.strip ? data.codeResult.code.strip() : data.codeResult.code;
                        
                        if (codigoFinal.length >= 5) {
                            playBeep();
                            if (navigator.vibrate) navigator.vibrate(150);
                            
                            document.getElementById('resultado').innerText = "¡DETECTADO!: " + codigoFinal;
                            document.getElementById('resultado').style.color = "#2ecc71";
                            
                            // Remover listener y frenar cámara inmediatamente para ahorrar recursos
                            Quagga.offDetected(interceptorLectura);
                            Quagga.stop();
                            
                            // Inyección de estado limpia mediante API Streamlit
                            const inputElement = window.parent.document.querySelector('input[data-testid="stTextInput"]');
                            if(inputElement) {
                                inputElement.value = codigoFinal;
                                inputElement.dispatchEvent(new Event('input', { bubbles: true }));
                                inputElement.dispatchEvent(new Event('change', { bubbles: true }));
                            }
                            
                            window.parent.postMessage({
                                type: 'streamlit:set_widget_value',
                                key: 'barcode_detected',
                                value: codigoFinal
                            }, '*');
                        }
                    }
                };
                
                // Activamos la ráfaga de escucha continua en este instante
                Quagga.onDetected(interceptorLectura);
                
                // Ventana de escaneo de 1.6 segundos. Si no lee, resetea el botón para reintentar ordenadamente
                setTimeout(() => {
                    Quagga.offDetected(interceptorLectura);
                    analizandoRafaga = false;
                    
                    // Restauramos diseño del botón
                    document.getElementById('disparador').style.backgroundColor = "#e74c3c";
                    document.getElementById('disparador').style.boxShadow = "0px 6px 20px rgba(231,76,60,0.5)";
                    
                    if (document.getElementById('resultado').innerText === "⚡ PROCESANDO RÁFAGA (30 FPS)...") {
                        document.getElementById('resultado').innerText = "❌ No se detectó un patrón claro. Reubica y vuelve a gatillar.";
                        document.getElementById('resultado').style.color = "#e74c3c";
                    }
                }, 1600);
            });
            </script>
            """
            components.html(html_code, height=305)
        else:
            st.info("💡 Lector en modo reposo para optimizar batería. Presioná el botón verde para activarlo.")

    # --- RECEPTOR NATIVO DE ALTA VELOCIDAD ---
    if 'barcode_detected' in st.session_state and st.session_state.barcode_detected:
        st.session_state.buscar_este_codigo = str(st.session_state.barcode_detected).strip()
        st.session_state.barcode_detected = "" # Vaciar puente
        st.rerun()

    # --- PROCESADOR Y RENDERIZADOR DE PRECIOS PREMIUM ---
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
            
            # Formateo estricto del historial
            registro_historial = f"{desc} - **${precio:,}**"
            if not st.session_state.historial or st.session_state.historial[0] != registro_historial:
                st.session_state.historial.insert(0, registro_historial)
                if len(st.session_state.historial) > 3:
                    st.session_state.historial.pop()

            st.markdown(f"### 📦 Resultado de Consulta:")
            
            for index, fila in resultados.iterrows():
                cod_int_texto = str(fila['Codigo Interno']).split('.')[0] if '.' in str(fila['Codigo Interno']) and str(fila['Codigo Interno']).split('.')[1] == '0' else str(fila['Codigo Interno'])
                scanner_texto = str(fila['codigoscanner']).split('.')[0] if '.' in str(fila['codigoscanner']) else str(fila['codigoscanner'])
                
                st.markdown(f"""
                <div class="producto-card">
                    <h2 style='margin:0; color:#2c3e50; font-size:25px; font-weight:700;'>{fila['Descripcion']}</h2>
                    <p class="precio-enorme">💰 ${fila['Precio']:,}</p>
                    <p style='margin:0; color:#7f8c8d; font-size:15px; line-height: 1.6; border-top: 1px solid #eee; padding-top: 12px; margin-top: 5px;'>
                        🔢 <b>Cód. Interno:</b> <span style="color:#2c3e50;">{cod_int_texto if pd.notna(fila['Codigo Interno']) else 'N/A'}</span><br>
                        📁 <b>Sector / Rubro:</b> <span style="color:#2c3e50;">{fila['Descrip Sector'] if pd.notna(fila['Descrip Sector']) else 'N/A'}</span><br>
                        🏷️ <b>Scanner o EAN:</b> <span style="color:#2c3e50;">{scanner_texto if pd.notna(fila['codigoscanner']) else 'N/A'}</span>
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning(f"🔍 El artículo '{st.session_state.buscar_este_codigo}' no figura en la base de datos de productos.")

    # --- PANEL HISTÓRICO DE AUDITORÍA ---
    if st.session_state.historial:
        st.write("---")
        st.subheader("📋 Últimas referencias:")
        for item in st.session_state.historial:
            st.markdown(f'<div class="historial-item">🔹 {item}</div>', unsafe_allow_html=True)
