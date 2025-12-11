import debugpy
debugpy.listen(5678)
print("Waiting for debugger attach...")

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import mesop as me
from app.state import State
from app.styles import styles as S
from app.events import load, on_url_input, on_toggle_debate

@me.component
def agent_card(key: str, result: dict):
    status = result["status"]
    with me.box(style=S.card_container(status)):
        with me.box(style=S.CARD_HEADER):
            me.icon(result["icon"])
            with me.box(style=S.CARD_TITLE_BOX):
                me.text(result["name"], type="headline-6", style=S.CARD_TITLE_TEXT)
            
            if status != "" and status != "PENDING":
                me.text(f"{int(result['confidence'] * 100)}%", type="subtitle-1")

        if status == "PENDING":
            with me.box(style=S.SPINNER_BOX):
                 me.progress_spinner(diameter=30, stroke_width=3)
        elif status != "":
            me.text(f"Verdict: {status}", style=S.VERDICT_LABEL)
            if result["evidence"]:
                with me.expansion_panel(title="View Evidence", icon="description"):
                    me.text(result["evidence"])

@me.page(path="/app", title="CrossCheck", on_load=load, security_policy=me.SecurityPolicy(dangerously_disable_trusted_types=True))
def app():
    state = me.state(State)
    with me.box(style=S.APP_CONTAINER):
        me.text("URL Cross-Check", type="headline-1", style=S.APP_HEADER)
        
        with me.box(style=S.INPUT_ROW):
            me.input(label="Enter URL", value=state.url_input, on_input=on_url_input, style=S.INPUT_FIELD, appearance="outline")
            with me.box(style=S.TOGGLE_BOX):
                me.slide_toggle(label="Run Analysis", checked=state.debate_active, on_change=on_toggle_debate, color="primary")

        with me.box(style=S.GRID_LAYOUT):
            for key, agent in state.agents.items():
                agent_card(key, agent)

        if state.final_verdict:
            with me.box(style=S.verdict_box(state.final_verdict)):
                me.text(f"FINAL VERDICT: {state.final_verdict}", type="headline-4")
                me.text("The high council has spoken.", type="subtitle-1")