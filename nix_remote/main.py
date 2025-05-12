import sys
import tempfile
import textwrap
from pathlib import Path

from loguru import logger

from nix_remote.args import Args
from nix_remote.builder import Builder
from nix_remote.darwin import DARWIN_BUILDER_INSTALLABLE, start_darwin_builder
from nix_remote.sudo import check_sudo


def main() -> None:
    args = Args.parse_args()

    check_sudo()

    if sys.platform == "darwin":
        logger.info(f"Running on macOS, starting {DARWIN_BUILDER_INSTALLABLE}")

        args.builders.append(Builder.darwin_builder())

        logger.info(f"{Builder.darwin_builder().as_nix_config()}")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            with start_darwin_builder(cwd=tmpdir) as proc:
                logger.info(proc)

    nix_config = textwrap.dedent(
        """
        builders = {builders}

        # Not strictly necessary, but this will reduce your disk utilization
        builders-use-substitutes = true
        """.format(
            builders=" ; ".join([builder.as_nix_config() for builder in args.builders])
        )
    )

    env = {
        "NIX_CONFIG": nix_config,
    }

    logger.info(f"env: {env}")


if __name__ == "__main__":
    main()
