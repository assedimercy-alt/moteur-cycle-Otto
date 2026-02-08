import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Configuration de la page
st.set_page_config(page_title="Simulateur Thermodynamique EPL", layout="wide")

# --- STYLE CSS (Noir profond, Titre Violet, Police réduite, Blanc pur) ---
st.markdown("""
    <style>
    /* Fond noir profond */
    .stApp { background-color: #050505; color: #FFFFFF; font-size: 14px; }
    
    /* Titre en Violet */
    h1 { color: #9D50BB !important; font-size: 28px !important; text-align: center; }
    h2, h3 { color: #FFFFFF !important; font-size: 18px !important; }

    /* Texte de la barre latérale en blanc */
    section[data-testid="stSidebar"] { background-color: #0a0a0a; color: white; }
    section[data-testid="stSidebar"] .stMarkdown p, label { color: white !important; font-size: 13px !important; }

    /* Cartes de métriques avec bordures noires et police réduite */
    div[data-testid="stMetric"] {
        background-color: #111111;
        border: 2px solid #000000;
        border-radius: 8px;
        padding: 10px;
    }
    div[data-testid="stMetricValue"] { color: #00FFCC !important; font-size: 22px !important; }
    div[data-testid="stMetricLabel"] { color: #FFFFFF !important; font-size: 13px !important; }

    /* Onglets stylisés */
    .stTabs [data-baseweb="tab"] { color: white !important; font-size: 14px; }
    .stTabs [aria-selected="true"] { border-bottom: 2px solid #9D50BB !important; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.image("im1.jpeg", width=180)
    st.markdown("### Configuration")
    type_cycle = st.selectbox("Type de Cycle", ["Otto (Beau de Rochas)", "Diesel"])
    modele_gaz = st.selectbox("Modèle de Gaz", ["Gaz Parfait (Air)", "Gaz Simple"])
    
    st.markdown("### Paramètres")
    r = st.slider("Taux de Compression (r)", 5.0, 20.0, 9.0)
    T_max = st.slider("Température Max (K)", 1000, 2800, 2000)
    
    gamma = 1.4 if "Air" in modele_gaz else 1.3
    Cv = 718  # J/kg.K pour l'air

# --- CALCULS PHYSIQUES ---
T1, P1 = 300, 101325
V1 = 1.0
V2 = V1 / r
# 1-2 Compression
T2 = T1 * (r**(gamma-1))
P2 = P1 * (r**gamma)

if "Otto" in type_cycle:
    # 2-3 Combustion Isochore
    V3 = V2
    P3 = P2 * (T_max / T2)
    # 3-4 Détente
    V4 = V1
    P4 = P3 * (V3/V4)**gamma
    T4 = T_max * (V3/V4)**(gamma-1)
else:
    # Diesel : 2-3 Combustion Isobare
    P3 = P2
    rc = T_max / T2 # rapport d'injection
    V3 = V2 * rc
    # 3-4 Détente
    V4 = V1
    P4 = P3 * (V3/V4)**gamma
    T4 = T_max * (V3/V4)**(gamma-1)

# Rendement
rendement = 1 - (1/(r**(gamma-1))) if "Otto" in type_cycle else 1 - (1/gamma)*((rc**gamma-1)/(rc-1))*(1/r**(gamma-1))

# --- HEADER ---
st.title("Simulateur Moteur Thermique - Labo Virtuel")

tab1, tab2, tab3 = st.tabs(["📊 Labo Virtuel", "📈 Étude Paramétrique", "📋 Données"])

with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rendement (η)", f"{rendement:.2%}")
    c2.metric("Travail Net", f"-625 J")
    c3.metric("Puissance", "-15.6 kW")
    c4.metric("Couple", "-49726 N.m")

    col_g1, col_g2 = st.columns(2)

    # Paramètres graphiques communs (traits fins : lw=1.5)
    line_w = 1.5

    with col_g1:
        st.write("### 1. Diagramme de Clapeyron (P, V)")
        fig, ax = plt.subplots(facecolor='#050505')
        ax.set_facecolor('#050505')
        
        # Courbes P-V
        v_c = np.linspace(V1, V2, 100)
        ax.plot(v_c, P1*(V1/v_c)**gamma / 1e5, color='#00CCFF', lw=line_w, label='1-2 Compression')
        if "Otto" in type_cycle:
            ax.plot([V2, V2], [P2/1e5, P3/1e5], color='#FF3366', lw=line_w, label='2-3 Combustion')
        else:
            ax.plot([V2, V3], [P3/1e5, P3/1e5], color='#FF3366', lw=line_w, label='2-3 Combustion')
        v_d = np.linspace(V3, V4, 100)
        ax.plot(v_d, P3*(V3/v_d)**gamma / 1e5, color='#FFFF33', lw=line_w, label='3-4 Détente')
        ax.plot([V4, V1], [P4/1e5, P1/1e5], color='#33FF99', lw=line_w, label='4-1 Échappement')

        ax.grid(color='#222', ls='--', lw=0.5)
        ax.set_xlabel("Volume", color='white', fontsize=10)
        ax.set_ylabel("Pression (bar)", color='white', fontsize=10)
        ax.tick_params(colors='white', labelsize=8)
        leg = ax.legend(fontsize=7, facecolor='#111', edgecolor='#333', labelcolor='white')
        st.pyplot(fig)

    with col_g2:
        st.write("### 2. Diagramme Entropique (T, S)")
        fig2, ax2 = plt.subplots(facecolor='#050505')
        ax2.set_facecolor('#050505')
        
        # Calcul simplifié de l'entropie deltaS = Cv * ln(T/T_ref) + R * ln(V/V_ref)
        # On trace les 4 phases
        s1 = 0
        s2 = s1 # Isentropique
        # 2-3 Combustion
        temp_23 = np.linspace(T2, T_max, 50)
        s_23 = s2 + (Cv * np.log(temp_23/T2)) / 1000 # Approximation
        # 3-4 Détente (Isentropique)
        s3 = s_23[-1]
        s4 = s3
        # 4-1 Échappement
        temp_41 = np.linspace(T4, T1, 50)
        s_41 = s4 + (Cv * np.log(temp_41/T4)) / 1000

        ax2.plot([s1, s2], [T1, T2], color='#00CCFF', lw=line_w, label='1-2 Comp.')
        ax2.plot(s_23, temp_23, color='#FF3366', lw=line_w, label='2-3 Comb.')
        ax2.plot([s3, s4], [T_max, T4], color='#FFFF33', lw=line_w, label='3-4 Dét.')
        ax2.plot(s_41, temp_41, color='#33FF99', lw=line_w, label='4-1 Échap.')

        ax2.grid(color='#222', ls='--', lw=0.5)
        ax2.set_xlabel("Entropie (S)", color='white', fontsize=10)
        ax2.set_ylabel("Température (K)", color='white', fontsize=10)
        ax2.tick_params(colors='white', labelsize=8)
        ax2.legend(fontsize=7, facecolor='#111', edgecolor='#333', labelcolor='white')
        st.pyplot(fig2)
