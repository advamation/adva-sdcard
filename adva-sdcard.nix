# Nix-package for adva-sdcard, as standalone-package.
# 
# - build:   ``nix-build adva-sdcard.nix``
# - install: ``nix-env -i adva-sdcard -f adva-sdcard.nix``
#
# :Author:  Advamation / Roland Freikamp <support@advamation.de>
# :Version: 2025-03-17

with import <nixpkgs> {};

stdenv.mkDerivation {
  pname = "adva-sdcard";
  version = "1.2.0";

  src = ./.;
  installFlags = [ "prefix=$(out)" ];

  meta = {
    description = "Advamation SD-card software";
    long_description = ''Get information (CID, SMART) from microSD-/SD-cards.

    Mainly intended to get SMART-/endurance-information from industrial
    microSD-cards, e.g. on a Raspberry Pi.
    '';
    homepage = "https://www.advamation.de";
    license = [ lib.licenses.mit ];
    maintainers = [ lib.maintainers.rkoe ];
    #platforms = with platforms; [ raspberrypi ];
  };
}

