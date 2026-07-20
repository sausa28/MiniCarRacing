import io
from dataclasses import dataclass


def main():
    path = "game/datfile.dat"
    output_dir = "data"

    with open(path, "rb") as f:
        header = read_header(f)

        for (i, segment) in enumerate(header.data_segments):
            target_file = f"{output_dir}/{i:03d}.dat"
            print("Extracting", target_file)
            extract_segment_to_file(f, segment, target_file)


@dataclass
class DataSegmentInfo:
    offset: int
    length: int


@dataclass
class Header:
    data_segments: list[DataSegmentInfo]
    segment_count: int


def read_header(datfile: io.BufferedReader) -> Header:
    datfile.seek(0, 0)
    first_offset = int.from_bytes(datfile.read(4), byteorder='little')
    segment_count = first_offset // 8

    data_segments = []
    datfile.seek(0, 0)
    for i in range(segment_count):
        offset = int.from_bytes(datfile.read(4), byteorder='little')
        length = int.from_bytes(datfile.read(4), byteorder='little')
        segment = DataSegmentInfo(offset, length)
        data_segments.append(segment)

    return Header(data_segments, segment_count)


def extract_segment_to_file(datfile: io.BufferedReader, segment: DataSegmentInfo, file: str):
    datfile.seek(segment.offset, 0)
    data = datfile.read(segment.length)

    with open(file, "wb") as target:
        target.write(data)


main()

"""
For the file types of each dat file, these are my suspisions:
- 0-51 are the largest, and so are almost certainly the tracks.
- 315 revealed itself to be a .wav file by leaving in the header. By comparing the binviz of 315 with other files, I suspect there are many audio files that just stripped the wav header.
- So, 309 to 373 are the audio files I think. How do I test it?
"""
