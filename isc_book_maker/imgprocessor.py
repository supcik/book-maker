################################################################################
# @brief       : Image processing (drawio -> pdf) for the book_maker system
# @author      : Jacques Supcik <jacques.supcik@hefr.ch>
# @date        : 28 September 2021
# ------------------------------------------------------------------------------
# @copyright   : Copyright (c) 2023 HEIA-FR / ISC
#                Haute école d'ingénierie et d'architecture de Fribourg
#                Informatique et Systèmes de Communication
# @attention   : SPDX-License-Identifier: MIT OR Apache-2.0
################################################################################

"""Image processing (drawio -> pdf) for the book_maker system"""

import logging
import os
import platform
import subprocess
import sys
from pathlib import Path

import click

from . import util

logger = logging.getLogger(__name__)

stderr_filter = [
    "Failed to connect to socket",
    "Could not parse server address",
    "Floss manager not present",
    "Exiting GPU process",
    "called with multiple threads",
    "extension not supported",
    "Failed to send GpuControl.CreateCommandBuffer",
    "Init observer found at shutdown",
    "Failed to call method: org.freedesktop.portal.Settings.Read:",
]

stdout_filter = [
    "Checking for beta autoupdate feature for deb/rpm distributions",
    "Found package-type: deb",
]


def do_image_processor(  # noqa: C901
    config: dict,
    force: bool = False,
):
    source_dir = config["source_dir"]
    build_dir = config["build_dir"]
    c = config["tools"]["drawio"]
    drawio_bin = c["bin"]
    drawio_args = c["args"]
    t = eval(c["transformer"])

    xvfb = None
    if platform.system() == "Linux":
        if os.getenv("DISPLAY") is None:
            logger.info("Starting xvfb")
            xvfb = util.Xvfb()
            xvfb.start()
            os.environ["DISPLAY"] = ":42"

    logger.info("Converting drawio files")
    for src in c["source"]:
        for f in Path(source_dir).glob(src):
            dest = Path(build_dir) / t(f).relative_to(source_dir)

            if (
                not force
                and dest.exists()
                and dest.stat().st_ctime >= f.stat().st_ctime
            ):
                logger.debug(f"{dest} is up to date")
                continue

            os.makedirs(dest.parent, exist_ok=True)
            logger.info(f"Converting {f} -> {dest}")

            # WARNING: the current version of drawio requires that the "--no-sandbox"
            # option is passed after the input file name. So we have to remove it
            # from the arguments and add it back after the input file name.
            needs_no_sandbox = "--no-sandbox" in drawio_args
            drawio_args = [i for i in drawio_args if i != "--no-sandbox"]
            cmd = [drawio_bin, *drawio_args, "-o", str(dest), str(f)]
            if needs_no_sandbox or (platform.system() == "Linux" and os.getuid() == 0):
                cmd.append("--no-sandbox")
            logger.debug(f"Command = {' '.join(cmd)}")
            res = subprocess.run(cmd, capture_output=True, text=True, check=False)
            for line in util.filtered_lines(
                [i for i in res.stdout.split("\n") if i != ""], stdout_filter
            ):
                logger.debug(f"* {line}")
            for line in util.filtered_lines(
                [i for i in res.stderr.split("\n") if i != ""], stderr_filter
            ):
                logger.warning(f"* {line}")
            if res.returncode != 0:
                logger.error(f"Pandoc failed: {res.returncode}")
                sys.exit(1)

    if xvfb is not None:
        xvfb.stop()


@click.command()
@click.pass_context
def imgproc(ctx):
    do_image_processor(ctx.obj["CONFIG"])
