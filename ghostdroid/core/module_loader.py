import importlib
import inspect
import os
import sys
from typing import Dict, Any, List, Optional, Type
from dataclasses import dataclass, field

from core.ui import print_status, console


@dataclass
class ModuleMetadata:
    name: str
    version: str
    description: str
    author: str = "GhostDroid"
    risk_level: str = "low"
    requires_adb: bool = False
    requires_root: bool = False
    category: str = "general"


class BaseModule:
    metadata: ModuleMetadata = ModuleMetadata(
        name="base",
        version="1.0.0",
        description="Base module class",
    )

    def __init__(self, session_id: str = None):
        self.session_id = session_id

    def run(self, *args, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError("Modules must implement run()")

    def get_metadata(self) -> Dict:
        return {
            "name": self.metadata.name,
            "version": self.metadata.version,
            "description": self.metadata.description,
            "author": self.metadata.author,
            "risk_level": self.metadata.risk_level,
            "requires_adb": self.metadata.requires_adb,
            "category": self.metadata.category,
        }


class ModuleManager:
    def __init__(self):
        self.modules: Dict[str, BaseModule] = {}
        self._discover_modules()

    def _discover_modules(self):
        modules_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "modules")
        sys.path.insert(0, os.path.dirname(modules_dir))

        if not os.path.exists(modules_dir):
            os.makedirs(modules_dir, exist_ok=True)
            return

        for f in os.listdir(modules_dir):
            if f.endswith(".py") and not f.startswith("__"):
                module_name = f[:-3]
                try:
                    module_path = f"modules.{module_name}"
                    spec = importlib.util.spec_from_file_location(
                        module_path,
                        os.path.join(modules_dir, f)
                    )
                    if spec and spec.loader:
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)

                        for name, obj in inspect.getmembers(mod):
                            if (inspect.isclass(obj) and
                                issubclass(obj, BaseModule) and
                                obj != BaseModule):
                                instance = obj()
                                self.modules[instance.metadata.name] = instance
                                break
                except Exception as e:
                    print_status(f"Failed to load module {module_name}: {e}", "error")

    def list_modules(self) -> List[Dict]:
        return [m.get_metadata() for m in self.modules.values()]

    def get_module(self, name: str) -> Optional[BaseModule]:
        return self.modules.get(name)

    def get_module_names(self) -> List[str]:
        return list(self.modules.keys())

    def module_exists(self, name: str) -> bool:
        return name in self.modules
