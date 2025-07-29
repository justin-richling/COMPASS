from ..core.io import get_cam_ds
import os
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib import patheffects

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.patches import Rectangle
import xarray as xr
from concurrent.futures import ProcessPoolExecutor, as_completed
import dask
import numpy as np
import multiprocessing


def main():

    def has_time(da, time_val):
        return any(t == time_val for t in da['time'].values)

    init_casenl_name = "nudged-socrates-inithist-004-window"
    init_casenl_path = f"/glade/derecho/scratch/richling/{init_casenl_name}/user_nl_cam"
    init_cam_path = Path(f"/glade/derecho/scratch/richling/{init_casenl_name}/run/")
    h0a_init_ds, h1a_init_ds, h2i_init_ds = get_cam_ds(init_casenl_path, init_cam_path)
    merra_ds = xr.open_dataset('/glade/work/richling/cesm-diagnostics/COMPASS/merra2_12012017-02282018_fixed.nc')

    time_values = h1a_init_ds['time'].values
    lev_values = h1a_init_ds.sel(lev=slice(700, 1000))['lev'].values
    var_names = ["T", "Q"]
    extent = [120, 175, -25, -75]
    shrink = 0.625
    pad = 0.02
    lat_name = next((dim for dim in h2i_init_ds.dims if 'lat' in dim.lower()), None)
    lon_name = next((dim for dim in h2i_init_ds.dims if 'lon' in dim.lower()), None)
    lev_unit = h0a_init_ds.lev.units

    def plot_map_task(var_name, time_val, lev_val):
        image_dir = Path(f"plots/init_case_vs_merra/{var_name}/")
        image_dir.mkdir(parents=True, exist_ok=True)

        time_part = np.datetime_as_string(time_val, unit='h').replace("T", "_").replace(":", "_")
        lev_r = int(lev_val)
        filename = f"{time_part}_{lev_r}hPa.png"
        filepath = image_dir / filename

        if filepath.exists():
            return f"Skipped (already exists): {filepath}"

        if not all([
            has_time(merra_ds, time_val),
            has_time(h1a_init_ds, time_val),
        ]):
            return f"Missing time: {time_val}"

        coords = {}
        if lat_name and lon_name and h2i_init_ds[lat_name].ndim == 2:
            coords['x'] = h2i_init_ds[lon_name]
            coords['y'] = h2i_init_ds[lat_name]

        merra_ds_sfc = merra_ds[var_name].sel(lev=lev_val, method='nearest').sel(time=time_val)
        h1a_target_ds_sfc = h1a_init_ds[f"Target_{var_name}"].sel(lev=lev_val, method='nearest').sel(time=time_val)
        diff = h1a_target_ds_sfc - merra_ds_sfc

        fig, axes = plt.subplots(1, 3, figsize=(15, 5), subplot_kw={'projection': ccrs.PlateCarree()})

        for ax in axes:
            ax.set_extent(extent, crs=ccrs.PlateCarree())
            ax.add_feature(cfeature.LAND, zorder=0)
            ax.add_feature(cfeature.COASTLINE)
            gl = ax.gridlines(draw_labels=True)
            gl.right_labels = False
            gl.top_labels = False
            box = Rectangle((130, -65), 30, 30, linewidth=2, edgecolor='black', facecolor='none', transform=ccrs.PlateCarree())
            ax.add_patch(box)

        im0 = h1a_target_ds_sfc.plot.pcolormesh(ax=axes[0], transform=ccrs.PlateCarree(), cmap="coolwarm", vmin=270, vmax=300, add_colorbar=False, **coords)
        axes[0].set_title(f"CESM: Target_{var_name} @ {str(time_val)}\nlev={lev_r} {lev_unit}")
        fig.colorbar(im0, ax=axes[0], orientation='vertical', shrink=shrink, pad=pad).set_label(f"({h1a_init_ds[var_name].attrs.get('units', '')})")

        im1 = merra_ds_sfc.plot.pcolormesh(ax=axes[1], transform=ccrs.PlateCarree(), cmap="coolwarm", vmin=270, vmax=300, add_colorbar=False, **coords)
        axes[1].set_title(f"MERRA2: {var_name} @ {str(time_val)}\nlev={lev_r} {lev_unit}")
        fig.colorbar(im1, ax=axes[1], orientation='vertical', shrink=shrink, pad=pad).set_label(f"({merra_ds[var_name].attrs.get('units', '')})")

        im2 = diff.plot.pcolormesh(ax=axes[2], transform=ccrs.PlateCarree(), cmap="coolwarm", vmin=-10, vmax=10, add_colorbar=False, **coords)
        axes[2].set_title(f"CESM Target_{var_name} minus MERRA2 {var_name}\nlev={lev_r} {lev_unit}")
        fig.colorbar(im2, ax=axes[2], orientation='vertical', shrink=shrink, pad=pad).set_label(f"({h1a_target_ds_sfc.attrs.get('units', '')})")

        plt.tight_layout()
        fig.savefig(filepath, dpi=150)
        plt.close(fig)

        return f"Saved plot: {filepath}"

    task_list = []
    for time in time_values:
        for lev in lev_values:
            for var in var_names:
                task_list.append((var, time, lev))

    num_workers = min(multiprocessing.cpu_count(), 8)  # Tune for Casper
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(plot_map_task, *task) for task in task_list]
        for future in as_completed(futures):
            result = future.result()
            print(result)

    print("All Done!")

if __name__ == "__main__":
    main()
