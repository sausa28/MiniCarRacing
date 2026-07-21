import argparse
import ctypes
import struct
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
    language: int
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

FILE_LENGTH = 27764
HEADER_LENGTH = 16
TIMETRIALS_LENGTH = 800
PLAYER_DATA_LENGTH = 3368
PLAYER_COUNT = 8

def parse_file(filebytes: bytes):
    if len(filebytes) != FILE_LENGTH:
        raise Exception(f"Expected length of file to be {FILE_LENGTH} but was {len(filebytes)}")

    offset = 0
    headerbytes = filebytes[offset:HEADER_LENGTH]
    offset += HEADER_LENGTH
    header = header_from_bytes(headerbytes)
    print(header)

    timetrials_bytes = filebytes[offset:offset + TIMETRIALS_LENGTH]
    offset += TIMETRIALS_LENGTH
    timetrials = timetrials_from_bytes(timetrials_bytes)
    print(timetrials)

    for _ in range(PLAYER_COUNT):
        playerdata_bytes = filebytes[offset:offset + PLAYER_DATA_LENGTH]
        offset += PLAYER_DATA_LENGTH
        playerdata = player_data_from_bytes(playerdata_bytes)
    pass

def header_from_bytes(headerbytes: bytes) -> Header:
    if len(headerbytes) != HEADER_LENGTH:
        raise Exception(f"Header should be {HEADER_LENGTH} bytes long")

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

    language = headerbytes[9]
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

    return Header(car_graphics, language, volume, mul_selections)


def timetrials_from_bytes(bytes: bytes) -> Timetrials:
    if len(bytes) != TIMETRIALS_LENGTH:
        raise Exception(f"Expected {TIMETRIALS_LENGTH} bytes for timetrials data but got {len(bytes)}")

    names_data = bytes[:16*40]
    times_data = bytes[16*40:]

    times_ints: list[int] = list(struct.unpack("<40i", times_data))

    names: list[str | None] = []
    times: list[timedelta | None] = []
    for i, time in enumerate(times_ints):
        if time == -1:
            names.append(None)
            times.append(None)
        else:
            timedelt = timedelta(seconds=time/120)
            times.append(timedelt)
            name_bytes = names_data[i*16:i*16+16]
            name = ctypes.c_char_p(name_bytes).value
            if name is None:
                print("WARN: Expected valid c string but found null")
                names.append(None)
            else:
                names.append(name.decode("cp1252"))
            
    return Timetrials(names, times)

def player_data_from_bytes(bytes: bytes) -> PlayerData | None:
    if len(bytes) != PLAYER_DATA_LENGTH:
        raise Exception(f"Expected {PLAYER_DATA_LENGTH} bytes but got {len(bytes)}")
    offset = 0
    name_data = bytes[offset:offset+16]; offset += 16
    name = ctypes.c_char_p(name_data).value
    if name is None or len(name) == 0:
        return None

    name = name.decode("cp1252")

    print(name)
    controls_data = bytes[offset:offset+108]; offset += 108
    keycodes: list[int] = []
    controls_count = 9
    for i in range(controls_count):
        raw = controls_data[i*12:i*12 + 12]
        unpacked = struct.unpack("<xBxxxBxxxBxx", raw)
        if unpacked[0] != 4 and unpacked[2] != 1:
            print("WARN Unrecognised key data, possibly a non-keyboard device?")
        assert isinstance(unpacked[1], int)
        keycodes.append(unpacked[1])

    controls: dict[str,int] = {}
    controls["Right"]           = keycodes[0]
    controls["Throttle"]        = keycodes[1]
    controls["Left"]            = keycodes[2]
    controls["Brake"]           = keycodes[3]
    controls["Front Weapon 1"]  = keycodes[4]
    controls["Front Weapon 2"]  = keycodes[5]
    controls["Front Weapon 3"]  = keycodes[6]
    controls["Extra"]           = keycodes[7]
    controls["Rear Weapon"]     = keycodes[8]
    print(controls)
        

    pass


main()
