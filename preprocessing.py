# Compatibility shim to support unpickling of artifacts that reference
# a top-level `preprocessing` module. Re-exports functions from the
# real implementation in the `src` package.

from src.preprocessing import clean_text

__all__ = ["clean_text"]
