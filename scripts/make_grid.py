"""
The run script for making the grid files for the experiment.
"""

from argparse import ArgumentParser
from pathlib import Path

from uwtools.api.drivers import esg_grid, global_equiv_resol, make_hgrid, make_solo_mosaic, shave

parser = ArgumentParser(
    description="Script that runs the make_grid task via uwtools API",
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
    help="Dot-separated path of keys leading through the config to the tasks's YAML block",
    metavar="KEY[.KEY...]",
    required=True,
)

args = parser.parse_args()
expt_config = get_yaml_config(args.config_file)
make_grid_config = get_yaml_config(expt_config[args.key_path])
task_rundir = Path(make_grid_config["rundir"])
print(f"Will run make_grid in {task_rundir}")

# Run either make_hgrid or esg_grid 

if COSA???:
    make_hgrid_driver = MakeHgrid(
        config=args.config_file,
        key_path=args.key_path,
    )
    rundir = Path(make_hgrid_driver.config["rundir"])
    print(f"Will run make_hgrid_driver in {rundir}")
    make_hgrid_driver.run()

    if not (rundir / "runscript.make_hgrid.done").is_file():
        print("Error occurred running make_hgrid. Please see component error logs.")
else:
    esg_grid_driver = ESGGrid(
        config=args.config_file,
        key_path=args.key_path,
    )
    rundir = Path(esg_grid_driver.config["rundir"])
    print(f"Will run esg_grid_driver in {rundir}")
    esg_grid_driver.run()

    if not (rundir / "runscript.esg_grid.done").is_file():
        print("Error occurred running esg_grid. Please see component error logs.")

# Run global_equiv_resol

global_equiv_resol_driver = GlobalEquivResol(
    config=args.config_file,
    key_path=args.key_path,
)
rundir = Path(global_equiv_resol_driver.config["rundir"])
print(f"Will run global_equiv_resol_driver in {rundir}")
global_equiv_resol_driver.run()

if not (rundir / "runscript.global_equiv_resol.done").is_file():
    print("Error occurred running global_equiv_resol. Please see component error logs.")

# Run shave (repeatedly, with different numbers of halo grid cells)

# ELC: WHAT SOMETHING???
for sub_path in something:
    key_path=".".join([args.key_path, sub_path])
    shave_driver = Shave(
        config=args.config_file,
        key_path=key_path,
    )
    rundir = Path(shave_driver.config["rundir"])
    print(f"Will run {sub_path} in {rundir}")
    shave_driver.run()
    if not (rundir / "runscript.shave.done").is_file():
       print(f"Error occurred running {sub_path}. Please see component error logs.")

# Run make_solo_mosaic

make_solo_mosaic_driver = MakeSoloMosaic(
    config=args.config_file,
    key_path=args.key_path,
)
rundir = Path(make_solo_mosaic_driver.config["rundir"])
print(f"Will run make_solo_mosaic_driver in {rundir}")
make_solo_mosaic_driver.run()

if not (rundir / "runscript.make_solo_mosaic.done").is_file():
    print("Error occurred running make_solo_mosaic. Please see component error logs.")




