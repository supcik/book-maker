################################################################################
# @brief       : LaTeX runner for the book_maker system
# @author      : Jacques Supcik <jacques.supcik@hefr.ch>
# @date        : 28 September 2021
# ------------------------------------------------------------------------------
# @copyright   : Copyright (c) 2023 HEIA-FR / ISC
#                Haute école d'ingénierie et d'architecture de Fribourg
#                Informatique et Systèmes de Communication
# @attention   : SPDX-License-Identifier: MIT OR Apache-2.0
################################################################################

"""LaTeX runner for the book_maker system"""

import logging
import os
import subprocess
import sys
from pathlib import Path

import click

logger = logging.getLogger(__name__)


def do_latex(conf: dict, src: str):
    c = conf["tools"]["latexmk"]
    cwd = os.getcwd()
    os.chdir(conf["build_dir"])
    logger.info(f"Latexmk: {src}")
    cmd = [c["bin"], *c["args"], str(src)]
    logger.debug(f"Command = {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    for line in [i for i in res.stdout.split("\n") if i != ""]:
        logger.debug(f"* {line}")
    for line in [i for i in res.stderr.split("\n") if i != ""]:
        logger.warning(f"* {line}")
    if res.returncode != 0:
        logger.error(f"LaTeXmk failed: {res.returncode}")
        sys.exit(1)

    os.chdir(cwd)


@click.command()
@click.pass_context
@click.argument("src")
def latex(ctx, src):
    if Path(src).suffix == "":
        src = Path(src).with_suffix(".tex")
    do_latex(ctx.obj["CONFIG"], str(src))
