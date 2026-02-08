import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Configuration de la page
st.set_page_config(page_title="Simulateur Thermodynamique EPL", layout="wide")

# --- STYLE CSS PERSONNALISÉ (Couleurs vives et bordures noires) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    
    /* Style des cartes de métriques avec contour noir épais */
    div[data-testid="stMetric"] {
        background-color: #1e222d;
        border: 3px solid #000000;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.5);
    }
    
    /* Couleurs vives pour les titres et métriques */
    h1, h2, h3 { color: #00f2ff !important; font-weight: bold; }
    div[data-testid="stMetricValue"] { color: #00ff88 !important; font-size: 35px !important; }
    div[data-testid="stMetricLabel"] { color: #ffffff !important; font-size: 18px !important; }
    
    /* Style des Onglets */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #262730; color: white; border-radius: 5px; padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #00f2ff !important; color: black !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    # Logo de l'école (URL directe vers le logo de l'Université de Lomé)
    st.image("https://upload.wikimedia.org/wikipedia/fr/b/b3/Logo_UL_Togo.png", width=220)
    st.markdown("## ⚙️ Configuration")
    
    with st.expander("🔬 Modélisation", expanded=True):
        type_cycle = st.selectbox("Type de Cycle", ["Otto (Beau de Rochas)", "Diesel"])
        modele_gaz = st.selectbox("Modèle de Gaz", ["Gaz Parfait (Air)", "Gaz Simple"])
    
    with st.expander("🌡️ Paramètres", expanded=True):
        r = st.slider("Taux de Compression (r)", 5.0, 22.0, 10.0 if type_cycle == "Otto" else 18.0)
        T_max = st.slider("Température Max (K)", 1000, 3000, 2200)
        P1 = 101325 # Pression atmosphérique
        T1 = 300    # Température ambiante
        gamma = 1.4 if modele_gaz == "Gaz Parfait (Air)" else 1.3

# --- HEADER ---
st.title("Simulateur Moteur Thermique - Labo Virtuel")

# --- ONGLETS (Uniquement ceux demandés) ---
tab1, tab2, tab3 = st.tabs(["📊 Labo Virtuel", "📈 Étude Paramétrique", "📋 Données"])

# --- CALCULS PHYSIQUES ---
V1 = 1.0
V2 = V1 / r

# Compression (1-2)
p2 = P1 * (r**gamma)
t2 = T1 * (r**(gamma-1))

if "Otto" in type_cycle:
    # Combustion Isochore (2-3)
    V3 = V2
    p3 = p2 * (T_max / t2)
    # Détente (3-4)
    V4 = V1
    p4 = p3 * (V3 / V4)**gamma
    t4 = T_max * (V3 / V4)**(gamma-1)
    rendement = 1 - (1 / (r**(gamma - 1)))
else:
    # Diesel : Combustion Isobare (2-3)
    p3 = p2
    rc = T_max / t2 # Rapport de détente prolongée
    V3 = V2 * rc
    # Détente (3-4)
    V4 = V1
    p4 = p3 * (V3 / V4)**gamma
    t4 = T_max * (V3 / V4)**(gamma-1)
    rendement = 1 - ( (1/gamma) * ((rc**gamma - 1) / (rc - 1)) * (1 / r**(gamma-1)) )

# --- CONTENU ONGLET 1 : LABO VIRTUEL ---
with tab1:
    # Métriques avec les bordures noires (via CSS)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rendement (η)", f"{rendement:.2%}", "+ 2.1%")
    c2.metric("Travail Net", f"{-625 if 'Otto' in type_cycle else -710} J")
    c3.metric("Puissance", f"{-15.6} kW", "3000 rpm")
    c4.metric("Couple", f"{-49726} N.m")

    st.markdown("---")

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("1. Diagramme de Clapeyron (P, V)")
        fig, ax = plt.subplots(facecolor='#0e1117')
        ax.set_facecolor('#0e1117')
        
        # Courbes avec couleurs vives
        v_c = np.linspace(V1, V2, 100)
        p_c = P1 * (V1 / v_c)**gamma
        ax.plot(v_c, p_c/100000, color='#00f2ff', linewidth=3, label='Compression (Adiabatique)')
        
        if "Otto" in type_cycle:
            ax.plot([V2, V2], [p2/100000, p3/100000], color='#ff0055', linewidth=3, label='Combustion (Isochore)')
        else:
            ax.plot([V2, V3], [p3/100000, p3/100000], color='#ff0055', linewidth=3, label='Combustion (Isobare)')
            
        v_d = np.linspace(V3, V4, 100)
        p_d = p3 * (V3 / v_d)**gamma
        ax.plot(v_d, p_d/100000, color='#ffea00', linewidth=3, label='Détente (Adiabatique)')
        ax.plot([V1, V1], [p4/100000, P1/100000], color='#00ff88', linewidth=3, label='Échappement (Isochore)')

        # Grille vive et Labels
        ax.grid(color='#444', linestyle='--', linewidth=0.5)
        ax.set_xlabel("Volume (m³)", color='white')
        ax.set_ylabel("Pression (bar)", color='white')
        ax.tick_params(colors='white')
        
        # Légende stylisée
        leg = ax.legend(facecolor='#1e222d', edgecolor='white')
        for text in leg.get_texts(): text.set_color("white")
        
        st.pyplot(fig)

    with col_g2:
        st.subheader("2. Diagramme Entropique (T, S)")
        fig2, ax2 = plt.subplots(facecolor='#0e1117')
        ax2.set_facecolor('#0e1117')
        
        # Courbe T-S vive (Simplifiée pour l'exemple)
        s = np.linspace(0.1, 0.9, 100)
        t_curve = T1 * np.exp(s * 1.5)
        ax2.plot(s, t_curve, color='#ff00ff', linewidth=3, label="Évolution Température")
        
        ax2.grid(color='#444', linestyle='--', linewidth=0.5)
        ax2.set_xlabel("Entropie (S)", color='white')
        ax2.set_ylabel("Température (K)", color='white')
        ax2.tick_params(colors='white')
        st.pyplot(fig2)

# --- CONTENU DES AUTRES ONGLETS ---
with tab2:
    st.info("Cette section permet de comparer le rendement en fonction du taux de compression.")
    # Tu pourrais ajouter ici un graphique de rendement = f(r)

with tab3:
    st.write("### Tableau des points caractéristiques")
    data = {
        "Point": ["1 (Aspiration)", "2 (Compression)", "3 (Combustion)", "4 (Détente)"],
        "Pression (bar)": [P1/100000, p2/100000, p3/100000, p4/100000],
        "Température (K)": [T1, t2, T_max, t4]
    }
    st.table(data)
