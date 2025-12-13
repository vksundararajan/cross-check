import debugpy
debugpy.listen(5678)
print("Debugger Enabled...\n")

import logging
import litellm

# Suppress verbose logging
litellm.suppress_debug_info = True
logging.getLogger("LiteLLM").setLevel(logging.CRITICAL)
logging.getLogger("google.adk").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.WARNING)