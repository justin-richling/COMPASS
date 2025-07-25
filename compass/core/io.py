
import xarray as xr
def get_cam_ds(usernl_path,cam_path):
    search_text, full_text = load_and_search_user_nl(usernl_path,"fincl1lonlat")
    print(search_text)
    ahh = search_text.replace("'","").replace("fincl1lonlat = ","")
    fincl_latlon_str = ahh.replace(":","_to_")
    print(fincl_latlon_str)
    
    indv_ahh = ahh.partition("_")
    print(indv_ahh)
    fincl_lon = indv_ahh[0].replace(":","_to_")
    fincl_lat = indv_ahh[2].replace(":","_to_")
    print(fincl_lon,"   ",fincl_lat)
    
    
    #cam_path = Path(f"/glade/derecho/scratch/richling/cases/{case_name}/run/")
    h1a_files = sorted(cam_path.glob("*h1a*00.nc"))
    h2i_files = sorted(cam_path.glob("*h2i*00.nc"))
    #h0a_files = sorted(cam_path.glob("*h0a*00.nc"))
    h0a_files = sorted(cam_path.glob("*h0a*00.nc"))
    #nudge-socrates.cam.h0a_new_all.nc
    
    h2i_ds = xr.open_mfdataset(h2i_files, combine="nested", concat_dim="time")
    h2i_ds = h2i_ds.sortby('time')
    
    h1a_ds = xr.open_mfdataset(h1a_files, combine="nested", concat_dim="time")
    h1a_ds = h1a_ds.sortby('time')
    
    h0a_ds = xr.open_mfdataset(h0a_files, combine="nested", concat_dim="time")
    h0a_ds = h0a_ds.sortby('time')
    h0a_ds
    
    # Rename the variables in the second dataset by removing the substring
    new_var_names = {var: var.replace(f"_{fincl_latlon_str}", "") for var in h0a_ds.data_vars}
    
    # Apply the renaming to the dataset
    h0a_ds = h0a_ds.rename(new_var_names)
    
    # Rename the variables in the second dataset by removing the substring
    new_dim_names = {var: var.replace(f"_physgrid_{fincl_lon}", "") for var in h0a_ds.dims}
    # Apply the renaming to the dataset
    h0a_ds = h0a_ds.rename(new_dim_names)
    
    # Rename the variables in the second dataset by removing the substring
    new_dim_names = {var: var.replace(f"_physgrid_{fincl_lat}", "") for var in h0a_ds.dims}
    # Apply the renaming to the dataset
    h0a_ds = h0a_ds.rename(new_dim_names)
    
    print("All done")
    return h0a_ds, h1a_ds, h2i_ds