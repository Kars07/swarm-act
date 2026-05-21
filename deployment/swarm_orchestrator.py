import modal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json

# The orchestrator is extremely lightweight because it does not host models locally
orchestrator_image = modal.Image.debian_slim().pip_install("langgraph", "fastapi", "pydantic", "requests")

app = modal.App("bct-swarm-orchestrator")
web_app = FastAPI()

# =====================================================================
# PASTE YOUR DEPLOYED SERVICE ENDPOINTS HERE
# =====================================================================
# =====================================================================
# MODAL 1.0 ALIGNED INTERNAL ROUTING MESH
# =====================================================================
ALPHA_SERVICE_URL = "https://wakamateservices--bct-alpha-service-alphaservice-generate.modal.run"
BETA_SERVICE_URL = "https://wakamateservices--bct-beta-service-betaservice-generate.modal.run"
from typing import Dict, TypedDict

class SwarmState(TypedDict):
    user_prompt: str
    target_item_id: str
    alpha_parsed_json: Dict
    beta_raw_output: str
    beta_parsed_json: Dict

class SwarmRequest(BaseModel):
    prompt: str
    target_item_id: str

def execute_alpha_node(state: SwarmState) -> Dict:
    payload = {"prompt": state["user_prompt"], "target_item_id": state["target_item_id"]}
    response = requests.post(ALPHA_SERVICE_URL, json=payload)
    if response.status_code != 200:
        raise Exception(f"Alpha Service failed with status {response.status_code}: {response.text}")
    res = response.json()
    return {"alpha_parsed_json": res["parsed_json"]}

def execute_beta_node(state: SwarmState) -> Dict:
    payload = {"prompt": state["user_prompt"], "alpha_insight": state["alpha_parsed_json"]}
    response = requests.post(BETA_SERVICE_URL, json=payload)
    if response.status_code != 200:
        raise Exception(f"Beta Service failed with status {response.status_code}: {response.text}")
    res = response.json()
    return {"beta_raw_output": res["raw_output"], "beta_parsed_json": res["parsed_json"]}

# =====================================================================
# 5. LIGHTWEIGHT ROUTING ENTRY POINT (CPU ONLY - NO GPU BURN)
# =====================================================================
@web_app.post("/v1/swarm/process")
async def process_swarm_pipeline(req: SwarmRequest):
    from langgraph.graph import StateGraph, END
    
    workflow = StateGraph(SwarmState)
    workflow.add_node("Agent_Alpha", execute_alpha_node)
    workflow.add_node("Agent_Beta", execute_beta_node)
    
    workflow.set_entry_point("Agent_Alpha")
    workflow.add_edge("Agent_Alpha", "Agent_Beta")
    workflow.add_edge("Agent_Beta", END)
    
    compiled_swarm = workflow.compile()
    
    initial_state = {
        "user_prompt": req.prompt, 
        "target_item_id": req.target_item_id,
        "alpha_parsed_json": {}, 
        "beta_raw_output": "", 
        "beta_parsed_json": {}
    }
    
    try:
        final_state = compiled_swarm.invoke(initial_state)
        return {
            "status": "success",
            "alpha_extraction": final_state["alpha_parsed_json"],
            "beta_reasoning": {
                "raw_monologue": final_state["beta_raw_output"].split("</thinking>")[0] + "</thinking>" if "</thinking>" in final_state["beta_raw_output"] else "No thinking block.",
                "payload": final_state["beta_parsed_json"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# We run this on standard CPU infrastructure since it just brokers network traffic
@app.function(
    image=orchestrator_image,
    min_containers=0, # Scales down immediately when not receiving payloads
    timeout=600
)
@modal.asgi_app()
def swarm_endpoint(): 
    return web_app