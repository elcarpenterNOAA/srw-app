"""
The run script for SfcClimoGen
"""

import datetime as dt
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


# Extract driver config from experiment config
sfc_climo_gen_driver = SfcClimoGen(
    config=args.config_file,
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
expt_config = get_yaml_config(args.config_file)
sfc_climo_gen_config = expt_config[args.key_path]

links = {}
for label in sfc_climo_gen_config["output_file_labels"]:
    # deepcopy here because desired_output_name is parameterized within the loop
    expt_config_cp = get_yaml_config(deepcopy(expt_config.data))
    expt_config_cp.dereference(
        context={
            "file_label": label,
            **expt_config_cp,
        }
    )
    sfc_climo_gen_block = expt_config_cp[args.key_path]
    desired_output_fn = sfc_climo_gen_block["desired_output_name"]
    sfc_climo_gen_output_fn = rundir / f"{label.sfc_climo_gen()}"
    links[desired_output_fn] = str(sfc_climo_gen_output_fn)

uwlink(target_dir=rundir.parent, config=links)
