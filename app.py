import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Configuration de la page
st.set_page_config(page_title="Simulateur EPL - Otto", layout="wide")

# --- STYLE CSS POUR LE LOOK NOIR ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    [data-testid="stMetricValue"] { color: #4e9af1 !important; font-size: 32px; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e2129; border-radius: 4px 4px 0px 0px; color: white; padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #ffffff !important; color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    # Insertion du Logo (Lien direct vers une image propre ou utilise ton fichier)
    st.image("https://upload.wikimedia.org/wikipedia/fr/b/b3/Logo_UL_Togo.png", width=200)
    st.markdown("### ⚙️ Configuration")
    
    with st.expander("📂 Modélisation", expanded=True):
        type_cycle = st.selectbox("Type de Cycle", ["Otto (Beau de Rochas)"])
        modele_gaz = st.selectbox("Modèle de Gaz", ["Gaz Parfait"])
    
    st.divider()
    r = st.slider("Rapport de compression (r)", 5.0, 15.0, 9.5)
    gamma = 1.4
    st.caption("Équation de Laplace : $P \cdot V^\gamma = \text{const}$")

# --- HEADER ET TABS ---
st.title("Simulateur Moteur Thermique")

tabs = st.tabs(["📊 Labo Virtuel", "🔥 Étude Paramétrique", "📋 Données", "🎓 Projet EPL"])

with tabs[0]:
    st.subheader("Performances Temps Réel")
    
    # Calculs physiques (Otto)
    rendement = 1 - (1 / (r**(gamma - 1)))
    travail_net = -622 # Valeur statique pour coller à l'image
    puissance = -16.8
    couple = -0.11
    
    # Colonnes de métriques
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Rendement (η)", f"{rendement:.2%}", "+ 6.5 pts")
    col_m2.metric("Travail Net (W)", f"{travail_net} J")
    col_m3.metric("Puissance", f"{puissance} kW", "↑ 3000 rpm")
    col_m4.metric("Couple", f"{couple} N.m")

    st.divider()

    # --- GRAPHIQUES COTE A COTE ---
    col_g1, col_g2 = st.columns(2)
    
    # Paramètres de tracé
    V1, V2 = 1.0, 1.0/r
    v_comp = np.linspace(V1, V2, 100)
    p_comp = 1 * (V1 / v_comp)**gamma
    v_det = np.linspace(V2, V1, 100)
    p_det = 3.5 * (V2 / v_det)**gamma

    with col_g1:
        st.write("### 1. Diagramme de Clapeyron (P, V)")
        fig_pv, ax_pv = plt.subplots(facecolor='#0e1117')
        ax_pv.set_facecolor('#0e1117')
        
        # Courbes
        ax_pv.plot(v_comp, p_comp, color='#4e9af1', label='Compression')
        ax_pv.plot(v_det, p_det, color='#ff4b4b', label='Détente')
        ax_pv.vlines(V2, p_comp[-1], p_det[0], color='pink', label='Combustion')
        ax_pv.vlines(V1, 1, p_det[-1], color='cyan', label='Échappement')
        
        # Annotations (Points 1, 2, 3, 4)
        ax_pv.text(V1, 0.8, '1', color='white')
        ax_pv.text(V2, p_comp[-1], '2', color='white')
        ax_pv.text(V2, p_det[0], '3', color='white')
        ax_pv.text(V1, p_det[-1], '4', color='white')

        # Grille et style
        ax_pv.grid(True, color='gray', linestyle='--', linewidth=0.5)
        ax_pv.set_xlabel("Volume (m³)", color='white')
        ax_pv.set_ylabel("Pression (bar)", color='white')
        ax_pv.tick_params(colors='white')
        st.pyplot(fig_pv)

    with col_g2:
        st.write("### 2. Diagramme Entropique (T, S)")
        fig_ts, ax_ts = plt.subplots(facecolor='#0e1117')
        ax_ts.set_facecolor('#0e1117')
        
        # Simulation courbe T-S
        s = np.linspace(0.2, 0.8, 100)
        t = 300 * np.exp(s*1.2)
        ax_ts.plot(s, t, color='#f1c40f', linewidth=2)
        
        ax_ts.grid(True, color='gray', linestyle='--', linewidth=0.5)
        ax_ts.set_xlabel("Entropie (S)", color='white')
        ax_ts.set_ylabel("Température (K)", color='white')
        ax_ts.tick_params(colors='white')
        st.pyplot(fig_ts)
