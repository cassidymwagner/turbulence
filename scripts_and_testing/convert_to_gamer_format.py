import h5py
import numpy as np

def convert():

    data = {}

    for field in ["Density", "Vx", "Vy", "Vz","Bx","By","Bz"]:
        f = h5py.File("mhd256li_properIC.%s" % field)
        data[field] = f["/mhd256li_properIC.%s" % field][:]
        f.close()

    data["Vx2"] = data["Vx"] * (data["Density"]**(-1/2))
    data["Vy2"] = data["Vy"] * (data["Density"]**(-1/2))
    data["Vz2"] = data["Vz"] * (data["Density"]**(-1/2))

    data["Px"] = data["Density"] * data["Vx2"]
    data["Py"] = data["Density"] * data["Vy2"]
    data["Pz"] = data["Density"] * data["Vz2"]

    data["V"] = np.sqrt(data["Vx2"]**2+data["Vy2"]**2+data["Vz2"]**2) 
    data["P"] = np.sqrt(data["Px"]**2+data["Py"]**2+data["Pz"]**2)
    # data["P"] = np.ones((256,256,256))

    data["Energy"] = (
                      0.5 * data["Density"] * data["V"]**2 + 
                      data["P"]/(1.001 - 1)) 

    data["All"] = np.asarray((data["Density"],data["Px"],data["Py"],data["Pz"],data["Energy"]))

    with open("UM_IC", "wb") as f:
            np.float32(data["All"].T).tofile(f)

