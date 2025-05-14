{
  lib,
  newScope,
  inputs,
}:
lib.makeScope newScope (
  self:
  {
    inherit inputs;
  }
  // (lib.packagesFromDirectoryRecursive {
    # See: https://github.com/NixOS/nixpkgs/pull/406885
    directory = ./packages;
    inherit (self) callPackage;
  })
)
