let
  npins = import ./npins;
  pkgs = import npins.nixpkgs.outPath { };
in
pkgs.callPackage (
  {
    mkShell,
    uv,
    python3,
    pyright,
    ruff,
  }:
  mkShell {
    packages = [
      uv
      python3
      pyright
      ruff
    ];
  }
) { }
