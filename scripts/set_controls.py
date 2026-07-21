import argparse
import io
import os
import struct
import sys

FILE_LENGTH = 27764
HEADER_LENGTH = 16
TIMETRIALS_LENGTH = 800
PLAYER_DATA_LENGTH = 3368
PLAYER_COUNT = 8
NAME_LENGTH = 16
CONTROLS_COUNT = 9

def main():
    parser = argparse.ArgumentParser(
        description="A script to set all the player controls for testing purposes")
    _ = parser.add_argument("filepath",
        type=str,
        help="The path to the MiniCarRacing.ini file")
    _ = parser.add_argument("i",
        type=int,
        help="The iteration, starting from 0")

    args = parser.parse_args()
    filepath: str = args.filepath  # pyright: ignore[reportAny]
    i: int = args.i  # pyright: ignore[reportAny]

    with open(filepath, "rb+") as file:
        update_control_codes(file, i*CONTROLS_COUNT*PLAYER_COUNT)
    

def update_control_codes(file: io.BufferedRandom, start: int = 0):
    control_code = start
    for i in range(PLAYER_COUNT):
        print("Writing player", i + 1)
        controls_start = HEADER_LENGTH + TIMETRIALS_LENGTH + PLAYER_DATA_LENGTH * i + NAME_LENGTH
        _ = file.seek(controls_start, os.SEEK_SET)
        for _ in range(CONTROLS_COUNT):
            data = struct.pack("xBxxxBxxxBxx", 6, control_code, 1)
            c = file.write(data)
            assert c == 12
            control_code += 1
            if control_code >= 255:
                break
        if control_code >= 255:
            break

            

if __name__ == "__main__":
    sys.exit(main())

