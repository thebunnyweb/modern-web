import litellm
from functools import wraps
import inspect

# Save the original function so we can still call it later
_original_completion = litellm.completion

@wraps(_original_completion)
def patched_completion(*args, **kwargs):
    # --- flatten extra_body ---
    extra = kwargs.pop("extra_body", None)
    if isinstance(extra, dict):
        # Move each key (e.g. metadata) to the top-level
        for k, v in extra.items():
            if k not in kwargs:
                kwargs[k] = v
        # If you prefer to override, use: kwargs.update(extra)

    return _original_completion(*args, **kwargs)

# Apply the patch
litellm.completion = patched_completion
print("[Patch] LiteLLM completion() monkey-patched to flatten extra_body.")