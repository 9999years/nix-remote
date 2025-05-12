import subprocess

from loguru import logger


def check_sudo() -> None:
    logger.info("Checking `sudo` access")
    proc = subprocess.run(
        ["sudo", "whoami"], stdout=subprocess.PIPE, check=True, text=True
    )

    if proc.stdout.strip() != "root":
        raise PermissionError("nix-remote requires root privileges")
