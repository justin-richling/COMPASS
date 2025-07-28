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


