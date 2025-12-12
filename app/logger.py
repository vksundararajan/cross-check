import debugpy
debugpy.listen(5678)
print("Debugger Enabled...\n")

import logging
import threading
import litellm

litellm.suppress_debug_info = True
litellm.set_verbose = False

logging.getLogger("LiteLLM").setLevel(logging.CRITICAL)
logging.getLogger("google.adk").setLevel(logging.CRITICAL)
logging.getLogger("google.adk.runners").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.WARNING)

threading.excepthook = lambda args: None