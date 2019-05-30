import h5py
import numpy as np
import tarfile
import io

def convert(infile, outfile):

    # We assume infile is in targz

    data = {}

    tar_src = tarfile.open(infile)

    for field in ["Density", "Vx", "Vy", "Vz","Bx","By","Bz"]:
        tarinfo = tar_src.getmember("mhd256li_properIC.%s" % field)
        byte_source = io.BytesIO(tar_src.extractfile(tarinfo).read())
        f = h5py.File(byte_source, driver='fileobj')
        data[field] = f["/mhd256li_properIC.%s" % field][:]
        f.close()

    tar_src.close()

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

    with open(outfile, "wb") as f:
            np.float32(data["All"].T).tofile(f)

