#!/usr/bin/env python3
"""
Genesis block builder/miner for a Dogecoin-style (scrypt PoW) chain.
Reproduces the exact serialization used in dogecoin/src/chainparams.cpp
CreateGenesisBlock(), so we can both verify against the real Dogecoin
genesis and mine a brand new genesis block for "Mulacoin".
"""
import hashlib
import struct
import time
import sys

COIN = 100000000  # 1 coin = 1e8 base units


def sha256d(b: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(b).digest()).digest()


def scrypt_hash(header80: bytes) -> bytes:
    # Litecoin/Dogecoin scrypt params: N=1024, r=1, p=1, 32-byte output
    return hashlib.scrypt(header80, salt=header80, n=1024, r=1, p=1, dklen=32)


def ser_scriptnum(n: int) -> bytes:
    """Mirrors CScriptNum::serialize() used by CScript::operator<<(int64_t)."""
    if n == 0:
        return b""
    neg = n < 0
    absvalue = -n if neg else n
    result = bytearray()
    while absvalue:
        result.append(absvalue & 0xFF)
        absvalue >>= 8
    if result[-1] & 0x80:
        result.append(0x80 if neg else 0x00)
    elif neg:
        result[-1] |= 0x80
    return bytes(result)


def push(data: bytes) -> bytes:
    """Minimal data push (only handles len<76, enough for our use)."""
    assert len(data) < 76
    return bytes([len(data)]) + data


def varint(n: int) -> bytes:
    if n < 0xfd:
        return bytes([n])
    elif n <= 0xffff:
        return b"\xfd" + struct.pack("<H", n)
    elif n <= 0xffffffff:
        return b"\xfe" + struct.pack("<I", n)
    else:
        return b"\xff" + struct.pack("<Q", n)


def build_coinbase_tx(psz_timestamp: bytes, pubkey_hex: str, genesis_reward: int) -> bytes:
    script_sig = (
        push(ser_scriptnum(486604799))
        + push(ser_scriptnum(4))
        + push(psz_timestamp)
    )
    pubkey = bytes.fromhex(pubkey_hex)
    script_pubkey = push(pubkey) + b"\xac"  # OP_CHECKSIG

    tx = b""
    tx += struct.pack("<i", 1)            # nVersion
    tx += varint(1)                       # vin count
    tx += b"\x00" * 32                    # prevout hash (null)
    tx += struct.pack("<I", 0xffffffff)   # prevout index
    tx += varint(len(script_sig)) + script_sig
    tx += struct.pack("<I", 0xffffffff)   # sequence
    tx += varint(1)                       # vout count
    tx += struct.pack("<q", genesis_reward)
    tx += varint(len(script_pubkey)) + script_pubkey
    tx += struct.pack("<I", 0)            # nLockTime
    return tx


def build_header(version: int, prev_hash: bytes, merkle_root: bytes,
                  ntime: int, nbits: int, nonce: int) -> bytes:
    return (
        struct.pack("<i", version)
        + prev_hash
        + merkle_root
        + struct.pack("<I", ntime)
        + struct.pack("<I", nbits)
        + struct.pack("<I", nonce)
    )


def bits_to_target(nbits: int) -> int:
    exponent = nbits >> 24
    coeff = nbits & 0x007fffff
    return coeff * (1 << (8 * (exponent - 3)))


def hexbe(b: bytes) -> str:
    """Display hash bytes the way Bitcoin/Dogecoin source prints them (reversed)."""
    return b[::-1].hex()


def make_genesis(psz_timestamp: str, pubkey_hex: str, ntime: int, nbits: int,
                  version: int, genesis_reward_coins: int, start_nonce: int = 0):
    coinbase = build_coinbase_tx(psz_timestamp.encode("ascii"), pubkey_hex,
                                  genesis_reward_coins * COIN)
    txid = sha256d(coinbase)          # internal byte order
    merkle_root = txid                # single tx -> merkle root == txid
    prev_hash = b"\x00" * 32

    nonce = start_nonce
    target = bits_to_target(nbits)
    t0 = time.time()
    while True:
        header = build_header(version, prev_hash, merkle_root, ntime, nbits, nonce)
        pow_hash = scrypt_hash(header)          # used ONLY for difficulty/target check
        h_int = int.from_bytes(pow_hash, "little")
        if h_int <= target:
            break
        nonce += 1
        if nonce % 20000 == 0:
            elapsed = time.time() - t0
            print(f"  ... {nonce} tentativas, {elapsed:.1f}s", file=sys.stderr)
    elapsed = time.time() - t0
    block_hash = sha256d(header)                # the ACTUAL block hash (GetHash()), like Bitcoin
    print(f"Encontrado! nonce={nonce}  ({elapsed:.1f}s)", file=sys.stderr)

    return {
        "genesis_hash": hexbe(block_hash),
        "merkle_root": hexbe(merkle_root),
        "nonce": nonce,
        "ntime": ntime,
        "nbits": hex(nbits),
        "version": version,
        "pszTimestamp": psz_timestamp,
        "reward_coins": genesis_reward_coins,
    }


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "verify"

    DOGE_PUBKEY = ("040184710fa689ad5023690c80f3a49c8f13f8d45b8c857fbcbc8bc4a8e4d3eb4b1"
                   "0f4d4604fa08dce601aaf0f470216fe1b51850b4acf21b179c45070ac7b03a9")

    if mode == "verify":
        # Reproduce the REAL Dogecoin mainnet genesis block to validate our code.
        result = make_genesis(
            psz_timestamp="Nintondo",
            pubkey_hex=DOGE_PUBKEY,
            ntime=1386325540,
            nbits=0x1e0ffff0,
            version=1,
            genesis_reward_coins=88,
            start_nonce=99943,  # we know the answer, just confirm the hash at this nonce
        )
        print(result)
        expected_hash = "1a91e3dace36e2be3bf030a65679fe821aa1d6ef92e7c9902eb318182c355691"
        expected_merkle = "5b2a3f53f605d62c53e62932dac6925e3d74afa5a4b459745c36d42d0ed26a69"
        print("hash match:  ", result["genesis_hash"] == expected_hash)
        print("merkle match:", result["merkle_root"] == expected_merkle)
