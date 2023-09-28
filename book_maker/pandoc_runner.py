################################################################################
# @brief       : Pandoc runner for the book_maker system
# @author      : Jacques Supcik <jacques.supcik@hefr.ch>
# @date        : 28 September 2021
# ------------------------------------------------------------------------------
# @copyright   : Copyright (c) 2023 HEIA-FR / ISC
#                Haute école d'ingénierie et d'architecture de Fribourg
#                Informatique et Systèmes de Communication
# @attention   : SPDX-License-Identifier: MIT OR Apache-2.0
################################################################################

"""Pandoc runner for the book_maker system"""

import logging
import os
import subprocess
import sys
from pathlib import Path

import click

logger = logging.getLogger(__name__)


def do_pandoc(conf: dict, src: str, dst: str):
    c = conf["tools"]["pandoc"]
    cwd = os.getcwd()
    os.chdir(conf["build_dir"])
    logger.info(f"Pandoc: {src} -> {dst}")
    cmd = [c["bin"], *c["args"], "-o", str(dst), str(src)]
    logger.debug(f"Command = {' '.join(cmd)}")

    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    for line in [i for i in res.stdout.split("\n") if i != ""]:
        logger.debug(f"* {line}")
    for line in [i for i in res.stderr.split("\n") if i != ""]:
        logger.warning(f"* {line}")
    if res.returncode != 0:
        logger.error(f"Pandoc failed: {res.returncode}")
        sys.exit(1)

    os.chdir(cwd)


@click.command()
@click.pass_context
@click.option("--pdf", is_flag=True, default=False)
@click.argument("src")
@click.argument("dst", required=False)
def pandoc(ctx, pdf, src, dst):
    if Path(src).suffix == "":
        src = Path(src).with_suffix(".md")
    if dst is None:
        dst = Path(src).with_suffix(".pdf" if pdf else ".tex")
    do_pandoc(ctx.obj["CONFIG"], str(src), str(dst))
