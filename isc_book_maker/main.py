################################################################################
# @brief       : book_maker system
# @author      : Jacques Supcik <jacques.supcik@hefr.ch>
# @date        : 28 September 2021
# ------------------------------------------------------------------------------
# @copyright   : Copyright (c) 2023 HEIA-FR / ISC
#                Haute école d'ingénierie et d'architecture de Fribourg
#                Informatique et Systèmes de Communication
# @attention   : SPDX-License-Identifier: MIT OR Apache-2.0
################################################################################

"""book_maker system"""

import importlib.metadata
import logging
from pathlib import Path

import click
import colorlog
import tomllib

from . import clean, imgprocessor, latex_runner, pandoc_runner, preprocessor, util

__version__ = importlib.metadata.version("isc-book-maker")


@click.group(invoke_without_command=True)
@click.option("--debug/--no-debug", default=False)
@click.option("--quiet/--no-quiet", default=False)
@click.option("--version", is_flag=True, help="Print version and exit.")
@click.option(
    "--config",
    "-c",
    default="book.toml",
    type=click.Path(exists=True),
    help="Configuration file.",
)
@click.pass_context
def cli(ctx, debug, quiet, version, config):
    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug

    if version:
        click.echo(f"Book Builder Version : {__version__}")
        click.echo("By Jacques Supcik, ISC, HEIA-FR")
        ctx.exit()
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter("%(log_color)s%(levelname)s:%(name)s:%(message)s")
    )

    logging.basicConfig(
        level=logging.DEBUG if debug else logging.WARNING if quiet else logging.INFO,
        handlers=[handler],
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    with open(Path(__file__).parent / "default.toml", "rb") as f:
        default = tomllib.load(f)

    default["tools"]["drawio"]["bin"] = util.which_drawio()
    default["tools"]["pandoc"]["bin"] = util.which_pandoc()
    default["tools"]["latexmk"]["bin"] = util.which_latexmk()

    with open(config, "rb") as f:
        ctx.obj["CONFIG"] = default | tomllib.load(f)


cli.add_command(preprocessor.pp)
cli.add_command(imgprocessor.imgproc)
cli.add_command(pandoc_runner.pandoc)
cli.add_command(latex_runner.latex)
cli.add_command(clean.clean)


@cli.command()
@click.pass_context
@click.option("--keep", is_flag=True, default=False)
@click.option("--latex/--no-latex", default=True)
@click.argument("src", type=click.Path())
@click.argument("dst", type=click.Path(), required=False)
def build(ctx, keep, latex, src, dst):
    conf = ctx.obj["CONFIG"]

    if Path(src).suffix == "":
        src = Path(src).with_suffix(".md")

    if dst is None:
        dst = src

    main_md = Path(dst).with_suffix(".md")
    main_tex = Path(dst).with_suffix(".tex")

    preprocessor.do_copy_assets(conf)
    preprocessor.do_preprocessor(conf, str(src), str(main_md))
    imgprocessor.do_image_processor(conf)
    pandoc_runner.do_pandoc(conf, str(main_md), str(main_tex))
    if not latex:
        return

    latex_runner.do_latex(conf, str(main_tex))
    if not keep:
        clean.do_clean(conf, str(main_tex))


if __name__ == "__main__":
    cli(obj={})
