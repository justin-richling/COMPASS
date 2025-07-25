from .core.colormap_loader import register_colormaps

register_colormaps()

import matplotlib.pyplot as plt

print(plt.colormaps())