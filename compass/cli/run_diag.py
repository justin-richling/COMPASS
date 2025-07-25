# cli/run_diag.py

import sys
import importlib
from compass.core.config import Config

def main(config_path):
    cfg = Config(config_path)
    diagnostics = cfg.get_diagnostics()

    for diag in diagnostics:
        name = diag["name"]
        print(f"Running diagnostic: {name}")
        try:
            # Dynamically import: climdiag.diagnostics.amv_index
            module = importlib.import_module(f"climdiag.diagnostics.{name}")
            # Convention: each diagnostic has a `run()` function
            module.run(cfg, diag)
        except Exception as e:
            print(f"Error running {name}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m climdiag.cli.run_diag <config.yaml>")
        sys.exit(1)
    main(sys.argv[1])
