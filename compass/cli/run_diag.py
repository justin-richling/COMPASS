# cli/run_diag.py

"""import sys
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
    main(sys.argv[1])"""

# cli/run_diag.py

import sys
import matplotlib.pyplot as plt
from compass.core.colormap_loader import register_colormaps


def main():
    #register_colormaps()

    #from compass.diagnostics import satellite_plot
    #satellite_plot.main()

    from compass.diagnostics import model_init_analysis
    model_init_analysis.main()

    # If no config passed, just print registered colormaps and exit
    if len(sys.argv) < 2:
        print("No config file provided")
        #print(plt.colormaps())
        import subprocess
        subprocess.run(["jupyter", "notebook"])
        return

    config_path = sys.argv[1]
    print(f"Config path provided: {config_path}")
    # Here you would load and run diagnostics with your config
    # For now just print a placeholder
    print("Would load config and run diagnostics here.")

if __name__ == "__main__":
    main()

