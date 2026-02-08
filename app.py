import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Configuration
st.set_page_config(page_title="Simulateur EPL", layout="wide")

# --- STYLE CSS (Noir Intense, Blanc pur pour les titres, Cyan Néon) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: white; font-size: 12px; }
    .title-epl { color: #d65cf5; text-align: center; font-size: 22px; font-weight: bold; margin-bottom: 15px; }
    
    /* Titres Sidebar et Graphiques en BLANC */
    section[data-testid="stSidebar"] .stMarkdown h2, 
    section[data-testid="stSidebar"] .stMarkdown h3, 
    section[data-testid="stSidebar"] label,
    .graph-title { color: #ffffff !important; font-weight: bold; }

    /* Cartes avec contour NOIR INTENSE */
    div[data-testid="stMetric"] {
        background-color: #0a0a0a;
        border: 2px solid #1a1a1a;
        border-radius: 6px;
        padding: 8px;
    }
    div[data-testid="stMetricValue"] { color: #00ffff !important; font-size: 20px !important; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 5px; }
    .stTabs [data-baseweb="tab"] { background-color: #0a0a0a; color: white; font-size: 11px; }
    .stTabs [aria-selected="true"] { border-bottom: 2px solid #d65cf5 !important; color: #d65cf5 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("im1.jpeg", width=250)
    st.markdown("## MODÉLISATION")
    type_cycle = st.selectbox("Type de Cycle", ["Otto", "Diesel"])
    modele_gaz = st.selectbox("Modèle de Gaz", ["Gaz Parfait", "Gaz Simple"])
    
    st.markdown("### PARAMÈTRES D'ENTRÉE")
    V1 = st.number_input("Volume V1 (m³)", value=0.03000, format="%.5f")
    P1 = st.number_input("Pression P1 (Pa)", value=101328)
    T1 = st.number_input("Température T1 (K)", value=302)
    
    st.markdown("### VARIABLES")
    r = st.slider("Taux de Compression (r)", 5.0, 20.0, 9.5)
    T_max = st.slider("Température Max (K)", 1000, 3500, 2100)

# --- CALCULS PHYSIQUES PRÉCIS ---
gamma = 1.4 if modele_gaz == "Gaz Parfait" else 1.32
R = 287
mass = (P1 * V1) / (R * T1)
V2 = V1 / r

# 1 -> 2 : Compression
p2 = P1 * (r**gamma)
t2 = T1 * (r**(gamma-1))

if type_cycle == "Otto":
    V3, p3 = V2, p2 * (T_max / t2)
    V4, p4 = V1, p3 * (1/r)**gamma
    t4 = T_max * (1/r)**(gamma-1)
    rendement = 1 - (1 / (r**(gamma - 1)))
else:
    p3 = p2
    rc = T_max / t2 # Rapport d'injection
    V3 = V2 * rc
    V4, p4 = V1, p3 * (V3/V4)**gamma
    t4 = T_max * (V3/V4)**(gamma-1)
    rendement = 1 - ( (1/gamma) * ((rc**gamma - 1) / (rc - 1)) * (1 / r**(gamma-1)) )

travail_net = (mass * R * (t2 - T1))/(1-gamma) + (mass * R * (t4 - T_max))/(1-gamma)

# --- INTERFACE ---
st.markdown('<p class="title-epl">SIMULATEUR MOTEUR THERMIQUE - EPL</p>', unsafe_allow_html=True)
t_labo, t_param, t_data = st.tabs(["📊 Labo Virtuel", "📈 Étude Paramétrique", "📋 Données"])

with t_labo:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rendement (η)", f"{rendement:.2%}")
    c2.metric("Travail Net", f"-{abs(travail_net):.1f} J")
    c3.metric("Puissance", f"-{abs(travail_net*50/1000):.1f} kW")
    c4.metric("Couple", f"-{abs((travail_net*50)/(2*np.pi*50)):.1f} N.m")

    st.divider()
    g1, g2 = st.columns(2)
    
    with g1:
        st.markdown('<p class="graph-title">1. Diagramme de Clapeyron (P, V)</p>', unsafe_allow_html=True)
        fig, ax = plt.subplots(facecolor='#000000')
        ax.set_facecolor('#000000')
        
        # Courbes fines (lw=0.8)
        v_comp = np.linspace(V1, V2, 100)
        ax.plot(v_comp, P1*(V1/v_comp)**gamma, color='#00ffff', lw=0.8, label='1-2 Comp.')
        ax.plot([V2, V3], [p2/100000, p3/100000], color='#ff0055', lw=0.8, label='2-3 Comb.')
        v_det = np.linspace(V3, V4, 100)
        ax.plot(v_det, p3*(V3/v_det)**gamma, color='#ffea00', lw=0.8, label='3-4 Détente')
        ax.plot([V4, V1], [p4/100000, P1/100000], color='#d65cf5', lw=0.8, label='4-1 Échap.')
        
        ax.grid(color='#222', lw=0.5); ax.tick_params(colors='white'); ax.legend(fontsize='7', labelcolor='white', facecolor='#000')
        st.pyplot(fig)

    with g2:
        st.markdown('<p class="graph-title">2. Diagramme Entropique (T, S)</p>', unsafe_allow_html=True)
        fig2, ax2 = plt.subplots(facecolor='#000000')
        ax2.set_facecolor('#000000')
        
        # Tracé schématique des 4 phases entropiques
        ax2.plot([0, 0], [T1, t2], color='#00ffff', lw=0.8, label='1-2 Isentrop.')
        s_comb = np.linspace(0, 2, 100)
        ax2.plot(s_comb, t2 + (T_max-t2)*(s_comb/2)**2, color='#ff0055', lw=0.8, label='2-3 Apport Q')
        ax2.plot([2, 2], [T_max, t4], color='#ffea00', lw=0.8, label='3-4 Isentrop.')
        ax2.plot(s_comb[::-1], T1 + (t4-T1)*(s_comb/2), color='#d65cf5', lw=0.8, label='4-1 Rejet Q')
        
        ax2.grid(color='#222', lw=0.5); ax2.tick_params(colors='white'); ax2.legend(fontsize='7', labelcolor='white', facecolor='#000')
        st.pyplot(fig2)

with t_param:
    st.write("### Étude Paramétrique")
    r_vals = np.linspace(5, 20, 100)
    st.line_chart(1 - (1 / (r_vals**(gamma - 1))))

with t_data:
    st.write("### Données du Cycle")
    st.table({"État": [1,2,3,4], "P (bar)": [P1/1e5, p2/1e5, p3/1e5, p4/1e5], "T (K)": [T1, t2, T_max, t4]})
