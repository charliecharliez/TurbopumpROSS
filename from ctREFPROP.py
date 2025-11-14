from ctREFPROP.ctREFPROP import REFPROPFunctionLibrary
import os

# If you know the exact folder containing REFPRP64.DLL, set it here:
dll_path = r"C:\Users\zhu1271\OneDrive - purdue.edu\PURPL\Simulation\TurbopumpROSS"

os.environ["RPPREFIX"] = dll_path

RP = REFPROPFunctionLibrary(dll_path + r"\REFPRP64.DLL")

result = RP.REFPROPd("Water", "T", "P", 0, 0, 0, 300, 101325, [1.0])
print(result)