
{ pkgs }: {
  deps = [
    pkgs.nss
    pkgs.qtwebengine
    pkgs.qt5.full
    pkgs.libGL
    pkgs.libGLU
    pkgs.pkg-config
  ];
}
