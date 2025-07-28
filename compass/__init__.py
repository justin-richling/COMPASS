from .core.colormap_loader import register_colormaps

register_colormaps()

"""import matplotlib.pyplot as plt
import matplotlib as mpl

print(plt.colormaps())

fig = plt.figure(figsize=(8, 3))
ax1 = fig.add_axes([0.05, 0.80, 0.9, 0.15])
mpl.colorbar.ColorbarBase(ax1, cmap="viirs_ir_default",
                                    orientation='horizontal')
plt.show()
"""

# mypackage/__init__.py

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
import importlib.resources as pkg_resources  # For loading files inside packages

# Example using pre-saved .npy arrays
from . import colormaps  # your subpackage or folder with .npy files

def register_custom_colormaps():
    for name in colormaps.list_available():  # Custom function you write
        data = colormaps.load_colormap(name)  # Loads the .npy file as array
        cmap = ListedColormap(data, name=name)
        plt.register_cmap(name=name, cmap=cmap)

register_custom_colormaps()

