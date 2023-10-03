################################################################################
# @brief       : Text Preprocessor (Jinja2) for the book_maker system
# @author      : Jacques Supcik <jacques.supcik@hefr.ch>
# @date        : 28 September 2021
# ------------------------------------------------------------------------------
# @copyright   : Copyright (c) 2023 HEIA-FR / ISC
#                Haute école d'ingénierie et d'architecture de Fribourg
#                Informatique et Systèmes de Communication
# @attention   : SPDX-License-Identifier: MIT OR Apache-2.0
################################################################################

"""Text Preprocessor (Jinja2) for the book_maker system"""

import logging
import os
import shutil
from pathlib import Path

import click
from jinja2 import Environment, FileSystemLoader, pass_context, select_autoescape

logger = logging.getLogger(__name__)


class BookEnvironment(Environment):
    """Override join_path() to enable relative template paths."""

    def join_path(self, template, parent):
        return os.path.join(os.path.dirname(parent), template)


@pass_context
def drawio_to_pdf(context, path):
    # return Path(path).with_suffix(".pdf").name
    return Path(context.name).parent / Path(path).with_suffix(".pdf")


def do_copy_assets(
    conf: dict,
):
    logger.info("Copying assets")
    for asset in conf["tool"]["preprocessor"]["assets"]:
        for file in Path(conf["source_dir"]).glob(asset):
            dest_path = Path(conf["build_dir"]) / file.relative_to(conf["source_dir"])
            os.makedirs(dest_path.parent, exist_ok=True)
            if dest_path.exists() and dest_path.stat().st_ctime >= file.stat().st_ctime:
                continue

            logger.info(f"Copying {file} -> {dest_path}")
            shutil.copy(file, dest_path)


def do_preprocessor(conf: dict, src: str, dst: str):
    env = BookEnvironment(loader=FileSystemLoader("."), autoescape=select_autoescape())
    env.filters["drawio2pdf"] = drawio_to_pdf

    cwd = os.getcwd()
    os.chdir(conf["source_dir"])
    template = env.get_template(src)
    res = template.render(conf["variables"])
    os.chdir(cwd)

    dest_path = Path(conf["build_dir"]) / dst
    os.makedirs(dest_path.parent, exist_ok=True)
    logger.info(f"Writing {dest_path}")
    with open(dest_path, "w") as f:
        f.write(res)


@click.command()
@click.pass_context
@click.argument("src", type=click.Path())
@click.argument("dest", type=click.Path())
def pp(ctx, src, dst):
    conf = ctx.obj["CONFIG"]
    if Path(src).suffix == "":
        src = Path(src).with_suffix(".md")

    if dst is None:
        dst = src

    do_copy_assets(conf)
    do_preprocessor(conf, str(src), dst)
