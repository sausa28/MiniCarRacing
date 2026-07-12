export STEAM_COMPAT_CLIENT_INSTALL_PATH=$HOME/.steam/steam

export STEAM_COMPAT_DATA_PATH=$HOME/.steam/steam/steamapps/compatdata/2193092650

proton="$HOME/.steam/steam/steamapps/common/Proton 10.0/proton"

cd game
"$proton" run minicarracing.exe
