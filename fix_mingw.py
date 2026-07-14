import sys

path = "/usr/share/mingw-w64/include/winbase.h"
marker = "GetNumaProcessorNodeEx"
typedef_fix = (
    "typedef struct _PROCESSOR_NUMBER { WORD Group; BYTE Number; BYTE Reserved; }"
    " PROCESSOR_NUMBER, *PPROCESSOR_NUMBER; /* MinGW fix */\n"
)

with open(path) as f:
    lines = f.readlines()

# Encontrar o bloco #if que contém o marker
for i, line in enumerate(lines):
    if marker in line:
        print(f"Marker na linha {i}: {line.strip()}")
        # Procurar o #if mais próximo acima
        for j in range(i-1, max(0, i-20), -1):
            print(f"  {j}: {lines[j].strip()}")
            if lines[j].strip().startswith("#if") or lines[j].strip().startswith("#ifdef"):
                # Inserir o typedef logo após o #if
                if "PROCESSOR_NUMBER" not in lines[j+1]:
                    lines.insert(j+1, typedef_fix)
                    print(f"typedef inserido na linha {j+1}")
                break
        break

with open(path, "w") as f:
    f.writelines(lines)
print("Fix aplicado!")
