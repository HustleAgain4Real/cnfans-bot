
{ pkgs }: {
  deps = [
    pkgs.python310
    pkgs.python310Packages.pip
    pkgs.libffi
    pkgs.openssl
  ];
}
