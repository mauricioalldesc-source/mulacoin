import sys, os

path = "/usr/share/mingw-w64/include/winbase.h"
marker = "GetNumaProcessorNodeEx"
include_fix = "#include <winnt.h>\n"

with open(path) as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
fixed = False
for i, line in enumerate(lines):
    if marker in line:
        print(f"Found marker at line {i}: {line.strip()}")
        if i > 0 and "winnt.h" not in lines[i-1]:
            lines.insert(i, include_fix)
            fixed = True
            print(f"Inserted include at line {i}")
        break

if fixed:
    with open(path, "w") as f:
        f.writelines(lines)
    print("Fix applied!")
else:
    print("Already fixed or marker not found")
