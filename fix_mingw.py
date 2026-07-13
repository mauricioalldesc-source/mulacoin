import sys

path = "/usr/share/mingw-w64/include/winbase.h"
# Incluir winnt.h antes do bloco que usa PPROCESSOR_NUMBER
fix = '#include <winnt.h> // Fix: needed for PROCESSOR_NUMBER\n'

with open(path) as f:
    content = f.read()

if 'Fix: needed for PROCESSOR_NUMBER' in content:
    print("Already fixed!")
    sys.exit(0)

if "GetNumaProcessorNodeEx" not in content:
    print("Marker not found!")
    sys.exit(1)

# Encontrar o bloco #if que contém GetNumaProcessorNodeEx
idx = content.index("GetNumaProcessorNodeEx")
# Voltar ate o #if mais proximo
block_start = content.rfind("\n#if", 0, idx)
if block_start == -1:
    block_start = content.rfind("\n", 0, idx) + 1
else:
    block_start += 1

content = content[:block_start] + fix + content[block_start:]

with open(path, "w") as f:
    f.write(content)

print("Fix applied: winnt.h included before PROCESSOR_NUMBER usage!")
