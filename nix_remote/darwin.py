import contextlib
import subprocess
from pathlib import Path
from typing import Generator

from loguru import logger

from nix_remote.backoff import Backoff, BackoffTimeout
from nix_remote.builder import Builder

# https://nixos.org/manual/nixpkgs/stable/#sec-darwin-builder
DARWIN_BUILDER_INSTALLABLE: str = "nixpkgs#darwin.linux-builder"


@contextlib.contextmanager
def start_darwin_builder(cwd: Path) -> Generator[subprocess.Popen[bytes], None, None]:
    builder = Builder.darwin_builder()

    private_key = cwd / "keys" / "builder_ed25519"
    logger.debug(f"Builder key: {private_key!s}")

    proc = subprocess.Popen(["nix", "run", DARWIN_BUILDER_INSTALLABLE], cwd=cwd)

    try:
        for _ in Backoff():
            try:
                subprocess.run(
                    [
                        "ssh",
                        "-i",
                        str(private_key),
                        builder.host.removeprefix("ssh-ng://"),
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                logger.trace(f"Failed to connect to {builder.host}: {e.stderr.strip()}")

            if (returncode := proc.poll()) is not None:
                raise subprocess.CalledProcessError(
                    returncode=returncode, cmd=proc.args
                )

        yield proc
    except BackoffTimeout:
        logger.error(f"Failed to start {DARWIN_BUILDER_INSTALLABLE}")
        raise
    finally:
        logger.info(f"Killing {DARWIN_BUILDER_INSTALLABLE}")
        proc.terminate()
        proc.kill()
