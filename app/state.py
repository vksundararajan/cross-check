import mesop as me
from dataclasses import field

@me.stateclass
class State:
    url_input: str = ""
    final_verdict: str = ""
    is_analyzing: bool = False
    debate_toggle: bool = False
    agents: dict[str, dict] = field(default_factory=lambda: {
        "url_analyst_agent": {
            "name": "URL Analyst", 
            "status": "", 
            "confidence": 0.0, 
            "evidence": "", 
            "icon": "link", 
            "raw_buffer": ""
        },
        "html_structure_agent": {
            "name": "HTML Structure", 
            "status": "", 
            "confidence": 0.0, 
            "evidence": "", 
            "icon": "code", 
            "raw_buffer": ""
        },
        "content_semantic_agent": {
            "name": "Content Semantic", 
            "status": "", 
            "confidence": 0.0, 
            "evidence": "", 
            "icon": "chat", 
            "raw_buffer": ""
        },
        "brand_impersonation_agent": {
            "name": "Brand Inspector", 
            "status": "", 
            "confidence": 0.0, 
            "evidence": "", 
            "icon": "verified", 
            "raw_buffer": ""
        },
    })