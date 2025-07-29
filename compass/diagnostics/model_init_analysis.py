#!/usr/bin/env python3
"""
Parallel plotting of CESM nudged case vs MERRA2 using Dask + multiprocessing.
Targeted for NCAR Casper.

Author: [Your Name]
"""

import os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from functools import partial
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import xarray as xr
import numpy as np
from ..core.io import get_cam_ds


def plot_map(var, time, lev, h1a, merra_ds, image_dir, extent, coords, lev_unit):
    """Worker function: load slices, compute, and plot."""
    # Reopen datasets (must reopen in each process)
    #h1a = xr.open_dataset(h1a_path, chunks={})
    #merra = xr.open_dataset(merra_path, chunks={})

    #time = np.datetime64(time_str)

    target_sfc = h1a[f"Target_{var}"].sel(time=time, lev=lev, method='nearest').compute()
    merra_sfc = merra_ds[var].sel(time=time, lev=lev, method='nearest').compute()
    diff = target_sfc - merra_sfc

    # Output filename
    #lev_r = int(lev)
    #filename = f"{str(time).replace(':','_')}_{lev_r}hPa.png"
    
    time_part = time.strftime("%Y_%m_%d_%H:00")
    #lev_part = f"_lev{lev_idx}" if lev_idx is not None else "_nolev"
    lev_r = int(lev)
    filename = f"{time_part}_{lev_r}hPa.png"

    filepath = Path(image_dir) / var / filename
    if filepath.exists():
        print(f"Skipped (already exists): {filepath}")
        return
    filepath.parent.mkdir(parents=True, exist_ok=True)
    print(f"Saving: {filepath}")

    # === Plotting ===
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), subplot_kw={'projection': ccrs.PlateCarree()})
    shrink, pad = 0.625, 0.02
    vmin, vmax = 270, 300

    for ax, data, title, vmin_, vmax_ in zip(
        axes,
        [target_sfc, merra_sfc, diff],
        [
            f"CESM: Target_{var}\n{str(target_sfc['time'].values)} @ {lev_r} {lev_unit}",
            f"MERRA2: {var}\n{str(merra_sfc['time'].values)} @ {lev_r} {lev_unit}",
            f"CESM Target - MERRA2\n{var} @ {lev_r} {lev_unit}",
        ],
        [vmin, vmin, -10],
        [vmax, vmax, 10]
    ):
        pcm = data.plot.pcolormesh(
            ax=ax, transform=ccrs.PlateCarree(), cmap="coolwarm",
            vmin=vmin_, vmax=vmax_, add_colorbar=False, **coords
        )
        cbar = fig.colorbar(pcm, ax=ax, shrink=shrink, pad=pad)
        cbar.set_label(f"({data.attrs.get('units', '')})")
        ax.set_title(title)
        ax.set_extent(extent, crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.LAND, zorder=0)
        ax.add_feature(cfeature.COASTLINE)
        gl = ax.gridlines(draw_labels=True)
        gl.top_labels = False
        gl.right_labels = False
        box = Rectangle((130, -65), 30, 30, linewidth=2,
                        edgecolor='black', facecolor='none', transform=ccrs.PlateCarree())
        ax.add_patch(box)

    plt.tight_layout()
    fig.savefig(filepath, dpi=150)
    plt.close(fig)


def main():

    # === Input paths ===
    #case_name = "nudged-socrates-inithist-004-window"
    #run_path = Path(f"/glade/derecho/scratch/richling/{case_name}/run/")
    #h1a_path = run_path / "h1a.cam.h1.nc"  # adjust to actual file
    #merra_path = "/glade/work/richling/cesm-diagnostics/COMPASS/merra2_12012017-02282018_fixed.nc"

    init_casenl_name = "nudged-socrates-inithist-004-window"
    init_casenl_path = f"/glade/derecho/scratch/richling/{init_casenl_name}/user_nl_cam"
    init_cam_path = Path(f"/glade/derecho/scratch/richling/{init_casenl_name}/run/")
    h0a_init_ds, h1a_init_ds, h2i_init_ds = get_cam_ds(init_casenl_path, init_cam_path)

    # === Output settings ===
    image_base_dir = Path("plots/init_case_vs_merra")
    extent = [120, 175, -25, -75]
    var_names = ["T", "Q"]

    # === Pre-open datasets with Dask (for metadata)
    #h1a_ds = xr.open_dataset(h1a_path, chunks={"time": 1})
    merra_path = '/glade/work/richling/cesm-diagnostics/COMPASS/merra2_12012017-02282018_fixed.nc'
    merra_ds = xr.open_dataset(merra_path, chunks={})

    lev_unit = h0a_init_ds.lev.units
    coords = {}
    lat_name = next((dim for dim in h0a_init_ds.dims if 'lat' in dim.lower()), None)
    lon_name = next((dim for dim in h0a_init_ds.dims if 'lon' in dim.lower()), None)
    if lat_name and lon_name and h0a_init_ds[lat_name].ndim == 2:
        coords = {'x': h0a_init_ds[lon_name], 'y': h0a_init_ds[lat_name]}

    times = h0a_init_ds.time.values
    #h1a_init_ds['time'].values
    levs = h0a_init_ds.sel(lev=slice(700, 1000)).lev.values

    # === Build task list ===
    tasks = []
    for var in var_names:
        for time in times:
            for lev in levs:
                #time_str = str(np.datetime_as_string(time, unit='h'))
                tasks.append((var, time, float(lev), h1a_init_ds, merra_ds, str(image_base_dir), extent, coords, lev_unit))

    print(f"Prepared {len(tasks)} plot tasks...")

    # === Dispatch with multiprocessing ===
    with ProcessPoolExecutor() as executor:
        executor.map(lambda args: plot_map(*args), tasks)

    print("All done!")


if __name__ == "__main__":
    main()
