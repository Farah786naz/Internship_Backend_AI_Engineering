from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


_module_path = Path(__file__).resolve().parent / "week-1" / "main.py"
_spec = spec_from_file_location("week_1_main", _module_path)

if _spec is None or _spec.loader is None:
    raise ImportError(f"Could not load application module from {_module_path}")

_module = module_from_spec(_spec)
_spec.loader.exec_module(_module)

for name in dir(_module):
    if not name.startswith("_"):
        globals()[name] = getattr(_module, name)