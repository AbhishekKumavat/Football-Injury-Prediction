import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import requests
from io import BytesIO

# Add this near the top of the file, after the initial imports and before the page config
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# Page configuration
st.set_page_config(
    page_title="Football Injury Predictor Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add this right after st.set_page_config
# Theme toggle button
theme_toggle = st.button("🌓 Toggle Theme" if st.session_state.theme == 'light' else "☀️ Toggle Theme")
if theme_toggle:
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

# Enhanced CSS with brighter theme
st.markdown(f"""
    <style>
    /* Main theme */
    .main {{
        background: {('#1a1a1a' if st.session_state.theme == 'dark' else '#f8f9fa')};
        color: {('#ffffff' if st.session_state.theme == 'dark' else '#333333')};
    }}
    
    /* Header */
    .header-container {{
        background: {('#2d2d2d' if st.session_state.theme == 'dark' else '#ffffff')};
        padding: 40px;
        border-radius: 15px;
        margin-bottom: 30px;
        border: 1px solid {('#404040' if st.session_state.theme == 'dark' else '#e0e0e0')};
        box-shadow: 0 4px 12px {('rgba(0,0,0,0.3)' if st.session_state.theme == 'dark' else 'rgba(0,0,0,0.1)')};
    }}
    
    /* Cards with clean feel */
    .stat-card {{
        background: {('#2d2d2d' if st.session_state.theme == 'dark' else '#ffffff')};
        padding: 25px;
        border-radius: 15px;
        border: 1px solid {('#404040' if st.session_state.theme == 'dark' else '#e0e0e0')};
        margin: 15px 0;
        box-shadow: 0 2px 8px {('rgba(0,0,0,0.3)' if st.session_state.theme == 'dark' else 'rgba(0,0,0,0.05)')};
    }}
    
    /* Analysis card */
    .pitch-card {{
        background: {('#2d2d2d' if st.session_state.theme == 'dark' else '#ffffff')};
        padding: 30px;
        border-radius: 15px;
        border: 1px solid {('#404040' if st.session_state.theme == 'dark' else '#e0e0e0')};
        margin: 15px 0;
        box-shadow: 0 2px 8px {('rgba(0,0,0,0.3)' if st.session_state.theme == 'dark' else 'rgba(0,0,0,0.05)')};
    }}
    
    /* Risk indicators */
    .injury-high {{
        color: #dc3545;
        padding: 15px;
        border-radius: 10px;
        font-weight: bold;
        background: rgba(220,53,69,0.1);
        border: 1px solid #dc3545;
    }}
    
    .injury-medium {{
        color: #ffc107;
        padding: 15px;
        border-radius: 10px;
        font-weight: bold;
        background: rgba(255,193,7,0.1);
        border: 1px solid #ffc107;
    }}
    
    .injury-low {{
        color: #28a745;
        padding: 15px;
        border-radius: 10px;
        font-weight: bold;
        background: rgba(40,167,69,0.1);
        border: 1px solid #28a745;
    }}
    
    /* Slider styling */
    .stSlider > div > div {{
        background-color: #2e7d32 !important;
    }}
    
    .stSlider > div > div > div > div {{
        background-color: #ffffff !important;
    }}
    
    /* Progress bar */
    .stProgress > div > div > div > div {{
        background-color: #2e7d32 !important;
    }}
    
    /* Custom button */
    .custom-button {{
        background-color: #2e7d32;
        color: white;
        padding: 12px 30px;
        border-radius: 25px;
        border: none;
        cursor: pointer;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease;
    }}
    
    .custom-button:hover {{
        background-color: #1b5e20;
        box-shadow: 0 0 15px rgba(46,125,50,0.5);
    }}
    
    /* Animated elements */
    @keyframes pulse {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.05); }}
        100% {{ transform: scale(1); }}
    }}
    
    .pulse {{
        animation: pulse 2s infinite;
    }}
    
    /* Footer styling */
    .footer {{
        background: {('#2d2d2d' if st.session_state.theme == 'dark' else '#ffffff')};
        padding: 20px;
        border-radius: 15px;
        border: 1px solid {('#404040' if st.session_state.theme == 'dark' else '#e0e0e0')};
        margin-top: 30px;
        box-shadow: 0 -2px 8px {('rgba(0,0,0,0.3)' if st.session_state.theme == 'dark' else 'rgba(0,0,0,0.05)')};
    }}
    
    /* Additional decorative elements */
    .field-lines {{
        border-left: 2px dashed #2e7d32;
        height: 100%;
        position: absolute;
        left: 50%;
        opacity: 0.3;
    }}
    
    /* Headers and text */
    h1, h2, h3, h4, h5 {{
        color: {('#4CAF50' if st.session_state.theme == 'dark' else '#2e7d32')};
    }}
    
    p {{
        color: {('#ffffff' if st.session_state.theme == 'dark' else '#333333')};
    }}
    
    /* Responsive design adjustments */
    @media (max-width: 768px) {{
        .header-container {{
            padding: 20px;
        }}
        .stat-card {{
            padding: 15px;
        }}
    }}

    /* Streamlit specific elements */
    .stSelectbox label {{
        color: {('#ffffff' if st.session_state.theme == 'dark' else '#333333')} !important;
    }}

    .stSlider label {{
        color: {('#ffffff' if st.session_state.theme == 'dark' else '#333333')} !important;
    }}

    .stNumberInput label {{
        color: {('#ffffff' if st.session_state.theme == 'dark' else '#333333')} !important;
    }}

    /* Stadium background */
    .main {{
        background: linear-gradient(
            {('rgba(26, 26, 26, 0.85)' if st.session_state.theme == 'dark' else 'rgba(248, 249, 250, 0.75)')},
            {('rgba(26, 26, 26, 0.85)' if st.session_state.theme == 'dark' else 'rgba(248, 249, 250, 0.75)')}
        ),
        url('https://images.unsplash.com/photo-1577223625816-7546f13df25d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=3540&q=80');
        background-position: center;
        background-repeat: no-repeat;
        background-size: cover;
        background-attachment: fixed;
    }}

    /* Adjust container backgrounds for better visibility */
    .header-container {{
        background: {('rgba(45, 45, 45, 0.85)' if st.session_state.theme == 'dark' else 'rgba(255, 255, 255, 0.85)')};
        backdrop-filter: blur(8px);
    }}

    .stat-card {{
        background: {('rgba(45, 45, 45, 0.85)' if st.session_state.theme == 'dark' else 'rgba(255, 255, 255, 0.85)')};
        backdrop-filter: blur(8px);
    }}

    .pitch-card {{
        background: {('rgba(45, 45, 45, 0.85)' if st.session_state.theme == 'dark' else 'rgba(255, 255, 255, 0.85)')};
        backdrop-filter: blur(8px);
    }}

    .footer {{
        background: {('rgba(45, 45, 45, 0.85)' if st.session_state.theme == 'dark' else 'rgba(255, 255, 255, 0.85)')};
        backdrop-filter: blur(8px);
    }}

    /* Enhanced text contrast */
    p, .stSelectbox label, .stSlider label, .stNumberInput label {{
        color: {('#ffffff' if st.session_state.theme == 'dark' else '#1a1a1a')} !important;
        font-weight: 500;
    }}

    /* Stronger text shadow for better readability */
    h1, h2, h3, h4, h5 {{
        text-shadow: 2px 2px 4px {('rgba(0,0,0,0.4)' if st.session_state.theme == 'dark' else 'rgba(0,0,0,0.2)')};
    }}

    /* Enhanced container shadows */
    .header-container, .stat-card, .pitch-card, .footer {{
        box-shadow: 0 4px 15px {('rgba(0,0,0,0.5)' if st.session_state.theme == 'dark' else 'rgba(0,0,0,0.2)')};
    }}

    /* Player profile text styling */
    .stSelectbox > div > div > div > div {{
        color: {('#ffffff' if st.session_state.theme == 'dark' else '#2e7d32')} !important;
    }}

    /* Input fields text */
    .stTextInput > div > div > input {{
        color: {('#ffffff' if st.session_state.theme == 'dark' else '#2e7d32')} !important;
    }}

    /* Dropdown menu items */
    .stSelectbox > div > div > div {{
        color: {('#ffffff' if st.session_state.theme == 'dark' else '#2e7d32')} !important;
        background-color: {('#2d2d2d' if st.session_state.theme == 'dark' else '#ffffff')} !important;
    }}

    /* Form labels and text */
    .stMarkdown p, .stText p {{
        color: {('#ffffff' if st.session_state.theme == 'dark' else '#2e7d32')} !important;
        font-weight: 500;
    }}

    /* Number input styling */
    .stNumberInput > div > div > input {{
        color: {('#ffffff' if st.session_state.theme == 'dark' else '#2e7d32')} !important;
        background-color: {('rgba(45, 45, 45, 0.9)' if st.session_state.theme == 'dark' else 'rgba(255, 255, 255, 0.9)')} !important;
    }}

    /* Form field labels */
    .stSelectbox label, .stNumberInput label {{
        color: {('#ffffff' if st.session_state.theme == 'dark' else '#2e7d32')} !important;
        font-weight: 500 !important;
    }}

    /* Container backgrounds */
    .element-container, .stTextInput > div, .stSelectbox > div {{
        background-color: transparent !important;
    }}

    /* Add New Player button styling */
    .stButton > button {{
        color: {('#ffffff' if st.session_state.theme == 'dark' else '#2e7d32')} !important;
        background-color: {('rgba(45, 45, 45, 0.9)' if st.session_state.theme == 'dark' else 'rgba(255, 255, 255, 0.9)')} !important;
        border: 1px solid {('#404040' if st.session_state.theme == 'dark' else '#2e7d32')} !important;
    }}

    .stButton > button:hover {{
        color: #ffffff !important;
        background-color: #2e7d32 !important;
        border-color: #2e7d32 !important;
    }}

    /* Form submit button styling */
    .stFormSubmitButton > button {{
        color: #ffffff !important;
        background-color: #2e7d32 !important;
        border-color: #2e7d32 !important;
    }}

    .stFormSubmitButton > button:hover {{
        color: #ffffff !important;
        background-color: #1b5e20 !important;
        border-color: #1b5e20 !important;
    }}

    /* Button text */
    button p {{
        color: inherit !important;
    }}

    /* Tab Navigation */
    .tab-container {{
        display: flex;
        justify-content: center;
        gap: 20px;
        margin: 20px 0;
    }}
    
    .tab {{
        padding: 10px 20px;
        border-radius: 20px;
        cursor: pointer;
        transition: all 0.3s ease;
    }}
    
    .tab-active {{
        background: #2e7d32;
        color: white;
    }}
    
    .tab:hover {{
        transform: translateY(-2px);
    }}
    
    /* Player Card Styling */
    .player-card {{
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }}
    
    .player-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }}
    
    /* Loading Animation */
    @keyframes pulse-green {{
        0% {{ box-shadow: 0 0 0 0 rgba(46, 125, 50, 0.7); }}
        70% {{ box-shadow: 0 0 0 10px rgba(46, 125, 50, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(46, 125, 50, 0); }}
    }}
    
    .loading {{
        animation: pulse-green 1.5s infinite;
    }}
    </style>
    """, unsafe_allow_html=True)

# Load model and data
model = pickle.load(open('model.pkl', 'rb'))
scaler = pickle.load(open('scaler.pkl', 'rb'))
feature_names = pickle.load(open('X_train_columns.pkl', 'rb'))

# Header with enhanced styling
st.markdown(f"""
    <div class="header-container">
        <div style="text-align: center;">
            <span class="soccer-ball glow" style="font-size: 60px;">⚽</span>
            <h1 class="glow" style="color: {('#ffffff' if st.session_state.theme == 'dark' else '#2e7d32')}; font-size: 3em;">Football Injury Predictor Pro</h1>
            <p style="color: {('#4CAF50' if st.session_state.theme == 'dark' else '#2e7d32')}; font-size: 1.2em;">Advanced AI-Powered Injury Risk Assessment</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Move these helper functions to the top of the file, right after the imports
def get_position(player_data):
    """Get player position from position flags"""
    positions = ['GK', 'DF', 'MF', 'FW']
    for pos in positions:
        if player_data.get(f'position_{pos}', 0) == 1:
            return pos
    return 'Unknown'

def generate_historical_data(player):
    """Generate historical performance data for a player"""
    player_data = st.session_state.player_profiles[player]
    
    # Create sample historical data
    dates = pd.date_range(end=pd.Timestamp.now(), periods=10, freq='W')
    data = {
        'Date': dates,
        'Minutes Played': np.linspace(0, player_data['minutes'], 10),
        'Fitness Score': np.random.normal(80, 10, 10).clip(0, 100),
        'Risk Score': np.random.normal(50, 15, 10).clip(0, 100)
    }
    return pd.DataFrame(data)

def compare_players(player1, player2):
    """Compare two players side by side"""
    data1 = st.session_state.player_profiles[player1]
    data2 = st.session_state.player_profiles[player2]
    
    # Create comparison metrics
    metrics = {
        'Games': ['games', 'Games Played'],
        'Minutes': ['minutes', 'Minutes Played'],
        'Shots': ['shots', 'Shots Taken'],
        'Injuries': ['n_injuries', 'Previous Injuries'],
        'Severe Injuries': ['n_severe_injuries', 'Severe Injuries'],
        'Age': ['age', 'Age']
    }
    
    # Display comparison radar chart
    categories = list(metrics.keys())
    values1 = [data1[m[0]] for m in metrics.values()]
    values2 = [data2[m[0]] for m in metrics.values()]
    
    # Normalize values for comparison
    max_values = {
        'Games': 15,
        'Minutes': 1350,
        'Shots': 30,
        'Injuries': 5,
        'Severe Injuries': 3,
        'Age': 35
    }
    
    values1_norm = [min(v/max_values[c]*100, 100) for v, c in zip(values1, categories)]
    values2_norm = [min(v/max_values[c]*100, 100) for v, c in zip(values2, categories)]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values1_norm,
        theta=categories,
        fill='toself',
        name=player1
    ))
    fig.add_trace(go.Scatterpolar(
        r=values2_norm,
        theta=categories,
        fill='toself',
        name=player2
    ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        title='Player Comparison'
    )
    
    # Display metrics side by side
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### {player1}")
        for metric, (key, label) in metrics.items():
            st.metric(label, data1[key])
            
    with col2:
        st.markdown(f"### {player2}")
        for metric, (key, label) in metrics.items():
            st.metric(label, data2[key])
    
    st.plotly_chart(fig, use_container_width=True)

def show_injury_history(player):
    """Display injury history for a player"""
    data = st.session_state.player_profiles[player]
    
    # Create injury timeline
    st.markdown(f"### {player}'s Injury History")
    
    # Summary statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Injuries", data['n_injuries'])
    with col2:
        st.metric("Severe Injuries", data['n_severe_injuries'])
    with col3:
        injury_rate = (data['n_injuries'] / max(data['games'], 1)) * 100
        st.metric("Injury Rate", f"{injury_rate:.1f}%")
    
    # Create sample injury timeline
    if data['n_injuries'] > 0:
        injuries = []
        # Add severe injuries first
        for i in range(data['n_severe_injuries']):
            injuries.append({
                'Type': "Severe",
                'Recovery Time': '4-6 weeks'
            })
        
        # Add minor injuries
        minor_injuries = data['n_injuries'] - data['n_severe_injuries']
        if minor_injuries > 0:
            injuries.append({
                'Type': "Minor",
                'Recovery Time': '1-2 weeks'
            })
        
        # Show injury details in cards
        st.markdown("#### Injury Details")
        
        for injury in injuries:
            color = '#dc3545' if injury['Type'] == 'Severe' else '#ffc107'
            bg_color = 'rgba(220,53,69,0.1)' if injury['Type'] == 'Severe' else 'rgba(255,193,7,0.1)'
            
            st.markdown(f"""
                <div style='
                    padding: 20px;
                    border-radius: 10px;
                    margin: 10px 0;
                    background: {bg_color};
                    border: 2px solid {color};
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                '>
                    <div>
                        <h4 style='margin: 0; color: {color};'>{injury['Type']} Injury</h4>
                        <p style='margin: 5px 0;'>Recovery Period: {injury['Recovery Time']}</p>
                    </div>
                    <div style='
                        width: 40px;
                        height: 40px;
                        border-radius: 50%;
                        background: {color};
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        font-size: 20px;
                    '>
                        {'🏥' if injury['Type'] == 'Severe' else '⚕️'}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.success("No injury history recorded")

# Initialize player_profiles in session state if not already present
if 'player_profiles' not in st.session_state:
    st.session_state.player_profiles = {
        "Lionel Messi": {
            "age": 23,
            "games": 14,
            "minutes": 1260,
            "minutes_90s": 14,
            "shots": 20,
            "n_injuries": 2,
            "n_severe_injuries": 0,
            "position_FW": 1,
            "position_MF": 0,
            "position_DF": 0,
            "position_GK": 0
        },
        "Cristiano Ronaldo": {
            "age": 28,
            "games": 12,
            "minutes": 873,
            "minutes_90s": 9.7,
            "shots": 15,
            "n_injuries": 4,
            "n_severe_injuries": 1,
            "position_MF": 0,
            "position_FW": 1,
            "position_DF": 0,
            "position_GK": 0
        },
        "Sergio Ramos": {
            "age": 31,
            "games": 8,
            "minutes": 701,
            "minutes_90s": 7.8,
            "shots": 9,
            "n_injuries": 1,
            "n_severe_injuries": 0,
            "position_MF": 0,
            "position_FW": 0,
            "position_DF": 1,
            "position_GK": 0
        },
        "Toni Kroos": {
            "age": 25,
            "games": 15,
            "minutes": 1350,
            "minutes_90s": 15,
            "shots": 25,
            "n_injuries": 3,
            "n_severe_injuries": 1,
            "position_MF": 1,
            "position_FW": 0,
            "position_DF": 0,
            "position_GK": 0
        },
        "Pepe": {
            "age": 29,
            "games": 10,
            "minutes": 900,
            "minutes_90s": 10,
            "shots": 12,
            "n_injuries": 0,
            "n_severe_injuries": 0,
            "position_MF": 0,
            "position_FW": 0,
            "position_DF": 1,
            "position_GK": 0
        }
    }

if 'page' not in st.session_state:
    st.session_state['page'] = 'main'

# Add single button after the header section but before player profiles
if st.button("➕ Add New Player", key="add_player_btn"):
    st.session_state['page'] = 'add_player'
    st.rerun()

# Add this before the player selection section
if st.session_state['page'] == 'add_player':
    st.markdown("<h3 style='text-align: center;'>Add New Player Information</h3>", unsafe_allow_html=True)
    
    if st.button("← Back to Main Page", key="back_btn"):
        st.session_state['page'] = 'main'
        st.rerun()
    
    # Player Information Form
    with st.form("player_info_form"):
        st.markdown("<h4>Basic Information</h4>", unsafe_allow_html=True)
        name = st.text_input("Player Name")
        age = st.number_input("Age", min_value=16, max_value=45, value=25)
        
        st.markdown("<h4>Performance Stats</h4>", unsafe_allow_html=True)
        games = st.number_input("Games Played", min_value=0, max_value=50, value=0)
        minutes = st.number_input("Minutes Played", min_value=0, max_value=4500, value=0)
        minutes_90s = st.number_input("Minutes per 90s", min_value=0.0, max_value=50.0, value=0.0)
        shots = st.number_input("Shots Taken", min_value=0, max_value=100, value=0)
        
        st.markdown("<h4>Injury History</h4>", unsafe_allow_html=True)
        n_injuries = st.number_input("Number of Previous Injuries", min_value=0, max_value=20, value=0)
        n_severe_injuries = st.number_input("Number of Severe Injuries", min_value=0, max_value=10, value=0)
        
        st.markdown("<h4>Position</h4>", unsafe_allow_html=True)
        position = st.selectbox("Primary Position", ["Forward", "Midfielder", "Defender", "Goalkeeper"])
        
        submitted = st.form_submit_button("Add Player")
        
        if submitted and name:
            # Create position flags
            position_flags = {
                "position_FW": 1 if position == "Forward" else 0,
                "position_MF": 1 if position == "Midfielder" else 0,
                "position_DF": 1 if position == "Defender" else 0,
                "position_GK": 1 if position == "Goalkeeper" else 0
            }
            
            # Add new player to profiles in session state
            st.session_state.player_profiles[name] = {
                "age": age,
                "games": games,
                "minutes": minutes,
                "minutes_90s": minutes_90s,
                "shots": shots,
                "n_injuries": n_injuries,
                "n_severe_injuries": n_severe_injuries,
                **position_flags
            }
            
            st.success(f"Successfully added {name} to the database!")
            st.session_state['page'] = 'main'
            st.rerun()
        elif submitted:
            st.error("Please enter a player name")

# After the player selection dropdown and before the columns
selected_player = st.selectbox(
    "Choose a player to analyze:",
    list(st.session_state.player_profiles.keys()),
    key="player_selector"
)

# Get the selected player's data
player_data = st.session_state.player_profiles[selected_player]

# Create two columns for the main content
col1, col2 = st.columns([1, 2])

with col1:
    # Update the slider function to use player data as default values
    def slider_with_textbox(label, min_val, max_val, default_val, key=None):
        st.markdown(f"""
            <div style='margin-bottom: 5px; color: #2e7d32; font-weight: 500;'>
                {label}
            </div>
        """, unsafe_allow_html=True)
        return st.slider("", 
                        min_value=float(min_val), 
                        max_value=float(max_val), 
                        value=float(default_val), 
                        key=f"slider_{key}",
                        step=1.0 if max_val > 100 else 0.1)

    # Primary Risk Factors
    st.markdown("<div class='stat-card'><h5>🚨 Primary Risk Factors</h5>", unsafe_allow_html=True)
    n_severe_injuries = slider_with_textbox("Severe Injuries", 0, 5, player_data['n_severe_injuries'], "severe")
    n_injuries = slider_with_textbox("Total Injuries", 0, 10, player_data['n_injuries'], "total")
    age = slider_with_textbox("Age", 18, 40, player_data['age'], "age")
    minutes_90s = slider_with_textbox("Minutes per 90s", 0, 45, player_data['minutes_90s'], "minutes")
    st.markdown("</div>", unsafe_allow_html=True)

    # Performance Metrics
    st.markdown("<div class='stat-card'><h5>⚽ Performance Metrics</h5>", unsafe_allow_html=True)
    games = slider_with_textbox("Games Played", 0, 40, player_data['games'], "games")
    minutes = slider_with_textbox("Minutes Played", 0, 4000, player_data['minutes'], "min")
    shots = slider_with_textbox("Shots Taken", 0, 50, player_data['shots'], "shots")
    st.markdown("</div>", unsafe_allow_html=True)

    # Position Selection
    st.markdown("<div class='stat-card'><h5>📍 Position</h5>", unsafe_allow_html=True)
    position_DF = slider_with_textbox("Defender", 0, 1, player_data['position_DF'], "def")
    position_MF = slider_with_textbox("Midfielder", 0, 1, player_data['position_MF'], "mid")
    position_FW = slider_with_textbox("Forward", 0, 1, player_data['position_FW'], "fwd")
    position_GK = slider_with_textbox("Goalkeeper", 0, 1, player_data['position_GK'], "gk")
    st.markdown("</div>", unsafe_allow_html=True)

    # Display current values
    st.markdown("<div class='stat-card'><h5>👤 Player Stats</h5>", unsafe_allow_html=True)
    st.markdown(f"Age: {player_data['age']}")
    st.markdown(f"Games: {player_data['games']}")
    st.markdown(f"Minutes: {player_data['minutes']}")
    st.markdown(f"Minutes per 90: {player_data['minutes_90s']}")
    st.markdown(f"Shots: {player_data['shots']}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='stat-card'><h5>🏥 Injury History</h5>", unsafe_allow_html=True)
    st.markdown(f"Previous Injuries: {player_data['n_injuries']}")
    st.markdown(f"Severe Injuries: {player_data['n_severe_injuries']}")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="pitch-card">
            <h4 style="color: #2e7d32;">🎯 Risk Assessment Results</h4>
        </div>
        """, unsafe_allow_html=True)

    # Now we can use the slider values for calculations
    injury_risk_score = (
        n_injuries * 1.5 + 
        n_severe_injuries * 2.5 +
        (minutes_90s > 30) * 1.0 +
        (age > 30) * 1.0
    )

    # Prepare data for model using slider values
    input_data = {
        "age": age,
        "games": games,
        "minutes": minutes,
        "minutes_90s": minutes_90s,
        "shots": shots,
        "n_injuries": n_injuries,
        "n_severe_injuries": n_severe_injuries,
        "injury_risk_score": injury_risk_score,
        "position_MF": position_MF,
        "position_FW": position_FW,
        "position_DF": position_DF,
        "position_GK": position_GK
    }

    # Create DataFrame and ensure all required columns are present
    input_df = pd.DataFrame([input_data])
    missing_cols = set(feature_names) - set(input_df.columns)
    for col in missing_cols:
        input_df[col] = 0
    input_df = input_df[feature_names]

    # Scale the input data
    input_scaled = scaler.transform(input_df)

    # Get prediction probability based on slider inputs
    probability = model.predict_proba(input_scaled)[:, 1][0] * 100

    # Determine risk level and status using slider values
    def determine_injury_risk(probability, risk_score, n_injuries, n_severe_injuries):
        if (probability > 0.6 or risk_score >= 8 or n_severe_injuries >= 2 or n_injuries >= 4):
            return "High", True
        elif (probability > 0.3 or risk_score >= 4 or n_severe_injuries >= 1 or n_injuries >= 2):
            return "Medium", probability > 0.45
        else:
            return "Low", False

    risk_level, is_injured = determine_injury_risk(
        probability, injury_risk_score, n_injuries, n_severe_injuries
    )

    # Update the results display section with more detailed probability info
    st.markdown("""
        <div class="stat-card">
            <h5>📊 Injury Risk Analysis</h5>
        """, unsafe_allow_html=True)
    
    # Enhanced status indicator with detailed probability
    status = "🔴 High Risk" if is_injured else "🟢 Low Risk"
    st.markdown(f"""
        <div class='injury-{'high' if is_injured else 'low'}' style='text-align: center;'>
            <h2>{status}</h2>
            <div style='font-size: 2em; margin: 10px 0;'>
                Injury Probability: {probability:.1%}
            </div>
            <div style='font-size: 1.2em; margin: 5px 0;'>
                Raw Score: {probability:.3f}
            </div>
            <div style='font-size: 1.2em; margin: 5px 0;'>
                Confidence Level: {'High' if abs(probability - 0.5) > 0.3 else 'Medium' if abs(probability - 0.5) > 0.15 else 'Low'}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Detailed probability breakdown
    st.markdown("""
        <div style='margin: 20px 0;'>
            <h5>Probability Breakdown:</h5>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Base Probability", f"{probability:.1%}")
    with col2:
        st.metric("Risk Score", f"{injury_risk_score:.1f}")
    with col3:
        st.metric("Risk Level", risk_level)

    # Risk level indicator with more detail
    risk_color = "injury-high" if risk_level == "High" else "injury-medium" if risk_level == "Medium" else "injury-low"
    st.markdown(f"""
        <div class='{risk_color}' style='text-align: center; margin: 20px 0; padding: 15px;'>
            <h3>Overall Risk Assessment</h3>
            <div style='font-size: 1.5em; margin: 10px 0;'>
                Risk Level: {risk_level} ({injury_risk_score:.1f})
            </div>
            <div style='font-size: 1.2em; margin: 5px 0;'>
                Probability Range: {max(0, probability-0.1):.1%} - {min(1, probability+0.1):.1%}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Risk Factors with improved styling
    st.markdown("""
        <div class="stat-card" style='margin-top: 20px;'>
            <h5 style='color: #2e7d32; margin-bottom: 15px;'>⚠️ Risk Factors</h5>
    """, unsafe_allow_html=True)
    
    risk_factors = []
    if n_injuries > 0:
        severity = "High" if n_injuries >= 3 else "Moderate" if n_injuries >= 2 else "Low"
        risk_factors.append({
            'icon': '🤕',
            'text': f"Previous injuries: {n_injuries}",
            'severity': severity
        })
    if n_severe_injuries > 0:
        risk_factors.append({
            'icon': '🏥',
            'text': f"Severe injuries: {n_severe_injuries}",
            'severity': 'High'
        })
    if minutes_90s > 30:
        risk_factors.append({
            'icon': '⚡',
            'text': "High match load",
            'severity': 'Medium'
        })
    if age > 30:
        risk_factors.append({
            'icon': '📅',
            'text': f"Age factor: {age} years",
            'severity': 'Medium'
        })
    if games < 10:
        risk_factors.append({
            'icon': '⚠️',
            'text': "Limited game time",
            'severity': 'Low'
        })

    if risk_factors:
        for factor in risk_factors:
            severity_color = "#ff4444" if factor['severity'] == 'High' else "#ffbb33" if factor['severity'] == 'Medium' else "#00C851"
            st.markdown(f"""
                <div style='
                    background: rgba({255 if factor['severity'] == 'High' else 255 if factor['severity'] == 'Medium' else 0}, 
                                   {68 if factor['severity'] == 'High' else 187 if factor['severity'] == 'Medium' else 200},
                                   {68 if factor['severity'] == 'High' else 51 if factor['severity'] == 'Medium' else 81}, 0.1);
                    padding: 10px;
                    border-radius: 8px;
                    margin: 5px 0;
                    border: 1px solid {severity_color};
                '>
                    <span style='font-size: 1.2em;'>{factor['icon']}</span>
                    <span style='margin-left: 10px;'>{factor['text']}</span>
                    <span style='float: right; color: {severity_color};'>{factor['severity']} Risk</span>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style='text-align: center; color: #00C851; padding: 20px;'>
                <span style='font-size: 2em;'>✅</span>
                <p>No significant risk factors identified</p>
            </div>
        """, unsafe_allow_html=True)

    # Add Workload Management Analysis
    st.markdown("""
        <div class="stat-card" style='margin-top: 20px;'>
            <h5 style='color: #2e7d32; margin-bottom: 15px;'>📊 Workload Analysis</h5>
    """, unsafe_allow_html=True)
    
    # Calculate workload metrics
    match_load = minutes_90s
    season_load = minutes
    match_fitness = minutes / max(games, 1)
    
    # Display workload metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Match Load", f"{match_load:.1f} mins/90", 
                 delta="High" if match_load > 30 else "Normal")
    with col2:
        st.metric("Season Minutes", f"{season_load}", 
                 delta="High" if season_load > 3000 else "Normal")
    with col3:
        st.metric("Match Fitness", f"{match_fitness:.1f} mins/game",
                 delta="Low" if match_fitness < 60 else "Good")

    # Add Fitness Management Recommendations
    st.markdown("""
        <div class="stat-card" style='margin-top: 20px;'>
            <h5 style='color: #2e7d32; margin-bottom: 15px;'>💪 Fitness Management</h5>
    """, unsafe_allow_html=True)
    
    # Generate recommendations based on metrics
    recommendations = []
    
    if match_load > 30:
        recommendations.append({
            'icon': '⚠️',
            'text': "High match load detected - Consider rotation",
            'action': "Reduce minutes in next few games"
        })
    
    if season_load > 3000:
        recommendations.append({
            'icon': '📊',
            'text': "High season workload - Monitor fatigue",
            'action': "Implement additional recovery sessions"
        })
    
    if match_fitness < 60:
        recommendations.append({
            'icon': '🏃',
            'text': "Match fitness below optimal",
            'action': "Gradually increase game time"
        })
    
    if n_injuries > 2:
        recommendations.append({
            'icon': '🏥',
            'text': "Injury history requires attention",
            'action': "Custom training program recommended"
        })

    # Display recommendations
    for rec in recommendations:
        st.markdown(f"""
            <div style='
                background: rgba(46, 125, 50, 0.1);
                padding: 15px;
                border-radius: 8px;
                margin: 10px 0;
                border: 1px solid #2e7d32;
            '>
                <span style='font-size: 1.2em;'>{rec['icon']}</span>
                <span style='margin-left: 10px; font-weight: bold;'>{rec['text']}</span>
                <div style='margin-left: 35px; margin-top: 5px; color: #666;'>
                    Action: {rec['action']}
                </div>
            </div>
        """, unsafe_allow_html=True)

    if not recommendations:
        st.markdown("""
            <div style='text-align: center; color: #00C851; padding: 20px;'>
                <span style='font-size: 2em;'>✅</span>
                <p>All workload and fitness parameters are within optimal ranges</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Add Historical Trend Analysis if available
    if 'historical_data' in st.session_state:
        st.markdown("""
            <div class="stat-card" style='margin-top: 20px;'>
                <h5 style='color: #2e7d32; margin-bottom: 15px;'>📈 Fitness Trend Analysis</h5>
        """, unsafe_allow_html=True)
        
        # Add trend visualization here
        st.line_chart(st.session_state.historical_data)

# Enhanced footer
st.markdown("""
    <div class="footer">
        <div style="text-align: center;">
            <p style="color: #2e7d32;">Developed with ⚽ using Advanced AI & Sports Science</p>
            <div style="display: flex; justify-content: center; gap: 20px; margin: 20px 0;">
                <span>🏆 Premier League</span>
                <span>🌟 Champions League</span>
                <span>🌍 World Cup</span>
            </div>
            <p style="color: #666; font-size: 0.8em;">Version 2.0 | © 2024 Football Injury Predictor Pro</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Add this after your existing session state initializations
if 'selected_view' not in st.session_state:
    st.session_state.selected_view = 'Overview'

# Add this after the header section
# Tab Navigation
st.markdown("""
    <style>
    .tab-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin: 20px 0;
    }
    .tab {
        padding: 10px 20px;
        border-radius: 20px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .tab-active {
        background: #2e7d32;
        color: white;
    }
    .tab:hover {
        transform: translateY(-2px);
    }
    
    /* Player Card Styling */
    .player-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .player-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    
    /* Loading Animation */
    @keyframes pulse-green {
        0% { box-shadow: 0 0 0 0 rgba(46, 125, 50, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(46, 125, 50, 0); }
        100% { box-shadow: 0 0 0 0 rgba(46, 125, 50, 0); }
    }
    .loading {
        animation: pulse-green 1.5s infinite;
    }
    </style>
""", unsafe_allow_html=True)

# Add tabs
tabs = ['Overview', 'Detailed Analysis', 'Comparison', 'History']
col1, col2, col3, col4 = st.columns(4)
for idx, tab in enumerate([col1, col2, col3, col4]):
    with tab:
        if st.button(tabs[idx], key=f'tab_{idx}', 
                    help=f"View {tabs[idx]} section",
                    use_container_width=True):
            st.session_state.selected_view = tabs[idx]

# Main content based on selected view
if st.session_state.selected_view == 'Overview':
    # Player Selection with enhanced card
    selected_player = st.selectbox("Select Player", list(st.session_state.player_profiles.keys()))
    player_data = st.session_state.player_profiles[selected_player]
    
    # Player Card
    st.markdown(f"""
        <div class="player-card">
            <div style="display: flex; align-items: center; gap: 20px;">
                <div style="font-size: 40px;">⚽</div>
                <div>
                    <h2>{selected_player}</h2>
                    <p>Position: {get_position(player_data)}</p>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 20px;">
                <div>
                    <h4>Age</h4>
                    <p>{player_data['age']}</p>
                </div>
                <div>
                    <h4>Games</h4>
                    <p>{player_data['games']}</p>
                </div>
                <div>
                    <h4>Minutes</h4>
                    <p>{player_data['minutes']}</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Create radar chart for player stats
    categories = ['Games', 'Minutes', 'Shots', 'Fitness', 'Experience']
    values = [
        player_data['games']/15*100,
        player_data['minutes']/1350*100,
        player_data['shots']/30*100,
        (1-player_data['n_injuries']/5)*100,
        min(player_data['age']/35*100, 100)
    ]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=selected_player
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.selected_view == 'Detailed Analysis':
    # Detailed analysis view
    st.markdown("### Detailed Performance Analysis")
    selected_player = st.selectbox("Select Player for Analysis", 
                                 list(st.session_state.player_profiles.keys()))
    
    # Show historical trend
    historical_data = generate_historical_data(selected_player)
    
    # Create separate line charts for each metric
    fig = go.Figure()
    
    # Add traces for each metric
    fig.add_trace(go.Scatter(
        x=historical_data['Date'],
        y=historical_data['Minutes Played'],
        name='Minutes Played',
        line=dict(color='#2e7d32')
    ))
    
    fig.add_trace(go.Scatter(
        x=historical_data['Date'],
        y=historical_data['Fitness Score'],
        name='Fitness Score',
        line=dict(color='#1976d2')
    ))
    
    fig.add_trace(go.Scatter(
        x=historical_data['Date'],
        y=historical_data['Risk Score'],
        name='Risk Score',
        line=dict(color='#d32f2f')
    ))
    
    # Update layout
    fig.update_layout(
        title='Performance Trends',
        xaxis_title='Date',
        yaxis_title='Value',
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # Show the plot
    st.plotly_chart(fig, use_container_width=True)
    
    # Add metric cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Average Minutes",
            f"{historical_data['Minutes Played'].mean():.0f}",
            f"{historical_data['Minutes Played'].diff().mean():.1f}"
        )
    with col2:
        st.metric(
            "Fitness Trend",
            f"{historical_data['Fitness Score'].mean():.1f}%",
            f"{historical_data['Fitness Score'].diff().mean():.1f}%"
        )
    with col3:
        st.metric(
            "Risk Level",
            f"{historical_data['Risk Score'].mean():.1f}%",
            f"{historical_data['Risk Score'].diff().mean():.1f}%"
        )

elif st.session_state.selected_view == 'Comparison':
    # Comparison view
    st.markdown("### Player Comparison")
    col1, col2 = st.columns(2)
    with col1:
        player1 = st.selectbox("Select First Player", 
                             list(st.session_state.player_profiles.keys()),
                             key='player1')
    with col2:
        player2 = st.selectbox("Select Second Player", 
                             list(st.session_state.player_profiles.keys()),
                             key='player2')
    
    if player1 != player2:
        compare_players(player1, player2)

else:  # History view
    st.markdown("### Injury History")
    selected_player = st.selectbox("Select Player", 
                                 list(st.session_state.player_profiles.keys()))
    show_injury_history(selected_player)
