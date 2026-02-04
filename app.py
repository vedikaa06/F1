import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

# --- THEME & CSS ---
st.set_page_config(page_title="F1 Velocity Hub", layout="wide")

# Mapping team names to their brand hex colors for the dynamic background effect
TEAM_COLORS = {
    'Ferrari': '#FF2800', 'Mercedes': '#00D2BE', 'Red Bull': '#0600EF',
    'McLaren': '#FF8700', 'Aston Martin': '#006F62', 'Alpine': '#0090FF',
    'Williams': '#005AFF', 'Haas': '#FFFFFF', 'RB': '#6692FF', 'Kick Sauber': '#52E252'
}

def inject_custom_design():
    st.markdown(f"""
    <style>
    /* Main Background & Watermark */
    .stApp {{
        background-color: #000000;
        color: white;
    }}
    .stApp::before {{
        content: "F1";
        position: fixed;
        top: 30%; left: 50%;
        transform: translate(-50%, -50%);
        font-size: 600px;
        font-weight: 900;
        color: rgba(255, 255, 255, 0.03);
        z-index: -1;
    }}
    
    /* Smooth Scroll */
    html {{ scroll-behavior: smooth; }}
    
    /* Premium Cards */
    .f1-card {{
        background: rgba(255, 255, 255, 0.05);
        border-left: 5px solid #E10600;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }}
    .f1-card:hover {{
        transform: scale(1.02);
        background: rgba(255, 255, 255, 0.1);
    }}
    
    /* Hide Streamlit Header/Footer */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

inject_custom_design()

# --- LOAD DATA ---
@st.cache_data
def load_all_f1_data():
    df = pd.read_csv('f1_master_dataset.csv')
    return df

df = load_all_f1_data()

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    selected = option_menu(
        "F1 Velocity", ["Home", "Hall of Fame", "Search Hub", "ML Predictor"],
        icons=['house', 'trophy', 'search', 'robot'],
        menu_icon="speedometer2", default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#111"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#E10600"},
            "nav-link-selected": {"background-color": "#E10600"},
        }
    )

# --- SECTION 1: HOME ---
if selected == "Home":
    st.markdown("<h1 style='text-align: center; color: #E10600; font-size: 80px;'>VELOCITY HUB</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 20px;'>Decoding 70+ Years of Racing DNA</p>", unsafe_allow_html=True)
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Grand Prix Analyzed", "1,100+")
    col2.metric("Legendary Drivers", "850+")
    col3.metric("Data Points", "2M+")

# --- SECTION 2: HALL OF FAME ---
elif selected == "Hall of Fame":
    st.header("🏆 The Pantheon of Speed")
    decade = st.select_slider("Select Era", options=sorted(df['decade'].unique()))
    
    top_drivers = df[df['decade'] == decade].groupby('driver_full_name')['is_win'].sum().sort_values(ascending=False).head(5)
    
    st.subheader(f"King of the {int(decade)}s")
    st.bar_chart(top_drivers, color="#E10600")

# --- SECTION 3: SEARCH HUB (Dynamic Colors) ---
elif selected == "Search Hub":
    st.header("🔍 Driver & Team Intelligence")
    
    search_driver = st.selectbox("Select Driver", df['driver_full_name'].unique())
    driver_stats = df[df['driver_full_name'] == search_driver].iloc[0]
    team_name = driver_stats['team_name']
    
    # Dynamic Team Background Logic
    team_color = TEAM_COLORS.get(team_name, '#E10600')
    
    st.markdown(f"""
        <div style="background: linear-gradient(90deg, {team_color}44 0%, #111 100%); padding: 30px; border-radius: 15px; border-left: 10px solid {team_color};">
            <h2 style="margin: 0;">{search_driver}</h2>
            <p style="font-size: 18px; color: #ccc;">Driving for: {team_name}</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    c1, c2, c3 = st.columns(3)
    c1.metric("Career Points", int(df[df['driver_full_name'] == search_driver]['points'].sum()))
    c2.metric("Total Wins", int(df[df['driver_full_name'] == search_driver]['is_win'].sum()))
    c3.metric("Podiums", int(df[df['driver_full_name'] == search_driver]['is_podium'].sum()))

# --- SECTION 4: ML PREDICTOR ---
elif selected == "ML Predictor":
    st.header("🤖 Artificial Intelligence Predictor")
    st.write("Simulate any Driver + Team + Circuit combination.")
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        d = st.selectbox("Driver", df['driver_full_name'].unique())
    with col_b:
        t = st.selectbox("Team", df['team_name'].unique())
    with col_c:
        c = st.selectbox("Circuit", df['circuit_name'].unique())
        
    if st.button("RUN INFERENCE"):
        with st.spinner('Calculating Strength Index...'):
            # Placeholder for your pkl model logic
            score = 88.4 
            st.markdown(f"""
                <div style="text-align: center; padding: 50px;">
                    <h1 style="font-size: 70px; color: #E10600;">{score} / 100</h1>
                    <h3>Tier: ELITE PERFORMANCE</h3>
                </div>
            """, unsafe_allow_html=True)
            st.progress(score/100)
