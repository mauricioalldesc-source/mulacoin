#include "totp.h"
#include <openssl/hmac.h>
#include <openssl/rand.h>
#include <chrono>
#include <cstring>
#include <sstream>
#include <iomanip>

static const char BASE32_CHARS[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";

std::string TOTP::base32Encode(const unsigned char* data, size_t len)
{
    std::string result;
    int buffer = 0, bitsLeft = 0;
    for (size_t i = 0; i < len; i++) {
        buffer = (buffer << 8) | data[i];
        bitsLeft += 8;
        while (bitsLeft >= 5) {
            result += BASE32_CHARS[(buffer >> (bitsLeft - 5)) & 0x1F];
            bitsLeft -= 5;
        }
    }
    if (bitsLeft > 0)
        result += BASE32_CHARS[(buffer << (5 - bitsLeft)) & 0x1F];
    return result;
}

std::vector<unsigned char> TOTP::base32Decode(const std::string& encoded)
{
    std::vector<unsigned char> result;
    int buffer = 0, bitsLeft = 0;
    for (char c : encoded) {
        if (c == '=' || c == ' ') continue;
        const char* p = strchr(BASE32_CHARS, toupper(c));
        if (!p) continue;
        buffer = (buffer << 5) | (p - BASE32_CHARS);
        bitsLeft += 5;
        if (bitsLeft >= 8) {
            result.push_back((buffer >> (bitsLeft - 8)) & 0xFF);
            bitsLeft -= 8;
        }
    }
    return result;
}

std::string TOTP::generateSecret()
{
    unsigned char randomBytes[20];
    RAND_bytes(randomBytes, sizeof(randomBytes));
    return base32Encode(randomBytes, sizeof(randomBytes));
}

std::string TOTP::generateURI(const std::string& secret,
                               const std::string& account,
                               const std::string& issuer)
{
    return "otpauth://totp/" + issuer + ":" + account +
           "?secret=" + secret +
           "&issuer=" + issuer +
           "&algorithm=SHA1&digits=6&period=30";
}

uint32_t TOTP::generateCode(const std::string& secret, int64_t timestamp)
{
    if (timestamp < 0)
        timestamp = std::chrono::duration_cast<std::chrono::seconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();

    int64_t timeStep = timestamp / 30;

    // Big-endian encoding do time step
    unsigned char msg[8];
    for (int i = 7; i >= 0; i--) {
        msg[i] = timeStep & 0xFF;
        timeStep >>= 8;
    }

    // Decodificar chave Base32
    std::vector<unsigned char> key = base32Decode(secret);

    // HMAC-SHA1
    unsigned char hmacResult[20];
    unsigned int hmacLen = 20;
    HMAC(EVP_sha1(), key.data(), key.size(), msg, 8, hmacResult, &hmacLen);

    // Dynamic truncation
    int offset = hmacResult[19] & 0x0F;
    uint32_t truncated = ((hmacResult[offset]     & 0x7F) << 24) |
                         ((hmacResult[offset + 1] & 0xFF) << 16) |
                         ((hmacResult[offset + 2] & 0xFF) << 8)  |
                          (hmacResult[offset + 3] & 0xFF);

    return truncated % 1000000;
}

bool TOTP::verifyCode(const std::string& secret, uint32_t code, int64_t timestamp)
{
    if (timestamp < 0)
        timestamp = std::chrono::duration_cast<std::chrono::seconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();

    // Aceitar ±1 intervalo de 30 segundos
    for (int delta = -1; delta <= 1; delta++) {
        if (generateCode(secret, timestamp + delta * 30) == code)
            return true;
    }
    return false;
}
