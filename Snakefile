import os
import sys
import numpy as np 
import glob
from snakemake.remote.HTTP import RemoteProvider as HTTPRemoteProvider

sys.path.insert(0, 'scripts_and_testing')
import convert_to_gamer_format

HTTP = HTTPRemoteProvider()

# run templating function to create template files
driving_amps = list(np.arange(1,11))

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
        'gamer/bin/gamer'
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

rule template:
    run:
        for amp in driving_amps:
            print("driven_amp{:05}".format(amp))
            dest_path = os.path.join("initialize", "templates",
                "driven_amp{:05}".format(amp) )
            create_templates( {'driven_amp': float(amp)}, dest_path = dest_path)

# run gamer based on all template files and move the output data to the appropriate directory
rule gamer:
    run:
        shell('for VARIABLE in {{00001..00010}}; do cp templates/driven_amp$VARIABLE/Input__TestProb .; ./gamer; mv Data* Diag* Record* templates/driven_amp$VARIABLE; done')
