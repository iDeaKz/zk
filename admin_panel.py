# admin_panel.py — ChronoMorph Admin Dashboard
import streamlit as st
import requests

st.set_page_config(page_title='ChronoMorph Admin', layout='wide')
st.title("🔧 ChronoMorph Admin Panel")

API_URL = "http://localhost:8000"

try:
    agents = requests.get(f"{API_URL}/agents").json()
    st.subheader("Active Agents")
    for agent in agents:
        st.markdown(f"**{agent['name']}** — Level {agent['level']}")
        st.json(agent['traits'])
except Exception as e:
    st.error(f"API not reachable: {e}")