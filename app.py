import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Simulateur Thermique EPL", layout="wide")

# Configuration du style
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #1E40AF;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .cycle-info {
        background-color: #F0F9FF;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #3B82F6;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background-color: #3B82F6;
        color: white;
        font-weight: bold;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# Titre principal
st.markdown('<h1 class="main-header">SIMULATEUR MOTEUR THERMIQUE - EPL</h1>', unsafe_allow_html=True)

# Sidebar pour les paramètres
with st.sidebar:
    st.markdown("## Simulateur Thermique EPL - Streamlit")
    
    # Sélection du cycle
    cycle_type = st.radio(
        "**Sélectionnez le cycle**",
        ["Otto (Beau de Rochas)", "Diesel"],
        index=0
    )
    
    st.markdown("### Modèle de Gaz")
    st.markdown("- Gaz Simple")
    
    st.markdown("### Paramètres d'Entrée")
    
    # Paramètres communs
    V1 = st.number_input("Volume initial $V_1$ (m³)", 
                         value=0.03000, 
                         format="%.5f",
                         step=0.001)
    
    P1 = st.number_input("Pression initiale $P_1$ (Pa)", 
                         value=101328.0,
                         step=1000.0)
    
    T1 = st.number_input("Température initiale $T_1$ (K)", 
                         value=302.0,
                         step=10.0)
    
    # Variables selon le cycle
    st.markdown("### Variables de Modélisation")
    
    if cycle_type == "Otto (Beau de Rochas)":
        r = st.slider("Taux de Compression ($r$)", 
                      min_value=6.0, 
                      max_value=12.0, 
                      value=9.5,
                      step=0.1)
        
        T_max = st.slider("Température Max (K)", 
                          min_value=1800.0, 
                          max_value=2500.0, 
                          value=2100.0,
                          step=50.0)
        
        # Paramètres spécifiques Otto
        gamma = 1.4  # Rapport des capacités calorifiques
        R = 287.0    # Constante des gaz parfaits (J/kg·K)
        
    else:  # Cycle Diesel
        r = st.slider("Taux de Compression ($r$)", 
                      min_value=12.0, 
                      max_value=20.0, 
                      value=16.0,
                      step=0.5)
        
        r_c = st.slider("Taux de coupure ($r_c$)", 
                        min_value=1.5, 
                        max_value=3.0, 
                        value=2.0,
                        step=0.1)
        
        T_max = st.slider("Température Max (K)", 
                          min_value=1800.0, 
                          max_value=2500.0, 
                          value=2000.0,
                          step=50.0)
        
        # Paramètres spécifiques Diesel
        gamma = 1.4
        R = 287.0
    
    # Bouton de simulation
    simuler = st.button("🚀 Lancer la Simulation")

# Fonction pour calculer le cycle Otto
def calculate_otto_cycle(V1, P1, T1, r, T_max, gamma=1.4, R=287.0):
    # Points du cycle
    # Point 1: début compression
    V1 = V1
    P1 = P1
    T1 = T1
    
    # Point 2: fin compression adiabatique
    V2 = V1 / r
    P2 = P1 * (r ** gamma)
    T2 = T1 * (r ** (gamma - 1))
    
    # Point 3: fin combustion isochore
    V3 = V2
    T3 = T_max
    P3 = P2 * (T3 / T2)
    
    # Point 4: fin détente adiabatique
    V4 = V1
    P4 = P3 / (r ** gamma)
    T4 = T3 / (r ** (gamma - 1))
    
    # Calcul des travaux et chaleurs
    # Travail de compression (1-2)
    W_12 = (P2 * V2 - P1 * V1) / (1 - gamma)
    
    # Chaleur ajoutée (2-3)
    Q_23 = (gamma * R / (gamma - 1)) * (T3 - T2) * (P1 * V1) / (R * T1)
    
    # Travail de détente (3-4)
    W_34 = (P4 * V4 - P3 * V3) / (1 - gamma)
    
    # Chaleur rejetée (4-1)
    Q_41 = (gamma * R / (gamma - 1)) * (T1 - T4) * (P1 * V1) / (R * T1)
    
    # Travail net et rendement
    W_net = W_12 + W_34
    Q_in = Q_23
    eta = abs(W_net / Q_in) if Q_in != 0 else 0
    
    # Calcul de l'entropie (simplifié)
    # Pour un gaz parfait: ΔS = cv * ln(T2/T1) + R * ln(V2/V1)
    cv = R / (gamma - 1)
    
    S1 = 0  # Référence
    S2 = S1 + cv * np.log(T2/T1) + R * np.log(V2/V1)
    S3 = S2 + cv * np.log(T3/T2)  # Isochore
    S4 = S3 + cv * np.log(T4/T3) + R * np.log(V4/V3)
    
    return {
        'points': {
            'V': [V1, V2, V3, V4, V1],
            'P': [P1, P2, P3, P4, P1],
            'T': [T1, T2, T3, T4, T1],
            'S': [S1, S2, S3, S4, S1]
        },
        'travail_net': W_net,
        'rendement': eta,
        'puissance': abs(W_net) * 50,  # Approximation
        'couple': abs(W_net) * 0.159   # Approximation
    }

# Fonction pour calculer le cycle Diesel
def calculate_diesel_cycle(V1, P1, T1, r, r_c, T_max, gamma=1.4, R=287.0):
    # Points du cycle
    # Point 1: début compression
    V1 = V1
    P1 = P1
    T1 = T1
    
    # Point 2: fin compression adiabatique
    V2 = V1 / r
    P2 = P1 * (r ** gamma)
    T2 = T1 * (r ** (gamma - 1))
    
    # Point 3: fin combustion isobare
    V3 = V2 * r_c
    T3 = T_max
    P3 = P2  # Isobare
    
    # Point 4: fin détente adiabatique
    V4 = V1
    P4 = P3 * ((V3 / V4) ** gamma)
    T4 = T3 * ((V3 / V4) ** (gamma - 1))
    
    # Calcul entropie
    cv = R / (gamma - 1)
    cp = gamma * cv
    
    S1 = 0
    S2 = S1 + cv * np.log(T2/T1) + R * np.log(V2/V1)
    S3 = S2 + cp * np.log(T3/T2)  # Isobare
    S4 = S3 + cv * np.log(T4/T3) + R * np.log(V4/V3)
    
    # Travail net approximatif
    W_net = (P3 * V3 - P2 * V2) + (P4 * V4 - P3 * V3) / (1 - gamma)
    Q_in = cp * (T3 - T2) * (P1 * V1) / (R * T1)
    eta = 1 - (1 / (r ** (gamma - 1))) * ((r_c ** gamma - 1) / (gamma * (r_c - 1)))
    
    return {
        'points': {
            'V': [V1, V2, V3, V4, V1],
            'P': [P1, P2, P3, P4, P1],
            'T': [T1, T2, T3, T4, T1],
            'S': [S1, S2, S3, S4, S1]
        },
        'travail_net': W_net,
        'rendement': eta,
        'puissance': abs(W_net) * 50,
        'couple': abs(W_net) * 0.159
    }

# Interface principale
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("## Labo Virtuel")
    st.markdown("### Étude Paramétrique")
    st.markdown("### Données du Cycle")
    
    # Afficher les résultats
    if simuler:
        if cycle_type == "Otto (Beau de Rochas)":
            results = calculate_otto_cycle(V1, P1, T1, r, T_max)
        else:
            results = calculate_diesel_cycle(V1, P1, T1, r, r_c, T_max)
        
        # Création du tableau des résultats
        data = {
            "Paramètre": ["Rendement (η)", "Travail Net", "Puissance", "Couple"],
            "Valeur": [
                f"{results['rendement']*100:.2f} %",
                f"{results['travail_net']:.2f} J",
                f"{results['puissance']/1000:.1f} kW",
                f"{results['couple']:.1f} N.m"
            ]
        }
        
        df = pd.DataFrame(data)
        st.table(df)
        
        # Points du cycle pour affichage
        st.markdown("### Points du Cycle")
        points_df = pd.DataFrame({
            "Point": ["1", "2", "3", "4"],
            "V (m³)": [f"{v:.6f}" for v in results['points']['V'][:4]],
            "P (Pa)": [f"{p:.0f}" for p in results['points']['P'][:4]],
            "T (K)": [f"{t:.1f}" for t in results['points']['T'][:4]]
        })
        st.table(points_df)
    else:
        st.info("⚠️ Cliquez sur 'Lancer la Simulation' pour voir les résultats")

with col2:
    if simuler:
        # Calcul des résultats
        if cycle_type == "Otto (Beau de Rochas)":
            results = calculate_otto_cycle(V1, P1, T1, r, T_max)
            cycle_name = "Cycle Otto"
        else:
            results = calculate_diesel_cycle(V1, P1, T1, r, r_c, T_max)
            cycle_name = "Cycle Diesel"
        
        points = results['points']
        
        # Création des graphiques
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # 1. Diagramme de Clapeyron (P, V)
        ax1 = axes[0]
        ax1.plot(points['V'], points['P'], 'b-', linewidth=2)
        
        # Coloration des zones et points
        colors = ['red', 'green', 'blue', 'orange']
        labels = ['1-2 Compression', '2-3 Combustion', '3-4 Détente', '4-1 Échappement']
        
        for i in range(4):
            ax1.plot(points['V'][i:i+2], points['P'][i:i+2], 
                    color=colors[i], linewidth=3, label=labels[i])
            ax1.plot(points['V'][i], points['P'][i], 
                    'ko', markersize=8)
            ax1.text(points['V'][i]*1.02, points['P'][i]*1.02, 
                    f'{i+1}', fontsize=12, fontweight='bold')
        
        ax1.set_xlabel('Volume (m³)', fontsize=12)
        ax1.set_ylabel('Pression (Pa)', fontsize=12)
        ax1.set_title(f'Diagramme de Clapeyron (P, V) - {cycle_name}', 
                     fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='best')
        ax1.set_xscale('log')
        ax1.set_yscale('log')
        
        # 2. Diagramme Entropique (T, S)
        ax2 = axes[1]
        ax2.plot(points['S'], points['T'], 'b-', linewidth=2)
        
        for i in range(4):
            ax2.plot(points['S'][i:i+2], points['T'][i:i+2], 
                    color=colors[i], linewidth=3, label=labels[i])
            ax2.plot(points['S'][i], points['T'][i], 
                    'ko', markersize=8)
            ax2.text(points['S'][i]*1.02, points['T'][i]*1.02, 
                    f'{i+1}', fontsize=12, fontweight='bold')
        
        ax2.set_xlabel('Entropie (J/K)', fontsize=12)
        ax2.set_ylabel('Température (K)', fontsize=12)
        ax2.set_title(f'Diagramme Entropique (T, S) - {cycle_name}', 
                     fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='best')
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Téléchargement des données
        st.markdown("---")
        st.markdown("### Export des Données")
        
        # Création d'un DataFrame pour l'export
        export_data = pd.DataFrame({
            'Point': ['1', '2', '3', '4', '1'],
            'Volume (m³)': points['V'],
            'Pression (Pa)': points['P'],
            'Température (K)': points['T'],
            'Entropie (J/K)': points['S']
        })
        
        csv = export_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger les données du cycle",
            data=csv,
            file_name=f"cycle_{cycle_type.replace(' ', '_').lower()}_data.csv",
            mime="text/csv"
        )
    else:
        # Message d'attente
        st.info("🎯 Configurez les paramètres dans la barre latérale et cliquez sur 'Lancer la Simulation'")
        
        # Image d'exemple ou explication
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background-color: #F0F9FF; border-radius: 10px;">
            <h3 style="color: #1E40AF;">Prêt à Simuler!</h3>
            <p>Ce simulateur vous permet d'analyser les cycles thermiques Otto et Diesel.</p>
            <p>Configurez les paramètres et visualisez les diagrammes P-V et T-S.</p>
        </div>
        """, unsafe_allow_html=True)

# Section d'explication
st.markdown("---")
st.markdown('<h2 class="sub-header">Explication des Cycles</h2>', unsafe_allow_html=True)

col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    with st.expander("**Cycle Otto (Beau de Rochas)**", expanded=True):
        st.markdown("""
        **Phases du cycle:**
        1. **1→2**: Compression adiabatique
        2. **2→3**: Combustion isochore (à volume constant)
        3. **3→4**: Détente adiabatique
        4. **4→1**: Échappement isochore
        
        **Caractéristiques:**
        - Moteur à allumage commandé
        - Taux de compression typique: 8-12
        - Rendement théorique: η = 1 - (1/r^(γ-1))
        """)

with col_exp2:
    with st.expander("**Cycle Diesel**", expanded=True):
        st.markdown("""
        **Phases du cycle:**
        1. **1→2**: Compression adiabatique
        2. **2→3**: Combustion isobare (à pression constante)
        3. **3→4**: Détente adiabatique
        4. **4→1**: Échappement isochore
        
        **Caractéristiques:**
        - Moteur à allumage par compression
        - Taux de compression élevé: 12-20
        - Taux de coupure (r_c) important
        - Rendement théorique: η = 1 - (1/r^(γ-1)) × ((r_c^γ - 1)/(γ(r_c - 1)))
        """)

# Pied de page
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Simulateur Thermique EPL - Labo Virtuel d'Étude des Moteurs - © 2024"
    "</div>",
    unsafe_allow_html=True
)
