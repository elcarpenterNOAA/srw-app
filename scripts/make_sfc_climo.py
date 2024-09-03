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

src = Path(expt_config["workflow"]["FIXlam"])
for fpath in glob.glob(str(rundir / "*.nc")):
    fn = Path(fpath).name
    dst = src / f"{CRES}.{fn}"
    dst.symlink_to(src)
    if "halo" in fn:
        dst = src / f"{CRES}_{(fn.replace('halo', 'halo4'))}" 
        dst.symlink_to(src)
    else:
        bn = fn.split(".nc")[0]
        dst = src / f"{CRES}.{bn}.halo0.nc"
        dst.symlink_to(src)

Path(rundir / "make_sfc_climo_task_complete.txt").touch()
