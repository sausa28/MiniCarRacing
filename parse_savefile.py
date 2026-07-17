import argparse
from dataclasses import dataclass
from datetime import timedelta


def main():
    parser = argparse.ArgumentParser(
        description="A script to parse the save file format for Mini Car Racing.")
    _ = parser.add_argument("filepath",
        type=str,
        help="The path to the MiniCarRacing.ini file to parse")

    args = parser.parse_args()
    filepath: str = args.filepath  # pyright: ignore[reportAny]

    with open(filepath, 'rb') as f:
        filebytes = f.read()

    parse_file(filebytes)


@dataclass
class Header:
    car_graphics: str
    sound_volume: int
    multiplayer_selections: list[int | None]


@dataclass
class Timetrials:
    player_names: list[str | None]
    record_times: list[timedelta | None]

@dataclass
class SaveSlot:
    league: int
    # TODO: Add the rest of the save slot data

@dataclass
class PlayerData:
    name: str
    controls: dict[str, str]
    color_pref: int
    save_slots: list[SaveSlot | None]

@dataclass
class MiniCarRacingIniFile:
    header: Header
    timetrials: Timetrials
    players: list[PlayerData | None]


def parse_file(filebytes: bytes):
    file_len = 27764
    if len(filebytes) != file_len:
        raise Exception(f"Expected length of file to be {file_len} but was {len(filebytes)}")

    headerbytes = filebytes[:16]
    header = header_from_bytes(headerbytes)
    print(header)
    pass

def header_from_bytes(headerbytes: bytes) -> Header:
    if len(headerbytes) != 16:
        raise Exception("Header should be 16 bytes long")

    car_graphics_val = int.from_bytes(headerbytes[:4], byteorder='little')
    match (car_graphics_val):
        case 0:
            car_graphics = "Normal"
        case 1:
            car_graphics = "Good"
        case 2:
            car_graphics = "Excellent"
        case _:
            print("WARN: Invalid car graphics value")
            car_graphics = "Invalid"

    volume = headerbytes[10]
    if volume > 100:
        print("WARN: Invalid volume value")

    mul_selection_bytes = headerbytes[11:15]
    mul_selections: list[int | None] = []
    for x in mul_selection_bytes:
        if x == 255:
            mul_selections.append(None)
            continue
        if x >= 8:
            print("WARN: Invalid multiplayer selection value")
        mul_selections.append(x)

    return Header(car_graphics, volume, mul_selections)



main()
