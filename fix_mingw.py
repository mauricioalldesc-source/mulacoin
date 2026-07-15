import sys

# O problema: windows.h inclui winnt.h (linha 69) e winbase.h (linha 70)
# winbase.h inclui processthreadsapi.h (linha 29)
# processthreadsapi.h usa PPROCESSOR_NUMBER mas winnt.h ainda nao foi carregado
# porque windows.h inclui winbase.h antes de winnt.h processar completamente

# Solucao: adicionar #include <winnt.h> no inicio do processthreadsapi.h
path = "/usr/share/mingw-w64/include/processthreadsapi.h"
with open(path) as f:
    lines = f.readlines()

print(f"Primeiras 10 linhas de processthreadsapi.h:")
for i, l in enumerate(lines[:10]):
    print(f"  {i}: {l.rstrip()}")

# Verificar se ja tem winnt.h
has_winnt = any('winnt' in l.lower() for l in lines[:20])
print(f"Ja tem winnt.h: {has_winnt}")

if not has_winnt:
    # Inserir apos os guards de include (#ifndef/#define)
    insert_at = 0
    for i, line in enumerate(lines[:10]):
        if line.strip().startswith('#define') and '_PROCESSTHREADSAPI' in line:
            insert_at = i + 1
            break
    
    lines.insert(insert_at, '#include <winnt.h> /* Fix: needed before PPROCESSOR_NUMBER */\n')
    
    with open(path, 'w') as f:
        f.writelines(lines)
    print(f"winnt.h inserido na linha {insert_at}!")
else:
    print("ja tem winnt.h, verificando o problema...")
    for i, l in enumerate(lines):
        if 'PPROCESSOR_NUMBER' in l:
            print(f"  Primeiro uso linha {i}: {l.rstrip()}")
            break
