from satpy import Scene, find_files_and_readers
from satpy.resample import get_area_def
from satpy.writers import get_enhanced_image
from satpy import Scene
#from satpy.multiscene import MultiScene

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import matplotlib.ticker as mticker
import matplotlib.patheffects as patheffects

import cartopy.crs as ccrs
import cartopy.feature as cfeature

def main():

    def test_image(prod,file_list,im_save_path):
        print(prod)
        scn = Scene(reader='ahi_hsd', filenames=files)
        if prod == "B13":
            print("AHHHH")
            scn.load(["B13"], calibration="brightness_temperature")
        elif prod == "B03":
            scn.load(['B03'], calibration='radiance')  # Load in radiance units
        else:
            scn.load([prod])
        #print(scn)
        #scn = scn.resample( resampler='native') #scn.min_area(),

        scn = scn.resample(resampler='native')
        #scn = scn.resample(scn.min_area(), resampler='native')
        #scn.save_dataset('true_color', filename='true_color'+'.png')

        fig = plt.figure(figsize=(15, 10), dpi=300)
        if prod == "true_color":
            var = get_enhanced_image(scn[prod]).data
            var = var.transpose('y', 'x', 'bands')
            abi_crs = var.attrs['area'].to_cartopy_crs()
        elif prod == "B03":
            #scn = Scene(filenames=files, reader='ahi_hsd')
            #scn.load(['B03'], calibration='radiance')  # Load in radiance units
            var = data = scn['B03']#.data
            abi_crs = var.attrs['area'].to_cartopy_crs()
            
            data = scn['B03'].values
            
            # Scale based on known radiance range for B03 (approximate)
            min_radiance = 0.0
            max_radiance = 100.0  # Adjust based on data range you observe
            var = (255 * np.clip((data - min_radiance) / (max_radiance - min_radiance), 0, 1)).astype(np.uint8)
        else:
            var = scn[prod]#.data
            abi_crs = var.attrs['area'].to_cartopy_crs()

        # Get true color data to use later and reorder the dimensions so matplotlib can use the image
        # Sadly, this operation is not lazy (bad performance) in xarray at the time of writing
        #var = var.transpose('y', 'x', 'bands')
        

        # Add the map and set the extent
        #ax = plt.subplot(111, projection=abi_crs)
        ax = plt.subplot(111, projection=ccrs.PlateCarree())
        #extent = [-130., -65, 20., 60.]
        #extent = [-130., -65, 20., 75.]
        #134e:148e_41s:51s
        extent = [120., 180, -30., -70.]

        ax.set_extent(extent,ccrs.PlateCarree())
        ax.add_feature(cfeature.COASTLINE.with_scale('10m'), edgecolor='w',linewidth=0.2)
        ax.add_feature(cfeature.STATES.with_scale('10m'), edgecolor='w',linewidth=0.2)

        # Define the outline effect
        outline_effect = [patheffects.withStroke(linewidth=1, foreground='black')]
        latlon_outline_effect = [patheffects.withStroke(linewidth=1, foreground='black')]
        
        # Add latitude/longitude gridlines
        # Gridlines
        gl = ax.gridlines(draw_labels=False, linewidth=1, color='gray', alpha=0.5, linestyle='--')
        
        # Set your tick positions
        xticks = np.arange(125, 176, 5)
        yticks = [-35, -40, -45, -50, -55, -60, -65]
        
        # Set the ticks at those positions using PlateCarree projection
        ax.set_xticks(xticks, crs=ccrs.PlateCarree())
        ax.set_yticks(yticks, crs=ccrs.PlateCarree())
        
        # Format tick labels (longitude and latitude)
        lon_formatter = mticker.FuncFormatter(lambda x, _: f"{int(x)}°E")
        lat_formatter = mticker.FuncFormatter(lambda y, _: f"{int(abs(y))}°S" if y < 0 else f"{int(y)}°N")
        ax.xaxis.set_major_formatter(lon_formatter)
        ax.yaxis.set_major_formatter(lat_formatter)
        
        # Turn on ticks on top and right; off on bottom and left
        ax.tick_params(axis='x', bottom=False, top=True, labelbottom=False, labeltop=True,
                    direction='in', pad=-15, labelsize=6, colors='white')
        ax.tick_params(axis='y', left=True, right=False, labelleft=True, labelright=False,
                    direction='in', pad=-25, labelsize=6, colors='white')
        
        # Optional: Apply path effects (outline) to tick labels
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_path_effects(latlon_outline_effect)


        """
        im = ax.imshow(var,
                transform=abi_crs,
                #cmap=cmap,
                    #vmin=vmin,
                    #vmax=vmax,
                            extent=(var.x[0], var.x[-1], var.y[-1], var.y[0]),origin='upper')
        """
        print("var dims:", var.dims)
        print("var shape:", var.shape)
        print("var.x coords:", var.x.values)
        print("var.y coords:", var.y.values)

        extent = (float(var.x.min()), float(var.x.max()), float(var.y.min()), float(var.y.max()))
        print("Extent:", extent)

        data = var.values
        print("data shape:", data.shape)

        if prod == "B13":
            cmap = "nesdis_ir" #IR_cmap
            vmin=158
            vmax=330
            im = ax.imshow(var,
                transform=abi_crs,
                cmap=cmap,
                    vmin=vmin,
                    vmax=vmax,
                            extent=(var.x[0], var.x[-1], var.y[-1], var.y[0]),origin='upper')
        elif prod == "B03":
            cmap = "Greys"
            vmin=0
            vmax=255
            im = ax.imshow(var,
                transform=abi_crs,
                cmap=cmap,
                    vmin=vmin,
                    vmax=vmax,
                            extent=(scn[prod].x[0], scn[prod].x[-1], scn[prod].y[-1], scn[prod].y[0]),origin='upper')
        else:
            im = ax.imshow(var,
                transform=abi_crs,
                            extent=(var.x[0], var.x[-1], var.y[-1], var.y[0]),origin='upper')

        ax.set_aspect(1.5)
        #plt.colorbar(orientation="horizontal", label="Brightness Temperature (K)")

        if prod != "true_color":
            # Get axis position
            pos = ax.get_position()
            
            # Custom colorbar position
            cbar_width = 0.01
            cbar_height = 0.7 * pos.height
            cbar_x = pos.x1 - 0.01
            cbar_y = pos.y0 + (pos.height - cbar_height) / 2
            
            cbar_ax = fig.add_axes([cbar_x, cbar_y, cbar_width, cbar_height])
            
            cbar = fig.colorbar(im, cax=cbar_ax)

            # Set custom tick positions
            custom_ticks = list(np.arange(165, 325 + 1, 10))+[330]
            cbar.set_ticks(custom_ticks)
            
            # Optional: Custom tick labels (e.g., rounded or annotated)
            custom_labels = [f"{int(t)}" for t in custom_ticks]
            cbar.set_ticklabels(custom_labels)
            
            # Style tick labels
            cbar.ax.tick_params(labelsize=6)
            cbar.ax.yaxis.set_ticks_position('left')
            cbar.ax.yaxis.set_label_position('left')
            
            # Apply outline effect to tick labels
            for label in cbar.ax.get_yticklabels():
                label.set_color('white')
                label.set_path_effects(outline_effect)

            
            """
            cbar = fig.colorbar(im, cax=cbar_ax)
            
            # Change tick label font size
            cbar.ax.tick_params(labelsize=6)
            
            # Move ticks and labels to the left
            cbar.ax.yaxis.set_ticks_position('left')
            cbar.ax.yaxis.set_label_position('left')
        
            # Apply to each tick label (Y-axis in this case)
            for label in cbar.ax.get_yticklabels():
                label.set_color('white')
                label.set_path_effects(outline_effect)
            """

        text_prod = ax.text(.005, 0.01, 
                "{0:%d-%B-%Y %H%MZ}".format(scn[prod].start_time),
                horizontalalignment='left', transform=ax.transAxes,
                color='white', fontsize=7, weight='bold',
                        )
        text_time = ax.text(.995, 0.01, 
                f'{scn[prod].attrs["platform_name"]} {scn[prod].attrs["sensor"]} {prod.replace("_"," ")}',
                horizontalalignment='right', transform=ax.transAxes,
                color='white', fontsize=7, weight='bold',
                        )
        
        text_time.set_path_effects(outline_effect)
        text_prod.set_path_effects(outline_effect)
        
        
        #scn.save_dataset(prod, filename=f"{var.attrs['start_time']:%Y-%m-%d %H%MZ}_{prod}.png")
        #plt.savefig(f"{im_save_path}/{scn[prod].attrs['start_time']:%Y_%m_%d_%H%MZ}_{prod}.png",bbox_inches='tight')
        plt.savefig(f"{scn[prod].attrs['start_time']:%Y_%m_%d_%H%MZ}_{prod}.png",bbox_inches='tight')
        #plt.savefig('himawari_ahi_truecolor_{datetime}.png'.format(datetime=scn.start_time.strftime('%Y%m%d%H%M')),bbox_inches='tight')
        plt.close()
        #plt.show()

    files = find_files_and_readers(#start_time=datetime(2016, 11, 17, 3, 0),
                                #end_time=datetime(2016, 11, 17, 12, 10),
                                #base_dir="/data/satellite/Himawari-8/HSD",
                                base_dir="/glade/work/richling/cesm-diagnostics/COMPASS/data/himawari/",
                                reader='ahi_hsd')
    #test_image('true_color',files,".")
    #prod = "true_color"
    prod = "B13"
    #prod = "B03"
    test_image(prod,files,".")
    #Image.open(f"2018_02_19_2300Z_{prod}.png")


if __name__ == "__main__":
    main()
