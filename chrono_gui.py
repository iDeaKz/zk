"""
chrono_gui.py

Streamlit GUI for ChronoMorph Visual Cognitive Storytelling Engine.
"""

import streamlit as st
import requests
import json
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from PIL import Image
import time
import random

# Configure the page
st.set_page_config(
    page_title="ChronoMorph Vault",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    css_file = "static/styles.css"
    if os.path.exists(css_file):
        with open(css_file, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("Custom CSS file not found. Using default styling.")

try:
    load_css()
except Exception as e:
    st.warning(f"Error loading CSS: {e}")

# API URL - connect to the local FastAPI backend
API_URL = "http://localhost:8000"

# Sidebar navigation
st.sidebar.image("https://pixabay.com/get/g550a97845ef06caf67242205b52a022ec3f1ca02e9bd4f107116fd9342e7c0c04e4aa9122d4c24398c1007b9f8385a9d9f68c884e80f9506c1ecf8ebd0b7628c_1280.jpg", use_container_width=True)
st.sidebar.title("ChronoMorph Vault")
st.sidebar.markdown("*Visual Cognitive Storytelling Engine*")

# Navigation
nav = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Agent Creation", "Simulation", "Memory Replay", "Leaderboard", "Export"]
)

# Function to get agents from API
def get_agents():
    try:
        response = requests.get(f"{API_URL}/agents")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching agents: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return []

# Dashboard
if nav == "Dashboard":
    st.title("🧠 ChronoMorph Dashboard")
    st.markdown("### Cognitive Simulation Controller")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.image("https://pixabay.com/get/g09dc99658c03ea111853f962221d96156761aaddf0a84e376a10782fa640441b88765f436a278e6aac4e94a9fb78caa2533980ff94473f3b0ff9f08f126ee296_1280.jpg", use_container_width=True)
        st.markdown("### Active Agents")
        
        agents = get_agents()
        if agents:
            for agent in agents:
                st.markdown(f"**{agent['name']}** (Level {agent.get('level', 1)})")
                stability = agent.get('traits', {}).get('stability', 0.5)
                st.progress(stability)
        else:
            st.info("No agents found. Create a new agent to begin.")
    
    with col2:
        st.image("https://pixabay.com/get/g3ef15f1194a19388a58e4961cdb88cfa5a63d21dde5b7c3ead3f93db7d5bff590fabc20f962897a1463b04ce166e85915f6f19a92684d290231ce10f30f7f783_1280.jpg", use_container_width=True)
        st.markdown("### System Stats")
        
        stats_col1, stats_col2 = st.columns(2)
        with stats_col1:
            st.metric("Active Agents", len(agents) if agents else 0)
            st.metric("Simulations Run", random.randint(5, 50))
        
        with stats_col2:
            st.metric("Memory Entries", random.randint(20, 200))
            st.metric("Entropy Spikes", random.randint(3, 15))

# Agent Creation
elif nav == "Agent Creation":
    st.title("🧠 Create New Agent")
    
    st.image("https://pixabay.com/get/g1fa369de751cf76a62418c27872e26d29cf404076747ac0684388248847d5fcfaa1221d724c9f7a51009a52f1b92aed78890d0e79f14c1f930cffd1a6e3e80ed_1280.jpg", use_container_width=True)
    
    with st.form("agent_creation_form"):
        agent_name = st.text_input("Agent Name")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            novelty = st.slider("Novelty", 0, 10, 5)
        with col2:
            recursion = st.slider("Recursion", 0, 10, 5)
        with col3:
            stability = st.slider("Stability", 0, 10, 5)
        
        st.markdown("### Initial Memory")
        memory_note = st.text_area("Memory Note", "Initial cognitive seed.")
        
        submit = st.form_submit_button("Create Agent")
        
        if submit:
            if not agent_name:
                st.error("Agent name is required")
            else:
                try:
                    response = requests.post(
                        f"{API_URL}/agents",
                        json={
                            "name": agent_name,
                            "traits": {
                                "novelty": novelty / 10,
                                "recursion": recursion / 10,
                                "stability": stability / 10
                            },
                            "memory": {
                                "note": memory_note,
                                "steps": []
                            }
                        }
                    )
                    
                    if response.status_code == 200:
                        st.success(f"Agent {agent_name} created successfully!")
                        
                        # Display agent card
                        st.markdown("### Agent Created")
                        st.json(response.json())
                    else:
                        st.error(f"Error creating agent: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Error connecting to API: {e}")

# Simulation
elif nav == "Simulation":
    st.title("🧠 Agent Simulation")
    
    st.image("https://pixabay.com/get/gb54fa3dd778108d17439e2e886c896d4376e2cd8d0049220a61cbd7f38067219c3589577243339c8416713a11abaa10945388a961d5105c75f4985bdcb0ce0cb_1280.jpg", use_container_width=True)
    
    agents = get_agents()
    
    if not agents:
        st.info("No agents found. Create a new agent first.")
    else:
        agent_names = [agent["name"] for agent in agents]
        selected_agent = st.selectbox("Select Agent", agent_names)
        
        with st.form("simulation_form"):
            st.markdown("### Simulation Parameters")
            
            rungs = st.slider("Simulation Rungs", 1, 20, 10)
            reward_bias = st.slider("Reward Bias", 0.0, 1.0, 0.5)
            enable_mutation = st.checkbox("Enable Mutation", True)
            
            submit = st.form_submit_button("Run Simulation")
            
            if submit:
                try:
                    with st.spinner("Running simulation..."):
                        response = requests.post(
                            f"{API_URL}/simulate",
                            json={
                                "agent_name": selected_agent,
                                "rungs": rungs,
                                "reward_bias": reward_bias,
                                "enable_mutation": enable_mutation
                            }
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            st.success("Simulation completed!")
                            
                            # Display results
                            st.markdown("### Simulation Results")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("#### Agent Stats")
                                st.json(result["agent"])
                                
                                st.markdown("#### Mutations")
                                if result.get("mutations"):
                                    st.json(result["mutations"])
                                else:
                                    st.info("No mutations occurred")
                            
                            with col2:
                                st.markdown("#### Entropy Tracking")
                                
                                # Display entropy chart
                                if "entropy_data" in result:
                                    entropy_data = result["entropy_data"]
                                    
                                    fig, ax = plt.subplots(figsize=(10, 4))
                                    ax.plot(entropy_data, marker='o', color='darkorange')
                                    ax.set_title("Entropy Over Simulation")
                                    ax.set_xlabel("Rung")
                                    ax.set_ylabel("Entropy")
                                    ax.grid(True)
                                    st.pyplot(fig)
                                
                                # Display any alerts
                                if "alerts" in result and result["alerts"]:
                                    st.markdown("#### Entropy Alerts")
                                    for alert in result["alerts"]:
                                        st.warning(f"Rung {alert['rung']}: {alert['alert']} (Δ{alert['delta']})")
                        else:
                            st.error(f"Error running simulation: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Error connecting to API: {e}")

# Memory Replay
elif nav == "Memory Replay":
    st.title("🧠 Memory Replay")
    
    st.image("https://pixabay.com/get/g8ca7d08ea42966698647f6be3e2a73255a5001bf355d92c04d00b4ebb87ee00f89aa157b94e0123508babec592f1bcd5c35bf934471579700ffa588903ee2271_1280.jpg", use_container_width=True)
    
    agents = get_agents()
    
    if not agents:
        st.info("No agents found. Create a new agent first.")
    else:
        agent_names = [agent["name"] for agent in agents]
        selected_agent = st.selectbox("Select Agent", agent_names)
        
        try:
            response = requests.get(f"{API_URL}/memory/{selected_agent}")
            
            if response.status_code == 200:
                memory_data = response.json()
                
                # Memory summary
                st.markdown("### Agent Memory")
                memory_steps = memory_data.get("steps", [])
                
                if not memory_steps:
                    st.info("No memory steps found for this agent.")
                else:
                    # Memory visualization
                    st.markdown("### Memory Timeline")
                    
                    # Create memory chart
                    rewards = [step.get("reward", 0) for step in memory_steps]
                    entropy = [step.get("entropy", 0) for step in memory_steps]
                    
                    fig, ax = plt.subplots(figsize=(10, 4))
                    ax.plot(rewards, marker='o', label='Reward', color='green')
                    ax.plot(entropy, marker='x', label='Entropy', color='red')
                    ax.set_title("Memory Timeline")
                    ax.set_xlabel("Step")
                    ax.set_ylabel("Value")
                    ax.legend()
                    ax.grid(True)
                    st.pyplot(fig)
                    
                    # Memory steps
                    st.markdown("### Memory Steps")
                    for i, step in enumerate(memory_steps):
                        with st.expander(f"Step {i+1}"):
                            st.markdown(f"**Reward:** {step.get('reward', 0)}")
                            st.markdown(f"**Entropy:** {step.get('entropy', 0)}")
                            st.markdown(f"**Note:** {step.get('note', 'No note')}")
                    
                    # Replay visualization
                    st.markdown("### Visual Replay")
                    if st.button("Generate Visual Replay"):
                        with st.spinner("Generating replay..."):
                            try:
                                replay_response = requests.get(f"{API_URL}/replay/{selected_agent}")
                                
                                if replay_response.status_code == 200:
                                    replay_data = replay_response.json()
                                    if "replay_url" in replay_data:
                                        st.success("Replay generated!")
                                        st.markdown(f"![Replay]({API_URL}{replay_data['replay_url']})")
                                    else:
                                        st.error("No replay URL returned")
                                else:
                                    st.error(f"Error generating replay: {replay_response.status_code} - {replay_response.text}")
                            except Exception as e:
                                st.error(f"Error connecting to API: {e}")
            else:
                st.error(f"Error fetching memory: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Error connecting to API: {e}")

# Leaderboard
elif nav == "Leaderboard":
    st.title("🏆 Agent Leaderboard")
    
    st.image("https://pixabay.com/get/g41444b1209cb45ab4973e6dc6d1eff4e212e9bc82660e1b775e1066a64d0fae230ba952e9f3093d7d842f5028abe6d185bb73b3cd3d185534be7a1ab284db4d4_1280.jpg", use_container_width=True)
    
    try:
        response = requests.get(f"{API_URL}/leaderboard")
        
        if response.status_code == 200:
            leaderboard_data = response.json()
            
            if not leaderboard_data:
                st.info("No agents in the leaderboard yet.")
            else:
                # Create dataframe for leaderboard
                df = pd.DataFrame(leaderboard_data)
                
                # Format the dataframe
                if "name" in df.columns:
                    # Display the dataframe with highlighting
                    st.dataframe(df[["name", "level", "score", "novelty", "recursion", "stability"]])
                    
                    # Top agent highlight
                    if len(df) > 0:
                        top_agent = df.iloc[0]
                        
                        st.markdown("### Top Agent")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**Name:** {top_agent['name']}")
                            st.markdown(f"**Level:** {top_agent.get('level', 1)}")
                            st.markdown(f"**Score:** {top_agent.get('score', 0)}")
                        
                        with col2:
                            # Traits radar chart
                            traits = {
                                "novelty": top_agent.get("novelty", 0),
                                "recursion": top_agent.get("recursion", 0),
                                "stability": top_agent.get("stability", 0)
                            }
                            
                            categories = list(traits.keys())
                            values = list(traits.values())
                            
                            # Complete the loop
                            values += values[:1]
                            categories += categories[:1]
                            
                            # Create radar chart
                            fig = plt.figure(figsize=(5, 5))
                            ax = fig.add_subplot(111, polar=True)
                            
                            # Plot the values
                            ax.plot(np.linspace(0, 2*np.pi, len(values)), values, marker='o')
                            ax.fill(np.linspace(0, 2*np.pi, len(values)), values, alpha=0.25)
                            
                            # Set the labels
                            ax.set_thetagrids(np.degrees(np.linspace(0, 2*np.pi, len(categories)-1, endpoint=False)), categories[:-1])
                            
                            st.pyplot(fig)
                else:
                    st.error("Invalid leaderboard data structure")
        else:
            st.error(f"Error fetching leaderboard: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Error connecting to API: {e}")

# Export
elif nav == "Export":
    st.title("📼 Export Agent Media")
    
    st.image("https://pixabay.com/get/gc9f988f7ded03e67ee8bd3c6b658a7143ad6adbe2f6e2f22f57350c7255fc752a944979176ca68cf2233dadab4344f58a28b6a60f0756062d3023f96c0681d4f_1280.jpg", use_container_width=True)
    
    agents = get_agents()
    
    if not agents:
        st.info("No agents found. Create a new agent first.")
    else:
        agent_names = [agent["name"] for agent in agents]
        selected_agent = st.selectbox("Select Agent", agent_names)
        
        export_formats = ["mp4", "gif", "wav", "summary"]
        selected_format = st.selectbox("Export Format", export_formats)
        
        include_audio = st.checkbox("Include Audio", True, disabled=(selected_format != "mp4"))
        
        if st.button("Generate Export"):
            try:
                with st.spinner(f"Generating {selected_format.upper()} export..."):
                    response = requests.post(
                        f"{API_URL}/export",
                        json={
                            "agent_name": selected_agent,
                            "format": selected_format,
                            "include_audio": include_audio
                        }
                    )
                    
                    if response.status_code == 200:
                        export_data = response.json()
                        st.success(f"{selected_format.upper()} export generated!")
                        
                        if selected_format == "mp4":
                            # Display MP4
                            st.video(f"{API_URL}/exports/{export_data['id']}.mp4")
                        elif selected_format == "gif":
                            # Display GIF
                            st.markdown(f"![GIF]({API_URL}/exports/{export_data['id']}.gif)")
                        elif selected_format == "wav":
                            # Display audio
                            st.audio(f"{API_URL}/exports/{export_data['id']}.wav")
                        elif selected_format == "summary":
                            # Display summary
                            st.markdown("### Agent Cognitive Summary")
                            st.markdown(export_data.get("text", "No summary available."))
                    else:
                        st.error(f"Error generating export: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Error connecting to API: {e}")
        
        # List previous exports
        st.markdown("### Previous Exports")
        try:
            exports_response = requests.get(f"{API_URL}/exports/{selected_agent}")
            
            if exports_response.status_code == 200:
                exports = exports_response.json()
                
                if not exports:
                    st.info("No previous exports found.")
                else:
                    for export in exports:
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**Format:** {export.get('format', 'Unknown').upper()} | **Date:** {export.get('created_at', 'Unknown')}")
                        
                        with col2:
                            if export.get('format') == "mp4":
                                st.markdown(f"[View MP4]({API_URL}/exports/{export.get('uuid')}.mp4)")
                            elif export.get('format') == "gif":
                                st.markdown(f"[View GIF]({API_URL}/exports/{export.get('uuid')}.gif)")
                            elif export.get('format') == "wav":
                                st.markdown(f"[Listen]({API_URL}/exports/{export.get('uuid')}.wav)")
                            elif export.get('format') == "summary":
                                st.markdown(f"[View Summary]({API_URL}/exports/{export.get('uuid')}.txt)")
            else:
                st.error(f"Error fetching exports: {exports_response.status_code} - {exports_response.text}")
        except Exception as e:
            st.error(f"Error connecting to API: {e}")