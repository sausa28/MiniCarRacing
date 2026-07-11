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
    buf_id: int
    offset: int
    length: int


def get_file_segments_from_func_calls(func_calls: list[FuncCall]):
    offset = 0
    file_segments = []

    for call in func_calls:
        if (call.name == "ReadFile"):
            buf_id = call.args[1]
            bytes_to_read = call.args[2]
            segment = FileSegment()
            segment.buf_id = buf_id
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

    return file_segments


def main():
    logpath = "fileactions_race.log"
    lines = []
    with open(logpath, "r") as f:
        lines = f.readlines()

    func_calls = []
    for line in lines:
        func_calls.append(parse_line(line))

    file_segments = get_file_segments_from_func_calls(func_calls)
    for segment in file_segments:
        print("Buf_id:", segment.buf_id, "Offset:", segment.offset, "Length:", segment.length)


main()
