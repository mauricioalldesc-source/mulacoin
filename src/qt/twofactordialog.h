#ifndef BITCOIN_QT_TWOFACTORDIALOG_H
#define BITCOIN_QT_TWOFACTORDIALOG_H

#include <QDialog>
#include <QString>

class QLineEdit;
class QLabel;
class CWallet;

/** Diálogo de verificação 2FA — solicita código TOTP antes de enviar */
class TwoFactorDialog : public QDialog
{
    Q_OBJECT

public:
    explicit TwoFactorDialog(CWallet *wallet, QWidget *parent = nullptr);
    QString getCode() const;
    bool wasAccepted() const { return accepted; }

private Q_SLOTS:
    void onVerify();
    void onCancel();

private:
    CWallet   *wallet;
    QLineEdit *codeEdit;
    QLabel    *errorLabel;
    bool       accepted;
};

/** Diálogo de configuração 2FA — mostra QR code e configura */
class TwoFactorSetupDialog : public QDialog
{
    Q_OBJECT

public:
    explicit TwoFactorSetupDialog(CWallet *wallet, QWidget *parent = nullptr);
    QString getSecret() const { return secret; }
    bool wasConfigured() const { return configured; }

private Q_SLOTS:
    void onConfirm();

private:
    CWallet   *wallet;
    QString    secret;
    bool       configured;
    QLineEdit *codeEdit;
    QLabel    *errorLabel;
};

#endif // BITCOIN_QT_TWOFACTORDIALOG_H
