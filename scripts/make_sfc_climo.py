"""
The run script for SfcClimoGen
"""

import glob
import os
import sys
from argparse import ArgumentParser
from pathlib import Path

from uwtools.api.fs import link as uwlink
from uwtools.api.sfc_climo_gen import SfcClimoGen 
from uwtools.api.config import get_yaml_config


def link_files(dest_dir, files):
    """
    Link a given list of files to the destination directory using the same file names.
    """
    for fpath in files:
        path = Path(fpath)
        fn = Path(fpath).name
    
        if "halo" in fn:
            fn = f"{CRES}.{(fn.replace('halo', 'halo4'))}"
            no_halo_fn = fn.replace("halo4.", "")
            for link in (fn, no_halo_fn):
                link = Path(link)
                if (linkname := dest_dir / link.name).is_symlink():
                    linkname.unlink()
                linkname.symlink_to(path)
    
        else:
            bn = fn.split(".nc")[0]
            fn = f"{CRES}.{bn}.halo0.nc"
            tile1_fn = fn.replace("tile7.halo0", "tile1")
            for link in (fn, tile1_fn):
                link = Path(link)
                if (linkname := dest_dir / link.name).is_symlink():
                    linkname.unlink()
                linkname.symlink_to(path)


parser = ArgumentParser(
    description="Script that runs SfcClimoGen via uwtools API.",
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
    help="Dot-separated path of keys leading through the config to the driver's YAML block.",
    metavar="KEY[.KEY...]",
    required=True,
    type=lambda s: s.split("."),
)

args = parser.parse_args()

expt_config = get_yaml_config(args.config_file)
CRES = expt_config["workflow"]["CRES"]
os.environ["CRES"] = CRES 
expt_config.dereference(
    context={
        **os.environ,
        **expt_config,
    }
)

args = parser.parse_args()

def make_sfc_climo(config_file, key_path):
    # Run sfc_climo_gen 
    sfc_climo_gen_driver = SfcClimoGen(
        config=config_file,
        key_path=key_path,
    ) 
    rundir = Path(sfc_climo_gen_driver.config["rundir"])
    print(f"Will run sfc_climo_gen in {rundir}")
    sfc_climo_gen_driver.run()
    
    if not (rundir / "runscript.sfc_climo_gen.done").is_file():
        print("Error occurred running sfc_climo_gen. Please see component error logs.")
        sys.exit(1)
    
    
    # Deliver output data
    fix_lam_path = Path(expt_config["workflow"]["FIXlam"])
    link_files(
        dest_dir=fix_lam_path,
        files=glob.glob(str(rundir / f"*.nc")),
    )
    
    Path(rundir / "make_sfc_climo_task_complete.txt").touch()


if __name__ == "__main__":

    make_sfc_climo(
        config_file=args.config_file,
        key_path=args.key_path,
    )
