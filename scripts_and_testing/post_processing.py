import yt
import numpy as np

def slice_plot(path, field, axis, idx_start=1, idx_end=100, didx=1,):
    ts = yt.load([path+'/Data_%06d'%idx for idx in range(idx_start, idx_end+1, didx)])
    ds = yt.load(path+'/Data_000001')

    cg = ds.covering_grid(0, left_edge = [0.0, 0.0, 0.0], dims=[256, 256, 256])
    cg.get_data(field)
    field_data = cg[field]

    field_min = field_data.min()
    field_max = field_data.max()
 
    for ds in ts.piter():
        
        sz = yt.SlicePlot(ds, axis, field)
        try:
            sz.set_log(field, True)
        except ValueError:
            pass
        sz.set_cmap(field,'arbre')
        sz.annotate_timestamp(time_unit='code_time', corner='upper_right', 
                              time_format='t = {time:.4f} {units}')
        sz.set_zlim(field, field_min, field_max)
        sz.save(name=path+'/images/'+str(ds))
         
def mach_number(path, idx_start=1, idx_end=100, didx=1,):
    ts = yt.load([path+'/Data_%06d'%idx for idx in range(idx_start, idx_end+1, didx)])
    ds = yt.load(path+'/Data_000001')

    cg = ds.covering_grid(0, left_edge = [0.0, 0.0, 0.0], dims=[256, 256, 256])
    cg.get_data(["density","mach_number","cell_mass"])
    density_data = cg["density"]
    mach_number_data= cg["mach_number"]
    cell_mass_data= cg["cell_mass"]
    
    dens_min = density_data.min()
    dens_max = density_data.max()
    mach_min = mach_number_data.min()
    mach_max = mach_number_data.max()
    cell_min = cell_mass_data.min()
    cell_max = cell_mass_data.max()

    for ds in ts.piter():

        ad = ds.all_data()
        plot = yt.PhasePlot(ad, "density", "mach_number", ["cell_mass"], 
                            weight_field=None)
 
        plot.set_xlim(dens_min, dens_max)
        plot.set_ylim(mach_min, mach_max)
        plot.set_zlim("cell_mass",cell_min, cell_max)       
        plot.save(name=path+'/images/'+str(ds))
