
import os
import re
import sys
import shutil
import tempfile
import subprocess
from pathlib import Path

from colorama import Fore, Style, init

init(autoreset=True)

OWNER = "uddinmdsamal-wq"
VERSION = "1.0.0"


def banner():
    print(Fore.CYAN + Style.BRIGHT + """
 _   _ _____  __     ______  _  ___  _   _
| \ | | ____| \ \   / /  _ \| |/ / \| | | |
|  \| |  _|    \ \ / /| |_) | ' /|  \| | | |
| |\  | |___    \ V / |  __/| . \| |\  | |_| |
|_| \_|_____|    \_/  |_|   |_|\_\_| \_|\___/

""" + Style.RESET_ALL)

    print(Fore.GREEN + "       NEXVION PACKAGE MANAGER")
    print(Fore.MAGENTA + f"              VERSION {VERSION}")
    print(Fore.CYAN + "-" * 48)


def progress_bar(percent, stage):
    percent = max(0, min(100, percent))

    width = 30
    filled = int(width * percent / 100)
    bar = "█" * filled + "░" * (width - filled)

    sys.stdout.write(
        "\r" + Fore.CYAN + f"{stage:<20} "
        + Fore.GREEN + f"[{bar}] "
        + Fore.MAGENTA + f"{percent:3d}%"
    )
    sys.stdout.flush()


def install(package):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", package):
        print(Fore.RED + "Invalid package name.")
        return

    if package in (".", ".."):
        print(Fore.RED + "Invalid package name.")
        return

    if shutil.which("git") is None:
        print(Fore.RED + "Git is not installed.")
        return

    parent = Path.cwd()
    target = parent / package

    if target.exists():
        print(Fore.YELLOW + f"{package} already exists.")
        return

    url = f"https://github.com/{OWNER}/{package}.git"

    print()
    print(Fore.CYAN + Style.BRIGHT +
          f"Installing {package}...")
    print()

    temp_path = None
    errors = []

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
                    "utf-8", errors="replace"
                )
                buffer = b""

                match = re.search(
                    r"(Receiving objects|Resolving deltas|"
                    r"Updating files):\s*(\d+)%",
                    line
                )

                if match:
                    stage = match.group(1)
                    percent = int(match.group(2))
                    progress_bar(percent, stage)

                elif line.strip():
                    errors.append(line.strip())
                    errors = errors[-8:]

            else:
                buffer += char

        return_code = process.wait()

        if return_code != 0:
            print()

            print(Fore.RED + "Installation failed!")

            for error in errors[-4:]:
                print(Fore.YELLOW + error)

            return

        if not temp_path.is_dir():
            print(Fore.RED + "Clone directory not found.")
            return

        shutil.move(str(temp_path), str(target))
        temp_path = None

        print()
        print()
        print(Fore.GREEN + Style.BRIGHT +
              f"✓ {package} installed successfully!")

        print(Fore.CYAN + f"Location: {target}")

    except KeyboardInterrupt:
        print()
        print(Fore.YELLOW + "Installation cancelled.")

    except Exception as error:
        print()
        print(Fore.RED + f"Error: {error}")

    finally:
        if temp_path and temp_path.exists():
            shutil.rmtree(temp_path, ignore_errors=True)


def help_menu():
    print(Fore.CYAN + """
Available commands:

  nex install PACKAGE
  nex help
  nex version
  exit
""")


def terminal():
    banner()

    print(Fore.GREEN + "NEXVION is ready.")
    print(Fore.YELLOW + "Type 'nex help' for commands.")

    while True:
        try:
            command = input(
                Fore.MAGENTA + "\nnex > " +
                Fore.WHITE
            ).strip()

            if not command:
                continue

            parts = command.split()

            if parts[0] == "exit":
                print(Fore.CYAN + "NEXVION closed.")
                break

            elif parts[0] == "nex":

                if len(parts) == 2 and parts[1] == "help":
                    help_menu()

                elif len(parts) == 2 and parts[1] == "version":
                    print(Fore.GREEN + VERSION)

                elif (
                    len(parts) == 3
                    and parts[1] == "install"
                ):
                    install(parts[2])

                else:
                    print(Fore.RED + "Invalid command.")
                    print(Fore.YELLOW + "Type nex help.")

            else:
                print(Fore.RED + "Unknown command.")

        except KeyboardInterrupt:
            print()
            print(Fore.YELLOW + "Use exit to close.")


if __name__ == "__main__":
    terminal()
