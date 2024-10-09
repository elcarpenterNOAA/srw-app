"""
The run script for making the grid files for the experiment.
"""

import glob
import logging
import os
import sys
from argparse import ArgumentParser
from pathlib import Path

from uwtools.api.config import get_yaml_config
from uwtools.api.esg_grid import ESGGrid
from uwtools.api.global_equiv_resol import GlobalEquivResol
from uwtools.api.logging import use_uwtools_logger
from uwtools.api.make_hgrid import MakeHgrid
from uwtools.api.make_solo_mosaic import MakeSoloMosaic
from uwtools.api.shave import Shave


def link_files(dest_dir, files):
    """
    Link a given list of files to the destination directory using the same file names.
    """
    for fpath in files:
        path = Path(fpath)
        linkname = dest_dir / path.name
        if linkname.is_symlink():
            linkname.unlink()
        logging.info(f"Linking {linkname} -> {path}")
        linkname.symlink_to(path)


def parse_args(argv):
    """
    Parse arguments for the script.
    """
    parser = ArgumentParser(
        description="Script that runs the make_grid task via uwtools API.",
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
        help="Dot-separated path of keys leading through the config to the tasks's YAML block.",
        metavar="KEY[.KEY...]",
        required=True,
        type=lambda s: s.split("."),
    )
    return parser.parse_args(argv)


# args = parser.parse_args()


def make_grid(config_file, key_path):
    """
    Run the series of drivers needed to produce NetCDF-formatted grid files.
    """
    expt_config = get_yaml_config(config_file)
    make_grid_dict = expt_config
    for kp in key_path:
        make_grid_dict = make_grid_dict[kp]
    make_grid_config = get_yaml_config(make_grid_dict)
    task_rundir = Path(make_grid_config["rundir"])
    logging.info(f"Will run make_grid in {task_rundir}")

    # The experiment config will have {{ CRES | env }} expressions in it that need to be
    # dereferenced during driver initialization.
    cres = expt_config["workflow"]["CRES"]
    os.environ["CRES"] = cres

    # Destination of important files from this process
    fix_lam_path = Path(expt_config["workflow"]["FIXlam"])

    # Run either make_hgrid or esg_grid
    if grid_gen_method == "GFDLgrid":
        run_driver(driver_class=MakeHgrid, config_file=config_file, key_path=key_path)
    # ELC: grid_fn="GFDLgrid.tile7.nc"
    elif grid_gen_method == "ESGgrid":
        run_driver(driver_class=ESGGrid, config_file=config_file, key_path=key_path)
    # ELC: regional_grid.nc in rundir

    # Run global_equiv_resol
    run_driver(
        driver_class=GlobalEquivResol, config_file=config_file, key_path=key_path
    )

    # Run shave for 3- and 4-cell-wide halo
    for subpath in ["shave3", "shave4"]:
        driver = run_driver(
            driver_class=Shave,
            config_file=config_file,
            key_path=[*key_path, subpath],
        )

    # Link shave output to fix directory (shave config points to task dir, not shave rundir)
    link_files(
        dest_dir=fix_lam_path,
        files=glob.glob(str(task_rundir / f"{cres}*.nc")),
    )

    # Run make_solo_mosaic
    for subpath in ["NHW", "NH3", "NH4", "NH0"]:
        driver = run_driver(
            driver_class=MakeSoloMosaic,
            config_file=config_file,
            key_path=[*key_path, subpath],
        )
    # Link make-solo_mosaic output to fix directory
    link_files(
        dest_dir=fix_lam_path,
        files=glob.glob(str(task_rundir / f"C*_mosaic.halo{subpath}.nc")),
    )
    # Mark the successful completion of the script on disk.
    Path(task_rundir / "make_grid_task_complete.txt").touch()


def run_driver(driver_class, config_file, key_path):
    """
    Initialize and run the provided UW driver.

    Return the configured object.
    """
    driver = driver_class(
        config=config_file,
        key_path=key_path,
    )
    rundir = Path(driver.config["rundir"])
    logging.info(f"Will run {driver.driver_name()} in {rundir}")
    driver.run()

    if not (rundir / f"runscript.{driver.driver_name()}.done").is_file():
        logging.error(
            f"Error occurred running {driver.driver_name()}. Please see component error logs."
        )
        sys.exit(1)
    return driver


if __name__ == "__main__":

    use_uwtools_logger()

    args = parse_args(sys.argv[1:])
    make_grid(
        config_file=args.config_file,
        key_path=args.key_path,
    )
