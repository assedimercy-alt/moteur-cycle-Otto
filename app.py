import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Configuration de la page
st.set_page_config(page_title="Simulateur Thermodynamique EPL", layout="wide")

# --- STYLE CSS (Interface Premium : Noir OLED, Cyan Néon et Blanc) ---
st.markdown("""
    <style>
    /* Fond noir total et police réduite */
    .stApp { background-color: #000000; color: white; font-size: 12px; }
    
    /* Titre du projet en Violet */
    .title-epl { color: #d65cf5; text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 20px; }
    
    /* Textes Sidebar en Blanc */
    section[data-testid="stSidebar"] .stMarkdown h3, 
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown p { color: white !important; font-weight: bold; font-size: 13px; }
    
    /* Cartes de métriques avec contour noir intense */
    div[data-testid="stMetric"] {
        background-color: #0a0a0a;
        border: 2px solid #1a1a1a;
        border-radius: 6px;
        padding: 8px;
        box-shadow: 0px 0px 10px rgba(214, 92, 245, 0.2);
    }
    
    /* Valeurs en Cyan */
    div[data-testid="stMetricValue"] { color: #00ffff !important; font-size: 20px !important; }
    
    /* Titres des graphiques en Blanc */
    .graph-title { color: white; font-weight: bold; font-size: 14px; margin-bottom: 10px; }

    /* Onglets épurés */
    .stTabs [data-baseweb="tab-list"] { gap: 5px; }
    .stTabs [data-baseweb="tab"] { background-color: #0a0a0a; color: white; padding: 5px 10px; }
    .stTabs [aria-selected="true"] { border-bottom: 2px solid #d65cf5 !important; color: #d65cf5 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.image("im1.jpeg", width=160)
    st.markdown("## MODÉLISATION")
    type_cycle = st.selectbox("Type de Cycle", ["Otto (Beau de Rochas)", "Diesel"])
    modele_gaz = st.selectbox("Modèle de Gaz", ["Gaz Parfait", "Gaz Simple"])
    
    st.markdown("### PARAMÈTRE D'ENTRÉE")
    V1 = st.number_input("Volume initial V1 (m³)", value=0.03000, format="%.5f")
    P1 = st.number_input("Pression initiale P1 (Pa)", value=101328)
    T1 = st.number_input("Température initiale T1 (K)", value=302)
    
    st.markdown("### VARIABLE")
    r = st.slider("Taux de Compression (r)", 5.0, 20.0, 9.5)
    T_max = st.slider("Température Max (K)", 1000, 3500, 2100)

# --- CALCULS ---
gamma = 1.4 if modele_gaz == "Gaz Parfait" else 1.32
R = 287
mass = (P1 * V1) / (R * T1)
V2 = V1 / r
p2 = P1 * (r**gamma)
t2 = T1 * (r**(gamma-1))

if "Otto" in type_cycle:
    V3, p3 = V2, p2 * (T_max / t2)
    V4, p4 = V1, p3 * (1/r)**gamma
    t4 = T_max * (1/r)**(gamma-1)
    rendement = 1 - (1 / (r**(gamma - 1)))
else:
    p3 = p2
    rc = T_max / t2 
    V3 = V2 * rc
    V4, p4 = V1, p3 * (V3/V1)**gamma
    t4 = T_max * (V3/V1)**(gamma-1)
    rendement = 1 - ( (1/gamma) * ((rc**gamma - 1) / (rc - 1)) * (1 / r**(gamma-1)) )

travail_net = (mass * R * (t2 - T1))/(1-gamma) + (mass * R * (t4 - T_max))/(1-gamma)
puissance = travail_net * 50 
couple = puissance / (2 * np.pi * 50)

# --- INTERFACE PRINCIPALE ---
st.markdown('<p class="title-epl">SIMULATEUR MOTEUR THERMIQUE - EPL</p>', unsafe_allow_html=True)

tab_labo, tab_param, tab_data = st.tabs(["📊 Labo Virtuel", "📈 Étude Paramétrique", "📋 Données"])

with tab_labo:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rendement (η)", f"{rendement:.2%}")
    c2.metric("Travail Net", f"-{abs(travail_net):.1f} J")
    c3.metric("Puissance", f"-{abs(puissance/1000):.1f} kW")
    c4.metric("Couple", f"-{abs(couple):.1f} N.m")

    st.divider()
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.markdown('<p class="graph-title">1. Diagramme de Clapeyron (P, V)</p>', unsafe_allow_html=True)
        fig, ax = plt.subplots(facecolor='#000000')
        ax.set_facecolor('#000000')
        v_12 = np.linspace(V1, V2, 100)
        ax.plot(v_12, P1*(V1/v_12)**gamma, color='#00ffff', lw=1, label='1-2 Compression')
        ax.plot([V2, V3], [p2/100000, p3/100000], color='#ff0055', lw=1, label='2-3 Combustion')
        v_34 = np.linspace(V3, V4, 100)
        ax.plot(v_34, p3*(V3/v_34)**gamma, color='#ffea00', lw=1, label='3-4 Détente')
        ax.plot([V4, V1], [p4/100000, P1/100000], color='#d65cf5', lw=1, label='4-1 Échappement')
        ax.grid(color='#222', lw=0.5); ax.legend(fontsize='x-small', labelcolor='white', facecolor='#000'); st.pyplot(fig)

    with col_g2:
        st.markdown('<p class="graph-title">2. Diagramme Entropique (T, S)</p>', unsafe_allow_html=True)
        fig2, ax2 = plt.subplots(facecolor='#000000')
        ax2.set_facecolor('#000000')
        s = np.linspace(0, 4, 100)
        ax2.plot([0, 0], [T1, t2], color='#00ffff', lw=1, label='1-2 Adiabatique')
        ax2.plot(s, t2*np.exp(s/3), color='#ff0055', lw=1, label='2-3 Apport Q')
        ax2.plot([4, 4], [T_max, t4], color='#ffea00', lw=1, label='3-4 Adiabatique')
        ax2.plot(s[::-1], T1 + (t4-T1)*(s/4), color='#d65cf5', lw=1, label='4-1 Rejet Q')
        ax2.grid(color='#222', lw=0.5); ax2.legend(fontsize='x-small', labelcolor='white', facecolor='#000'); st.pyplot(fig2)

with tab_param:
    st.write("### Évolution du rendement en fonction de r")
    r_range = np.linspace(5, 22, 100)
    eta_range = 1 - (1 / (r_range**(gamma - 1)))
    fig3, ax3 = plt.subplots(facecolor='#000000')
    ax3.set_facecolor('#000000')
    ax3.plot(r_range, eta_range, color='#00ffff', lw=1.5)
    ax3.set_xlabel("Taux r", color='white'); ax3.set_ylabel("Rendement", color='white')
    ax3.grid(color='#222'); ax3.tick_params(colors='white'); st.pyplot(fig3)

with tab_data:
    st.write("### Tableau de synthèse des points")
    st.table({
        "État": [1, 2, 3, 4],
        "Pression (bar)": [round(P1/100000, 2), round(p2/100000, 2), round(p3/100000, 2), round(p4/100000, 2)],
        "Température (K)": [round(T1, 1), round(t2, 1), round(T_max, 1), round(t4, 1)],
        "Volume (m³)": [f"{V1:.5f}", f"{V2:.5f}", f"{V3:.5f}", f"{V4:.5f}"]
    })
