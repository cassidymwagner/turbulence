import os
import sys
import numpy as np 
import glob
from snakemake.remote.HTTP import RemoteProvider as HTTPRemoteProvider

sys.path.insert(0, 'scripts_and_testing')
import convert_to_gamer_format
import post_processing

HTTP = HTTPRemoteProvider()

driving_amps = list(10**(np.linspace(-5,5,11)))
fields = ['density','velocity_magnitude']

def create_templates(parameters, dest_path):
    for fn in glob.glob("initialize/*.template"):
        contents = open(fn, "r").read()
        if not os.path.isdir(dest_path):
            os.makedirs(dest_path)
        dest_fn = os.path.join(dest_path, os.path.basename(fn.rsplit(".", 1)[0]))
        with open(dest_fn, "w") as f:
            f.write(contents.format(**parameters))
        dest_ic = os.path.join(dest_path, "UM_IC")
        src_ic = os.path.abspath("./UM_IC")
        if os.path.exists(dest_ic):
            os.unlink(dest_ic)
        os.symlink(src_ic, dest_ic)

# compile gamer and copy it to the working directory
rule compile:
    input:
        'gamer/src/Makefile'
    output:
        'gamer/src/gamer'
    run: 
        shell('make -j -C gamer/src')

# download initial conditions from Kritsuk 2011 and convert to gamer format
rule generate_ic:
    input:
        HTTP.remote('http://use.yt/upload/06d80397', keep_local=True)
    output:
        'UM_IC'
    run:
        convert_to_gamer_format.convert(input[0], output[0])

# run templating function to create template files
rule template:
    run:
        for amp in driving_amps:
            dest_path = os.path.join("initialize", "templates",
                "driven_amp{:05}".format(amp) )
            create_templates( {'driven_amp': float(amp)}, dest_path = dest_path)

# cd to appropriate directory and run gamer based on all template files
rule gamer:
    input: 
        directories=("initialize/templates/driven_amp{:05}".format(amp) for amp in driving_amps),
        gamer='gamer/src/gamer'
    run:
        for dir in input.directories:
            shell('cd {dir}; ./../../../{input.gamer}')

# make diagnostic plots
rule plots:
    input:
        directories=("initialize/templates/driven_amp{:05}".format(amp) for amp in driving_amps),
    run:
        for dir in input.directories:
            try:
                print("Making phase plots for the Mach number.")
                post_processing.mach_number(path=dir, idx_start=1, idx_end=100, didx=1)

            except OSError:
                print("Out of data, moving to next sim.")
                pass
            
            for i in fields:
                for j in ['x','y','z']:
                    try:
                        print("Making slice plots for "+str(i)+" along the "+str(j)+" axis.")
                        post_processing.slice_plot(path=dir, field = i, axis = j, 
                                                   idx_start=1, idx_end=100, didx=1) 
                    except OSError:
                        print("Out of data, moving to next sim.")
                        pass 
           
