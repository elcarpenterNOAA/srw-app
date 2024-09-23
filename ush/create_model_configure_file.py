#!/usr/bin/env python3
"""
Create a model_configure file for the FV3 forecast model from a
template.
"""
import argparse
import os
import sys
from textwrap import dedent
from uwtools.api.template import render
from uwtools.api.config import get_yaml_config


def create_model_configure_file(config_file, cycle):
    """
    Creates a model_config file for the specified cycle in the fcst rundir

    Args:

      config_file: path to the experiment configuration file
      cycle: the date of the current cycle
    """

    expt_config = get_yaml_config(config_file)
    fcst_config = get_yaml_config(expt_config["task_run_fcst"])
    fcst_config.dereference(
        context={
            "cycle": cycle,
            **expt_config,
        }
    )

    rundir = Path(fcst_config["rundir"])

    render(
        input_file = expt_config["workflow"]["MODEL_CONFIG_TMPL_FP"],
        output_file = run_dir / "model_configure"
        values_src = config_file,
        overrides = fcst_config,
        )


def parse_args(argv):
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Creates model configuration file.")

    parser.add_argument(
        "-c",
        "--cycle",
        dest="cycle",
        required=True,
        help="The cycle in ISO8601 format (e.g. 2024-07-15T18)",
        type=dt.datetime.fromisoformat,
    )

    parser.add_argument(
        "-p",
        "--path-to-defns",
        required=True,
        help="Path to var_defns file.",
        type=Path,
    )

    return parser.parse_args(argv)


if __name__ == "__main__":

    args = parse_args(sys.argv[1:])

    create_model_configure_file(
        cycle=args.cycle,
        config_file=args.path_to_defns,
    )
