import sys

fix_line = (
    "/* MinGW fix: forward declare PROCESSOR_NUMBER */\n"
    "#if !defined(_PROCESSOR_NUMBER_) && defined(_WIN32_WINNT) && _WIN32_WINNT >= 0x0601\n"
    "#define _PROCESSOR_NUMBER_\n"
    "typedef struct _PROCESSOR_NUMBER { WORD Group; BYTE Number; BYTE Reserved; } PROCESSOR_NUMBER, *PPROCESSOR_NUMBER;\n"
    "#endif\n"
)

# Fix processthreadsapi.h - inserir antes do primeiro uso de PPROCESSOR_NUMBER
path1 = "/usr/share/mingw-w64/include/processthreadsapi.h"
with open(path1) as f:
    content = f.read()

if "_PROCESSOR_NUMBER_" not in content and "PPROCESSOR_NUMBER" in content:
    idx = content.index("PPROCESSOR_NUMBER")
    nl = content.rfind("\n", 0, idx) + 1
    # Voltar ate o #if
    block = content.rfind("\n#if", 0, nl)
    if block != -1:
        insert_pos = block + 1
    else:
        insert_pos = nl
    content = content[:insert_pos] + fix_line + content[insert_pos:]
    with open(path1, "w") as f:
        f.write(content)
    print("processthreadsapi.h corrigido!")
else:
    print("processthreadsapi.h: ja corrigido ou PPROCESSOR_NUMBER nao encontrado")

# Fix winbase.h - inserir antes do primeiro uso de PPROCESSOR_NUMBER
path2 = "/usr/share/mingw-w64/include/winbase.h"
with open(path2) as f:
    content = f.read()

if "_PROCESSOR_NUMBER_" not in content and "PPROCESSOR_NUMBER" in content:
    idx = content.index("PPROCESSOR_NUMBER")
    nl = content.rfind("\n", 0, idx) + 1
    block = content.rfind("\n#if", 0, nl)
    if block != -1:
        insert_pos = block + 1
    else:
        insert_pos = nl
    content = content[:insert_pos] + fix_line + content[insert_pos:]
    with open(path2, "w") as f:
        f.write(content)
    print("winbase.h corrigido!")
else:
    print("winbase.h: ja corrigido ou PPROCESSOR_NUMBER nao encontrado")
