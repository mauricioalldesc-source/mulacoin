import sys

# O problema: windows.h inclui winnt.h DEPOIS de winbase.h
# winbase.h usa PPROCESSOR_NUMBER que so' e' definido em winnt.h
# Solucao: no windows.h, mover winnt.h para antes de winbase.h

path = "/usr/share/mingw-w64/include/windows.h"
with open(path) as f:
    content = f.read()

print("Linhas com winnt e winbase:")
for i, line in enumerate(content.split('\n')):
    if 'winnt' in line.lower() or 'winbase' in line.lower():
        print(f"  {i}: {line.strip()}")

# Ver a ordem atual
winnt_pos = content.lower().find('winnt')
winbase_pos = content.lower().find('winbase')
print(f"\nwinnt pos: {winnt_pos}, winbase pos: {winbase_pos}")
if winnt_pos > winbase_pos:
    print("PROBLEMA: winnt vem DEPOIS de winbase!")
else:
    print("OK: winnt vem antes de winbase")
