import io


class FuncCall:
    name: str
    args: list[int]


def parse_line(line: str) -> FuncCall:
    splits = line.split()
    func_call_str = splits[1]
    name_kernel = func_call_str.split('(')[0]
    name = name_kernel.split('.')[1]

    func_call = FuncCall()
    func_call.name = name

    args_str1 = func_call_str.split('(')[1][:-1]
    if (len(args_str1) > 0):
        args_str2 = args_str1.split(',')
        arg_values = [int(arg, 16) for arg in args_str2]
        func_call.args = arg_values
    else:
        func_call.args = []

    return func_call


class FileSegment:
    buf_ptr: int
    offset: int
    length: int


def get_file_segments_from_func_calls(func_calls: list[FuncCall]):
    offset = 0
    file_segments = []

    for call in func_calls:
        if (call.name == "ReadFile"):
            buf_ptr = call.args[1]
            bytes_to_read = call.args[2]
            segment = FileSegment()
            segment.buf_ptr = buf_ptr
            segment.offset = offset
            segment.length = bytes_to_read
            file_segments.append(segment)
            offset += bytes_to_read
        elif (call.name == "SetFilePointer"):
            distance_to_move_bytes = call.args[1].to_bytes(4)
            distance_to_move = int.from_bytes(distance_to_move_bytes, signed=True)

            distance_to_move_high = call.args[2]
            assert distance_to_move_high == 0

            move_method = call.args[3]
            match move_method:
                case 0:  # FILE_BEGIN
                    offset = distance_to_move
                case 1:  # FILE_CURRENT
                    offset += distance_to_move
                case 2:  # FILE_END
                    raise Exception("We don't know the file end position")

            assert offset >= 0
        else:
            print("Skipping", call.name)

    file_segments = consolidate_file_segments(file_segments)
    return file_segments


def consolidate_file_segments(file_segments: list[FileSegment]):
    consolidated_segs: list[FileSegment] = []

    prev_unfinished = False
    for segment in file_segments:
        if prev_unfinished:
            consolidated_segs[-1].length += segment.length
        else:
            consolidated_segs.append(segment)

        prev_unfinished = (segment.length == 100000)

    return consolidated_segs


def read_file_segment(datfile: io.BufferedReader, segment: FileSegment):
    datfile.seek(segment.offset, 0)
    data = datfile.read(segment.length)

    return data


def main():
    logpath = "fileactions_race.log"
    datfile_path = "game/datfile.dat"
    lines = []
    with open(logpath, "r") as f:
        lines = f.readlines()

    func_calls = []
    for line in lines:
        func_calls.append(parse_line(line))

    file_segments = get_file_segments_from_func_calls(func_calls)

    offsets = []
    lengths = []
    int_index = 0

    with open(datfile_path, "rb") as datfile:
        for segment in file_segments:
            data = read_file_segment(datfile, segment)
            if len(data) == 4:
                print(segment.offset)
                int_le = int.from_bytes(data, byteorder="little")
                if int_index % 2 == 0:
                    offsets.append(int_le)
                else:
                    lengths.append(int_le)
                int_index += 1

    matches = 0
    for i, offset in enumerate(offsets):
        length = lengths[i]
        print(i, offset, length)
        seg_matches = [seg for seg in file_segments
                       if seg.offset == offset and seg.length == length]
        if len(seg_matches) > 0:
            matches += 1

    print(f"Matches: {matches} out of {len(offsets)}")
    # 208 matches out of 594!
    # The missing ones are probably because the logs only covered 1 race.

    # So, based on the above, the format of the datfile is as follows:

    #               0          4         8
    #  Header     |-[offset   ][length  ]
    #             | [offset   ][length  ]
    #             | [offset   ][length  ]
    #             |     ...
    #  Data 0     ->[                   ]
    #                   ...
    #  Data 1     ->[                   ]
    #
    #  The header consists of (offset,length) pairs,
    #  which are each 4 byte LE integers.
    #  The first offset tells you the start of the first data segment,
    #  so everything before that is part of the header.
    #  In the datfile, it first offset is 4752.
    #  So the no. of data segments is 4752 / 8 = 594

    #  I think what I'll do is write a new script
    #  that loads the whole file and extracts individual data segments.


main()
