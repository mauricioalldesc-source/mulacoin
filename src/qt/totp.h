#ifndef BITCOIN_QT_TOTP_H
#define BITCOIN_QT_TOTP_H

#include <string>
#include <cstdint>
#include <vector>

/**
 * TOTP (Time-based One-Time Password) implementation
 * RFC 6238 compliant — compatible with Google Authenticator / Authy
 */
class TOTP
{
public:
    // Gerar uma chave secreta aleatória em Base32
    static std::string generateSecret();

    // Gerar URI para QR code (otpauth://)
    static std::string generateURI(const std::string& secret,
                                   const std::string& account = "Mulacoin",
                                   const std::string& issuer  = "Mulacoin");

    // Gerar código TOTP atual (6 dígitos)
    static uint32_t generateCode(const std::string& secret, int64_t timestamp = -1);

    // Verificar código TOTP (aceita ±1 intervalo de 30s)
    static bool verifyCode(const std::string& secret, uint32_t code, int64_t timestamp = -1);

    // Encode/decode Base32
    static std::string base32Encode(const unsigned char* data, size_t len);
    static std::vector<unsigned char> base32Decode(const std::string& encoded);
};

#endif // BITCOIN_QT_TOTP_H
