import os
from typing import Any
from .dataset import RawDataset, ProcDataset, StepDataset, StepItem, MaskItem


class Project:
    """TODO: config file"""
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self._scan()

    def _scan(self):
        self.dataclass = {}
        for d in os.listdir(self.path):
            """hard coded"""
            if d == "data":
                try:
                    self.dataclass[d] = RawDataset(os.path.join(self.path, d))
                except:
                    # no rawdata
                    self.dataclass[d] = None
            elif d == "proc":
                self.dataclass[d] = ProcDataset(os.path.join(self.path, d))
            elif d == "mask":
                self.dataclass[d] = ProcDataset(os.path.join(self.path, d), mask=True)
            elif d == "rst":
                pass

    def get_path(self, dataclass: str) -> str:
        return os.path.join(self.path, dataclass)

    def _init_step(self, id: str, name: str, annotation: str) -> str:
        info = StepItem(id, name, annotation, None)
        step_path = os.path.join(self.get_path('proc'), info.path)
        os.makedirs(step_path, exist_ok=True)
        return step_path
    
    def _init_mask(self, info: MaskItem):
        pass

    def reload(self):
        self._scan()
    
    def __getatt__(self, name: str) -> Any:
        if name in self.dataclass.keys():
            return self.dataclass[name]
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __repr__(self):
        repr = []
        for d, ds in self.dataclass.items():
            repr.append(f"{d}: {str(ds)}")
        return "\n".join(repr)