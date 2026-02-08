import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Configuration de la page
st.set_page_config(page_title="Simulateur Thermodynamique EPL", layout="wide")

# --- STYLE CSS (Bordures noires, Titres violets, Onglets EPL) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    div[data-testid="stMetric"] {
        background-color: #1e222d;
        border: 2px solid #000000;
        border-radius: 10px;
        padding: 15px;
    }
    h1, h2, h3 { color: #d65cf5 !important; }
    div[data-testid="stMetricValue"] { color: #00ff88 !important; font-size: 32px !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #262730; color: white; border-radius: 5px; padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { border-bottom: 3px solid #d65cf5 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("im1.jpeg", width=220)
    st.markdown("### 🛠️ Modélisation")
    type_cycle = st.selectbox("Type de Cycle", ["Otto (Beau de Rochas)"])
    modele_gaz = st.selectbox("Modèle de Gaz", ["Gaz Simple", "Gaz Parfait"])
    
    st.markdown("### 📝 Paramètres d'Entrée")
    V1 = st.number_input("Volume initial V1 (m³)", value=0.03000, format="%.5f")
    P1 = st.number_input("Pression initiale P1 (Pa)", value=101328)
    T1 = st.number_input("Température initiale T1 (K)", value=302)
    
    st.markdown("### 🌡️ Variables")
    r = st.slider("Taux de Compression (r)", 5.0, 15.0, 9.50)
    T_max = st.slider("Température Max (K)", 1000, 3000, 2100)

# --- CALCULS PHYSIQUES ---
gamma = 1.4 if modele_gaz == "Gaz Parfait" else 1.32
Cv = 718  # J/kg.K pour l'air
R = 287
mass = (P1 * V1) / (R * T1)
V2 = V1 / r

# Points du cycle
p2 = P1 * (r**gamma)
t2 = T1 * (r**(gamma-1))
p3 = p2 * (T_max / t2)
p4 = p3 * (1/r)**gamma
t4 = T_max * (1/r)**(gamma-1)

# Performances
W_net = mass * Cv * (T1 - t2 + T_max - t4)
rendement = 1 - (1 / (r**(gamma - 1)))
puissance = abs(W_net) * (3000 / 60)
couple = puissance / (2 * np.pi * 3000 / 60)

# --- AFFICHAGE ---
st.markdown("<h1 style='text-align: center;'>SIMULATEUR MOTEUR THERMIQUE - EPL</h1>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["📊 Labo Virtuel", "📈 Étude Paramétrique", "📋 Données", "🎓 Projet EPL"])

with tab1:
    st.subheader("Performances Temps Réel")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rendement (η)", f"{rendement:.2%}")
    c2.metric("Travail Net", f"{abs(W_net):.2f} J")
    c3.metric("Puissance", f"{puissance/1000:.2f} kW")
    c4.metric("Couple", f"{couple:.2f} N.m")

    st.divider()

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.write("### 1. Diagramme de Clapeyron (P, V)")
        fig, ax = plt.subplots(facecolor='#0e1117')
        ax.set_facecolor('#0e1117')
        
        # 1-2 Compression (Bleu ciel)
        v_12 = np.linspace(V1, V2, 100)
        p_12 = P1 * (V1 / v_12)**gamma
        ax.plot(v_12, p_12/100000, color='#00ccff', linewidth=2, label='1-2 Compression')
        
        # 2-3 Combustion (Rouge)
        ax.plot([V2, V2], [p2/100000, p3/100000], color='#ff3333', linewidth=2, label='2-3 Combustion')
        
        # 3-4 Détente (Jaune)
        v_34 = np.linspace(V2, V1, 100)
        p_34 = p3 * (V2 / v_34)**gamma
        ax.plot(v_34, p_34/100000, color='#ffff33', linewidth=2, label='3-4 Détente')
        
        # 4-1 Échappement (Vert)
        ax.plot([V1, V1], [p4/100000, P1/100000], color='#33ff33', linewidth=2, label='4-1 Échappement')

        ax.grid(color='#333', linestyle='--')
        ax.set_xlabel("Volume (m³)", color='white')
        ax.set_ylabel("Pression (bar)", color='white')
        ax.tick_params(colors='white')
        ax.legend(facecolor='#1e222d', labelcolor='white')
        st.pyplot(fig)

    with col_g2:
        st.write("### 2. Diagramme Entropique (T, S)")
        fig2, ax2 = plt.subplots(facecolor='#0e1117')
        ax2.set_facecolor('#0e1117')
        
        # Calcul de l'entropie deltaS = Cv * ln(T2/T1) + R * ln(V2/V1)
        # 1-2 Isentropique (S constant) -> Ligne verticale Bleu ciel
        ax2.plot([0, 0], [T1, t2], color='#00ccff', linewidth=2, label='1-2 Comp.')
        
        # 2-3 Apport de chaleur (Isochore) -> Courbe Rouge
        t_23 = np.linspace(t2, T_max, 100)
        s_23 = Cv * np.log(t_23 / t2)
        ax2.plot(s_23, t_23, color='#ff3333', linewidth=2, label='2-3 Comb.')
        
        # 3-4 Isentropique (S constant) -> Ligne verticale Jaune
        s_max = s_23[-1]
        ax2.plot([s_max, s_max], [T_max, t4], color='#ffff33', linewidth=2, label='3-4 Dét.')
        
        # 4-1 Rejet de chaleur (Isochore) -> Courbe Verte
        t_41 = np.linspace(t4, T1, 100)
        s_41 = s_max + Cv * np.log(t_41 / t4)
        ax2.plot(s_41, t_41, color='#33ff33', linewidth=2, label='4-1 Échap.')

        ax2.grid(color='#333', linestyle='--')
        ax2.set_xlabel("Entropie (S) [J/kg.K]", color='white')
        ax2.set_ylabel("Température (K)", color='white')
        ax2.tick_params(colors='white')
        ax2.legend(facecolor='#1e222d', labelcolor='white')
        st.pyplot(fig2)
