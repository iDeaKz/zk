import os, requests, json, random
from datetime import datetime

API_URL = 'http://localhost:8000'
os.makedirs('data/agents', exist_ok=True)
os.makedirs('data/memory', exist_ok=True)
os.makedirs('data/exports', exist_ok=True)

def supreme_agent_name():
    return random.choice(['Neo','Hyper','Glyph','Zeta','Omega']) + '_' + random.choice(['Pulse','Loop','Delta','Crux','Axis'])

def create_agent(name, traits=None, note="Injected Supreme Agent"):
    if traits is None:
        traits = {'novelty': 1.0, 'recursion': 1.0, 'stability': 1.0}
    payload = {
        'name': name,
        'traits': traits,
        'memory': {'note': note, 'steps': []}
    }
    try:
        r = requests.post(f'{API_URL}/agents', json=payload)
        if r.status_code == 200:
            print(f'✅ Created agent: {name}')
        else:
            print(f'❌ Creation failed: {r.text}')
    except Exception as e:
        print(f'❌ Error connecting to API: {e}')

def run_simulation(name, rungs=20, reward_bias=0.9, enable_mutation=True):
    payload = {
        'agent_name': name,
        'rungs': rungs,
        'reward_bias': reward_bias,
        'enable_mutation': enable_mutation
    }
    try:
        r = requests.post(f'{API_URL}/simulate', json=payload)
        if r.status_code == 200:
            result = r.json()
            print(f'🧠 Simulation complete for {name}')
            print('Deltas:', [d['delta'] for d in result.get('entropy_deltas', [])])
            print('Alerts:', result.get('alerts', []))
            print('Mutations:', result.get('mutations', {}))
            print('Theme:', result.get('theme_path', 'N/A'))
        else:
            print(f'❌ Simulation failed: {r.text}')
    except Exception as e:
        print(f'❌ API error: {e}')

def monitor_agent(agent_name, interval=5):
    import time
    try:
        while True:
            res = requests.get(f"{API_URL}/agents/{agent_name}")
            mem = requests.get(f"{API_URL}/memory/{agent_name}")
            if res.status_code == 200 and mem.status_code == 200:
                agent = res.json()
                steps = mem.json().get("steps", [])
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Agent {agent['name']} | Level {agent['level']}")
                print("Traits:", agent["traits"])
                if steps:
                    last = steps[-1]
                    print(f"  Last Step → Entropy: {last['entropy']}, Reward: {last['reward']}")
            else:
                print("⚠️ Could not fetch agent state.")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n🔕 Monitoring stopped.")

if __name__ == '__main__':
    print("ChronoMorph Replit Helper [Supreme Mode]")
    try:
        name = input("Enter agent name (Enter for auto): ").strip() or supreme_agent_name() + '_' + datetime.now().strftime('%H%M%S')
        create_agent(name)
        run_simulation(name)
        if input("Monitor this agent? [y/N]: ").lower() == 'y':
            monitor_agent(name)
    except KeyboardInterrupt:
        print("\n🚫 Cancelled by user.")
    except Exception as e:
        print(f"❌ Critical failure: {e}")