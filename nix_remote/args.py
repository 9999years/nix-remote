import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from nix_remote.builder import Builder


@dataclass
class Args:
    builders: list["Builder"]

    @classmethod
    def _argparser(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--builders",
            type=Path,
            help="Path to a TOML file containing builder definitions",
        )
        return parser

    @classmethod
    def parse_args(cls) -> Self:
        args = cls._argparser().parse_args()

        builders = Builder.parse_from_config(args.builders) if args.builders else []

        return cls(
            builders=builders,
        )
