"""
The run script for SfcClimoGen
"""

import datetime as dt
import glob
import os
import re
import sys
from argparse import ArgumentParser
from copy import deepcopy
from pathlib import Path

from uwtools.api.file import link as uwlink
from uwtools.api.sfc_climo_gen import SfcClimoGen 
from uwtools.api.config import get_yaml_config


parser = ArgumentParser(
    description="Script that runs SfcClimoGen via uwtools API",
)
parser.add_argument(
    "-c",
    "--config-file",
    metavar="PATH",
    required=True,
    help="Path to experiment config file.",
    type=Path,
)
parser.add_argument(
    "--key-path",
    help="Dot-separated path of keys leading through the config to the driver's YAML block",
    metavar="KEY[.KEY...]",
    required=True,
)
args = parser.parse_args()


# Deliver output data
expt_config = get_yaml_config(args.config_file)
CRES = expt_config["workflow"]["CRES"]
SFC_CLIMO_FIELDS = expt_config["fixed_files"]["SFC_CLIMO_FIELDS"]
TILE_RGNL = expt_config["constants"]["TILE_RGNL"]
os.environ["CRES"] = CRES 
expt_config.dereference(
    context={
        **os.environ,
        **expt_config,
    }
)


# Extract driver config from experiment config
sfc_climo_gen_driver = SfcClimoGen(
    config=expt_config,
    key_path=[args.key_path],
)
rundir = Path(sfc_climo_gen_driver.config["rundir"])
print(f"Will run in {rundir}")


# Run sfc_climo_gen 
sfc_climo_gen_driver.run()

if not (rundir / "runscript.sfc_climo_gen.done").is_file():
    print("Error occurred running sfc_climo_gen. Please see component error logs.")
    sys.exit(1)


# Deliver output data
sfc_climo_gen_config = expt_config[args.key_path]

fix_lam_path = Path(expt_config["workflow"]["FIXlam"])
for fpath in glob.glob(str(rundir / f"*.nc")):
    path = Path(fpath)
    fn = Path(fpath).name

#    if not "halo" in fn:
#        # fn = f"{CRES}.{SFC_CLIMO_FIELDS}.tile{TILE_RGNL}.halo4.nc"
#        bn = fn.split(".nc")[0]
#        fn = f"{CRES}.{bn}.halo0.nc"
#    else:
#        # fn = f"{CRES}.{SFC_CLIMO_FIELDS}.tile{TILE_RGNL}.halo0.nc"
#        fn = f"{CRES}.{(fn.replace('halo', 'halo4'))}"
#
    update_path = path.with_name(fn)
    fn = path.rename(update_path)

    linkname = fix_lam_path / fn.name 
    linkname.symlink_to(path)

Path(rundir / "make_sfc_climo_task_complete.txt").touch()
