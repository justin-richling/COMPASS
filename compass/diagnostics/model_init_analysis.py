#!/usr/bin/env python3
"""
Compare CESM nudged output to MERRA2 reanalysis at select levels and times.
Generates side-by-side plots of temperature and humidity fields.

Author: [Your Name or NCAR group]
"""

from pathlib import Path
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import xarray as xr

from ..core.io import get_cam_ds


def has_time(da, time_val):
    """Check if a specific time value exists in the dataset."""
    return any(t == time_val for t in da['time'].values)


def plot_map(var_name, target_time, lev, h1a_ds, merra_ds, image_dir, coords, extent, lev_unit, vmin=270, vmax=300):
    """Plot CESM target, MERRA2, and their difference."""
    time_str = target_time.strftime("%Y_%m_%d_%H:00")
    lev_r = int(lev)
    filename = f"{time_str}_{lev_r}hPa.png"
    filepath = image_dir / filename
    print("MODEL FILENAME:", filepath)

    if filepath.is_file():
        print(f"Skipped (already exists): {filepath}\n")
        return

    print(f"Saved plot: {filepath}\n")

    # Data selection
    merra_sfc = merra_ds[var_name].sel(lev=lev, method='nearest').sel(time=target_time)
    target_sfc = h1a_ds[f"Target_{var_name}"].sel(lev=lev, method='nearest').sel(time=target_time)
    diff = target_sfc - merra_sfc

    # === Plotting ===
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), subplot_kw={'projection': ccrs.PlateCarree()})
    shrink, pad = 0.625, 0.02

    titles = [
        f"CESM: Target_{var_name} @ {str(target_sfc['time'].values)}\nlev={lev_r} {lev_unit}",
        f"MERRA2: {var_name} @ {str(merra_sfc['time'].values)}\nlev={lev_r} {lev_unit}",
        f"CESM Target_{var_name} minus MERRA2 {var_name}\nlev={lev_r} {lev_unit}",
    ]
    datasets = [target_sfc, merra_sfc, diff]
    cmaps = ["coolwarm"] * 3
    vmaps = [(vmin, vmax), (vmin, vmax), (-10, 10)]

    for ax, title, data, cmap, (vmin_, vmax_) in zip(axes, titles, datasets, cmaps, vmaps):
        pcm = data.plot.pcolormesh(
            ax=ax, transform=ccrs.PlateCarree(), cmap=cmap,
            vmin=vmin_, vmax=vmax_, add_colorbar=False, **coords
        )
        ax.set_title(title)
        cbar = fig.colorbar(pcm, ax=ax, orientation='vertical', shrink=shrink, pad=pad)
        cbar.set_label(f"({data.attrs.get('units', '')})")

        ax.set_extent(extent, crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.LAND, zorder=0)
        ax.add_feature(cfeature.COASTLINE)
        gl = ax.gridlines(draw_labels=True)
        gl.right_labels = False
        gl.top_labels = False

        # Nudge region box
        box = Rectangle((130, -65), 30, 30, linewidth=2,
                        edgecolor='black', facecolor='none', transform=ccrs.PlateCarree())
        ax.add_patch(box)

    plt.tight_layout()
    fig.savefig(filepath, dpi=150)
    plt.close(fig)


def main():
    # Paths
    case_name = "nudged-socrates-inithist-004-window"
    casenl_path = f"/glade/derecho/scratch/richling/{case_name}/user_nl_cam"
    run_path = Path(f"/glade/derecho/scratch/richling/{case_name}/run/")
    merra_path = "/glade/work/richling/cesm-diagnostics/COMPASS/merra2_12012017-02282018_fixed.nc"

    # Load datasets
    h0a, h1a, h2i = get_cam_ds(casenl_path, run_path)
    merra = xr.open_dataset(merra_path)

    var_names = ["T", "Q"]
    extent = [120, 175, -25, -75]
    lev_unit = h0a.lev.units

    # Handle 2D lat/lon coordinates if necessary
    lat_name = next((dim for dim in h2i.dims if 'lat' in dim.lower()), None)
    lon_name = next((dim for dim in h2i.dims if 'lon' in dim.lower()), None)
    coords = {}
    if lat_name and lon_name and h2i[lat_name].ndim == 2:
        coords['x'] = h2i[lon_name]
        coords['y'] = h2i[lat_name]

    for time in h1a['time'].values:
        for lev in h1a.sel(lev=slice(700, 1000))['lev'].values:
            if not all(has_time(ds, time) for ds in [h1a, merra]):
                print(f"Time {time} not found in all datasets. Skipping.")
                continue

            for var in var_names:
                image_dir = Path(f"plots/init_case_vs_merra/{var}/")
                image_dir.mkdir(parents=True, exist_ok=True)
                plot_map(var, time, lev, h1a, merra, image_dir, coords, extent, lev_unit)

    print("All Done!")


if __name__ == "__main__":
    main()
