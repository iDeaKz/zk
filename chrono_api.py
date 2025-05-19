from pydantic import BaseModel
from typing import List

class AgentTraits(BaseModel):
    novelty: float
    recursion: float
    stability: float

class MemoryStep(BaseModel):
    reward: float
    entropy: float
    note: str

class Memory(BaseModel):
    note: str
    steps: List[MemoryStep]

class AgentModel(BaseModel):
    name: str
    traits: AgentTraits
    memory: Memory

"""
chrono_api.py

FastAPI backend for ChronoMorph Visual Cognitive Storytelling Engine.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import json
import random
import numpy as np
from datetime import datetime
import shutil
import uuid
import logging

# Import database modules
from utils.database import execute_query, get_db_connection
# Import our database models
import utils.models as db_models
from utils.import_agents import import_agents_from_directory

# Import utility modules
from utils.entropy_utils import calculate_entropy_delta, track_entropy_rungs, detect_entropy_alerts
from utils.audio_utils import generate_agent_theme
from utils.agent_utils import mutate_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create directories if they don't exist
os.makedirs("data/agents", exist_ok=True)
os.makedirs("data/memory", exist_ok=True)
os.makedirs("data/exports", exist_ok=True)
os.makedirs("audio_themes", exist_ok=True)
os.makedirs("temp", exist_ok=True)

app = FastAPI(title="ChronoMorph API", description="API for ChronoMorph Visual Cognitive Storytelling Engine")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class AgentTraits(BaseModel):
    novelty: float = 0.5
    recursion: float = 0.5
    stability: float = 0.5

class MemoryStep(BaseModel):
    reward: float = 0.0
    entropy: float = 0.0
    note: str = ""

class Memory(BaseModel):
    note: str = ""
    steps: List[MemoryStep] = []

class Agent(BaseModel):
    name: str
    traits: AgentTraits
    memory: Memory
    level: int = 1

class SimulationRequest(BaseModel):
    agent_name: str
    rungs: int = 10
    reward_bias: float = 0.5
    enable_mutation: bool = True

class ExportRequest(BaseModel):
    agent_name: str
    format: str
    include_audio: bool = True

@app.on_event("startup")
async def startup_event():
    """Import agents from JSON files on startup if database is empty"""
    try:
        # Check if agents table is empty
        agent_count = execute_query("SELECT COUNT(*) FROM agents")
        
        if agent_count and agent_count[0]['count'] == 0:
            logger.info("No agents found in database. Importing from JSON files...")
            count = import_agents_from_directory()
            logger.info(f"Imported {count} agents")
        else:
            logger.info("Database already contains agents, skipping import")
    except Exception as e:
        logger.error(f"Error during startup: {e}")

# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to ChronoMorph API"}

@app.get("/agents")
async def get_agents():
    """Get list of all agents"""
    try:
        return db_models.Agent.get_all()
    except Exception as e:
        logger.error(f"Error getting agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents")
async def create_agent(agent: AgentModel):
    """Create a new agent"""
    try:
        # Create agent in database
        agent_data = Agent.create(
            agent.name,
            agent.traits.dict(),
            agent.memory.note if agent.memory else None
        )
        
        # Generate theme music
        try:
            theme_path = generate_agent_theme(agent_data["traits"])
            if theme_path:
                Agent.add_theme(agent_data["id"], theme_path)
                agent_data["theme_path"] = theme_path
        except Exception as e:
            logger.error(f"Error generating theme: {e}")
            agent_data["theme_path"] = None
        
        return agent_data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/{agent_name}")
async def get_agent(agent_name: str):
    """Get agent details"""
    try:
        return Agent.get_by_name(agent_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/simulate")
async def simulate_agent(request: SimulationRequest):
    """Run a simulation for an agent"""
    try:
        # Get agent data
        agent_data = Agent.get_by_name(request.agent_name)
        agent_id = agent_data["id"]
        
        # Create new memory record
        memory_data = Memory.create(
            agent_id, 
            f"Simulation started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        memory_id = memory_data["id"]
        steps = []
        
        # Track entropy
        entropy_values = []
        entropy_deltas = []
        
        # Simulate rungs
        for i in range(request.rungs):
            # Calculate base values
            current_entropy = random.uniform(0, 1)
            if steps:
                previous_entropy = steps[-1]["entropy"]
            else:
                previous_entropy = 0
            
            # Apply trait effects
            novelty_factor = agent_data["traits"].get("novelty", 0.5)
            recursion_factor = agent_data["traits"].get("recursion", 0.5)
            stability_factor = agent_data["traits"].get("stability", 0.5)
            
            # Adjust entropy and reward based on traits
            current_entropy += novelty_factor * 0.2
            current_entropy -= stability_factor * 0.1
            current_entropy = max(0, min(1, current_entropy))
            
            reward = random.uniform(0, 1) * request.reward_bias
            reward += stability_factor * 0.2
            reward = max(0, min(1, reward))
            
            # Create step data
            step_data = {
                "entropy": round(current_entropy, 3),
                "entropy_before": round(previous_entropy, 3),
                "entropy_after": round(current_entropy, 3),
                "reward": round(reward, 3),
                "note": f"Simulation rung {i+1}",
                "rung_id": i,
                "recursive": random.random() < recursion_factor,
                "novel": random.random() < novelty_factor,
                "error": random.random() > stability_factor
            }
            
            # Add step to memory
            created_step = Memory.add_step(memory_id, step_data)
            steps.append(created_step)
            
            entropy_values.append(current_entropy)
            
            # Calculate entropy delta
            delta = calculate_entropy_delta(previous_entropy, current_entropy)
            entropy_deltas.append({
                "rung": i,
                "delta": delta,
                "spike": delta > 0.2
            })
        
        # Evaluate performance
        agent_traits = {
            "novelty": 0,
            "recursion": 0,
            "stability": 0
        }
        
        # Calculate traits based on steps
        for step in steps:
            if step["recursive"]:
                agent_traits["recursion"] += 1
            if step["novel"]:
                agent_traits["novelty"] += 1
            if step["error"]:
                agent_traits["stability"] -= 1
            else:
                agent_traits["stability"] += 1
        
        # Apply mutations if enabled
        mutations = {}
        if request.enable_mutation:
            # Apply trait mutations
            if agent_traits["novelty"] > 3:
                mutations["creative_mode"] = True
                Agent.add_mutation(agent_id, "creative_mode", True)
                
            if agent_traits["recursion"] > 2:
                mutations["loop_unroller"] = True
                Agent.add_mutation(agent_id, "loop_unroller", True)
                
            if agent_traits["stability"] > 4:
                mutations["resilience_bonus"] = 0.1
                Agent.add_mutation(agent_id, "resilience_bonus", 0.1)
            
            # Random rare mutation
            if random.random() < 0.05:
                mutations["mutation_token"] = "chaos_seed"
                Agent.add_mutation(agent_id, "mutation_token", "chaos_seed")
            
            # Update agent traits
            for trait, value in agent_traits.items():
                normalized_value = min(1.0, max(0.0, (agent_data["traits"].get(trait, 0) + value / 10) / 2))
                agent_data["traits"][trait] = normalized_value
            
            # Update traits in database
            Agent.update_traits(agent_id, agent_data["traits"])
            
            # Update agent level if stability increased
            if agent_traits["stability"] > 3:
                new_level = agent_data["level"] + 1
                Agent.update_level(agent_id, new_level)
                agent_data["level"] = new_level
        
        # Detect entropy alerts
        entropy_alerts = detect_entropy_alerts(entropy_deltas)
        
        # Generate new theme based on updated traits
        theme_path = None
        try:
            theme_path = generate_agent_theme(agent_data["traits"])
            if theme_path:
                Agent.add_theme(agent_id, theme_path)
        except Exception as e:
            logger.error(f"Error generating theme: {e}")
        
        # Return simulation results
        return {
            "agent": agent_data,
            "entropy_data": entropy_values,
            "entropy_deltas": entropy_deltas,
            "alerts": entropy_alerts,
            "mutations": mutations if mutations else None,
            "theme_path": theme_path
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error simulating agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory/{agent_name}")
async def get_memory(agent_name: str):
    """Get memory data for an agent"""
    try:
        agent_data = Agent.get_by_name(agent_name)
        return agent_data["memory"]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/replay/{agent_name}")
async def get_replay(agent_name: str, background_tasks: BackgroundTasks):
    """Generate a visual replay for an agent"""
    try:
        from utils.visualization_utils import generate_replay_visualization
        
        agent_data = Agent.get_by_name(agent_name)
        
        # Generate replay file
        os.makedirs("temp", exist_ok=True)
        output_path = f"temp/replay_{agent_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.gif"
        
        replay_path = generate_replay_visualization(agent_data, agent_data["memory"], output_path)
        
        # Create export record
        export_id = str(uuid.uuid4())
        export_data = Export.create(
            agent_data["id"],
            "gif",
            replay_path,
            os.path.getsize(replay_path) if os.path.exists(replay_path) else 0
        )
        
        # Copy file to exports directory with UUID filename
        os.makedirs("data/exports", exist_ok=True)
        dest_path = f"data/exports/{export_id}.gif"
        shutil.copy(replay_path, dest_path)
        
        return {"replay_url": f"/exports/{export_id}.gif"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating replay: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/leaderboard")
async def get_leaderboard():
    """Get leaderboard data"""
    try:
        agents = Agent.get_all()
        
        # Calculate scores
        for agent in agents:
            level = agent.get("level", 1)
            traits = agent.get("traits", {})
            
            score = level * 10
            score += traits.get("stability", 0) * 30
            score += traits.get("novelty", 0) * 20
            score += traits.get("recursion", 0) * 20
            
            # Add mutations bonus
            mutations = agent.get("mutations", {})
            if mutations:
                score += len(mutations) * 15
            
            agent["score"] = round(score)
        
        # Sort by score
        agents.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return agents
    except Exception as e:
        logger.error(f"Error getting leaderboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export")
async def export_agent(request: ExportRequest):
    """Export agent data in various formats"""
    try:
        from utils.export_utils import create_mp4_export, create_gif_export, create_summary
        
        agent_data = Agent.get_by_name(request.agent_name)
        agent_id = agent_data["id"]
        memory_data = agent_data["memory"]
        
        export_id = str(uuid.uuid4())
        os.makedirs("data/exports", exist_ok=True)
        
        if request.format == "mp4":
            # Generate MP4
            os.makedirs("temp", exist_ok=True)
            output_path = f"temp/export_{agent_data['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            
            mp4_path = create_mp4_export(
                agent_data, 
                memory_data, 
                output_path,
                include_audio=request.include_audio
            )
            
            # Copy to exports
            dest_path = f"data/exports/{export_id}.mp4"
            shutil.copy(mp4_path, dest_path)
            
            # Create export record
            export_data = Export.create(
                agent_id,
                "mp4",
                dest_path,
                os.path.getsize(dest_path) if os.path.exists(dest_path) else 0
            )
            
            return {
                "id": export_data["uuid"],
                "format": "mp4",
                "url": f"/exports/{export_id}.mp4",
                "size": export_data["size"]
            }
            
        elif request.format == "gif":
            # Generate GIF
            os.makedirs("temp", exist_ok=True)
            output_path = f"temp/export_{agent_data['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.gif"
            
            gif_path = create_gif_export(agent_data, memory_data, output_path)
            
            # Copy to exports
            dest_path = f"data/exports/{export_id}.gif"
            shutil.copy(gif_path, dest_path)
            
            # Create export record
            export_data = Export.create(
                agent_id,
                "gif",
                dest_path,
                os.path.getsize(dest_path) if os.path.exists(dest_path) else 0
            )
            
            return {
                "id": export_data["uuid"],
                "format": "gif",
                "url": f"/exports/{export_id}.gif",
                "size": export_data["size"]
            }
            
        elif request.format == "wav":
            # Generate audio theme
            output_path = generate_agent_theme(agent_data["traits"])
            
            # Copy to exports
            dest_path = f"data/exports/{export_id}.wav"
            shutil.copy(output_path, dest_path)
            
            # Create export record
            export_data = Export.create(
                agent_id,
                "wav",
                dest_path,
                os.path.getsize(dest_path) if os.path.exists(dest_path) else 0
            )
            
            return {
                "id": export_data["uuid"],
                "format": "wav",
                "url": f"/exports/{export_id}.wav",
                "size": export_data["size"]
            }
            
        elif request.format == "summary":
            # Generate text summary
            summary = create_summary(agent_data, memory_data)
            
            # Save summary to file
            summary_path = f"data/exports/{export_id}.txt"
            with open(summary_path, "w") as f:
                f.write(summary)
            
            # Create export record
            export_data = Export.create(
                agent_id,
                "summary",
                summary_path,
                os.path.getsize(summary_path) if os.path.exists(summary_path) else 0,
                summary
            )
            
            return {
                "id": export_data["uuid"],
                "format": "summary",
                "text": summary
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error exporting agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/exports/{agent_name}")
async def get_exports(agent_name: str):
    """Get list of exports for an agent"""
    try:
        agent_data = Agent.get_by_name(agent_name)
        exports = Export.get_by_agent_id(agent_data["id"])
        return exports
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting exports: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/exports/{export_id}.{format}")
async def serve_export(export_id: str, format: str):
    """Serve an export file"""
    try:
        export_data = Export.get_by_uuid(export_id)
        if export_data["format"] != format:
            raise HTTPException(status_code=400, detail=f"Format mismatch: {format} != {export_data['format']}")
        
        if not os.path.exists(export_data["path"]):
            raise HTTPException(status_code=404, detail="Export file not found")
        
        return FileResponse(export_data["path"])
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving export: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Additional model for Pydantic
class AgentModel(BaseModel):
    name: str
    traits: AgentTraits
    memory: Optional[Memory] = None
    level: int = 1
