"""Project enums package.

Note: package name `enum` is required by project structure request.
This module re-exports ALL stdlib enum symbols so imports like
`from enum import IntEnum, auto, _simple_enum` keep working.
"""

from __future__ import annotations

import importlib.util
import os
import sysconfig

_STDLIB_PATH = sysconfig.get_path("stdlib") or ""
_ENUM_PATH = os.path.join(_STDLIB_PATH, "enum.py")
_SPEC = importlib.util.spec_from_file_location("_stdlib_enum", _ENUM_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("Unable to load Python stdlib enum module")

_STDLIB_ENUM = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_STDLIB_ENUM)

for _name in dir(_STDLIB_ENUM):
    if _name.startswith("__"):
        continue
    globals()[_name] = getattr(_STDLIB_ENUM, _name)

from enum.auth_status import AuthStatus
from enum.backend_endpoint import BackendEndpoint

__all__ = [name for name in dir(_STDLIB_ENUM) if not name.startswith("__")]
__all__.extend(["AuthStatus", "BackendEndpoint"])
