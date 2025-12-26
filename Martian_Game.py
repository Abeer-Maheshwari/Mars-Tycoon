import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import random
import graphviz
import time

# --- CONFIGURATION ---
st.set_page_config(
    page_title="MARS TYCOON: SOL SURVIVAL",  
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp {background-color: #0b0f19;}
    .stat-card {
        background: #161b26; border: 1px solid #333; padding: 15px; border-radius: 8px; text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .news-ticker {
        background: #000; border-left: 4px solid #FF4B4B; color: #FF4B4B; 
        font-family: 'Courier New', monospace; padding: 10px; margin-bottom: 20px;
    }
    h1, h2, h3, h4 {font-family: 'Courier New', monospace; color: #E0E0E0;}
    .metric-value {font-size: 2rem; font-weight: bold; color: white;}
    .metric-label {font-size: 0.8rem; color: #888; text-transform: uppercase;}
    div.stButton > button:first-child {
        border-radius: 6px; font-weight: bold; border: 1px solid #555; height: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GAME CONSTANTS ---
BUILDINGS = {
    'Solar_Array': {'cost': 5000, 'desc': 'Generates Energy (Base: 150)', 'icon': '⚡'},
    'Data_Center': {'cost': 15000, 'desc': 'Mines Crypto (Consumes 100 Energy)', 'icon': '💾'},
    'O2_Scrubber': {'cost': 8000, 'desc': 'Generates Oxygen (Consumes 50 Energy)', 'icon': '🍃'},
    'Hab_Module': {'cost': 10000, 'desc': 'Housing (Consumes 20 Energy)', 'icon': '🏠'}
}

TECH_TREE = {
    "Perovskite_Cells": {"cost": 25000, "desc": "+50% Solar Output", "parent": None},
    "Quantum_ASICs": {"cost": 40000, "desc": "+50% Crypto Yield", "parent": "Perovskite_Cells"},
    "Nuclear_Reactor": {"cost": 75000, "desc": "Passive +2000 Energy (Weather-proof)", "parent": "Perovskite_Cells"},
    "Terraforming": {"cost": 250000, "desc": "WIN CONDITION: Colony Self-Sufficient", "parent": "Nuclear_Reactor"}
}

# --- INITIALIZATION ---
if 'game_state' not in st.session_state:
    st.session_state.game_state = {
        'day': 1,
        'cash': 40000,
        'oxygen': 800,
        'energy': 500,
        'pop': 10,
        'engineers': 5,
        'scientists': 5,
        'buildings': {'Solar_Array': 2, 'Data_Center': 1, 'O2_Scrubber': 1, 'Hab_Module': 1},
        'techs': [],
        'logs': ["Sol 1: Colony Established. Systems Nominal."],
        'game_over': False,
        'game_won': False,
        'land_capacity': 30,
        'btc_price': 65000
    }

# --- HELPER FUNCTIONS ---

def get_market_price():
    """Gets real BTC price safely."""
    try:
        btc = yf.Ticker("BTC-USD")
        return btc.history(period='1d')['Close'].iloc[-1]
    except:
        # Fallback simulation if API fails
        return 65000 + random.randint(-2000, 2000)

def log_event(msg):
    """Adds a message to the game log."""
    day = st.session_state.game_state['day']
    st.session_state.game_state['logs'].append(f"Sol {day}: {msg}")

# --- CORE LOGIC HANDLERS ---
# These functions modify state directly

def advance_time(days=1, strategy="SELL"):
    """The main game loop. Runs 'days' number of turns."""
    gs = st.session_state.game_state
    
    if gs['game_over'] or gs['game_won']:
        return

    # Update Market Price once per batch to save time
    gs['btc_price'] = get_market_price()
    
    for _ in range(days):
        gs['day'] += 1
        
        # 1. Calculate Multipliers
        solar_mult = 1.5 if "Perovskite_Cells" in gs['techs'] else 1.0
        crypto_mult = 1.5 if "Quantum_ASICs" in gs['techs'] else 1.0
        nuclear_power = 2000 if "Nuclear_Reactor" in gs['techs'] else 0
        
        # 2. Energy Grid Calculation
        # Efficiency is based on Engineer coverage of Solar Arrays
        needed_engineers = gs['buildings']['Solar_Array']
        if needed_engineers > 0:
            coverage = min(1.0, gs['engineers'] / needed_engineers)
            efficiency = 0.5 + (0.7 * coverage) # 50% base + up to 70% bonus
        else:
            efficiency = 1.0

        solar_output = gs['buildings']['Solar_Array'] * 150 * efficiency * solar_mult
        total_energy_prod = solar_output + nuclear_power
        
        energy_drain = (gs['buildings']['Data_Center'] * 100) + \
                       (gs['buildings']['O2_Scrubber'] * 50) + \
                       (gs['buildings']['Hab_Module'] * 20)
        
        net_energy = total_energy_prod - energy_drain
        gs['energy'] = max(0, min(20000, gs['energy'] + net_energy))
        
        # 3. Grid Check
        has_power = True
        if gs['energy'] <= 0:
            has_power = False
            # Only log blackout on single day steps to reduce spam
            if days == 1: log_event("BLACKOUT! Systems offline.")
            
        # 4. Production (Requires Power)
        ops_mult = 1.0 if has_power else 0.0
        
        # Scientists boost compute
        sci_bonus = 1 + (gs['scientists'] * 0.1)
        compute_generated = gs['buildings']['Data_Center'] * 50 * sci_bonus * ops_mult
        
        o2_generated = gs['buildings']['O2_Scrubber'] * 25 * ops_mult
        
        # 5. Life Support
        pop_consumption = gs['pop'] * 2
        gs['oxygen'] += (o2_generated - pop_consumption)
        
        # Death Check
        if gs['oxygen'] <= 0:
            gs['oxygen'] = 0
            deaths = random.randint(1, 3)
            gs['pop'] = max(0, gs['pop'] - deaths)
            if days == 1: log_event(f"CRITICAL FAILURE: {deaths} colonists suffocated.")
        
        if gs['pop'] <= 0:
            gs['game_over'] = True
            log_event("MISSION FAILED: Colony lost.")
            break
            
        # 6. Economics
        if strategy == "SELL":
            # Auto-sell compute for cash
            revenue = compute_generated * (gs['btc_price'] / 100000000) * 1000 * crypto_mult
            gs['cash'] += revenue
            if days == 1: log_event(f"Sold compute for ${int(revenue):,}")
        # If HODL, we assume they are stockpiling (not implemented for simplicity, just no cash gain)

def buy_building(b_type):
    gs = st.session_state.game_state
    cost = BUILDINGS[b_type]['cost']
    
    total_buildings = sum(gs['buildings'].values())
    if total_buildings >= gs['land_capacity']:
        st.error("Not enough land!")
        return

    if gs['cash'] >= cost:
        gs['cash'] -= cost
        gs['buildings'][b_type] += 1
        st.success(f"Constructed {b_type}")
    else:
        st.error("Insufficient Funds")

def research_tech(tech_key):
    gs = st.session_state.game_state
    data = TECH_TREE[tech_key]
    
    if data['parent'] and data['parent'] not in gs['techs']:
        st.error("Prerequisites not met!")
        return
        
    if gs['cash'] >= data['cost']:
        gs['cash'] -= data['cost']
        gs['techs'].append(tech_key)
        st.balloons()
        if tech_key == "Terraforming":
            gs['game_won'] = True
    else:
        st.error("Insufficient Funds")

# --- UI RENDERING ---

# 1. Header & Stats
gs = st.session_state.game_state
st.title("MARS TYCOON: SOL SURVIVAL")

if gs['game_over']:
    st.error("GAME OVER. The colony has fallen silent.")
    if st.button("RESTART SIMULATION"):
        st.session_state.clear()
        st.rerun()
    st.stop()

if gs['game_won']:
    st.success("VICTORY! Mars has been terraformed.")
    st.balloons()
    if st.button("PLAY AGAIN"):
        st.session_state.clear()
        st.rerun()
    st.stop()

# Stats Row
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("SOL (DAY)", gs['day'])
c2.metric("CASH", f"${int(gs['cash']):,}")
c3.metric("OXYGEN", int(gs['oxygen']), delta=int(gs['oxygen'] - (gs['pop']*2)))
c4.metric("ENERGY", int(gs['energy']))
c5.metric("POPULATION", gs['pop'])

# Log Ticker
last_log = gs['logs'][-1] if gs['logs'] else "..."
st.markdown(f"<div class='news-ticker'>{last_log}</div>", unsafe_allow_html=True)

# 2. Main Controls
tab1, tab2, tab3 = st.tabs(["BASE", "RESEARCH", "OPERATIONS"])

with tab1:
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.subheader("Construction")
        for b_name, b_data in BUILDINGS.items():
            if st.button(f"{b_data['icon']} {b_name.replace('_',' ')} (${b_data['cost']:,})", use_container_width=True):
                buy_building(b_name)
                st.rerun()
                
    with col_b:
        st.subheader("Base Overview")
        cols = st.columns(4)
        for i, (b_name, count) in enumerate(gs['buildings'].items()):
            with cols[i]:
                st.markdown(f"""
                <div class='stat-card'>
                    <div class='metric-value'>{count}</div>
                    <div class='metric-label'>{b_name}</div>
                </div>
                """, unsafe_allow_html=True)

with tab2:
    st.subheader("Tech Tree")
    
    # Graphviz Visualization
    graph = graphviz.Digraph()
    graph.attr(bgcolor='#0b0f19', rankdir='LR')
    graph.attr('node', shape='box', style='filled', fontname='Courier', fontcolor='white')
    graph.attr('edge', color='#555')
    
    for key, data in TECH_TREE.items():
        if key in gs['techs']:
            graph.node(key, label=f"✅ {key}", fillcolor='#00CC96', color='white')
        elif (data['parent'] is None) or (data['parent'] in gs['techs']):
            graph.node(key, label=f"{key}\n${data['cost']:,}", fillcolor='#FFcc00', color='white')
        else:
            graph.node(key, label=f"🔒 {key}", fillcolor='#333', color='gray')
            
        if data['parent']:
            graph.edge(data['parent'], key)
            
    st.graphviz_chart(graph)
    
    st.divider()
    
    # Research Buttons
    # Research Buttons
    r_cols = st.columns(len(TECH_TREE))
    for i, (key, data) in enumerate(TECH_TREE.items()):
        with r_cols[i]:
            unlocked = key in gs['techs']
            
            # --- FIX STARTS HERE ---
            # Explicitly check if parent exists to ensure result is True/False (not None)
            if data['parent'] is None:
                locked = False
            else:
                locked = data['parent'] not in gs['techs']
            # --- FIX ENDS HERE ---
            
            label = "RESEARCHED" if unlocked else f"RESEARCH\n${data['cost']:,}"
            
            # Ensure disabled is strictly a boolean
            is_disabled = bool(unlocked or locked)
            
            st.caption(f"**{key.replace('_',' ')}**")
            st.caption(data['desc'])
            
            if st.button(label, key=f"res_{key}", disabled=is_disabled, use_container_width=True):
                research_tech(key)
                st.rerun()

with tab3:
    st.subheader("Daily Operations")
    
    # Workforce Slider
    total_pop = gs['pop']
    eng = st.slider("Assign Engineers (Repair & Efficiency)", 0, total_pop, gs['engineers'])
    # Update state immediately on slide
    gs['engineers'] = eng
    gs['scientists'] = total_pop - eng
    
    c_w1, c_w2 = st.columns(2)
    c_w1.info(f"Engineers: {gs['engineers']}")
    c_w2.success(f"Scientists: {gs['scientists']}")
    
    st.divider()
    
    st.markdown("#### Execute Turn")
    
    col_strat, col_act1, col_act2 = st.columns([1, 1, 1])
    
    with col_strat:
        # We use a selectbox instead of radio for cleaner UI here
        strategy = st.selectbox("Market Strategy", ["SELL COMPUTE", "HODL (No Revenue)"])
        strat_code = "SELL" if "SELL" in strategy else "HODL"
        
    with col_act1:
        if st.button("SLEEP (1 Day)", type="primary", use_container_width=True):
            advance_time(1, strat_code)
            st.rerun()
            
    with col_act2:
        if st.button("SKIP WEEK (7 Days)", use_container_width=True):
            advance_time(7, strat_code)
            st.rerun()