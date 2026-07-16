import pyghidra
pyghidra.start()

import ghidra
from ghidra.app.util.headless import HeadlessAnalyzer
from ghidra.program.flatapi import FlatProgramAPI
from ghidra.base.project import GhidraProject
from java.lang import String
from ghidra.app.decompiler import DecompInterface

with pyghidra.open_program("minicarracing.exe") as flat_api:
    program = flat_api.getCurrentProgram()
    decompiler = DecompInterface()
    decompiler.openProgram(program)

    programListing = program.getListing()
    print(programListing)
    funcs = programListing.getFunctions(True)

    decompilation = ""
    for func in funcs:
        res = decompiler.decompileFunction(func, 30, None)
        if res.decompileCompleted():
            decompilation += res.getDecompiledFunction().getC()
        else:
            print("Func decomp timed out.", func)

    with open("minicar-decomp.c", 'w') as outfile:
        outfile.write(decompilation)
