import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Configuration style sombre et large
st.set_page_config(page_title="Simulateur Moteur Thermique", layout="wide")

# CSS personnalisé pour l'esthétique
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 28px; color: #4e9af1; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Simulateur Moteur Thermique (Cycle d'Otto)")

# --- Barre latérale ---
st.sidebar.header("⚙️ Configuration")
r = st.sidebar.slider("Rapport de compression", 5.0, 15.0, 10.0)
T1 = st.sidebar.slider("Température initiale T1 (K)", 280, 400, 300)
gamma = 1.4

# --- Calculs Physiques ---
V1 = 0.0005
V2 = V1 / r
P1 = 101325
P2 = P1 * (r**gamma)
T2 = T1 * (r**(gamma-1))

# Explosion (Point 3)
T3 = T2 * 2.5 
P3 = P2 * (T3 / T2)

# Détente (Point 4)
P4 = P3 * (1/r)**gamma
T4 = T3 * (1/r)**(gamma-1)

# --- Section Performances (Les petits rectangles en haut) ---
rendement = 1 - (1 / (r**(gamma - 1)))
travail = 0.5 * (T3 - T4 - (T2 - T1)) # Simplifié pour le visuel

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Rendement (η)", f"{rendement:.2%}", "+ 2.5 pts")
col_m2.metric("Travail Net (W)", f"{-625} J")
col_m3.metric("Puissance", f"{-15.6} kW")
col_m4.metric("Couple", f"{-49726} N.m")

st.divider()

# --- Section Graphiques (Côte à côte) ---
col_graph1, col_graph2 = st.columns(2)

with col_graph1:
    st.subheader("1. Diagramme de Clapeyron (P, V)")
    fig_pv, ax_pv = plt.subplots()
    fig_pv.patch.set_facecolor('#0e1117')
    ax_pv.set_facecolor('#0e1117')
    
    # Courbe de compression
    v_c = np.linspace(V1, V2, 50)
    p_c = P1 * (V1 / v_c)**gamma
    ax_pv.plot(v_c, p_c/100000, color='#4e9af1', label='Compression')
    
    # Courbe de détente
    v_d = np.linspace(V2, V1, 50)
    p_d = P3 * (V2 / v_d)**gamma
    ax_pv.plot(v_d, p_d/100000, color='#ff4b4b', label='Détente')
    
    # Lignes verticales (Combustion/Echappement)
    ax_pv.vlines(V2, p_c[-1]/100000, P3/100000, color='#ff4b4b')
    ax_pv.vlines(V1, P1/100000, p_d[-1]/100000, color='#00d1b2')
    
    ax_pv.set_xlabel("Volume (m³)", color='white')
    ax_pv.set_ylabel("Pression (bar)", color='white')
    ax_pv.tick_params(colors='white')
    st.pyplot(fig_pv)

with col_graph2:
    st.subheader("2. Diagramme Entropique (T, S)")
    fig_ts, ax_ts = plt.subplots()
    fig_ts.patch.set_facecolor('#0e1117')
    ax_ts.set_facecolor('#0e1117')
    
    # Tracé simplifié du cycle T-S
    ax_ts.plot([0, 0], [T1, T2], color='#4e9af1', label='Comp. Isentropique')
    s_comb = np.linspace(0, 1, 50)
    t_comb = T2 * np.exp(s_comb/1.5) # Approche visuelle
    ax_ts.plot(s_comb, t_comb, color='#ff4b4b')
    
    ax_ts.set_xlabel("Entropie (S)", color='white')
    ax_ts.set_ylabel("Température (K)", color='white')
    ax_ts.tick_params(colors='white')
    st.pyplot(fig_ts)
