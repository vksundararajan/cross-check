import litellm
from pathlib import Path

LOG_FILE = Path(__file__).parent / "server.log"

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[LOG] {msg}\n")

def on_success(kwargs, response, start_time, end_time):
    log(f"SUCCESS: {kwargs.get('model', '?')}")

def on_failure(kwargs, exception, start_time, end_time):
    err = type(exception).__name__ if exception else "Unknown"
    log(f"FAILURE: {kwargs.get('model', '?')} - {err}")

litellm.success_callback = [on_success]
litellm.failure_callback = [on_failure]
