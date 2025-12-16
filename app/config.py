import os
import debugpy
import logging
import litellm

# -------------------------- debugger in development ------------------------- #
if os.environ.get("DEBUG_ENABLED"):
    debugpy.listen(5678)
    print("Mesop Debugger Enabled...\n")

# ------------------------- Suppress verbose logging ------------------------- #
litellm.suppress_debug_info = True
logging.getLogger("LiteLLM").setLevel(logging.CRITICAL)
logging.getLogger("google.adk").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.WARNING)