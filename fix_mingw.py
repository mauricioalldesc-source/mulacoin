import sys
path = "/usr/share/mingw-w64/include/winbase.h"
fix = (
    "#ifndef _PROCESSOR_NUMBER_DEFINED\n"
    "#define _PROCESSOR_NUMBER_DEFINED\n"
    "typedef struct _PROCESSOR_NUMBER {\n"
    "  WORD Group;\n"
    "  BYTE Number;\n"
    "  BYTE Reserved;\n"
    "} PROCESSOR_NUMBER, *PPROCESSOR_NUMBER;\n"
    "#endif\n\n"
)
with open(path) as f:
    content = f.read()
if "_PROCESSOR_NUMBER_DEFINED" in content:
    print("Already fixed!")
    sys.exit(0)
if "GetNumaProcessorNodeEx" not in content:
    print("Marker not found!")
    sys.exit(1)
idx = content.index("GetNumaProcessorNodeEx")
nl = content.rfind("\n", 0, idx) + 1
content = content[:nl] + fix + content[nl:]
with open(path, "w") as f:
    f.write(content)
print("Fix applied!")
