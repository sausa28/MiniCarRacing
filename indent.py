indent_count = 0
indent = "|"
with open("wine.log", "r") as logfile:
    for line in logfile:
        if line.find("Call", 0, 20) > 0:
            print(indent*indent_count + line, end='')
            indent_count += 1
        elif line.find("Ret", 0, 20) > 0:
            indent_count -= 1
            print(indent*indent_count + line, end='')
        else:
            print(indent*indent_count + line, end='')

