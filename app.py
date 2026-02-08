import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Configuration de la page
st.set_page_config(page_title="Simulateur Thermodynamique EPL", layout="wide")

# --- STYLE CSS COMPLET (Bordures noires, couleurs vives, mode sombre) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    
    /* Cartes de métriques avec contour noir épais identique à ton image */
    div[data-testid="stMetric"] {
        background-color: #1e222d;
        border: 4px solid #000000;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.6);
    }
    
    h1, h2, h3 { color: #00f2ff !important; font-family: 'Arial'; }
    div[data-testid="stMetricValue"] { color: #00ff88 !important; font-size: 38px !important; font-weight: bold; }
    div[data-testid="stMetricLabel"] { color: #ffffff !important; font-size: 20px !important; }
    
    /* Style des Onglets blancs quand sélectionnés */
    .stTabs [data-baseweb="tab-list"] { gap: 12px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #262730; color: white; border-radius: 5px; padding: 12px 24px;
    }
    .stTabs [aria-selected="true"] { background-color: #ffffff !important; color: black !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    # Logo de l'école
    st.image("https://upload.wikimedia.org/wikipedia/fr/b/b3/Logo_UL_Togo.png", width=220)
    st.markdown("## ⚙️ Configuration")
    
    with st.expander("🔬 Modélisation", expanded=True):
        type_cycle = st.selectbox("Type de Cycle", ["Otto (Beau de Rochas)", "Diesel"])
        modele_gaz = st.selectbox("Modèle de Gaz", ["Gaz Parfait (Air)", "Gaz Simple"])
    
    with st.expander("🌡️ Paramètres Thermodynamiques", expanded=True):
        r = st.slider("Taux de Compression (r)", 5.0, 22.0, 9.5)
        T_max = st.slider("Température Max (K)", 1000, 3000, 2200)
        P1 = 101325 # Pa
        T1 = 300    # K
        gamma = 1.4 if modele_gaz == "Gaz Parfait (Air)" else 1.3
    
    st.info("💡 Conseil : Augmentez T_max pour obtenir un cycle moteur puissant.")

# --- CALCULS PHYSIQUES ---
R = 287  
V1 = 0.0005 
V2 = V1 / r
mass = (P1 * V1) / (R * T1)

# 1 -> 2 : Compression Adiabatique
p2 = P1 * (r**gamma)
t2 = T1 * (r**(gamma-1))
W_comp = (mass * R * (t2 - T1)) / (1 - gamma)

if "Otto" in type_cycle:
    # Combustion Isochore
    V3 = V2
    p3 = p2 * (T_max / t2)
    # Détente Adiabatique
    V4 = V1
    p4 = p3 * (V2 / V4)**gamma
    t4 = T_max * (V2 / V4)**(gamma-1)
    rendement = 1 - (1 / (r**(gamma - 1)))
else:
    # Diesel : Combustion Isobare
    p3 = p2
    rc = T_max / t2 
    V3 = V2 * rc
    V4 = V1
    p4 = p3 * (V3 / V4)**gamma
    t4 = T_max * (V3 / V4)**(gamma-1)
    rendement = 1 - ( (1/gamma) * ((rc**gamma - 1) / (rc - 1)) * (1 / r**(gamma-1)) )

# Travail de détente et bilan
W_det = (mass * R * (t4 - T_max)) / (1 - gamma)
travail_net = W_comp + W_det 
puissance_watt = travail_net * (3000 / 60)
couple_val = puissance_watt / (2 * np.pi * 3000 / 60)

# --- CORPS DU SITE ---
st.title("Simulateur Moteur Thermique - Labo Virtuel")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Labo Virtuel", "📈 Étude Paramétrique", "📋 Données", "🎓 Projet EPL"])

with tab1:
    st.subheader("Performances Temps Réel")
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Rendement (η)", f"{rendement:.2%}", "+ 6.5 pts")
    col_m2.metric("Travail Net (W)", f"{travail_net:.1f} J", 
                  delta="Moteur" if travail_net < 0 else "Compresseur",
                  delta_color="normal" if travail_net < 0 else "inverse")
    col_m3.metric("Puissance", f"{puissance_watt/1000:.1f} kW", "↑ 3000 rpm")
    col_m4.metric("Couple", f"{couple_val:.1f} N.m")

    st.divider()

    g1, g2 = st.columns(2)
    with g1:
        st.write("### 1. Diagramme de Clapeyron (P, V)")
        fig, ax = plt.subplots(facecolor='#0e1117')
        ax.set_facecolor('#0e1117')
        
        # Courbes avec couleurs vives et légendes
        v_c = np.linspace(V1, V2, 100)
        p_c = P1 * (V1 / v_c)**gamma
        ax.plot(v_c*1000, p_c/100000, color='#00f2ff', linewidth=3, label='Compression')
        
        if "Otto" in type_cycle:
            ax.plot([V2*1000, V2*1000], [p2/100000, p3/100000], color='#ff0055', linewidth=3, label='Combustion')
        else:
            ax.plot([V2*1000, V3*1000], [p3/100000, p3/100000], color='#ff0055', linewidth=3, label='Combustion')
            
        v_d = np.linspace(V3, V4, 100)
        p_d = p3 * (V3 / v_d)**gamma
        ax.plot(v_d*1000, p_d/100000, color='#ffea00', linewidth=3, label='Détente')
        ax.plot([V1*1000, V1*1000], [p4/100000, P1/100000], color='#00ff88', linewidth=3, label='Échappement')

        ax.grid(color='#444', linestyle='--', alpha=0.7)
        ax.set_xlabel("Volume (Litre)", color='white')
        ax.set_ylabel("Pression (bar)", color='white')
        ax.tick_params(colors='white')
        
        leg = ax.legend(facecolor='#1e222d', edgecolor='white')
        for text in leg.get_texts(): text.set_color("white")
        st.pyplot(fig)

    with g2:
        st.write("### 2. Diagramme Entropique (T, S)")
        fig2, ax2 = plt.subplots(facecolor='#0e1117')
        ax2.set_facecolor('#0e1117')
        
        # Courbe T-S dynamique
        s_base = np.linspace(0.2, 0.8, 100)
        t_curve = T1 + (T_max - T1) * (s_base**1.5)
        ax2.plot(s_base, t_curve, color='#ff00ff', linewidth=3, label="Cycle T-S")
        
        ax2.grid(color='#444', linestyle='--', alpha=0.7)
        ax2.set_xlabel("Entropie (S)", color='white')
        ax2.set_ylabel("Température (K)", color='white')
        ax2.tick_params(colors='white')
        st.pyplot(fig2)

with tab2:
    st.info("📊 Analyse de sensibilité : Le rendement augmente avec le taux de compression.")

with tab3:
    st.table({
        "État du Gaz": ["Aspiration (1)", "Fin Compression (2)", "Fin Combustion (3)", "Fin Détente (4)"],
        "Pression (bar)": [round(P1/100000, 2), round(p2/100000, 2), round(p3/100000, 2), round(p4/100000, 2)],
        "Volume (L)": [round(V1*1000, 2), round(V2*1000, 2), round(V3*1000, 2), round(V4*1000, 2)],
        "Température (K)": [round(T1, 1), round(t2, 1), round(T_max, 1), round(t4, 1)]
    })

with tab4:
    st.write("### 🎓 École Polytechnique de Lomé (EPL)")
    st.write("Ce simulateur a été développé pour l'étude des moteurs à combustion interne.")
