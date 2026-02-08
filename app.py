import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Configuration de la page
st.set_page_config(page_title="Simulateur EPL", layout="wide")

# --- STYLE CSS PERSONNALISÉ ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; font-size: 14px; }
    
    /* Titre du projet en Violet */
    .title-epl { color: #d65cf5; text-align: center; font-size: 28px; font-weight: bold; margin-bottom: 20px; }
    
    /* Configuration en blanc dans la sidebar */
    section[data-testid="stSidebar"] .stMarkdown h2 { color: white !important; }
    
    /* Cartes de métriques avec contour noir épais */
    div[data-testid="stMetric"] {
        background-color: #1e222d;
        border: 2px solid #000000;
        border-radius: 8px;
        padding: 10px;
    }
    
    /* Couleurs vives pour les résultats */
    div[data-testid="stMetricValue"] { color: #00ff88 !important; font-size: 24px !important; }
    
    /* Onglets stylés */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: #262730; color: white; padding: 8px 16px; }
    .stTabs [aria-selected="true"] { border-bottom: 2px solid #d65cf5 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.image("im1.jpeg", width=180)
    st.markdown("## Configuration") # Écrit en blanc via CSS
    
    type_cycle = st.selectbox("Type de Cycle", ["Otto", "Diesel"])
    modele_gaz = st.selectbox("Modèle de Gaz", ["Gaz Simple", "Gaz Parfait"])
    
    st.markdown("### Entrées Utilisateur")
    V1 = st.number_input("Volume initial V1 (m³)", value=0.03000, format="%.5f")
    P1 = st.number_input("Pression initiale P1 (Pa)", value=101328)
    T1 = st.number_input("Température initiale T1 (K)", value=302)
    
    st.markdown("### Modélisation")
    r = st.slider("Taux de Compression (r)", 5.0, 20.0, 9.5)
    T_max = st.slider("Température Max (K)", 1000, 3000, 2100)

# --- CALCULS ---
gamma = 1.4 if modele_gaz == "Gaz Parfait" else 1.32
R = 287
mass = (P1 * V1) / (R * T1)
V2 = V1 / r
p2 = P1 * (r**gamma)
t2 = T1 * (r**(gamma-1))

if type_cycle == "Otto":
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
puissance = travail_net * 50 # 3000 RPM
couple = puissance / (2 * np.pi * 50)

# --- AFFICHAGE ---
st.markdown('<p class="title-epl">SIMULATEUR MOTEUR THERMIQUE - EPL</p>', unsafe_allow_html=True)

t1, t2_tab, t3_tab = st.tabs(["📊 Labo Virtuel", "📋 Données du Cycle", "📈 Étude Paramétrique"])

with t1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rendement (η)", f"{rendement:.2%}")
    c2.metric("Travail Net (W)", f"-{abs(travail_net):.0f} J")
    c3.metric("Puissance", f"-{abs(puissance/1000):.1f} kW")
    c4.metric("Couple", f"-{abs(couple):.1f} N.m")

    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.write("<span style='color:white'>1. Diagramme de Clapeyron (P, V)</span>", unsafe_allow_html=True)
        fig, ax = plt.subplots(facecolor='#0e1117')
        ax.set_facecolor('#0e1117')
        v = np.linspace(V2, V1, 100)
        ax.plot(np.linspace(V1, V2, 100), P1*(V1/np.linspace(V1, V2, 100))**gamma, color='#00f2ff', lw=1, label='1-2 Compression')
        ax.plot([V2, V3], [p2/100000, p3/100000], color='#ff0055', lw=1, label='2-3 Combustion')
        ax.plot(np.linspace(V3, V4, 100), p3*(V3/np.linspace(V3, V4, 100))**gamma, color='#ffea00', lw=1, label='3-4 Détente')
        ax.plot([V4, V1], [p4/100000, P1/100000], color='#00ff88', lw=1, label='4-1 Échappement')
        ax.grid(color='#333', lw=0.5); ax.legend(fontsize='small'); st.pyplot(fig)

    with col_g2:
        st.write("<span style='color:white'>2. Diagramme Entropique (T, S)</span>", unsafe_allow_html=True)
        fig2, ax2 = plt.subplots(facecolor='#0e1117')
        ax2.set_facecolor('#0e1117')
        s = np.linspace(0, 5, 100)
        ax2.plot([0, 0], [T1, t2], color='#00f2ff', lw=1, label='1-2 Isentropique')
        ax2.plot(s, t2*np.exp(s/2.5), color='#ff0055', lw=1, label='2-3 Apport Chaleur')
        ax2.plot([5, 5], [T_max, t4], color='#ffea00', lw=1, label='3-4 Détente')
        ax2.plot(s[::-1], T1 + (t4-T1)*(s/5), color='#00ff88', lw=1, label='4-1 Rejet Chaleur')
        ax2.grid(color='#333', lw=0.5); ax2.legend(fontsize='small'); st.pyplot(fig2)

with t2_tab:
    st.write("### État des points du cycle")
    st.table({"Point": [1,2,3,4], "P (bar)": [P1/100000, p2/100000, p3/100000, p4/100000], "T (K)": [T1, t2, T_max, t4]})

with t3_tab:
    st.info("L'étude paramétrique analyse l'évolution du rendement en fonction du taux de compression r.")
    r_range = np.linspace(5, 20, 50)
    eta_range = 1 - (1 / (r_range**(gamma - 1)))
    fig3, ax3 = plt.subplots(facecolor='#0e1117')
    ax3.set_facecolor('#0e1117')
    ax3.plot(r_range, eta_range, color='#d65cf5')
    ax3.set_xlabel("Taux r"); ax3.set_ylabel("Rendement"); st.pyplot(fig3)
