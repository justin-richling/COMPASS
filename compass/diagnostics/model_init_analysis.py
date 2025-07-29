from ..core.io import get_cam_ds
import os
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib import patheffects
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.patches import Rectangle
import xarray as xr
from multiprocessing import Pool

def has_time(da, time_val):
    return any(t == time_val for t in da['time'].values)

def plot_map_multi_var_new(
    var_name,
    target_time,
    image_dir,
    lev,
    h1a_init_ds,
    merra_ds,
    extent,
    lev_unit,
    lat_name,
    lon_name
):
    coords = {}
    if lat_name and lon_name and h1a_init_ds[lat_name].ndim == 2:
        coords['x'] = h1a_init_ds[lon_name]
        coords['y'] = h1a_init_ds[lat_name]

    if not all([
        has_time(merra_ds, target_time),
        has_time(h1a_init_ds, target_time),
    ]):
        print("NO TIMES EH")
        return

    merra_ds_sfc = merra_ds[var_name].sel(lev=lev, method='nearest').sel(time=target_time)
    h1a_target_ds_sfc = h1a_init_ds[f"Target_{var_name}"].sel(lev=lev, method='nearest').sel(time=target_time)

    time_part = target_time.strftime("%Y_%m_%d_%H:00")
    lev_r = int(lev)
    filename = f"{time_part}_{lev_r}hPa.png"

    if not Path(image_dir).is_dir():
        Path(image_dir).mkdir(parents=True)

    filepath = os.path.join(image_dir, filename)
    print("MODEL FILENAME:", filepath)
    if not Path(filepath).is_file():
        print(f"Saved plot: {filepath}")
        do_it = True
    else:
        print(f"Skipped (already exists): {filepath}")
        do_it = False
    print()

    if not do_it:
        return

    shrink = 0.625
    pad = 0.02

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), subplot_kw={'projection': ccrs.PlateCarree()})

    axes[0].set_ylabel("Latitude", labelpad=40)
    axes[0].set_yticklabels([])
    axes[0].set_yticks([])

    c0cm = h1a_target_ds_sfc.plot.pcolormesh(
        ax=axes[0],
        transform=ccrs.PlateCarree(),
        cmap="coolwarm",
        vmin=270,
        vmax=300,
        add_colorbar=False,
        **coords
    )
    axes[0].set_title(f"CESM: Target_{var_name} @ {str(h1a_target_ds_sfc['time'].values)}\nlev={lev_r} {lev_unit}")
    cbar = axes[0].figure.colorbar(c0cm, ax=axes[0], orientation='vertical', shrink=shrink, pad=pad)
    cbar.set_label(f"({h1a_init_ds[var_name].attrs.get('units', '')})")

    mcm = merra_ds_sfc.plot.pcolormesh(
        ax=axes[1],
        transform=ccrs.PlateCarree(),
        cmap="coolwarm",
        vmin=270,
        vmax=300,
        add_colorbar=False,
        **coords
    )
    axes[1].set_title(f"MERRA2: {var_name} @ {str(merra_ds_sfc['time'].values)}\nlev={lev_r} {lev_unit}")
    cbar = axes[1].figure.colorbar(mcm, ax=axes[1], orientation='vertical', shrink=shrink, pad=pad)
    cbar.set_label(f"({merra_ds[var_name].attrs.get('units', '')})")

    diff = h1a_target_ds_sfc - merra_ds_sfc
    c0cm_target = diff.plot.pcolormesh(
        ax=axes[2],
        transform=ccrs.PlateCarree(),
        cmap="coolwarm",
        vmin=-10,
        vmax=10,
        add_colorbar=False,
        **coords
    )
    axes[2].set_title(f"CESM Target_{var_name} minus MERRA2 {var_name}\nlev={lev_r} {lev_unit}")
    cbar = axes[2].figure.colorbar(c0cm_target, ax=axes[2], orientation='vertical', shrink=shrink, pad=pad)
    cbar.set_label(f"({h1a_target_ds_sfc.attrs.get('units', '')})")

    for ax in axes:
        ax.set_extent(extent, crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.LAND, zorder=0)
        ax.add_feature(cfeature.COASTLINE)
        gl = ax.gridlines(draw_labels=True)
        gl.right_labels = False
        gl.top_labels = False

        nudge_lon_min = 130
        nudge_lon_max = 160
        nudge_lat_max = -35
        nudge_lat_min = -65
        box = Rectangle(
            (nudge_lon_min, nudge_lat_min),
            nudge_lon_max - nudge_lon_min,
            nudge_lat_max - nudge_lat_min,
            linewidth=2,
            edgecolor='black',
            facecolor='none',
            transform=ccrs.PlateCarree()
        )
        ax.add_patch(box)

    plt.tight_layout()
    fig.savefig(filepath, dpi=150)
    plt.close(fig)

def main():
    init_casenl_name = "nudged-socrates-inithist-004-window"
    init_casenl_path = f"/glade/derecho/scratch/richling/{init_casenl_name}/user_nl_cam"
    init_cam_path = Path(f"/glade/derecho/scratch/richling/{init_casenl_name}/run/")
    h0a_init_ds, h1a_init_ds, h2i_init_ds = get_cam_ds(init_casenl_path, init_cam_path)
    merra_ds = xr.open_dataset('/glade/work/richling/cesm-diagnostics/COMPASS/merra2_12012017-02282018_fixed.nc')

    var_names = ["T", "Q"]
    lev_unit = h0a_init_ds.lev.units
    extent = [120, 175, -25, -75]

    lat_name = next((dim for dim in h2i_init_ds.dims if 'lat' in dim.lower()), None)
    lon_name = next((dim for dim in h2i_init_ds.dims if 'lon' in dim.lower()), None)

    # Prepare tasks for multiprocessing
    tasks = []
    for time in h1a_init_ds['time'].values:
        for lev in h1a_init_ds.sel(lev=slice(700,1000))['lev'].values:
            for var in var_names:
                image_dir = Path(f"plots/init_case_vs_merra/{var}/")
                if not image_dir.is_dir():
                    image_dir.mkdir(parents=True)
                tasks.append((
                    var,
                    time,
                    image_dir,
                    lev,
                    h1a_init_ds,
                    merra_ds,
                    extent,
                    lev_unit,
                    lat_name,
                    lon_name
                ))

    # --- Multiprocessing ---
    # Uncomment below to use multiprocessing for plotting
    with Pool() as pool:
         pool.starmap(plot_map_multi_var_new, tasks)

    # --- Serial version ---
    #for args in tasks:
    #    plot_map_multi_var_new(*args)

    print("All Done!")

if __name__ == "__main__":
    main()