################################################################################
# @brief       : Utils for the book_maker system
# @author      : Jacques Supcik <jacques.supcik@hefr.ch>
# @date        : 28 September 2021
# ------------------------------------------------------------------------------
# @copyright   : Copyright (c) 2023 HEIA-FR / ISC
#                Haute école d'ingénierie et d'architecture de Fribourg
#                Informatique et Systèmes de Communication
# @attention   : SPDX-License-Identifier: MIT OR Apache-2.0
################################################################################

"""Utils for the book_maker system"""

import logging
import platform
import shutil
import subprocess
import sys

import psutil

logger = logging.getLogger(__name__)


def which_drawio() -> str:
    res = shutil.which("drawio.exe" if platform.system() == "Windows" else "drawio")
    if res is not None:
        return res
    res = shutil.which("draw.io.exe" if platform.system() == "Windows" else "draw.io")
    if res is not None:
        return res
    if platform.system() == "Darwin":
        res = shutil.which("draw.io", path="/Applications/draw.io.app/Contents/MacOS")
        if res is not None:
            return res


def which_pandoc() -> str:
    res = shutil.which("pandoc.exe" if platform.system() == "Windows" else "pandoc")
    if res is not None:
        return res


def which_latexmk() -> str:
    res = shutil.which("latexmk.exe" if platform.system() == "Windows" else "latexmk")
    if res is not None:
        return res


def filtered_lines(lines, line_filter):
    """
    Filter lines
    """
    seen = set()
    for line in lines:
        if len(line) == 0:
            continue
        if line in seen:
            continue
        if not any(f in line for f in line_filter):
            seen.add(line)
            yield line


class Xvfb:
    def __init__(self):
        self.process = None
        self.__get_process(force=True)

    def __get_process(self, force=False):
        """
        Get the Xvfb process or None
        """
        if self.process is not None and not force:
            return

        self.process = None
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            if proc.info["name"] == "Xvfb":
                self.process = proc

    def pid(self):
        """
        Return the PID of the Xvfb process or None
        """
        self.__get_process()
        if self.process is None:
            return None
        return self.process.info["pid"]

    def is_running(self) -> bool:
        """
        Return True if Xvfb is running
        """
        self.__get_process()
        return self.process is not None

    def start(self):
        """
        Check if Xvfb is running and start it if not
        """
        if self.is_running():
            logger.debug("Xvfb is already running (PID = %d)", self.pid())
            return
        logger.info("Starting Xvfb")
        subprocess.Popen(["Xvfb", ":42", "-screen", "0", "1024x768x24"])
        self.__get_process(force=True)
        if not self.is_running():
            logger.fatal("Failed to start Xvfb")

    def stop(self):
        """
        Stop Xvfb
        """
        if not self.is_running():
            logger.debug("Xvfb is not running")
            return
        logger.info("Stopping Xvfb (PID = %d)", self.pid())
        self.process.terminate()
        self.process.wait()
        self.__get_process(force=True)
        if not self.is_running():
            logger.debug("Xvfb stopped")
            return

        logger.error("Failed to stop Xvfb, trying to kill it")
        self.process.kill()
        self.process.wait(10)
        self.__get_process(force=True)
        if not self.is_running():
            logger.debug("Xvfb killed")
            return

        logger.fatal("Failed to stop Xvfb")
        sys.exit(1)
