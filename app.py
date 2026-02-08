import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Configuration de la page
st.set_page_config(page_title="Simulateur Thermodynamique EPL", layout="wide")

# --- STYLE CSS (Bordures noires, couleurs vives, mode sombre) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    
    /* Cartes de métriques avec contour noir épais comme sur l'image */
    div[data-testid="stMetric"] {
        background-color: #1e222d;
        border: 3px solid #000000;
        border-radius: 10px;
        padding: 15px;
    }
    
    h1, h2, h3 { color: #00f2ff !important; }
    div[data-testid="stMetricValue"] { color: #00ff88 !important; font-size: 32px !important; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #262730; color: white; border-radius: 5px; padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #00f2ff !important; color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.image("im1.jpeg", width=220)
    st.markdown("## ⚙️ Configuration")
    
    with st.expander("🔬 Modélisation", expanded=True):
        type_cycle = st.selectbox("Type de Cycle", ["Otto (Beau de Rochas)", "Diesel"])
        modele_gaz = st.selectbox("Modèle de Gaz", ["Gaz Parfait (Air)", "Gaz Simple"])
    
    with st.expander("🌡️ Paramètres", expanded=True):
        r = st.slider("Taux de Compression (r)", 5.0, 22.0, 10.0)
        T_max = st.slider("Température Max (K)", 1000, 3000, 2200)
        P1 = 101325 
        T1 = 300    
        gamma = 1.4 if modele_gaz == "Gaz Parfait (Air)" else 1.3

# --- CALCULS PHYSIQUES ---
R = 287  
V1 = 0.0005 
V2 = V1 / r
mass = (P1 * V1) / (R * T1)

# 1 -> 2 : Compression
p2 = P1 * (r**gamma)
t2 = T1 * (r**(gamma-1))
W_comp = (mass * R * (t2 - T1)) / (1 - gamma)

if "Otto" in type_cycle:
    V3 = V2
    p3 = p2 * (T_max / t2)
    V4 = V1
    p4 = p3 * (V2 / V4)**gamma
    t4 = T_max * (V2 / V4)**(gamma-1)
    rendement = 1 - (1 / (r**(gamma - 1)))
else:
    p3 = p2
    rc = T_max / t2 
    V3 = V2 * rc
    V4 = V1
    p4 = p3 * (V3 / V4)**gamma
    t4 = T_max * (V3 / V4)**(gamma-1)
    rendement = 1 - ( (1/gamma) * ((rc**gamma - 1) / (rc - 1)) * (1 / r**(gamma-1)) )

W_det = (mass * R * (t4 - T_max)) / (1 - gamma)
travail_net = W_comp + W_det 
puissance_watt = travail_net * (3000 / 60)
couple_val = puissance_watt / (2 * np.pi * 3000 / 60)

# --- CORPS DU SITE ---
st.title("Simulateur Moteur Thermique - Labo Virtuel")

tab1, tab2, tab3 = st.tabs(["📊 Labo Virtuel", "📈 Étude Paramétrique", "📋 Données"])

with tab1:
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Rendement (η)", f"{rendement:.2%}")
    col_m2.metric("Travail Net", f"{travail_net:.1f} J", 
                  delta="Moteur" if travail_net < 0 else "Compresseur",
                  delta_color="normal" if travail_net < 0 else "inverse")
    col_m3.metric("Puissance", f"{puissance_watt/1000:.1f} kW", "↑ 3000 rpm")
    col_m4.metric("Couple", f"{couple_val:.1f} N.m")

    st.divider()

    g1, g2 = st.columns(2)
    with g1:
        st.subheader("1. Diagramme de Clapeyron (P, V)")
        fig, ax = plt.subplots(facecolor='#0e1117')
        ax.set_facecolor('#0e1117')
        
        v_c = np.linspace(V1, V2, 100)
        p_c = P1 * (V1 / v_c)**gamma
        ax.plot(v_c, p_c/100000, color='#00f2ff', linewidth=3, label='Compression')
        
        if "Otto" in type_cycle:
            ax.plot([V2, V2], [p2/100000, p3/100000], color='#ff0055', linewidth=3, label='Combustion')
        else:
            ax.plot([V2, V3], [p3/100000, p3/100000], color='#ff0055', linewidth=3, label='Combustion')
            
        v_d = np.linspace(V3, V4, 100)
        p_d = p3 * (V3 / v_d)**gamma
        ax.plot(v_d, p_d/100000, color='#ffea00', linewidth=3, label='Détente')
        ax.plot([V1, V1], [p4/100000, P1/100000], color='#00ff88', linewidth=3, label='Échappement')

        ax.grid(color='#444', linestyle='--')
        ax.set_xlabel("Volume (m³)", color='white')
        ax.set_ylabel("Pression (bar)", color='white')
        ax.tick_params(colors='white')
        ax.legend()
        st.pyplot(fig)

    with g2:
        st.subheader("2. Diagramme Entropique (T, S)")
        fig2, ax2 = plt.subplots(facecolor='#0e1117')
        ax2.set_facecolor('#0e1117')
        
        # Courbe illustrative T-S
        s_vals = np.linspace(0, 1, 100)
        t_vals = T1 + (T_max - T1) * (s_vals**2)
        ax2.plot(s_vals, t_vals, color='#ff00ff', linewidth=3)
        
        ax2.grid(color='#444', linestyle='--')
        ax2.set_xlabel("Entropie (S)", color='white')
        ax2.set_ylabel("Température (K)", color='white')
        ax2.tick_params(colors='white')
        st.pyplot(fig2)

with tab2:
    st.info("Module d'étude paramétrique : Comparez les performances selon vos réglages.")

with tab3:
    st.table({"Point": ["1", "2", "3", "4"], 
              "Pression (bar)": [P1/100000, p2/100000, p3/100000, p4/100000],
              "Temp (K)": [T1, t2, T_max, t4]})
