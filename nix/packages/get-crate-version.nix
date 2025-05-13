{
  lib,
  writeShellApplication,
  nix-remote,
}:
writeShellApplication {
  name = "get-crate-version";

  text = ''
    echo ${lib.escapeShellArg nix-remote.version}
  '';
}
