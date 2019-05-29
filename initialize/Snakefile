import os
import numpy as np 
import glob

def create_templates(parameters, dest_path="."):
    for fn in glob.glob("*.template"):
        contents = open(fn, "r").read()
        if not os.path.isdir(dest_path):
            os.makedirs(dest_path)
        dest_fn = os.path.join(dest_path, fn.rsplit(".", 1)[0])
        with open(dest_fn, "w") as f:
            f.write(contents.format(**parameters))

# compile gamer and copy it to the working directory
rule compile:
    input:
        'gamer/src/Makefile',
	'gamer/src/gamer'
    shell: 'cd gamer/src; make -j; cp gamer /dpool/cwagner4/working/gamer_sims/driv_turbulence'

# download initial conditions, created from external python script [WILL ADD SCRIPT AND ORIGINAL DATA]
rule download:
    input:
        'UM_IC',
    shell: 'yt download UM_IC' # may not be updated file, but okay for now

# run templating function to create template files
driving_amps = list(np.arange(1,11))
rule template:
    run:
        for amp in driving_amps:
           	print("driven_amp"+str(amp)) 
		create_templates( {'driven_amp': float(amp)}, dest_path = ("initialize/templates/driven_amp" + str(amp)) ) 

# run gamer based on all template files and move the output data to the appropriate directory
rule gamer:
    shell: 'for VARIABLE in {1..10}; do cp templates/driven_amp$VARIABLE/Input__TestProb .; ./gamer; mv Data* Diag* Record* templates/driven_amp$VARIABLE; done'
