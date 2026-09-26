#include "twofactordialog.h"
#include "totp.h"
#include "wallet/walletdb.h"
#include "wallet/wallet.h"
#include "guiutil.h"

#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QLineEdit>
#include <QPushButton>
#include <QDialogButtonBox>
#include <QMessageBox>
#include <QSettings>
#include <QString>
#include <QPixmap>
#include <QPainter>

#include <qrencode.h>

// ── TwoFactorDialog (verificação) ─────────────────────────────────────────────

TwoFactorDialog::TwoFactorDialog(CWallet *pwallet, QWidget *parent)
    : QDialog(parent), wallet(pwallet), accepted(false)
{
    setWindowTitle(tr("🔐 2FA Verification"));
    setFixedSize(340, 220);
    setStyleSheet(
        "QDialog { background-color: #1A1208; color: #F5EDD6; }"
        "QLabel { color: #F5EDD6; }"
        "QLineEdit { background: #241A0E; color: #D4AF37; border: 1px solid #D4AF37;"
        "  padding: 8px; font-size: 24px; border-radius: 4px; }"
        "QPushButton { background: #241A0E; color: #D4AF37; border: 1px solid #D4AF37;"
        "  padding: 8px 20px; border-radius: 4px; }"
        "QPushButton:hover { background: #3D2800; }"
    );

    QVBoxLayout *layout = new QVBoxLayout(this);
    layout->setSpacing(12);
    layout->setContentsMargins(24, 24, 24, 24);

    QLabel *title = new QLabel(tr("🔐 Two-Factor Authentication"));
    title->setAlignment(Qt::AlignCenter);
    title->setStyleSheet("font-size: 15px; font-weight: bold; color: #D4AF37;");
    layout->addWidget(title);

    QLabel *sub = new QLabel(tr("Enter the 6-digit code from your authenticator app\n(Google Authenticator / Authy)"));
    sub->setAlignment(Qt::AlignCenter);
    sub->setStyleSheet("font-size: 11px; color: #A89070;");
    layout->addWidget(sub);

    codeEdit = new QLineEdit();
    codeEdit->setMaxLength(6);
    codeEdit->setAlignment(Qt::AlignCenter);
    codeEdit->setPlaceholderText("000000");
    layout->addWidget(codeEdit);

    errorLabel = new QLabel("");
    errorLabel->setAlignment(Qt::AlignCenter);
    errorLabel->setStyleSheet("color: #E53935; font-size: 12px;");
    layout->addWidget(errorLabel);

    QHBoxLayout *btnLayout = new QHBoxLayout();
    QPushButton *btnVerify = new QPushButton(tr("Verify"));
    QPushButton *btnCancel = new QPushButton(tr("Cancel"));
    btnVerify->setStyleSheet("background: linear-gradient(#D4AF37, #9C7A1E); color: #1A1208; font-weight: bold;");
    btnLayout->addWidget(btnCancel);
    btnLayout->addWidget(btnVerify);
    layout->addLayout(btnLayout);

    connect(btnVerify, &QPushButton::clicked, this, &TwoFactorDialog::onVerify);
    connect(btnCancel, &QPushButton::clicked, this, &TwoFactorDialog::onCancel);
    connect(codeEdit, &QLineEdit::returnPressed, this, &TwoFactorDialog::onVerify);
}

QString TwoFactorDialog::getCode() const
{
    return codeEdit->text();
}

void TwoFactorDialog::onVerify()
{
    // Ler chave 2FA do wallet.dat
    std::string secret;
    if (wallet) {
        CWalletDB walletdb(wallet->strWalletFile);
        walletdb.Read2FASecret(secret);
    }

    if (secret.empty()) {
        // 2FA não configurado — permitir envio
        accepted = true;
        accept();
        return;
    }

    bool ok;
    uint32_t code = codeEdit->text().toUInt(&ok);
    if (!ok || codeEdit->text().length() != 6) {
        errorLabel->setText(tr("Please enter a valid 6-digit code"));
        return;
    }

    if (TOTP::verifyCode(secret, code)) {
        accepted = true;
        accept();
    } else {
        errorLabel->setText(tr("Invalid code! Try again."));
        codeEdit->clear();
        codeEdit->setFocus();
    }
}

void TwoFactorDialog::onCancel()
{
    accepted = false;
    reject();
}

// ── TwoFactorSetupDialog (configuração) ───────────────────────────────────────

static QPixmap generateQRPixmap(const QString& uri)
{
    QRcode *qr = QRcode_encodeString(uri.toUtf8().constData(), 0, QR_ECLEVEL_L, QR_MODE_8, 1);
    if (!qr) return QPixmap();

    int size = qr->width;
    int scale = 4;
    QImage image((size + 2) * scale, (size + 2) * scale, QImage::Format_RGB32);
    image.fill(Qt::white);

    for (int y = 0; y < size; y++) {
        for (int x = 0; x < size; x++) {
            if (qr->data[y * size + x] & 1) {
                QRect rect((x + 1) * scale, (y + 1) * scale, scale, scale);
                for (int py = rect.top(); py < rect.bottom(); py++)
                    for (int px = rect.left(); px < rect.right(); px++)
                        image.setPixel(px, py, qRgb(0, 0, 0));
            }
        }
    }
    QRcode_free(qr);
    return QPixmap::fromImage(image);
}

TwoFactorSetupDialog::TwoFactorSetupDialog(CWallet *pwallet, QWidget *parent)
    : QDialog(parent), wallet(pwallet), configured(false)
{
    setWindowTitle(tr("🔐 Configure 2FA"));
    setFixedSize(420, 560);
    setStyleSheet(
        "QDialog { background-color: #1A1208; color: #F5EDD6; }"
        "QLabel { color: #F5EDD6; }"
        "QLineEdit { background: #241A0E; color: #D4AF37; border: 1px solid #D4AF37;"
        "  padding: 8px; font-size: 24px; border-radius: 4px; }"
        "QPushButton { background: #241A0E; color: #D4AF37; border: 1px solid #D4AF37;"
        "  padding: 10px 24px; border-radius: 4px; }"
        "QPushButton:hover { background: #3D2800; }"
    );

    // Gerar nova chave secreta
    secret = QString::fromStdString(TOTP::generateSecret());
    QString uri = QString::fromStdString(
        TOTP::generateURI(secret.toStdString(), "Mulacoin Wallet", "Mulacoin"));

    QVBoxLayout *layout = new QVBoxLayout(this);
    layout->setSpacing(12);
    layout->setContentsMargins(24, 24, 24, 24);

    QLabel *title = new QLabel(tr("🔐 CONFIGURE 2FA"));
    title->setAlignment(Qt::AlignCenter);
    title->setStyleSheet("font-size: 18px; font-weight: bold; color: #D4AF37;");
    layout->addWidget(title);

    QLabel *sub = new QLabel(tr("Scan the QR code with Google Authenticator or Authy"));
    sub->setAlignment(Qt::AlignCenter);
    sub->setStyleSheet("font-size: 11px; color: #A89070;");
    layout->addWidget(sub);

    // QR Code
    QLabel *qrLabel = new QLabel();
    QPixmap qrPixmap = generateQRPixmap(uri);
    qrLabel->setPixmap(qrPixmap.scaled(220, 220, Qt::KeepAspectRatio));
    qrLabel->setAlignment(Qt::AlignCenter);
    layout->addWidget(qrLabel);

    // Chave manual
    QLabel *manualLabel = new QLabel(tr("Or enter the key manually:"));
    manualLabel->setAlignment(Qt::AlignCenter);
    manualLabel->setStyleSheet("font-size: 11px; color: #A89070;");
    layout->addWidget(manualLabel);

    QLabel *secretLabel = new QLabel(secret);
    secretLabel->setAlignment(Qt::AlignCenter);
    secretLabel->setStyleSheet("font-family: monospace; font-size: 13px; font-weight: bold; color: #D4AF37;");
    layout->addWidget(secretLabel);

    // Verificação
    QLabel *verifyLabel = new QLabel(tr("Enter the code from the app to confirm:"));
    verifyLabel->setAlignment(Qt::AlignCenter);
    layout->addWidget(verifyLabel);

    codeEdit = new QLineEdit();
    codeEdit->setMaxLength(6);
    codeEdit->setAlignment(Qt::AlignCenter);
    codeEdit->setPlaceholderText("000000");
    layout->addWidget(codeEdit);

    errorLabel = new QLabel("");
    errorLabel->setAlignment(Qt::AlignCenter);
    errorLabel->setStyleSheet("color: #E53935; font-size: 12px;");
    layout->addWidget(errorLabel);

    QPushButton *btnConfirm = new QPushButton(tr("Confirm and Activate"));
    btnConfirm->setStyleSheet("background: linear-gradient(#D4AF37, #9C7A1E); color: #1A1208; font-weight: bold;");
    layout->addWidget(btnConfirm);

    connect(btnConfirm, &QPushButton::clicked, this, &TwoFactorSetupDialog::onConfirm);
    connect(codeEdit, &QLineEdit::returnPressed, this, &TwoFactorSetupDialog::onConfirm);
}

void TwoFactorSetupDialog::onConfirm()
{
    bool ok;
    uint32_t code = codeEdit->text().toUInt(&ok);
    if (!ok || codeEdit->text().length() != 6) {
        errorLabel->setText(tr("❌ Please enter a valid 6-digit code"));
        return;
    }

    if (TOTP::verifyCode(secret.toStdString(), code)) {
        // Salvar chave secreta no wallet.dat
        if (wallet) {
            CWalletDB walletdb(wallet->strWalletFile);
            walletdb.Write2FASecret(secret.toStdString());
        }
        // Remover do QSettings antigo se existir
        QSettings settings;
        settings.remove("2fa_secret");
        configured = true;
        QMessageBox::information(this, tr("2FA Activated!"),
            tr("Two-factor authentication activated successfully!\n\n"
               "From now on, a code will be required before sending coins.\n"
               "The 2FA key is stored securely in your wallet.dat file."));
        accept();
    } else {
        errorLabel->setText(tr("Incorrect code! Try again."));
        codeEdit->clear();
        codeEdit->setFocus();
    }
}
