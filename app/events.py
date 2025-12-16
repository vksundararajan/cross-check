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
    if "INVALID URL" in claim: return "INVALID URL"
    return "UNCERTAIN"

def set_all_agents(state, status, confidence=0.0, evidence=""):
    for agent in state.agents.values():
        agent.update({
            "status": status,
            "confidence": confidence,
            "evidence": evidence,
            "raw_buffer": ""
        })

def extract_event_text(event):
    if not event.content or not event.content.parts:
        return None
    return event.content.parts[0].text or None

def process_agent_response(agent, text):
    agent["raw_buffer"] += text
    data = parse_agent_json(agent["raw_buffer"])
    if data:
        agent["status"] = normalize_status(data.get("Claim"))
        agent["evidence"] = data.get("reasoning", "")
        agent["confidence"] = float(data.get("confidence", 0.0))
        return True
    return False

# ------------------------------ Event Handlers ------------------------------ #
def load(e: me.LoadEvent):
    me.set_theme_mode("dark")

def on_url_input(e: me.InputEvent):
    me.state(State).url_input = e.value

def on_toggle_debate(e: me.SlideToggleChangeEvent):
    state = me.state(State)
    state.debate_toggle = not state.debate_toggle
    if state.debate_toggle:
        yield from run_analysis_process()
    else:
        state.url_input = ""
        state.input_key += 1
        state.final_verdict = ""
        state.is_analyzing = False
        set_all_agents(state, status="", confidence=0.0, evidence="")
        yield

# ------------------------------- Process Logic ------------------------------ #
def run_analysis_process():
    state = me.state(State)
    state.is_analyzing = True
    state.final_verdict = ""
    set_all_agents(state, status="PENDING")
    yield

    try:
        for event in interface.stream_analysis(state.url_input):
            text = extract_event_text(event)
            if not text:
                continue

            state_changed = False
            if event.author == "judgement_agent":
                state.final_verdict = normalize_status(text)
                if (state.final_verdict == "INVALID URL"):
                    set_all_agents(
                        state, 
                        status="INVALID URL", 
                        confidence=0.0, 
                        evidence="Provided URL is invalid or could not be processed."
                    )
                state_changed = True
            elif event.author in state.agents:
                state_changed = process_agent_response(state.agents[event.author], text)

            if state_changed:
                yield

    except Exception as e:
        state.final_verdict = "Error"
        set_all_agents(
            state, 
            status="ERROR", 
            confidence=0.0, 
            evidence="An error occurred during analysis."
        )
    
    if not state.final_verdict:
        state.final_verdict = "REQUEST TOO LARGE"
        set_all_agents(
            state, 
            status="UNCERTAIN", 
            confidence=0.0, 
            evidence="Processing incomplete due to rate limit."
        )

    state.is_analyzing = False
    yield