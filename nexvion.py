
import os
import re
import sys
import shutil
import tempfile
import subprocess
from pathlib import Path

from colorama import Fore, Style, init

init(autoreset=True)

# =====================================
# NEXVION CONFIGURATION
# =====================================

OWNER = "uddinmdsamal-wq"
VERSION = "1.0.0"

BLUE = Fore.BLUE + Style.BRIGHT
CYAN = Fore.CYAN + Style.BRIGHT
GREEN = Fore.GREEN + Style.BRIGHT
WHITE = Fore.WHITE + Style.BRIGHT
YELLOW = Fore.YELLOW + Style.BRIGHT
RED = Fore.RED + Style.BRIGHT
DIM = Style.DIM


# =====================================
# BANNER
# =====================================

def banner():

    os.system("")

    print()
    print(BLUE + "  NEXVION")
    print(CYAN + "  Package Manager")
    print(DIM + "  ──────────────────────────────")
    print(WHITE + f"  Version {VERSION}")
    print(GREEN + "  System ready.")
    print(DIM + "  ──────────────────────────────")
    print()


# =====================================
# PROGRESS BAR
# =====================================

def progress_bar(percent, stage):

    percent = max(0, min(100, percent))

    width = 12
    filled = int(width * percent / 100)

    bar = "━" * filled + "─" * (width - filled)

    sys.stdout.write(
        "\r\033[K"
        + CYAN + f"  {stage:<19}"
        + BLUE + f"[{bar}] "
        + GREEN + f"{percent:3d}%"
    )

    sys.stdout.flush()


# =====================================
# INSTALL PACKAGE
# =====================================

def install(package):

    if not re.fullmatch(r"[A-Za-z0-9_.-]+", package):
        print(RED + "  Invalid package name.")
        return

    if package in (".", ".."):
        print(RED + "  Invalid package name.")
        return

    if shutil.which("git") is None:
        print(RED + "  Git is not installed.")
        return

    parent = Path.cwd()
    target = parent / package

    if target.exists():
        print(YELLOW + f"  {package} already exists.")
        return

    url = f"https://github.com/{OWNER}/{package}.git"

    print()
    print(CYAN + f"  Installing {package}")
    print()

    temp_path = None
    errors = []

    def process_line(line):

        line = line.strip()

        if not line:
            return

        match = re.search(
            r"(Receiving objects|Resolving deltas|"
            r"Updating files):\s*(\d+)%",
            line
        )

        if match:

            stage = match.group(1)
            percent = int(match.group(2))

            progress_bar(percent, stage)

        else:

            errors.append(line)

            if len(errors) > 8:
                errors.pop(0)

    try:

        temp_path = Path(tempfile.mkdtemp(
            prefix=f".nexvion-{package}-",
            dir=parent
        ))

        temp_path.rmdir()

        process = subprocess.Popen(
            [
                "git",
                "clone",
                "--progress",
                url,
                str(temp_path)
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            bufsize=0
        )

        buffer = b""

        while True:

            char = process.stderr.read(1)

            if not char:
                break

            if char in (b"\r", b"\n"):

                line = buffer.decode(
                    "utf-8",
                    errors="replace"
                )

                buffer = b""

                process_line(line)

            else:

                buffer += char

        if buffer:

            process_line(
                buffer.decode(
                    "utf-8",
                    errors="replace"
                )
            )

        return_code = process.wait()

        if return_code != 0:

            print("\r\033[K")
            print(RED + "  Installation failed!")

            for error in errors[-4:]:
                print(YELLOW + "  " + error)

            return

        if not temp_path.is_dir():

            print(RED + "  Clone directory not found.")
            return

        shutil.move(str(temp_path), str(target))
        temp_path = None

        progress_bar(100, "Completed")

        print()
        print()

        print(
            GREEN
            + f"  ✓ {package} installed successfully!"
        )

        print(CYAN + f"  Location: {target}")
        print()

    except KeyboardInterrupt:

        print()
        print(YELLOW + "  Installation cancelled.")

    except Exception as error:

        print()
        print(RED + f"  Error: {error}")

    finally:

        if temp_path and temp_path.exists():

            shutil.rmtree(
                temp_path,
                ignore_errors=True
            )


# =====================================
# PACKAGE LIST
# =====================================

def package_list():

    packages = [
        "OpenEngine"
    ]

    print()
    print(CYAN + "  INSTALLED PACKAGES")
    print(DIM + "  ──────────────────────────────")

    for index, package in enumerate(
        packages,
        start=1
    ):

        print(
            BLUE + f"  {index}."
            + CYAN + f" {package}"
        )

    print(DIM + "  ──────────────────────────────")
    print()


# =====================================
# PACKAGE VERSION CHECK
# =====================================

def check_package(package):

    installed_packages = {
        "OpenEngine": "1.0.0"
    }

    if package not in installed_packages:

        print()
        print(RED + f"  ✗ {package} not found.")
        print()

        return

    version = installed_packages[package]

    print()

    print(
        GREEN
        + f"  ✓ {package} latest v{version}"
    )

    print()


# =====================================
# HELP MENU
# =====================================

def help_menu():

    print()
    print(CYAN + "  COMMANDS")
    print(DIM + "  ──────────────────────────────")

    print(WHITE + "  nex install PACKAGE")
    print(DIM + "      Install a GitHub package")

    print(WHITE + "  nex pkg list")
    print(DIM + "      Show installed packages")

    print(WHITE + "  nex check -v PACKAGE")
    print(DIM + "      Check package version")

    print(WHITE + "  nex version")
    print(DIM + "      Show NEXVION version")

    print(WHITE + "  nex help")
    print(DIM + "      Show commands")

    print(WHITE + "  exit")
    print(DIM + "      Close NEXVION")

    print()


# =====================================
# MAIN TERMINAL
# =====================================

def terminal():

    banner()

    while True:

        try:

            command = input(
                BLUE + "  NEXVION"
                + CYAN + " ❯ "
                + WHITE
            ).strip()

            if not command:
                continue

            parts = command.split()

            # EXIT

            if parts[0] == "exit":

                print()
                print(CYAN + "  NEXVION closed.")
                break

            # NEX COMMANDS

            elif parts[0] == "nex":

                # HELP

                if (
                    len(parts) == 2
                    and parts[1] == "help"
                ):

                    help_menu()

                # VERSION

                elif (
                    len(parts) == 2
                    and parts[1] == "version"
                ):

                    print(
                        GREEN
                        + f"  NEXVION {VERSION}"
                    )

                # INSTALL

                elif (
                    len(parts) == 3
                    and parts[1] == "install"
                ):

                    install(parts[2])

                # PACKAGE LIST

                elif (
                    len(parts) == 3
                    and parts[1] == "pkg"
                    and parts[2] == "list"
                ):

                    package_list()

                # PACKAGE VERSION CHECK

                elif (
                    len(parts) == 4
                    and parts[1] == "check"
                    and parts[2] == "-v"
                ):

                    check_package(parts[3])

                # INVALID COMMAND

                else:

                    print(RED + "  Invalid command.")
                    print(YELLOW + "  Type 'nex help'.")

            else:

                print(RED + "  Unknown command.")

        except KeyboardInterrupt:

            print()
            print(YELLOW + "  Use 'exit' to close.")


# =====================================
# ENTRY POINT
# =====================================

if __name__ == "__main__":

    terminal()
