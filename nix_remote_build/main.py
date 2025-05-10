import argparse
import base64
import multiprocessing
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Self
import subprocess
import tempdir
import logging

import toml

# https://nixos.org/manual/nixpkgs/stable/#sec-darwin-builder


def main() -> None:
    args = Args.parse_args()

    if sys.platform == "darwin":
        args.builders.append(
            Builder(
                host="ssh-ng://builder@linux-builder",
                systems=[],
                private_key=Path("/etc/nix/builder_ed25519"),
                max_builds=multiprocessing.cpu_count(),
                speed_factor=None,
                features=["benchmark", "big-parallel"],
                mandatory_features=[],
                public_key="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJBWcxb/Blaqt1auOtE+F8QUWrUotiC5qBJ+UuEWdVCb root@nixos",
            )
        )

    proc = subprocess.
    # nix run nixpkgs#darwin.linux-builder

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
    def parse_args(cls) -> "Self":
        args = cls._argparser().parse_args()

        builders = parse_builders(args.builders) if args.builders else []

        return cls(
            builders=builders,
        )


@dataclass
class Builder:
    host: str
    """The URI of the remote store in the format ssh://[username@]hostname,
    e.g. ssh://nix@mac or ssh://mac. For backward compatibility, ssh:// may be
    omitted. The hostname may be an alias defined in your ~/.ssh/config.
    """

    systems: list[str] | None
    """A comma-separated list of Nix platform type identifiers, such as
    x86_64-darwin. It is possible for a machine to support multiple platform
    types, e.g., i686-linux,x86_64-linux. If omitted, this defaults to the
    local platform type.
    """

    private_key: Path | None
    """The SSH identity file to be used to log in to the remote machine. If
    omitted, SSH will use its regular identities.
    """

    max_builds: int | None
    """The maximum number of builds that Lix will execute in parallel on the
    machine. Typically this should be equal to the number of CPU cores. For
    instance, the machine itchy in the example will execute up to 8 builds in
    parallel.
    """

    speed_factor: int | None
    """The “speed factor”, indicating the relative speed of the machine. If
    there are multiple machines of the right type, Lix will prefer the fastest,
    taking load into account.
    """

    features: list[str] | None
    """A comma-separated list of supported features. If a derivation has the
    requiredSystemFeatures attribute, then Lix will only perform the derivation
    on a machine that has the specified features.
    """

    mandatory_features: list[str] | None
    """A comma-separated list of mandatory features. A machine will only be
    used to build a derivation if all of the machine’s mandatory features
    appear in the derivation’s requiredSystemFeatures attribute.
    """

    public_key: Path | str | None
    """A path to the public host key of the remote machine, or the public host key.

    This is NOT base64-encoded.
    """

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        host = data["host"]
        systems = data.get("systems", None)

        private_key_ = data.get("private_key", None)
        private_key = Path(private_key_) if private_key_ else None

        max_builds = data.get("max_builds", None)
        speed_factor = data.get("speed_factor", None)
        features = data.get("features", None)
        mandatory_features = data.get("mandatory_features", None)

        public_key_ = data.get("public_key", None)
        if public_key_ is not None:
            public_key = Path(public_key_)
            if not public_key.exists():
                public_key = public_key_
        else:
            public_key = public_key_

        return cls(
            host=host,
            systems=systems,
            private_key=private_key,
            max_builds=max_builds,
            speed_factor=speed_factor,
            features=features,
            mandatory_features=mandatory_features,
            public_key=public_key,
        )

    def as_nix_config(self) -> str:
        ret = [self.host]

        ret.append(",".join(self.systems) if self.systems else "-")
        ret.append(str(self.private_key) if self.private_key is not None else "-")
        ret.append(str(self.max_builds) if self.max_builds is not None else "-")
        ret.append(str(self.speed_factor) if self.speed_factor is not None else "-")
        ret.append(",".join(self.features) if self.features else "-")
        ret.append(
            ",".join(self.mandatory_features) if self.mandatory_features else "-"
        )

        if self.public_key is not None:
            if isinstance(self.public_key, Path):
                public_key_bytes = self.public_key.read_bytes()
            else:
                public_key_bytes = self.public_key.encode("utf-8")

            ret.append(base64.standard_b64encode(public_key_bytes).decode("utf-8"))
        else:
            ret.append("-")

        return " ".join(ret)


def parse_builders(path: Path) -> list[Builder]:
    raw = toml.load(path)
    return [Builder.from_dict(builder) for builder in raw["builders"]]


if __name__ == "__main__":
    main()
