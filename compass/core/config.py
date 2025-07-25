# core/config.py

import yaml
from pathlib import Path

class Config:
    def __init__(self, config_path):
        self.config_path = Path(config_path)
        self.raw = self._load_yaml()
        self._validate()

    def _load_yaml(self):
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def _validate(self):
        if "datasets" not in self.raw:
            raise ValueError("Missing required section: datasets")

        if "diagnostics" not in self.raw:
            raise ValueError("Missing required section: diagnostics")

        # Set defaults if not defined
        self.raw.setdefault("plotting", {})
        self.raw["plotting"].setdefault("dpi", 150)
        self.raw["plotting"].setdefault("savefig", True)

    def get_dataset(self, kind):
        return self.raw["datasets"].get(kind)

    def get_diagnostics(self):
        return self.raw["diagnostics"]

    def get_plot_config(self):
        return self.raw["plotting"]

    def get(self, key, default=None):
        return self.raw.get(key, default)
