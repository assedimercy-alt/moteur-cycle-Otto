import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Configuration de la page
st.set_page_config(page_title="Simulateur Thermodynamique EPL", layout="wide")

# --- STYLE CSS (Fidèle à l'image : Dashboard sombre et bordures noires) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    
    /* Cartes de métriques avec contour noir */
    div[data-testid="stMetric"] {
        background-color: #1e222d;
        border: 2px solid #000000;
        border-radius: 8px;
        padding: 15px;
    }
    
    h1, h2, h3 { color: #d65cf5 !important; font-family: 'sans-serif'; } /* Titre violet comme image */
    div[data-testid="stMetricValue"] { color: #00ff88 !important; font-size: 28px !important; }
    
    /* Style des Onglets */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #262730; color: white; border-radius: 5px; padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { border-bottom: 2px solid #d65cf5 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRE LATÉRALE (Paramètres d'entrée) ---
with st.sidebar:
    st.image("im1.jpeg", width=220)
    
    st.selectbox("Type de Cycle", ["Otto (Beau de Rochas)"], key="type")
    st.selectbox("Modèle de Gaz", ["Gaz Simple", "Gaz Parfait"], key="gaz")
    
    st.markdown("### Paramètres d'Entrée")
    V1 = st.number_input("Volume initial V1 (m³)", value=0.03000, format="%.5f")
    P1 = st.number_input("Pression initiale P1 (Pa)", value=101328)
    T1 = st.number_input("Température initiale T1 (K)", value=302)
    
    st.markdown("### Variables de Modélisation")
    r = st.slider("Taux de Compression (r)", 5.0, 15.0, 9.50)
    T_max = st.slider("Température Max (K)", 1000, 3000, 2100)

# --- CALCULS PHYSIQUES ---
gamma = 1.4 if st.session_state.gaz == "Gaz Parfait" else 1.32
R = 287
mass = (P1 * V1) / (R * T1)
V2 = V1 / r

# Points du Cycle Otto
# 1->2 : Compression
p2 = P1 * (r**gamma)
t2 = T1 * (r**(gamma-1))
W_comp = (mass * R * (t2 - T1)) / (1 - gamma)

# 2->3 : Combustion
p3 = p2 * (T_max / t2)

# 3->4 : Détente
p4 = p3 * (1/r)**gamma
t4 = T_max * (1/r)**(gamma-1)
W_det = (mass * R * (t4 - T_max)) / (1 - gamma)

# Résultats finaux
travail_net = W_comp + W_det
rendement = 1 - (1 / (r**(gamma - 1)))
puissance = travail_net * (3000 / 60) # Simulée à 3000 RPM
couple = puissance / (2 * np.pi * 3000 / 60)

# --- AFFICHAGE PRINCIPAL ---
st.markdown("<h2 style='text-align: center;'>SIMULATEUR MOTEUR THERMIQUE - EPL</h2>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 Labo Virtuel", "📈 Étude Paramétrique", "📋 Données du Cycle"])

with tab1:
    # Métriques
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rendement (η)", f"{rendement:.2%}")
    c2.metric("Travail Net", f"{abs(travail_net):.2f} J")
    c3.metric("Puissance", f"{abs(puissance/1000):.1f} kW")
    c4.metric("Couple", f"{abs(couple):.1f} N.m")

    st.divider()

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.write("### 1. Diagramme de Clapeyron (P, V)")
        fig, ax = plt.subplots(facecolor='#0e1117')
        ax.set_facecolor('#0e1117')
        
        # Courbes
        v_c = np.linspace(V1, V2, 100)
        p_c = P1 * (V1 / v_c)**gamma
        ax.plot(v_c, p_c/100000, color='#00f2ff', label='1-2 Compression')
        
        ax.plot([V2, V2], [p2/100000, p3/100000], color='#ff0055', label='2-3 Combustion')
        
        v_d = np.linspace(V2, V1, 100)
        p_d = p3 * (V2 / v_d)**gamma
        ax.plot(v_d, p_d/100000, color='#ffea00', label='3-4 Détente')
        
        ax.plot([V1, V1], [p4/100000, P1/100000], color='#00ff88', label='4-1 Échappement')

        ax.grid(color='#444', linestyle='--', linewidth=0.5)
        ax.set_xlabel("Volume (m³)", color='white')
        ax.set_ylabel("Pression (bar)", color='white')
        ax.tick_params(colors='white')
        ax.legend(facecolor='#1e222d', labelcolor='white')
        st.pyplot(fig)

    with col_g2:
        st.write("### 2. Diagramme Entropique (T, S)")
        fig2, ax2 = plt.subplots(facecolor='#0e1117')
        ax2.set_facecolor('#0e1117')
        
        # Simulation T-S
        s = np.linspace(0, 8, 100)
        t_c = T1 + (t2-T1)*(s/8)
        t_d = t4 + (T_max-t4)*(s/8)
        ax2.plot(s, t_c, color='#00ff88')
        ax2.plot(s, t_d, color='#ff0055')
        
        ax2.grid(color='#444', linestyle='--', linewidth=0.5)
        ax2.set_xlabel("Entropie (S)", color='white')
        ax2.set_ylabel("Température (K)", color='white')
        ax2.tick_params(colors='white')
        st.pyplot(fig2)
