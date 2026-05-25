{
  description = "Lyric Utils Flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      systemDeps = with pkgs; [
        stdenv.cc.cc.lib
        ffmpeg
      ];
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [
          pkgs.python311
          pkgs.uv
          pkgs.ffmpeg
        ];
        shellHook = ''
          export LD_LIBRARY_PATH="/usr/lib/wsl/lib:${pkgs.lib.makeLibraryPath systemDeps}:$LD_LIBRARY_PATH"
          source .venv/bin/activate
          echo "Loaded lyricutil environment"
          export TORCHAUDIO_USE_TORCHCODEC=0
        '';
      };
    };
}
