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
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [
          pkgs.python311
          pkgs.uv
        ];
        shellHook = ''
          source .venv/bin/activate
          echo "Loaded lyricutil environment"
        '';
      };
    };
}
