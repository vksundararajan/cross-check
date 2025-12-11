import sys
import json
import mesop as me
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent.parent))
load_dotenv(Path(__file__).parent.parent / ".env")

import engine.interface as interface
from app.state import State

# ---------------------------------- Helpers --------------------------------- #
def parse_agent_json(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None

def normalize_status(claim):
    if not claim: return "UNCERTAIN"
    claim = claim.upper()
    if "LEGITIMATE" in claim: return "LEGITIMATE"
    if "PHISHING" in claim: return "PHISHING"
    return "UNCERTAIN"

# ------------------------------ Event Handlers ------------------------------ #
def load(e: me.LoadEvent):
    me.set_theme_mode("dark")

def on_url_input(e: me.InputEvent):
    state = me.state(State)
    state.url_input = e.value

def on_toggle_debate(e: me.SlideToggleChangeEvent):
    state = me.state(State)
    state.debate_active = not state.debate_active
    if state.debate_active:
        yield from run_analysis_process()
    else:
        state.final_verdict = ""
        for k in state.agents:
            state.agents[k]["status"] = ""
            state.agents[k]["evidence"] = ""
            state.agents[k]["raw_buffer"] = ""
        yield

# ------------------------------- Process Logic ------------------------------ #
def run_analysis_process():
    state = me.state(State)
    state.is_analyzing = True
    state.final_verdict = ""
    
    # Reset all agents
    for agent in state.agents.values():
        agent.update({"status": "PENDING", "evidence": "", "raw_buffer": "", "confidence": 0.0})
    yield

    AGENT_MAPPING = {
        "url_analyst_agent": "url",
        "html_structure_agent": "html",
        "content_semantic_agent": "content",
        "brand_impersonation_agent": "brand",
        "judgement_agent": "final"
    }

    try:
        for event in interface.stream_analysis(state.url_input):
            if event.author not in AGENT_MAPPING:
                continue
            if not event.content or not event.content.parts:
                continue
            
            text = event.content.parts[0].text
            if not text:
                continue

            ui_key = AGENT_MAPPING[event.author]

            if ui_key == "final":
                if "LEGITIMATE" in text: state.final_verdict = "LEGITIMATE"
                elif "PHISHING" in text: state.final_verdict = "PHISHING"
                else: state.final_verdict = "UNCERTAIN"
            elif ui_key in state.agents:
                agent = state.agents[ui_key]
                agent["raw_buffer"] += text
                data = parse_agent_json(agent["raw_buffer"])
                
                if data:
                    agent["status"] = normalize_status(data.get("Claim"))
                    agent["evidence"] = data.get("reasoning", "")
                    try:
                        agent["confidence"] = float(data.get("confidence", 0.0))
                    except (ValueError, TypeError):
                        agent["confidence"] = 0.0
                else:
                    agent["evidence"] = agent["raw_buffer"]

            yield

    except Exception as e:
        print(f"Runtime Error: {e}")
        state.final_verdict = "Error"
    
    state.is_analyzing = False
    yield