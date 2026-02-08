import streamlit as st
import matplotlib.pyplot as plt
import numpy as np 

# Configuration de la page
st.set_page_config(page_title="Simulateur Thermodynamique EPL", layout="wide")

# --- STYLE CSS (Noir profond, Titre Violet, Police blanche et réduite) ---
st.markdown("""
    <style>
    /* Fond noir profond */
    .stApp { background-color: #050505; color: #FFFFFF; font-size: 13px; }
    
    /* Titre en Violet */
    h1 { color: #9D50BB !important; font-size: 26px !important; text-align: center; font-weight: bold; }
    h2, h3 { color: #FFFFFF !important; font-size: 16px !important; }

    /* Barre latérale - Fond sombre et texte blanc */
    section[data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #222; }
    section[data-testid="stSidebar"] .stMarkdown p, label { color: white !important; font-size: 12px !important; }

    /* Cartes de métriques avec bordures noires prononcées */
    div[data-testid="stMetric"] {
        background-color: #0d0d0d;
        border: 2px solid #000000;
        border-radius: 6px;
        padding: 8px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.8);
    }
    div[data-testid="stMetricValue"] { color: #00FFCC !important; font-size: 20px !important; }
    div[data-testid="stMetricLabel"] { color: #FFFFFF !important; font-size: 12px !important; }

    /* Onglets - Style épuré */
    .stTabs [data-baseweb="tab"] { color: white !important; font-size: 13px; }
    .stTabs [aria-selected="true"] { border-bottom: 2px solid #9D50BB !important; font-weight: bold; }
    
    /* Boutons et Sliders */
    .stSlider label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRE LATÉRALE ---
with st.sidebar:
    # Logo Université de Lomé et de l'Epl
    st.image("im1.jpeg", width=160)
    st.markdown("### Configuration")
    type_cycle = st.selectbox("Type de Cycle", ["Otto (Beau de Rochas)", "Diesel"])
    modele_gaz = st.selectbox("Modèle de Gaz", ["Gaz Parfait (Air)", "Gaz Simple"])
    
    st.markdown("### Paramètres d'Entrée")
    # L'utilisateur définit les conditions initiales et les limites
    V1 = st.number_input("Volume initial V1 (m³)", value=0.0005, format="%.5f")
    P1 = st.number_input("Pression initiale P1 (Pa)", value=101325)
    T1 = st.number_input("Température initiale T1 (K)", value=300)
    
    st.markdown("### Variables de Modélisation")
    r = st.slider("Taux de Compression (r)", 5.0, 22.0, 9.5)
    T_max = st.slider("Température Max (K)", 1000, 2800, 2100)
    
    # Constantes physiques
    gamma = 1.4 if "Air" in modele_gaz else 1.3
    Cv = 718  # J/kg.K
    R_gas = 287 # J/kg.K
    RPM = 3000

# --- CALCULS THERMODYNAMIQUES ---
V2 = V1 / r
m = (P1 * V1) / (R_gas * T1) # Masse d'air

# 1-2 Compression Isentropique
T2 = T1 * (r**(gamma-1))
P2 = P1 * (r**gamma)

if "Otto" in type_cycle:
    # 2-3 Combustion Isochore
    V3 = V2
    P3 = P2 * (T_max / T2)
    # 3-4 Détente Isentropique
    V4 = V1
    P4 = P3 * (V3/V4)**gamma
    T4 = T_max * (V3/V4)**(gamma-1)
    # Rendement théorique Otto
    rendement = 1 - (1/(r**(gamma-1)))
else:
    # Diesel : 2-3 Combustion Isobare
    P3 = P2
    rc = T_max / T2 # rapport d'injection
    V3 = V2 * rc
    # 3-4 Détente Isentropique
    V4 = V1
    P4 = P3 * (V3/V4)**gamma
    T4 = T_max * (V3/V4)**(gamma-1)
    # Rendement théorique Diesel
    rendement = 1 - ( (1/gamma) * ((rc**gamma - 1) / (rc - 1)) * (1 / r**(gamma-1)) )

# Bilan Énergétique
Q_in = m * Cv * (T_max - T2) if "Otto" in type_cycle else m * (Cv + R_gas) * (T_max - T2)
W_net = Q_in * rendement
puissance_kw = (W_net * RPM) / (60 * 1000)
couple_nm = (puissance_kw * 1000) / (2 * np.pi * RPM / 60)

# --- INTERFACE PRINCIPALE ---
st.title("SIMULATEUR MOTEUR THERMIQUE - EPL")

tab1, tab2, tab3 = st.tabs(["📊 Labo Virtuel", "📈 Étude Paramétrique", "📋 Données du Cycle"])

with tab1:
    # Métriques
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rendement (η)", f"{rendement:.2%}")
    c2.metric("Travail Net", f"{W_net:.2f} J")
    c3.metric("Puissance", f"{puissance_kw:.1f} kW")
    c4.metric("Couple", f"{abs(couple_nm):.1f} N.m")

    st.markdown("---")
    col_g1, col_g2 = st.columns(2)
    line_w = 1.2 # Traits fins demandés

    with col_g1:
        st.write("### 1. Diagramme de Clapeyron (P, V)")
        fig_pv, ax_pv = plt.subplots(facecolor='#050505')
        ax_pv.set_facecolor('#050505')
        
        # Phase 1-2
        v12 = np.linspace(V1, V2, 100)
        ax_pv.plot(v12, P1*(V1/v12)**gamma / 1e5, color='#00CCFF', lw=line_w, label='1-2 Compression')
        # Phase 2-3
        if "Otto" in type_cycle:
            ax_pv.plot([V2, V2], [P2/1e5, P3/1e5], color='#FF3366', lw=line_w, label='2-3 Combustion')
        else:
            ax_pv.plot([V2, V3], [P3/1e5, P3/1e5], color='#FF3366', lw=line_w, label='2-3 Combustion')
        # Phase 3-4
        v34 = np.linspace(V3, V4, 100)
        ax_pv.plot(v34, P3*(V3/v34)**gamma / 1e5, color='#FFFF33', lw=line_w, label='3-4 Détente')
        # Phase 4-1
        ax_pv.plot([V4, V1], [P4/1e5, P1/1e5], color='#33FF99', lw=line_w, label='4-1 Échappement')

        ax_pv.grid(color='#222', ls='--', lw=0.5)
        ax_pv.set_xlabel("Volume (m³)", color='white', fontsize=9)
        ax_pv.set_ylabel("Pression (bar)", color='white', fontsize=9)
        ax_pv.tick_params(colors='white', labelsize=8)
        ax_pv.legend(fontsize=7, facecolor='#111', edgecolor='#333', labelcolor='white')
        st.pyplot(fig_pv)

    with col_g2:
        st.write("### 2. Diagramme Entropique (T, S)")
        fig_ts, ax_ts = plt.subplots(facecolor='#050505')
        ax_ts.set_facecolor('#050505')
        
        # Calcul de l'entropie
        s1 = 0
        s2 = s1 # Isentropique
        # 2-3 (Chaleur ajoutée)
        temp_23 = np.linspace(T2, T_max, 50)
        s_23 = s2 + (Cv * np.log(temp_23/T2)) / 100 # Approx pour visuel
        s3 = s_23[-1]
        s4 = s3 # Isentropique
        # 4-1 (Chaleur rejetée)
        temp_41 = np.linspace(T4, T1, 50)
        s_41 = s4 + (Cv * np.log(temp_41/T4)) / 100

        ax_ts.plot([s1, s2], [T1, T2], color='#00CCFF', lw=line_w, label='1-2 Comp.')
        ax_ts.plot(s_23, temp_23, color='#FF3366', lw=line_w, label='2-3 Comb.')
        ax_ts.plot([s3, s4], [T_max, T4], color='#FFFF33', lw=line_w, label='3-4 Dét.')
        ax_ts.plot(s_41, temp_41, color='#33FF99', lw=line_w, label='4-1 Échap.')

        ax_ts.grid(color='#222', ls='--', lw=0.5)
        ax_ts.set_xlabel("Entropie (S)", color='white', fontsize=9)
        ax_ts.set_ylabel("Température (K)", color='white', fontsize=9)
        ax_ts.tick_params(colors='white', labelsize=8)
        ax_ts.legend(fontsize=7, facecolor='#111', edgecolor='#333', labelcolor='white')
        st.pyplot(fig_ts)

with tab2:
    st.subheader("Influence du Taux de Compression")
    r_axis = np.linspace(5, 22, 100)
    eta_axis = 1 - (1/(r_axis**(gamma-1))) if "Otto" in type_cycle else 1 - (1/gamma)*((1.5**gamma-1)/(1.5-1))*(1/r_axis**(gamma-1))
    
    fig_p, ax_p = plt.subplots(facecolor='#050505')
    ax_p.set_facecolor('#050505')
    ax_p.plot(r_axis, eta_axis*100, color='#9D50BB', lw=1.5)
    ax_p.scatter([r], [rendement*100], color='#00FFCC', s=50, label="Point Actuel")
    
    ax_p.set_xlabel("r", color='white')
    ax_p.set_ylabel("Rendement (%)", color='white')
    ax_p.grid(color='#222', ls='--', lw=0.5)
    ax_p.tick_params(colors='white')
    st.pyplot(fig_p)
    st.info("L'étude montre qu'augmenter le taux de compression 'r' améliore le rendement mais augmente la pression maximale P3.")

with tab3:
    st.subheader("États Thermodynamiques du Cycle")
    data = {
        "Point": ["1 (Aspiration)", "2 (Fin Compression)", "3 (Fin Combustion)", "4 (Fin Détente)"],
        "Volume (m³)": [f"{V1:.5f}", f"{V2:.5f}", f"{V3:.5f}", f"{V4:.5f}"],
        "Pression (bar)": [f"{P1/1e5:.2f}", f"{P2/1e5:.2f}", f"{P3/1e5:.2f}", f"{P4/1e5:.2f}"],
        "Température (K)": [f"{T1:.1f}", f"{T2:.1f}", f"{T_max:.1f}", f"{T4:.1f}"]
    }
    st.table(data)
    
    st.subheader("Bilan Énergétique Total")
    st.write(f"**Masse de fluide :** {m*1000:.4f} g")
    st.write(f"**Énergie introduite (Q_in) :** {Q_in:.2f} J")
    st.write(f"**Travail net produit :** {W_net:.2f} J")
