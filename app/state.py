import mesop as me
from dataclasses import field

@me.stateclass
class State:
    url_input: str = ""
    final_verdict: str = ""
    is_analyzing: bool = False
    debate_active: bool = False
    agents: dict[str, dict] = field(default_factory=lambda: {
        "url": {
            "name": "URL Analyst", 
            "status": "", 
            "confidence": 0.0, 
            "evidence": "", 
            "icon": "link", 
            "raw_buffer": ""
        },
        "html": {
            "name": "HTML Structure", 
            "status": "", 
            "confidence": 0.0, 
            "evidence": "", 
            "icon": "code", 
            "raw_buffer": ""
        },
        "content": {
            "name": "Content Semantic", 
            "status": "", 
            "confidence": 0.0, 
            "evidence": "", 
            "icon": "chat", 
            "raw_buffer": ""
        },
        "brand": {
            "name": "Brand Inspector", 
            "status": "", 
            "confidence": 0.0, 
            "evidence": "", 
            "icon": "verified", 
            "raw_buffer": ""
        },
    })