# Mulacoin

Fork do código-fonte do **Dogecoin Core** (que por sua vez é um fork do Litecoin/Bitcoin),
customizado com as seguintes regras:

| Parâmetro | Valor |
|---|---|
| Ticker | **FazoL** |
| Algoritmo de mineração | Scrypt (igual Dogecoin/Litecoin) |
| Tempo de bloco | 1 minuto (igual Dogecoin) |
| Recompensa por bloco | **13 FazoL fixos, para sempre** (sem halving) |
| Prefixo de endereço | endereços começam com **"M"** |
| Mensagem ao receber moedas | **"Picanha Cumpanheiro! 🍖🐮"** |
| Genesis block | exclusivo da Mulacoin (não é o genesis do Dogecoin) |

## O que foi alterado no código

1. **`src/dogecoin.cpp`** — função `GetDogecoinBlockSubsidy()` reescrita para retornar
   sempre `13 * COIN`, independente da altura do bloco. Removida toda a lógica de
   halving/recompensa-aleatória original do Dogecoin.

2. **`src/amount.cpp`** e **`src/qt/bitcoinunits.cpp`** — ticker trocado de `DOGE` para `FazoL`
   (incluindo as variações `mFazoL`, `kFazoL`, `MFazoL`, `μFazoL` exibidas na carteira).

3. **`src/qt/bitcoingui.cpp`** — a notificação que aparece quando uma transação chega
   (`incomingTransaction`) agora mostra **"Picanha Cumpanheiro! 🍖🐮"** em vez de
   "Incoming transaction". Isso é o equivalente ao clássico "Wow, such coin!" do Dogecoin.

4. **`src/chainparams.cpp`** (rede principal / `CMainParams`):
   - Novo **genesis block**, minerado especificamente para a Mulacoin (script usado:
     `genesis_miner.py`, incluído aqui). Mensagem do genesis:
     *"Mulacoin - Picanha pro Cumpanheiro - 25/Jun/2026"*.
   - `pchMessageStart` (magic bytes da rede P2P) trocados para não colidir com a rede do Dogecoin.
   - Porta padrão trocada de 22556 para **23556**.
   - Prefixos base58 trocados: endereços agora começam com **"M"** (PUBKEY_ADDRESS=50) e
     endereços de script com **"6"** (SCRIPT_ADDRESS=13).
   - DNS seeds e checkpoints antigos do Dogecoin removidos (é uma rede nova, do zero).
   - `nPowTargetSpacing` continua em 60 segundos (1 minuto) — já era o padrão do Dogecoin,
     não precisou mudar.

## Como compilar

Este código segue o mesmo processo de build do Bitcoin/Dogecoin Core (autotools + Boost +
OpenSSL/libssl + libevent + Berkeley DB 4.8 para a carteira, e Qt5 se quiser a GUI gráfica).

Num Ubuntu/Debian, de forma resumida:

```bash
sudo apt-get update
sudo apt-get install -y build-essential libtool autotools-dev automake pkg-config \
    libssl-dev libevent-dev bsdmainutils python3 \
    libboost-system-dev libboost-filesystem-dev libboost-chrono-dev \
    libboost-test-dev libboost-thread-dev

# Berkeley DB 4.8 (a versão exata que o Bitcoin/Dogecoin Core espera) precisa
# normalmente ser compilada à parte com o script em contrib/install_db4.sh

# Para a carteira gráfica (GUI), instale também:
sudo apt-get install -y qtbase5-dev qttools5-dev qttools5-dev-tools

cd mulacoin
./autogen.sh
./configure --with-incompatible-bdb   # ou apontando para sua libdb 4.8 compilada
make -j$(nproc)
```

Isso vai gerar `src/dogecoind`, `src/dogecoin-cli` e (se compilou com Qt) `src/qt/dogecoin-qt`
— os nomes dos binários ainda usam "dogecoin" internamente (renomear os binários/strings de
build é trivial, mas não foi feito aqui para manter o foco nas regras de consenso que você pediu).

## Como testar rapidinho (sem precisar configurar rede nenhuma)

Use o modo `regtest`, que já vem com um genesis "de brinquedo" e te deixa minerar blocos
manualmente, instantaneamente:

```bash
./src/dogecoind -regtest -daemon
./src/dogecoin-cli -regtest generate 5      # gera 5 blocos, 13 FazoL cada
./src/dogecoin-cli -regtest getbalance      # confere o saldo em FazoL
```

Isso já é suficiente pra confirmar que a recompensa está em 13 por bloco e que o ticker
aparece como FazoL.

## Como rodar a rede "de verdade" (mainnet própria)

Como é uma rede nova, ainda não existem outros nós rodando. Pra ter mais de uma carteira
conversando entre si:

1. Compile e rode o `dogecoind` em duas máquinas (ou duas pastas-datadir diferentes na mesma
   máquina, com `-port=` diferentes).
2. Conecte uma na outra manualmente: `./src/dogecoin-cli -addnode=IP:23556 add`.
3. Quando a rede crescer, você pode subir um servidor DNS seed e adicionar a linha
   `vSeeds.push_back(...)` de volta no `chainparams.cpp`, igual o Dogecoin original tinha.

## Avisos importantes

- Este código **não foi auditado**. É um fork educacional/meme, não uma fork pronta para
  produção com valor real. Antes de qualquer uso com dinheiro de verdade, vale revisar com
  calma toda a árvore de parâmetros de consenso (alguns detalhes legados do Dogecoin sobre
  múltiplos estágios de dificuldade/algoritmo continuam no código, embora não afetem o
  funcionamento básico).
- O genesis block foi minerado e validado localmente (o script `genesis_miner.py` reproduz
  primeiro o genesis real do Dogecoin byte-a-byte pra confirmar que a lógica de hash está
  certa, e só depois minera o genesis novo da Mulacoin).

## Testado de ponta a ponta (não é só teoria)

Tudo abaixo foi efetivamente compilado e executado, não apenas inspecionado no código:

1. **Build sem carteira/GUI** (`--disable-wallet --without-gui`) — node `dogecoind` rodando
   em modo `regtest`, minerando blocos reais via RPC. Recompensa confirmada em **13.0**
   direto na transação coinbase (`getblock ... 2`).
2. **Build com carteira** (`--with-incompatible-bdb`, usando o Berkeley DB 5.3 do próprio
   Ubuntu) — carteira real criando endereços, recebendo recompensas de mineração, enviando
   transações entre endereços próprios, com taxa de rede calculada e confirmação em bloco.
3. **Build com GUI completa** (`--with-gui=qt5`) — a carteira gráfica `dogecoin-qt` rodando
   de verdade (via Xvfb + `twm`, já que o ambiente de build não tem monitor), com:
   - Saldos exibidos em **FazoL**
   - Endereços começando com **"M"**
   - A notificação de recebimento mostrando o título **"Picanha Cumpanheiro! 🍖🐮"**
4. **Prefixo de endereço do regtest** também ajustado pra "M" (`PUBKEY_ADDRESS=50`,
   igual ao mainnet), só por consistência visual nos testes — mudança puramente cosmética.
5. **Localização em português (pt_BR)**:
   - Idioma **padrão** da carteira, sem precisar passar `-lang=` (prioridade:
     `-lang` na linha de comando > escolha do usuário em Configurações > padrão pt_BR)
   - Abas "Such Send"/"Much Receive" renomeadas para **"Picanha Enviada"**/**"Picanha
     Recebida"** (texto literal, funciona em qualquer idioma)
   - As 10 frases da "Dica útil do dia" e o respectivo título, todas traduzidas em
     `src/qt/locale/bitcoin_pt_BR.ts`
6. **Identidade visual própria**: o cachorro Shiba Inu original foi substituído por um
   mascote de mula relinchando "QUERO PICANHA!" em todos os lugares onde a imagem
   aparece (tela inicial, ícone do app, "Sobre", bandeja do sistema, `.ico` do Windows,
   `.icns` do Mac). Os arquivos-fonte (SVG) e o símbolo oficial da marca (ferradura + "M")
   estão na pasta `mulacoin-marca/` ao lado deste zip.

Compilar o projeto completo (principalmente a GUI em Qt5) é pesado e pode levar bastante
tempo dependendo da máquina (na máquina de 1 núcleo usada aqui, levou bem mais que em uma
máquina normal com vários núcleos) — mas funciona, do início ao fim.

