from ..core.io import get_cam_ds
import os
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib import patheffects

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.patches import Rectangle

def main():
    init_casenl_name = "nudged-socrates-inithist-004-window"
    init_casenl_path = f"/glade/derecho/scratch/richling/{init_casenl_name}/user_nl_cam"
    init_cam_path = Path(f"/glade/derecho/scratch/richling/{init_casenl_name}/run/")
    h0a_init_ds, h1a_init_ds, h2i_init_ds = get_cam_ds(init_casenl_path, init_cam_path)

    print(h0a_init_ds, h1a_init_ds, h2i_init_ds)

    case_name = "F2000climo.f09_f09_mg17.window.exp.24hrInit.R13.002" #exp_casenames[3]
    print(case_name)
    casenl_path = f"/glade/derecho/scratch/richling/cases/{case_name}/user_nl_cam"
    cam_path = f"/glade/derecho/scratch/richling/cases/{case_name}/run/"
    h0a_ds, h1a_ds, h2i_ds = get_cam_ds(casenl_path, cam_path)

    print(h0a_ds, h1a_ds, h2i_ds)


    # Loop over time and lev indices
    time_indices = range(len(h0a_ds['time'])) if 'time' in h0a_ds.dims else [None]
    lev_indices = range(len(h0a_ds['lev'])) if 'lev' in h0a_ds.dims else [None]

    #case_name = "nudged-socrates-inithist-002-window"  # Change this to your case
    #image_dir = Path(f"plots/{case_name}/MERRA_T_minus_T/")


    if 1==1:
        #lev_r = int(h2i_ds['lev'].values[-1])
        var_name = "T"
        var_names = ["T","Q"]
        var_names = ["Q"]
        shrink = 0.625
        pad = 0.02
        #time_idx = 5

        lev_unit = h0a_ds.lev.units
        extent = [120, 175, -25, -75]  # adjust as needed
        # Lat/lon detection
        lat_name = next((dim for dim in h2i_init_ds.dims if 'lat' in dim.lower()), None)
        lon_name = next((dim for dim in h2i_init_ds.dims if 'lon' in dim.lower()), None)
        lat_min, lat_max = -65, -35
        lon_min, lon_max = 130, 165

        minmax_dict = {763:[235,295],
                    820:[225,300],
                    976:[230,310]}

        def plot_map_multi_var_new(var_name, target_time, lev):

            image_dir = Path(f"plots/{case_name}_vs_init_case/{var_name}/")
            if not image_dir.is_dir():
                image_dir.mkdir(parents=True)
                    
            coords = {}
            if lat_name and lon_name and h2i_init_ds[lat_name].ndim == 2:
                coords['x'] = h2i_init_ds[lon_name]
                coords['y'] = h2i_init_ds[lat_name]


            h2i_init_ds_sfc = h2i_init_ds[var_name].sel(lev=lev,method='nearest').sel(time=target_time)
            h2i_ds_sfc = h2i_ds[var_name].sel(lev=lev,method='nearest').sel(time=target_time)
            h0a_ds_sfc = h0a_ds[var_name].sel(lev=lev,method='nearest').sel(time=target_time)
            #h1a_target_ds_sfc = h2i_ds.Target_T.sel(lev=lev,method='nearest').sel(time=target_time)
            #h1a_nudge_ds_sfc = h2i_ds.Nudge_T.sel(lev=lev,method='nearest').sel(time=target_time)
            #h0a_ds_sfc = h0a_ds.T.sel(lev=lev,method='nearest').sel(time=target_time)

            #time_part = f"{time_indices[time_idx]}" if time_idx is not None else "notime"
            time_part = target_time.strftime("%Y_%m_%d_%H:00")
            #lev_part = f"_lev{lev_idx}" if lev_idx is not None else "_nolev"
            lev_r = int(lev)
            filename = f"{time_part}_{lev_r}hPa.png"
            filepath = os.path.join(image_dir, filename)
            
            if not os.path.exists(filepath):
                print(f"Saved plot: {filepath}")
                do_it = True
            else:
                print(f"Skipped (already exists): {filepath}")
                do_it = False

            
            

            if do_it:
                #if merra_ds_sfc['time'].values != h1a_ds_sfc['time'].values:
                #    pass
                
                # === Plotting ===
                fig, axes = plt.subplots(1, 4, figsize=(15, 5), subplot_kw={'projection': ccrs.PlateCarree()})
            
                # Remove y-axis labels/ticks for all but first subplot
                #axes[1,0].set_ylabel("Latitude", labelpad=40)
                #axes[1,0].set_yticklabels([])
                #axes[1,0].set_yticks([])
            
                axes[0].set_ylabel("Latitude", labelpad=40)
                axes[0].set_yticklabels([])
                axes[0].set_yticks([])
            
                #h0a_ds.T.sel(lev=992,method='nearest').sel(time=target_time,method='nearest')

                #if lev_r in minmax_dict:
                if 2==1:
                    #min = minmax_dict[lev_r][0]
                    #max = minmax_dict[lev_r][-1]
            
                    c0cm = h2i_init_ds_sfc.plot.pcolormesh(
                        ax=axes[0],
                        transform=ccrs.PlateCarree(),
                        cmap="coolwarm",
                        #vmin=min,
                        #vmax=max,
                        #cbar_kwargs={'label': f"{var_name} ({h0a_ds.attrs.get('units', '')})"},
                        add_colorbar=False,  # We'll add manually
                        **coords
                    )
                    axes[0].set_title(f"CESM Init: {var_name} @ {str(h2i_init_ds_sfc['time'].values)}\nlev={lev_r} {lev_unit}")
                    cbar = axes[0].figure.colorbar(c0cm, ax=axes[0], orientation='vertical', shrink=shrink, pad=pad)
                    cbar.set_label(f"({h2i_init_ds.T.attrs.get('units', '')})")
        
                    mcm = h2i_ds_sfc.plot.pcolormesh(
                        ax=axes[1],
                        transform=ccrs.PlateCarree(),
                        cmap="coolwarm",
                        #vmin=min,
                        #vmax=max,
                        #cbar_kwargs={'label': f"{var_name} ({merra_ds.attrs.get('units', '')})"},
                        add_colorbar=False,  # We'll add manually
                        **coords
                    )
                    axes[1].set_title(f"CESM: {var_name} @ {str(time_part)}\nlev={lev_r} {lev_unit}")
                    # Custom colorbar matching height of axes
                    cbar = axes[1].figure.colorbar(mcm, ax=axes[1], orientation='vertical', shrink=shrink, pad=pad)
                else:
                    if var_name == "T":
                        min = 220
                        max = 310
                    if var_name == "Q":
                        min = 0
                        max = 0.018
                    c0cm = h2i_init_ds_sfc.plot.pcolormesh(
                        ax=axes[0],
                        transform=ccrs.PlateCarree(),
                        cmap="coolwarm",
                        vmin=min,
                        vmax=max,
                        #cbar_kwargs={'label': f"{var_name} ({h0a_ds.attrs.get('units', '')})"},
                        add_colorbar=False,  # We'll add manually
                        **coords
                    )
                    axes[0].set_title(f"CESM Init: {var_name} @ {str(h2i_init_ds_sfc['time'].values)}\nlev={lev_r} {lev_unit}")
                    cbar = axes[0].figure.colorbar(c0cm, ax=axes[0], orientation='vertical', shrink=shrink, pad=pad)
                    cbar.set_label(f"({h2i_init_ds.T.attrs.get('units', '')})")
            
                    mcm = h2i_ds_sfc.plot.pcolormesh(
                        ax=axes[1],
                        transform=ccrs.PlateCarree(),
                        cmap="coolwarm",
                        vmin=min,
                        vmax=max,
                        #cbar_kwargs={'label': f"{var_name} ({merra_ds.attrs.get('units', '')})"},
                        add_colorbar=False,  # We'll add manually
                        **coords
                    )
                    axes[1].set_title(f"CESM: {var_name} @ {str(time_part)}\nlev={lev_r} {lev_unit}")
                    # Custom colorbar matching height of axes
                    cbar = axes[1].figure.colorbar(mcm, ax=axes[1], orientation='vertical', shrink=shrink, pad=pad)

                    subset = h0a_ds_sfc.plot.pcolormesh(
                        ax=axes[3],
                        transform=ccrs.PlateCarree(),
                        cmap="coolwarm",
                        vmin=min,
                        vmax=max,
                        #cbar_kwargs={'label': f"{var_name} ({merra_ds.attrs.get('units', '')})"},
                        add_colorbar=False,  # We'll add manually
                        **coords
                    )
                    axes[3].set_title(f"CESM Subset: {var_name} @ {str(time_part)}\nlev={lev_r} {lev_unit}")
                    # Custom colorbar matching height of axes
                    cbar = axes[3].figure.colorbar(subset, ax=axes[3], orientation='vertical', shrink=shrink, pad=pad)
                
                cbar.set_label(f"({h0a_ds.T.attrs.get('units', '')})")

                diff = h2i_init_ds_sfc - h2i_ds_sfc
                c0cm_target = diff.plot.pcolormesh(
                    ax=axes[2],
                    transform=ccrs.PlateCarree(),
                    cmap="coolwarm",
                    vmin=-10,
                    vmax=10,
                    #cbar_kwargs={'label': f"{var_name} ({merra_ds.attrs.get('units', '')})"},
                    add_colorbar=False,  # We'll add manually
                    **coords
                )
                axes[2].set_title(f"CESM Init minus CESM - {var_name} @ {str(time_part)}\nlev={lev_r} {lev_unit}")
                # Custom colorbar matching height of axes
                cbar = axes[2].figure.colorbar(c0cm_target, ax=axes[2], orientation='vertical', shrink=shrink, pad=pad)
                cbar.set_label(f"({h2i_ds.T.attrs.get('units', '')})")

                # Flatten the 2D array of axes for easy iteration
                #for ax in axes.flat:
                for ax in axes:
                    ax.set_extent(extent, crs=ccrs.PlateCarree())
                    ax.add_feature(cfeature.LAND, zorder=0)
                    ax.add_feature(cfeature.COASTLINE)
                    gl = ax.gridlines(draw_labels=True)
                    gl.right_labels = False
                    gl.top_labels = False
                    # 147e_to_161e_42s_to_58s
                    nudge_lon_min = 130 #h0a_ds_sfc.lon.min().values
                    nudge_lon_max = 160 #h0a_ds_sfc.lon.max().values
                    nudge_lat_max = -35 #h0a_ds_sfc.lat.max().values
                    nudge_lat_min = -65 #h0a_ds_sfc.lat.min().values
                    #h0a_ds_sfc.lon.max().values,h0a_ds_sfc.lon.min().values
                    #h0a_ds_sfc.lat.max().values,h0a_ds_sfc.lat.min().values
                    # Create a rectangle (the box)
                    box = Rectangle((nudge_lon_min, nudge_lat_min),  # lower-left corner
                                    nudge_lon_max - nudge_lon_min,   # width
                                    nudge_lat_max - nudge_lat_min,   # height
                                    linewidth=2,
                                    edgecolor='black',
                                    facecolor='none',
                                    transform=ccrs.PlateCarree())  # Important: use map projection
                    
                    # Add the box to the map
                    ax.add_patch(box)
            
                plt.tight_layout()
                fig.savefig(filepath, dpi=150)
                #plt.show()
                
                # Filename

                #time_part = f"{time_indices[time_idx]}" if time_idx is not None else "notime"
                time_part = target_time.strftime("%Y_%m_%d_%H:00")
                #lev_part = f"_lev{lev_idx}" if lev_idx is not None else "_nolev"
                filename = f"{time_part}_{lev_r}hPa.png"
                filepath = os.path.join(image_dir, filename)
            
                if not os.path.exists(filepath):
                    fig.savefig(filepath, dpi=150)
                    print(f"Saved plot: {filepath}")
                else:
                    print(f"Skipped (already exists): {filepath}")
                
                plt.close(fig)
        


    for time in h2i_ds['time'].values:
        for lev in h2i_ds.sel(lev=slice(700,1000))['lev'].values:
            for var in var_names:
                plot_map_multi_var_new(var, time, lev=lev)
        #for lev_idx in lev_indices:
            #plot_map_multi_var(my_vars, time_idx, -1)
    print("All Done!")

if __name__ == "__main__":
    main()