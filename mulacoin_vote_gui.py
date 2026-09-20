#!/usr/bin/env python3
"""
Mulacoin Vote — Interface Gráfica de Votação
Versão 1.0.0

Requisitos:
- Carteira Mulacoin aberta e sincronizada
- Python 3.x (apenas para executar o .py)
- Para o .exe: não precisa de nada!
"""

import tkinter as tk
import pyotp
import qrcode
import os
import json
from tkinter import ttk, messagebox, font
import subprocess
import json
import binascii
import threading
import urllib.request
import os
import sys

# ── Idioma ───────────────────────────────────────────────────────────────────
import locale

def detectar_idioma():
    """Detecta o idioma — verifica config da carteira Mulacoin primeiro"""
    # 1) Verificar configuração salva da GUI de votação
    try:
        cfg_path = os.path.join(os.path.expanduser("~"), ".mulacoin_vote_lang")
        if os.path.exists(cfg_path):
            with open(cfg_path) as f:
                lang = f.read().strip()
                if lang in ('pt', 'en'):
                    return lang
    except:
        pass

    # 2) Verificar configuração da carteira Mulacoin (QSettings)
    try:
        import platform
        if platform.system() == "Windows":
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r"Software\Dogecoin\Mulacoin-Qt")
            lang, _ = winreg.QueryValueEx(key, "language")
            winreg.CloseKey(key)
            if lang and lang.startswith('en'):
                return 'en'
            if lang and lang.startswith('pt'):
                return 'pt'
        else:
            # Linux/Mac — ler arquivo .conf
            cfg = os.path.expanduser("~/.config/Dogecoin/Mulacoin-Qt.conf")
            if os.path.exists(cfg):
                with open(cfg) as f:
                    for line in f:
                        if line.startswith("language="):
                            lang = line.split("=", 1)[1].strip()
                            if lang.startswith("en"):
                                return 'en'
                            if lang.startswith("pt"):
                                return 'pt'
    except:
        pass

    # 3) Fallback: locale do sistema
    try:
        lang = locale.getdefaultlocale()[0] or ''
        if lang.startswith('pt'):
            return 'pt'
    except:
        pass

    return 'en'

IDIOMA = detectar_idioma()

STRINGS = {
    'pt': {
        'titulo':           'Mulacoin Vote — Votação Descentralizada',
        'subtitulo':        'Votação descentralizada na blockchain',
        'aba_votar':        '🗳️  Votar',
        'aba_resultados':   '📊  Resultados',
        'aba_sugerir':      '💡  Sugerir Tema',
        'aba_config':       '⚙️  Configurações',
        'selecione_tema':   'Selecione um tema:',
        'selecione_opcao':  '← Selecione um tema acima',
        'escolha_opcao':    'Escolha sua opção:',
        'btn_votar':        '🗳️  REGISTRAR VOTO NA BLOCKCHAIN',
        'btn_atualizar':    '🔄 Atualizar',
        'btn_atualizar_res':'🔄 Atualizar resultados',
        'carteira_ok':      '🟢 Carteira conectada',
        'carteira_off':     '🔴 Carteira offline — abra o mulacoin-qt primeiro',
        'bloco':            'Bloco: ',
        'confirmar_voto':   'Confirmar voto',
        'confirmar_msg':    'Você está prestes a registrar seu voto:\n\nTema: {titulo}\nOpção: {opcao}\n\n⚠️ Este voto será gravado PERMANENTEMENTE na blockchain!\nNão é possível alterar depois.\n\nConfirmar?',
        'voto_ok':          '✅ Voto registrado!',
        'voto_ok_msg':      'Seu voto foi gravado na blockchain!\n\nTema: {titulo}\nOpção: {opcao}\n\nTX: {tx}...\n\nAguarde ~1 minuto para confirmação\ne os resultados serão atualizados automaticamente.',
        'voto_dup':         'Voto duplicado',
        'voto_dup_msg':     'Você já votou neste tema!\n\nA blockchain registra apenas o primeiro voto por endereço.',
        'sem_utxo':         'Nenhum UTXO disponível.',
        'erro_voto':        'Não foi possível registrar o voto:\n\n{erro}\n\nVerifique se a carteira Mulacoin está aberta.',
        'ja_votou':         '⚠️  Você já votou neste tema!\n   Seu primeiro voto é o único válido na apuração.',
        'sugerir_titulo_label': 'Título da votação:',
        'sugerir_opcoes_label': 'Opções de voto (separe por vírgula):',
        'sugerir_prazo_label':  'Prazo de votação (AAAA-MM-DD):',
        'sugerir_btn':      '📤  ENVIAR SUGESTÃO PARA A BLOCKCHAIN',
        'sugerir_nota':     'ℹ️  Ao enviar, o tema será gravado permanentemente na blockchain Mulacoin.\nUma pequena taxa em FazoL será cobrada para registrar a transação.\nO tema ficará pendente até ser aprovado pelo administrador.',
        'sugerir_ok':       'Sugestão enviada!',
        'sugerir_ok_msg':   '✅ Sugestão enviada com sucesso!\n\nID do tema: {id}\nTX: {tx}...\n\nAguarde aprovação do administrador.\nCompartilhe o ID \'{id}\' se quiser acompanhar.',
        'sugerir_status':   '✅ Tema {id} enviado! Aguardando aprovação.',
        'config_titulo':    'Configuração RPC da Carteira',
        'config_2fa':       'Autenticação de Dois Fatores (2FA)',
        'config_2fa_ativo': '🔐 2FA ativo — suas transações estão protegidas',
        'config_2fa_off':   '⚠️ 2FA não configurado',
        'btn_config_2fa':   '🔐 Configurar 2FA',
        'btn_remover_2fa':  '🗑️ Remover 2FA',
        'config_nota':      '⚠️ A carteira Mulacoin precisa estar aberta e rodando\ncom as opções -server=1 -rpcuser=mula -rpcpassword=picanha',
        'config_salvo':     '✅ Configurações salvas!',
        'footer':           'mulacoin.com.br | Picanha Cumpanheiro! 🍖',
        'aviso_titulo':     'Atenção',
        'aviso_tema':       'Selecione um tema primeiro!',
        'aviso_opcao':      'Selecione uma opção para votar!',
        'aviso_titulo2':    'Digite o título da votação!',
        'aviso_opcoes2':    'Digite pelo menos 2 opções separadas por vírgula!',
        'aviso_prazo':      'Digite o prazo no formato AAAA-MM-DD!',
        'aviso_longo':      'Dados muito longos! Reduza o título ou as opções.\nTamanho atual: {tam} bytes (máximo: 200)',
        'confirmar_sugerir':'Confirmar sugestão',
        'confirmar_sug_msg':'Enviar sugestão de votação?\n\nTítulo: {titulo}\nOpções: {opcoes}\nPrazo: {prazo}\n\n⚠️ Será gravado na blockchain e cobrada uma taxa em FazoL.\nO tema ficará pendente até aprovação do administrador.\n\nConfirmar?',
        'encerrado':        '🔒 Votação encerrada',
        'nenhum_tema':      'Nenhum tema disponível',
        'carregando':       'Carregando temas...',
        'erro_carregar':    'Erro ao carregar',
        'bytes':            'Tamanho: {tam}/200 bytes',
        '2fa_titulo':       '🔐 Configurar 2FA',
        '2fa_sub':          'Escaneie o QR code com Google Authenticator ou Authy',
        '2fa_manual':       'Ou digite a chave manualmente:',
        '2fa_confirmar':    'Digite o código do app para confirmar:',
        '2fa_btn':          '✅ CONFIRMAR E ATIVAR',
        '2fa_ok':           '✅ 2FA Ativado!',
        '2fa_ok_msg':       'Autenticação de dois fatores ativada com sucesso!\n\nA partir de agora será necessário digitar o código\ndo seu aplicativo autenticador antes de votar.',
        '2fa_erro':         '❌ Código incorreto! Tente novamente.',
        '2fa_ver_titulo':   '🔐 Verificação 2FA',
        '2fa_ver_sub':      'Digite o código do seu aplicativo autenticador\n(Google Authenticator / Authy)',
        '2fa_ver_btn':      '✅ VERIFICAR',
        '2fa_invalido':     '❌ Código inválido! Tente novamente.',
        '2fa_remover_conf': 'Tem certeza que deseja remover a autenticação de dois fatores?\n\n⚠️ Suas transações ficarão menos protegidas!',
        '2fa_removido':     '2FA Removido',
        '2fa_removido_msg': 'Autenticação de dois fatores removida.',
        '2fa_nao_config':   '2FA não está configurado.',
        'remover_2fa_conf': 'Remover 2FA',
        'subtitulo_header': 'Votação descentralizada na blockchain',
        'sugerir_header':   '💡 Sugerir Novo Tema de Votação',
        'ex_titulo':        'Ex: Você merece picanha?',
        'ex_opcoes':        'Ex: Sim,Não,Talvez',
        'rpc_usuario':      'Usuário RPC:',
        'rpc_senha':        'Senha RPC:',
        'rpc_porta':        'Porta RPC:',
        'rpc_datadir':      'Datadir (opcional):',
        'rpc_cli':          'Caminho mulacoin-cli:',
        'btn_salvar':       '💾 Salvar e reconectar',
        'prazo_default':    '2026-10-04',
        'sugerir_desc':     'O tema será gravado na blockchain e enviado para aprovação do administrador.',
        'sugerir_nota2':    'ℹ️  Ao enviar, o tema será gravado permanentemente na blockchain Mulacoin.\nUma pequena taxa em FazoL será cobrada para registrar a transação.\nO tema ficará pendente até ser aprovado pelo administrador.',
        'btn_refresh_res':  '🔄 Atualizar resultados',
        'votos':            'votos',
        'bloco_label':      'Bloco',
        'prazo_label':      'Prazo',
        'total_label':      'Total',
    },
    'en': {
        'titulo':           'Mulacoin Vote — Decentralized Voting',
        'subtitulo':        'Decentralized blockchain voting',
        'aba_votar':        '🗳️  Vote',
        'aba_resultados':   '📊  Results',
        'aba_sugerir':      '💡  Suggest Topic',
        'aba_config':       '⚙️  Settings',
        'selecione_tema':   'Select a topic:',
        'selecione_opcao':  '← Select a topic above',
        'escolha_opcao':    'Choose your option:',
        'btn_votar':        '🗳️  REGISTER VOTE ON BLOCKCHAIN',
        'btn_atualizar':    '🔄 Refresh',
        'btn_atualizar_res':'🔄 Refresh results',
        'carteira_ok':      '🟢 Wallet connected',
        'carteira_off':     '🔴 Wallet offline — open mulacoin-qt first',
        'bloco':            'Block: ',
        'confirmar_voto':   'Confirm vote',
        'confirmar_msg':    'You are about to register your vote:\n\nTopic: {titulo}\nOption: {opcao}\n\n⚠️ This vote will be PERMANENTLY recorded on the blockchain!\nIt cannot be changed afterwards.\n\nConfirm?',
        'voto_ok':          '✅ Vote registered!',
        'voto_ok_msg':      'Your vote was recorded on the blockchain!\n\nTopic: {titulo}\nOption: {opcao}\n\nTX: {tx}...\n\nWait ~1 minute for confirmation\nand results will update automatically.',
        'voto_dup':         'Duplicate vote',
        'voto_dup_msg':     'You have already voted on this topic!\n\nThe blockchain records only the first vote per address.',
        'sem_utxo':         'No UTXO available.',
        'erro_voto':        'Could not register vote:\n\n{erro}\n\nMake sure the Mulacoin wallet is open.',
        'ja_votou':         '⚠️  You have already voted on this topic!\n   Your first vote is the only valid one.',
        'sugerir_titulo_label': 'Voting title:',
        'sugerir_opcoes_label': 'Voting options (separate with comma):',
        'sugerir_prazo_label':  'Deadline (YYYY-MM-DD):',
        'sugerir_btn':      '📤  SUBMIT SUGGESTION TO BLOCKCHAIN',
        'sugerir_nota':     'ℹ️  When submitted, the topic will be permanently recorded on the Mulacoin blockchain.\nA small FazoL fee will be charged to register the transaction.\nThe topic will be pending until approved by the administrator.',
        'sugerir_ok':       'Suggestion submitted!',
        'sugerir_ok_msg':   '✅ Suggestion submitted successfully!\n\nTopic ID: {id}\nTX: {tx}...\n\nWait for administrator approval.\nShare ID \'{id}\' to track it.',
        'sugerir_status':   '✅ Topic {id} submitted! Awaiting approval.',
        'config_titulo':    'Wallet RPC Settings',
        'config_2fa':       'Two-Factor Authentication (2FA)',
        'config_2fa_ativo': '🔐 2FA active — your transactions are protected',
        'config_2fa_off':   '⚠️ 2FA not configured',
        'btn_config_2fa':   '🔐 Configure 2FA',
        'btn_remover_2fa':  '🗑️ Remove 2FA',
        'config_nota':      '⚠️ The Mulacoin wallet must be open and running\nwith options -server=1 -rpcuser=mula -rpcpassword=picanha',
        'config_salvo':     '✅ Settings saved!',
        'footer':           'mulacoin.com.br | Picanha Cumpanheiro! 🍖',
        'aviso_titulo':     'Warning',
        'aviso_tema':       'Please select a topic first!',
        'aviso_opcao':      'Please select an option to vote!',
        'aviso_titulo2':    'Please enter a voting title!',
        'aviso_opcoes2':    'Please enter at least 2 options separated by comma!',
        'aviso_prazo':      'Please enter the deadline in YYYY-MM-DD format!',
        'aviso_longo':      'Data too long! Reduce the title or options.\nCurrent size: {tam} bytes (maximum: 200)',
        'confirmar_sugerir':'Confirm suggestion',
        'confirmar_sug_msg':'Submit voting suggestion?\n\nTitle: {titulo}\nOptions: {opcoes}\nDeadline: {prazo}\n\n⚠️ Will be recorded on the blockchain and a FazoL fee will be charged.\nThe topic will be pending until administrator approval.\n\nConfirm?',
        'encerrado':        '🔒 Voting closed',
        'nenhum_tema':      'No topics available',
        'carregando':       'Loading topics...',
        'erro_carregar':    'Error loading',
        'bytes':            'Size: {tam}/200 bytes',
        '2fa_titulo':       '🔐 Configure 2FA',
        '2fa_sub':          'Scan the QR code with Google Authenticator or Authy',
        '2fa_manual':       'Or enter the key manually:',
        '2fa_confirmar':    'Enter the app code to confirm:',
        '2fa_btn':          '✅ CONFIRM AND ACTIVATE',
        '2fa_ok':           '✅ 2FA Activated!',
        '2fa_ok_msg':       'Two-factor authentication activated successfully!\n\nFrom now on you will need to enter the code\nfrom your authenticator app before voting.',
        '2fa_erro':         '❌ Incorrect code! Try again.',
        '2fa_ver_titulo':   '🔐 2FA Verification',
        '2fa_ver_sub':      'Enter the code from your authenticator app\n(Google Authenticator / Authy)',
        '2fa_ver_btn':      '✅ VERIFY',
        '2fa_invalido':     '❌ Invalid code! Try again.',
        '2fa_remover_conf': 'Are you sure you want to remove two-factor authentication?\n\n⚠️ Your transactions will be less protected!',
        '2fa_removido':     '2FA Removed',
        '2fa_removido_msg': 'Two-factor authentication removed.',
        '2fa_nao_config':   '2FA is not configured.',
        'remover_2fa_conf': 'Remove 2FA',
        'subtitulo_header': 'Decentralized blockchain voting',
        'sugerir_header':   '💡 Suggest New Voting Topic',
        'ex_titulo':        'Ex: Do you deserve steak?',
        'ex_opcoes':        'Ex: Yes,No,Maybe',
        'rpc_usuario':      'RPC User:',
        'rpc_senha':        'RPC Password:',
        'rpc_porta':        'RPC Port:',
        'rpc_datadir':      'Datadir (optional):',
        'rpc_cli':          'mulacoin-cli path:',
        'btn_salvar':       '💾 Save and reconnect',
        'prazo_default':    '2026-10-04',
        'sugerir_desc':     'The topic will be recorded on the blockchain and sent for administrator approval.',
        'sugerir_nota2':    'ℹ️  When submitted, the topic will be permanently recorded on the Mulacoin blockchain.\nA small FazoL fee will be charged to register the transaction.\nThe topic will be pending until approved by the administrator.',
        'btn_refresh_res':  '🔄 Refresh results',
        'votos':            'votes',
        'bloco_label':      'Block',
        'prazo_label':      'Deadline',
        'total_label':      'Total',
    }
}

def T(key, **kwargs):
    """Retorna a string traduzida para o idioma atual"""
    s = STRINGS[IDIOMA].get(key, STRINGS['en'].get(key, key))
    if kwargs:
        s = s.format(**kwargs)
    return s

# ── Configuração ──────────────────────────────────────────────────────────────
API_URL      = "https://vote.mulacoin.com.br"
VOTE_PREFIX  = "MVOTE"
VERSION      = "1"

# Tentar detectar o caminho do mulacoin-cli automaticamente
def encontrar_cli():
    caminhos = [
        "mulacoin-cli",
        "./mulacoin-cli",
        os.path.join(os.path.dirname(sys.executable), "mulacoin-cli"),
        os.path.expanduser("~/Documentos/mulacoin-bin/mulacoin-cli"),
        "C:/mulacoin/mulacoin-cli.exe",
        "C:/Program Files/Mulacoin/mulacoin-cli.exe",
    ]
    for c in caminhos:
        try:
            r = subprocess.run([c, "--version"], capture_output=True, timeout=3)
            if r.returncode == 0:
                return c
        except:
            pass
    return None

# ── Arquivo de configuração 2FA ──────────────────────────────────────────────
ARQUIVO_2FA = os.path.join(os.path.expanduser("~"), ".mulacoin_2fa.json")

# ── Cores e estilos ───────────────────────────────────────────────────────────
COR_FUNDO    = "#1A1208"
COR_CARD     = "#241A0E"
COR_DOURADO  = "#D4AF37"
COR_TEXTO    = "#F5EDD6"
COR_MUTED    = "#A89070"
COR_VERDE    = "#4CAF50"
COR_VERMELHO = "#E53935"
COR_BORDA    = "#3D2800"

# ── Funções RPC ───────────────────────────────────────────────────────────────
cli_path   = None
rpc_user   = "mula"
rpc_pass   = "picanha"
rpc_port   = "23560"
datadir    = None

def rpc(method, *params):
    global cli_path
    if not cli_path:
        raise Exception("Carteira não encontrada")
    
    cmd = [cli_path]
    if datadir:
        cmd += [f"-datadir={datadir}"]
    cmd += [f"-rpcuser={rpc_user}", f"-rpcpassword={rpc_pass}",
            f"-rpcport={rpc_port}", method] + [str(p) for p in params]
    
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise Exception(r.stderr.strip())
    out = r.stdout.strip()
    try:
        return json.loads(out)
    except:
        return out

def from_hex(h):
    try:
        return binascii.unhexlify(h).decode('utf-8')
    except:
        return None

def to_hex(t):
    return binascii.hexlify(t.encode('utf-8')).decode('ascii')

# ── Interface Principal ────────────────────────────────────────────────────────
class MulacoinVoteApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"🐴 {T('titulo')}")
        self.root.geometry("700x600")
        self.root.configure(bg=COR_FUNDO)
        self.root.resizable(True, True)
        
        self.temas = []
        self.tema_selecionado = None
        self.opcao_var = tk.StringVar()
        self.secret_2fa = self.carregar_2fa()
        
        self.criar_interface()
        self.verificar_carteira()
        self.iniciar_auto_refresh()
        self.atualizar_status_2fa()

    def criar_interface(self):
        # Header
        header = tk.Frame(self.root, bg=COR_CARD, pady=16)
        header.pack(fill=tk.X)
        
        tk.Label(header, text="🐴 MULACOIN VOTE", 
                font=("Arial", 20, "bold"),
                fg=COR_DOURADO, bg=COR_CARD).pack()
        tk.Label(header, text=T("subtitulo_header"),
                font=("Arial", 10),
                fg=COR_MUTED, bg=COR_CARD).pack()

        # Status bar
        self.frame_status = tk.Frame(self.root, bg=COR_FUNDO, pady=8)
        self.frame_status.pack(fill=tk.X, padx=16)
        
        self.lbl_carteira = tk.Label(self.frame_status, 
                text="🔴 Verificando carteira...",
                font=("Arial", 10), fg=COR_MUTED, bg=COR_FUNDO)
        self.lbl_carteira.pack(side=tk.LEFT)
        
        self.lbl_blocos = tk.Label(self.frame_status,
                text="",
                font=("Arial", 10), fg=COR_MUTED, bg=COR_FUNDO)
        self.lbl_blocos.pack(side=tk.RIGHT)

        # Notebook (abas)
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background=COR_FUNDO, borderwidth=0)
        style.configure('TNotebook.Tab', background=COR_CARD, foreground=COR_MUTED,
                        padding=[16, 8], font=('Arial', 10))
        style.map('TNotebook.Tab', background=[('selected', COR_BORDA)],
                  foreground=[('selected', COR_DOURADO)])
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)

        # Aba 1: Votar
        self.frame_votar = tk.Frame(self.notebook, bg=COR_FUNDO)
        self.notebook.add(self.frame_votar, text=T("aba_votar"))
        self.criar_aba_votar()

        # Aba 2: Resultados
        self.frame_resultados = tk.Frame(self.notebook, bg=COR_FUNDO)
        self.notebook.add(self.frame_resultados, text=T("aba_resultados"))
        self.criar_aba_resultados()

        # Aba 3: Sugerir Tema
        self.frame_sugerir = tk.Frame(self.notebook, bg=COR_FUNDO)
        self.notebook.add(self.frame_sugerir, text=T("aba_sugerir"))
        self.criar_aba_sugerir()

        # Aba 4: Configurações
        self.frame_config = tk.Frame(self.notebook, bg=COR_FUNDO)
        self.notebook.add(self.frame_config, text=T("aba_config"))
        self.criar_aba_config()

        # Footer
        footer = tk.Frame(self.root, bg=COR_CARD, pady=8)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Label(footer, text=T("footer"),
                font=("Arial", 9), fg=COR_MUTED, bg=COR_CARD).pack()

    def criar_aba_votar(self):
        # Lista de temas
        tk.Label(self.frame_votar, text=T("selecione_tema"),
                font=("Arial", 11, "bold"), fg=COR_DOURADO, bg=COR_FUNDO).pack(
                anchor=tk.W, padx=16, pady=(16, 8))

        frame_lista = tk.Frame(self.frame_votar, bg=COR_FUNDO)
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=16)

        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.lista_temas = tk.Listbox(frame_lista,
                bg=COR_CARD, fg=COR_TEXTO,
                selectbackground=COR_BORDA, selectforeground=COR_DOURADO,
                font=("Arial", 11), relief=tk.FLAT,
                borderwidth=0, highlightthickness=1,
                highlightcolor=COR_DOURADO,
                yscrollcommand=scrollbar.set,
                activestyle='none')
        self.lista_temas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.lista_temas.yview)
        self.lista_temas.bind('<<ListboxSelect>>', self.ao_selecionar_tema)

        # Área de opções
        self.frame_opcoes = tk.Frame(self.frame_votar, bg=COR_FUNDO)
        self.frame_opcoes.pack(fill=tk.X, padx=16, pady=8)

        self.lbl_tema_titulo = tk.Label(self.frame_opcoes,
                text=T("selecione_opcao"),
                font=("Arial", 11), fg=COR_MUTED, bg=COR_FUNDO,
                wraplength=650, justify=tk.LEFT)
        self.lbl_tema_titulo.pack(anchor=tk.W, pady=(8, 4))

        self.frame_radio = tk.Frame(self.frame_opcoes, bg=COR_FUNDO)
        self.frame_radio.pack(fill=tk.X)

        # Frame inferior com botões
        frame_botoes = tk.Frame(self.frame_votar, bg=COR_FUNDO)
        frame_botoes.pack(fill=tk.X, padx=16, pady=8, side=tk.BOTTOM)

        tk.Button(frame_botoes,
                text="🔄 Atualizar",
                font=("Arial", 9),
                bg=COR_CARD, fg=COR_MUTED,
                relief=tk.FLAT, padx=10, pady=4,
                cursor="hand2",
                command=self.carregar_temas).pack(side=tk.RIGHT, padx=4)

        self.btn_votar = tk.Button(frame_botoes,
                text=T("btn_votar"),
                font=("Arial", 12, "bold"),
                bg=COR_DOURADO, fg=COR_FUNDO,
                relief=tk.FLAT, padx=20, pady=10,
                cursor="hand2",
                command=lambda: self.verificar_2fa(self.ao_votar),
                state=tk.DISABLED)
        self.btn_votar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

    def criar_aba_resultados(self):
        self.frame_res_scroll = tk.Frame(self.frame_resultados, bg=COR_FUNDO)
        self.frame_res_scroll.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        scrollbar2 = tk.Scrollbar(self.frame_res_scroll)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)

        self.texto_resultados = tk.Text(self.frame_res_scroll,
                bg=COR_CARD, fg=COR_TEXTO,
                font=("Courier", 10), relief=tk.FLAT,
                borderwidth=0, highlightthickness=0,
                yscrollcommand=scrollbar2.set,
                state=tk.DISABLED, wrap=tk.WORD)
        self.texto_resultados.pack(fill=tk.BOTH, expand=True)
        scrollbar2.config(command=self.texto_resultados.yview)

        tk.Button(self.frame_resultados,
                text=T("btn_atualizar_res"),
                font=("Arial", 10),
                bg=COR_DOURADO, fg=COR_FUNDO,
                relief=tk.FLAT, padx=16, pady=6,
                cursor="hand2",
                command=self.atualizar_resultados).pack(pady=8)

    def criar_aba_sugerir(self):
        # Titulo
        tk.Label(self.frame_sugerir,
                text=T("sugerir_header"),
                font=("Arial", 13, "bold"), fg=COR_DOURADO, bg=COR_FUNDO).pack(
                anchor=tk.W, padx=16, pady=(16, 4))

        tk.Label(self.frame_sugerir,
                text=T("sugerir_desc"),
                font=("Arial", 10), fg=COR_MUTED, bg=COR_FUNDO,
                wraplength=650, justify=tk.LEFT).pack(anchor=tk.W, padx=16, pady=(0, 16))

        # Título do tema
        frame_titulo = tk.Frame(self.frame_sugerir, bg=COR_FUNDO)
        frame_titulo.pack(fill=tk.X, padx=16, pady=4)
        tk.Label(frame_titulo, text=T("sugerir_titulo_label"),
                font=("Arial", 10, "bold"), fg=COR_TEXTO, bg=COR_FUNDO).pack(anchor=tk.W)
        self.sugerir_titulo = tk.Entry(frame_titulo,
                font=("Arial", 11), bg=COR_CARD, fg=COR_TEXTO,
                insertbackground=COR_DOURADO, relief=tk.FLAT,
                borderwidth=6)
        self.sugerir_titulo.pack(fill=tk.X, pady=4)
        tk.Label(frame_titulo, text=T("ex_titulo"),
                font=("Arial", 9), fg=COR_MUTED, bg=COR_FUNDO).pack(anchor=tk.W)

        # Opções
        frame_opcoes = tk.Frame(self.frame_sugerir, bg=COR_FUNDO)
        frame_opcoes.pack(fill=tk.X, padx=16, pady=8)
        tk.Label(frame_opcoes, text=T("sugerir_opcoes_label"),
                font=("Arial", 10, "bold"), fg=COR_TEXTO, bg=COR_FUNDO).pack(anchor=tk.W)
        self.sugerir_opcoes = tk.Entry(frame_opcoes,
                font=("Arial", 11), bg=COR_CARD, fg=COR_TEXTO,
                insertbackground=COR_DOURADO, relief=tk.FLAT,
                borderwidth=6)
        self.sugerir_opcoes.pack(fill=tk.X, pady=4)
        tk.Label(frame_opcoes, text=T("ex_opcoes"),
                font=("Arial", 9), fg=COR_MUTED, bg=COR_FUNDO).pack(anchor=tk.W)

        # Prazo
        frame_prazo = tk.Frame(self.frame_sugerir, bg=COR_FUNDO)
        frame_prazo.pack(fill=tk.X, padx=16, pady=8)
        tk.Label(frame_prazo, text=T("sugerir_prazo_label"),
                font=("Arial", 10, "bold"), fg=COR_TEXTO, bg=COR_FUNDO).pack(anchor=tk.W)
        self.sugerir_prazo = tk.Entry(frame_prazo,
                font=("Arial", 11), bg=COR_CARD, fg=COR_TEXTO,
                insertbackground=COR_DOURADO, relief=tk.FLAT,
                borderwidth=6, width=20)
        self.sugerir_prazo.insert(0, T("prazo_default"))
        self.sugerir_prazo.pack(anchor=tk.W, pady=4)

        # Aviso de tamanho
        self.lbl_sugerir_bytes = tk.Label(self.frame_sugerir,
                text="", font=("Arial", 9), fg=COR_MUTED, bg=COR_FUNDO)
        self.lbl_sugerir_bytes.pack(anchor=tk.W, padx=16)

        # Monitorar tamanho em tempo real
        def atualizar_contador(*args):
            titulo  = self.sugerir_titulo.get()
            opcoes  = self.sugerir_opcoes.get().replace(",", "|")
            prazo   = self.sugerir_prazo.get()
            dados   = f"MVOTE:1:CREATE:XXXXXXXX:{titulo}:{opcoes}:{prazo}"
            tamanho = len(dados.encode("utf-8"))
            cor     = COR_VERDE if tamanho <= 200 else COR_VERMELHO
            self.lbl_sugerir_bytes.config(
                text=f"Tamanho: {tamanho}/200 bytes", fg=cor)

        self.sugerir_titulo.bind("<KeyRelease>", atualizar_contador)
        self.sugerir_opcoes.bind("<KeyRelease>", atualizar_contador)
        self.sugerir_prazo.bind("<KeyRelease>", atualizar_contador)

        # Botão enviar
        self.btn_sugerir = tk.Button(self.frame_sugerir,
                text=T("sugerir_btn"),
                font=("Arial", 12, "bold"),
                bg=COR_DOURADO, fg=COR_FUNDO,
                relief=tk.FLAT, padx=20, pady=10,
                cursor="hand2",
                command=lambda: self.verificar_2fa(self.ao_sugerir_tema))
        self.btn_sugerir.pack(pady=16, padx=16, fill=tk.X)

        # Nota informativa
        nota = T("sugerir_nota2")
        tk.Label(self.frame_sugerir, text=nota,
                font=("Arial", 9), fg=COR_MUTED, bg=COR_FUNDO,
                justify=tk.LEFT, wraplength=640).pack(padx=16, anchor=tk.W)

        # Status
        self.lbl_sugerir_status = tk.Label(self.frame_sugerir,
                text="", font=("Arial", 10), fg=COR_VERDE, bg=COR_FUNDO,
                wraplength=640, justify=tk.LEFT)
        self.lbl_sugerir_status.pack(padx=16, pady=8, anchor=tk.W)

    def ao_sugerir_tema(self):
        titulo = self.sugerir_titulo.get().strip()
        opcoes = self.sugerir_opcoes.get().strip()
        prazo  = self.sugerir_prazo.get().strip()

        if not titulo:
            messagebox.showwarning(T("aviso_titulo"), T("aviso_titulo2"))
            return
        if not opcoes or "," not in opcoes:
            messagebox.showwarning(T("aviso_titulo"), T("aviso_opcoes2"))
            return
        if not prazo or len(prazo) != 10:
            messagebox.showwarning(T("aviso_titulo"), T("aviso_prazo"))
            return

        opcoes_fmt = "|".join([o.strip() for o in opcoes.split(",")])
        dados = f"MVOTE:1:CREATE:XXXXXXXX:{titulo}:{opcoes_fmt}:{prazo}"
        if len(dados.encode("utf-8")) > 200:
            messagebox.showwarning(T("aviso_titulo"),
                f"Dados muito longos! Reduza o título ou as opções.\n"
                f"Tamanho atual: {len(dados.encode())} bytes (máximo: 200)")
            return

        confirmar = messagebox.askyesno(
            T("confirmar_sugerir"),
            T("confirmar_sug_msg", titulo=titulo, opcoes=opcoes, prazo=prazo))

        if not confirmar:
            return

        self.btn_sugerir.config(state=tk.DISABLED, text="⏳ Enviando...")
        threading.Thread(target=self._sugerir_async,
                        args=(titulo, opcoes, prazo), daemon=True).start()

    def _sugerir_async(self, titulo, opcoes, prazo):
        try:
            import hashlib
            from datetime import datetime

            # Gerar ID único
            ts      = datetime.now().strftime("%Y%m%d%H%M%S")
            tema_id = hashlib.sha256(f"{titulo}{ts}".encode()).hexdigest()[:8].upper()

            opcoes_fmt = "|".join([o.strip() for o in opcoes.split(",")])
            dados      = f"MVOTE:1:CREATE:{tema_id}:{titulo}:{opcoes_fmt}:{prazo}"
            dados_hex  = to_hex(dados)

            utxos = rpc("listunspent")
            if not utxos:
                raise Exception(T("sem_utxo"))

            utxo   = utxos[0]
            txid   = utxo["txid"]
            vout   = utxo["vout"]
            amount = utxo["amount"]
            fee    = 0.001
            change = round(amount - fee, 8)

            endereco = rpc("getnewaddress")
            inputs   = json.dumps([{"txid": txid, "vout": vout}])
            outputs  = json.dumps({endereco: change, "data": dados_hex})

            raw_tx  = rpc("createrawtransaction", inputs, outputs)
            sign_tx = rpc("signrawtransaction", raw_tx)
            hex_tx  = sign_tx["hex"]
            final   = rpc("sendrawtransaction", hex_tx)

            msg = (f"✅ Sugestão enviada com sucesso!\n\n"
                   f"ID do tema: {tema_id}\n"
                   f"TX: {final[:32]}...\n\n"
                   f"Aguarde aprovação do administrador.\n"
                   f"Compartilhe o ID '{tema_id}' se quiser acompanhar.")

            self.root.after(0, lambda: messagebox.showinfo(T("sugerir_ok"), msg))
            self.root.after(0, lambda: self.lbl_sugerir_status.config(
                text=T("sugerir_status", id=tema_id),
                fg=COR_VERDE))
            self.root.after(0, lambda: self.sugerir_titulo.delete(0, tk.END))
            self.root.after(0, lambda: self.sugerir_opcoes.delete(0, tk.END))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                T("aviso_titulo"), f"{T('erro_voto', erro=str(e))}"))

        finally:
            self.root.after(0, lambda: self.btn_sugerir.config(
                state=tk.NORMAL,
                text=T("sugerir_btn")))

    def criar_aba_config(self):
        tk.Label(self.frame_config, text=T("config_titulo"),
                font=("Arial", 12, "bold"), fg=COR_DOURADO, bg=COR_FUNDO).pack(
                anchor=tk.W, padx=16, pady=16)

        campos = [
            (T("rpc_usuario"), "rpc_user_var", "mula"),
            (T("rpc_senha"), "rpc_pass_var", "picanha"),
            (T("rpc_porta"), "rpc_port_var", "23560"),
            (T("rpc_datadir"), "datadir_var", ""),
            (T("rpc_cli"), "cli_var", ""),
        ]

        self.config_vars = {}
        for label, var_name, default in campos:
            frame = tk.Frame(self.frame_config, bg=COR_FUNDO)
            frame.pack(fill=tk.X, padx=16, pady=4)
            
            tk.Label(frame, text=label, font=("Arial", 10),
                    fg=COR_MUTED, bg=COR_FUNDO, width=22, anchor=tk.W).pack(side=tk.LEFT)
            
            var = tk.StringVar(value=default)
            self.config_vars[var_name] = var
            
            entry = tk.Entry(frame, textvariable=var, font=("Arial", 10),
                           bg=COR_CARD, fg=COR_TEXTO,
                           insertbackground=COR_DOURADO,
                           relief=tk.FLAT, borderwidth=4)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Button(self.frame_config,
                text=T("btn_salvar"),
                font=("Arial", 10, "bold"),
                bg=COR_DOURADO, fg=COR_FUNDO,
                relief=tk.FLAT, padx=16, pady=8,
                cursor="hand2",
                command=self.salvar_config).pack(pady=16)

        self.lbl_config_status = tk.Label(self.frame_config,
                text="", font=("Arial", 10), fg=COR_VERDE, bg=COR_FUNDO)
        self.lbl_config_status.pack()

        # Seção 2FA
        tk.Frame(self.frame_config, bg=COR_BORDA, height=1).pack(fill=tk.X, padx=16, pady=16)

        tk.Label(self.frame_config, text=T("config_2fa"),
                font=("Arial", 12, "bold"), fg=COR_DOURADO, bg=COR_FUNDO).pack(
                anchor=tk.W, padx=16, pady=(0,8))

        self.lbl_2fa_status = tk.Label(self.frame_config,
                text="", font=("Arial", 10), bg=COR_FUNDO)
        self.lbl_2fa_status.pack(anchor=tk.W, padx=16, pady=(0,8))

        frame_2fa_btns = tk.Frame(self.frame_config, bg=COR_FUNDO)
        frame_2fa_btns.pack(anchor=tk.W, padx=16, pady=(0,16))

        tk.Button(frame_2fa_btns,
                text=T("btn_config_2fa"),
                font=("Arial", 10, "bold"),
                bg=COR_DOURADO, fg=COR_FUNDO,
                relief=tk.FLAT, padx=12, pady=6,
                cursor="hand2",
                command=self.configurar_2fa).pack(side=tk.LEFT, padx=(0,8))

        tk.Button(frame_2fa_btns,
                text=T("btn_remover_2fa"),
                font=("Arial", 10),
                bg=COR_CARD, fg=COR_VERMELHO,
                relief=tk.FLAT, padx=12, pady=6,
                cursor="hand2",
                command=self.remover_2fa).pack(side=tk.LEFT)

        # Nota
        nota = T("config_nota")
        tk.Label(self.frame_config, text=nota,
                font=("Arial", 9), fg=COR_MUTED, bg=COR_FUNDO,
                justify=tk.LEFT, wraplength=600).pack(padx=16, pady=16, anchor=tk.W)

    # ── Lógica ────────────────────────────────────────────────────────────────
    # ── 2FA ───────────────────────────────────────────────────────────────────
    def carregar_2fa(self):
        """Carrega configuração 2FA existente ou retorna None"""
        try:
            if os.path.exists(ARQUIVO_2FA):
                with open(ARQUIVO_2FA) as f:
                    dados = json.load(f)
                    return dados.get("secret")
        except:
            pass
        return None

    def salvar_2fa(self, secret):
        """Salva a chave secreta do 2FA"""
        with open(ARQUIVO_2FA, 'w') as f:
            json.dump({"secret": secret}, f)

    def configurar_2fa(self):
        """Abre janela de configuração inicial do 2FA"""
        secret = pyotp.random_base32()
        uri    = pyotp.totp.TOTP(secret).provisioning_uri(
                    name="Mulacoin Vote",
                    issuer_name="Mulacoin")

        # Gerar QR code
        img    = qrcode.make(uri)
        import io
        buf    = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)

        from PIL import Image, ImageTk
        pil_img = Image.open(buf).resize((220, 220))
        tk_img  = ImageTk.PhotoImage(pil_img)

        # Janela de configuração
        win = tk.Toplevel(self.root)
        win.title(T("btn_config_2fa"))
        win.configure(bg=COR_FUNDO)
        win.geometry("420x560")
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text="🔐 CONFIGURAR 2FA",
                font=("Arial", 16, "bold"), fg=COR_DOURADO, bg=COR_FUNDO).pack(pady=(24,4))
        tk.Label(win, text=T("2fa_sub"),
                font=("Arial", 10), fg=COR_MUTED, bg=COR_FUNDO,
                wraplength=360, justify=tk.CENTER).pack(pady=(0,16))

        # QR Code
        lbl_img = tk.Label(win, image=tk_img, bg=COR_FUNDO)
        lbl_img.image = tk_img
        lbl_img.pack()

        # Chave manual
        tk.Label(win, text=T("2fa_manual"),
                font=("Arial", 9), fg=COR_MUTED, bg=COR_FUNDO).pack(pady=(12,4))
        tk.Label(win, text=secret,
                font=("Space Mono", 11, "bold"), fg=COR_DOURADO, bg=COR_FUNDO).pack()

        # Verificação
        tk.Label(win, text=T("2fa_confirmar"),
                font=("Arial", 10), fg=COR_TEXTO, bg=COR_FUNDO).pack(pady=(20,4))

        codigo_var = tk.StringVar()
        entry = tk.Entry(win, textvariable=codigo_var,
                font=("Arial", 20), bg=COR_CARD, fg=COR_DOURADO,
                insertbackground=COR_DOURADO, relief=tk.FLAT,
                borderwidth=6, width=10, justify=tk.CENTER)
        entry.pack()
        entry.focus()

        lbl_erro = tk.Label(win, text="", font=("Arial", 10),
                fg=COR_VERMELHO, bg=COR_FUNDO)
        lbl_erro.pack(pady=4)

        def confirmar():
            totp   = pyotp.TOTP(secret)
            codigo = codigo_var.get().strip()
            if totp.verify(codigo):
                self.salvar_2fa(secret)
                self.secret_2fa = secret
                messagebox.showinfo(T("2fa_ok"),
                    "Autenticação de dois fatores ativada com sucesso!\n\n"
                    "A partir de agora será necessário digitar o código\n"
                    "do seu aplicativo autenticador antes de votar.")
                win.destroy()
                self.atualizar_status_2fa()
            else:
                lbl_erro.config(text=T("2fa_erro"))

        entry.bind("<Return>", lambda e: confirmar())

        tk.Button(win, text=T("2fa_btn"),
                font=("Arial", 12, "bold"),
                bg=COR_DOURADO, fg=COR_FUNDO,
                relief=tk.FLAT, padx=20, pady=10,
                cursor="hand2", command=confirmar).pack(pady=16)

    def verificar_2fa(self, callback):
        """Solicita código 2FA antes de executar o callback"""
        secret = self.carregar_2fa()
        if not secret:
            # 2FA não configurado — prossegue normalmente
            callback()
            return

        win = tk.Toplevel(self.root)
        win.title(T("2fa_ver_titulo"))
        win.configure(bg=COR_FUNDO)
        win.geometry("340x260")
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text="🔐 VERIFICAÇÃO 2FA",
                font=("Arial", 16, "bold"), fg=COR_DOURADO, bg=COR_FUNDO).pack(pady=(24,4))
        tk.Label(win, text=T("2fa_ver_sub"),
                font=("Arial", 10), fg=COR_MUTED, bg=COR_FUNDO,
                wraplength=300, justify=tk.CENTER).pack(pady=(0,16))

        codigo_var = tk.StringVar()
        entry = tk.Entry(win, textvariable=codigo_var,
                font=("Arial", 28, "bold"), bg=COR_CARD, fg=COR_DOURADO,
                insertbackground=COR_DOURADO, relief=tk.FLAT,
                borderwidth=6, width=8, justify=tk.CENTER)
        entry.pack()
        entry.focus()

        lbl_erro = tk.Label(win, text="", font=("Arial", 10),
                fg=COR_VERMELHO, bg=COR_FUNDO)
        lbl_erro.pack(pady=4)

        def verificar():
            totp   = pyotp.TOTP(secret)
            codigo = codigo_var.get().strip()
            if totp.verify(codigo):
                win.destroy()
                callback()
            else:
                lbl_erro.config(text=T("2fa_invalido"))
                entry.delete(0, tk.END)
                entry.focus()

        entry.bind("<Return>", lambda e: verificar())

        tk.Button(win, text=T("2fa_ver_btn"),
                font=("Arial", 12, "bold"),
                bg=COR_DOURADO, fg=COR_FUNDO,
                relief=tk.FLAT, padx=20, pady=10,
                cursor="hand2", command=verificar).pack(pady=12)

    def atualizar_status_2fa(self):
        """Atualiza o label de status do 2FA na aba de configurações"""
        secret = self.carregar_2fa()
        if hasattr(self, 'lbl_2fa_status'):
            if secret:
                self.lbl_2fa_status.config(
                    text=T("config_2fa_ativo"),
                    fg=COR_VERDE)
            else:
                self.lbl_2fa_status.config(
                    text=T("config_2fa_off"),
                    fg=COR_VERMELHO)

    def iniciar_auto_refresh(self):
        """Atualiza temas automaticamente a cada 60 segundos"""
        self.carregar_temas()
        self.root.after(60000, self.iniciar_auto_refresh)

    def verificar_carteira(self):
        global cli_path
        cli_path = encontrar_cli()
        
        if cli_path:
            self.config_vars['cli_var'].set(cli_path)
        
        threading.Thread(target=self._verificar_async, daemon=True).start()

    def _verificar_async(self):
        try:
            info = rpc("getblockchaininfo")
            blocos = info['blocks']
            self.root.after(0, lambda: self.lbl_carteira.config(
                text=T("carteira_ok"), fg=COR_VERDE))
            self.root.after(0, lambda: self.lbl_blocos.config(
                text=f"Bloco: {blocos:,}"))
            self.root.after(0, self.carregar_temas)
        except Exception as e:
            self.root.after(0, lambda: self.lbl_carteira.config(
                text=T("carteira_off"),
                fg=COR_VERMELHO))
            self.root.after(0, self.carregar_temas)

    def carregar_temas(self):
        self.lista_temas.delete(0, tk.END)
        self.lista_temas.insert(tk.END, T("carregando"))
        threading.Thread(target=self._carregar_temas_async, daemon=True).start()

    def _carregar_temas_async(self):
        try:
            req = urllib.request.Request(f"{API_URL}/temas",
                    headers={'User-Agent': 'MulacoinVoteGUI/1.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                self.temas = json.loads(resp.read().decode())
            
            self.root.after(0, self._atualizar_lista_temas)
        except Exception as e:
            self.root.after(0, lambda: self.lista_temas.delete(0, tk.END))
            self.root.after(0, lambda: self.lista_temas.insert(
                tk.END, f"  ❌ Erro ao carregar: {e}"))

    def _atualizar_lista_temas(self):
        self.lista_temas.delete(0, tk.END)
        if not self.temas:
            self.lista_temas.insert(tk.END, T("nenhum_tema"))
            return
        for tema in self.temas:
            status = "🔴 Encerrado" if tema.get('encerrado') else "🟢 Aberto"
            texto = f"  {status}  {tema['titulo']}  (ID: {tema['id']})  — {tema['total']} votos"
            self.lista_temas.insert(tk.END, texto)
        
        self.atualizar_resultados()

    def ao_selecionar_tema(self, event):
        sel = self.lista_temas.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx >= len(self.temas):
            return
        
        self.tema_selecionado = self.temas[idx]
        tema = self.tema_selecionado
        
        self.lbl_tema_titulo.config(
            text=f"📋 {tema['titulo']}\n{T('prazo_label')}: {tema['prazo']} | {tema['total']} {T('votos')}",
            fg=COR_DOURADO)

        # Limpar radio buttons anteriores
        for widget in self.frame_radio.winfo_children():
            widget.destroy()
        
        self.opcao_var.set("")
        
        tk.Label(self.frame_radio, text=T("escolha_opcao"),
                font=("Arial", 10), fg=COR_MUTED, bg=COR_FUNDO).pack(
                anchor=tk.W, pady=(8, 4))

        # Frame interno com grid de 2 colunas
        frame_grid = tk.Frame(self.frame_radio, bg=COR_FUNDO)
        frame_grid.pack(fill=tk.X, anchor=tk.W)
        frame_grid.columnconfigure(0, weight=1)
        frame_grid.columnconfigure(1, weight=1)

        col = 0
        row = 0
        for opcao in tema['opcoes']:
            count = tema['contagem'].get(opcao, 0)
            total = tema['total'] or 1
            pct   = count / total * 100
            texto = f"  {opcao}  ({count} {T('votos')} — {pct:.1f}%)"

            rb = tk.Radiobutton(frame_grid,
                    text=texto,
                    variable=self.opcao_var, value=opcao,
                    font=("Arial", 11),
                    fg=COR_TEXTO, bg=COR_FUNDO,
                    selectcolor=COR_BORDA,
                    activebackground=COR_FUNDO,
                    activeforeground=COR_DOURADO,
                    cursor="hand2")
            rb.grid(row=row, column=col, sticky=tk.W, padx=8, pady=2)
            col += 1
            if col > 1:
                col = 0
                row += 1

        encerrado = tema.get('encerrado', False)
        self.btn_votar.config(
            state=tk.DISABLED if encerrado else tk.NORMAL,
            text=T("encerrado") if encerrado else T("btn_votar"))

    def ao_votar(self):
        if not self.tema_selecionado:
            messagebox.showwarning(T("aviso_titulo"), T("aviso_tema"))
            return
        
        opcao = self.opcao_var.get()
        if not opcao:
            messagebox.showwarning(T("aviso_titulo"), T("aviso_opcao"))
            return
        
        tema_id = self.tema_selecionado['id']
        titulo  = self.tema_selecionado['titulo']
        
        confirmar = messagebox.askyesno(
            T("confirmar_voto"),
            T("confirmar_msg", titulo=titulo, opcao=opcao))
        
        if not confirmar:
            return
        
        self.btn_votar.config(state=tk.DISABLED, text="⏳ Registrando...")
        threading.Thread(target=self._votar_async,
                        args=(tema_id, opcao), daemon=True).start()

    def _votar_async(self, tema_id, opcao):
        try:
            # Verificar se já votou
            txs = rpc("listtransactions", "*", 500)
            for tx in txs:
                if tx.get("category") != "send":
                    continue
                try:
                    raw = rpc("getrawtransaction", tx["txid"], 1)
                    for vout in raw.get("vout", []):
                        script = vout.get("scriptPubKey", {})
                        if script.get("type") == "nulldata":
                            asm      = script.get("asm", "")
                            hex_data = asm.replace("OP_RETURN ", "")
                            texto    = from_hex(hex_data)
                            if texto and f"VOTE:{tema_id}:" in texto:
                                self.root.after(0, lambda: messagebox.showwarning(
                                    "Voto duplicado",
                                    "Você já votou neste tema!\n\n"
                                    "A blockchain registra apenas o primeiro voto por endereço."))
                                self.root.after(0, lambda: self.btn_votar.config(
                                    state=tk.NORMAL,
                                    text=T("btn_votar")))
                                return
                except:
                    continue

            # Criar e enviar transação
            dados     = f"{VOTE_PREFIX}:{VERSION}:VOTE:{tema_id}:{opcao}"
            dados_hex = to_hex(dados)

            utxos = rpc("listunspent")
            if not utxos:
                raise Exception(T("sem_utxo"))

            utxo   = utxos[0]
            txid   = utxo['txid']
            vout   = utxo['vout']
            amount = utxo['amount']
            fee    = 0.001
            change = round(amount - fee, 8)

            endereco = rpc("getnewaddress")
            inputs   = json.dumps([{"txid": txid, "vout": vout}])
            outputs  = json.dumps({endereco: change, "data": dados_hex})

            raw_tx  = rpc("createrawtransaction", inputs, outputs)
            sign_tx = rpc("signrawtransaction", raw_tx)
            hex_tx  = sign_tx['hex']
            final   = rpc("sendrawtransaction", hex_tx)

            self.root.after(0, lambda: messagebox.showinfo(
                T("voto_ok"),
                f"Seu voto foi gravado na blockchain!\n\n"
                f"Tema: {self.tema_selecionado['titulo']}\n"
                f"Opção: {opcao}\n\n"
                f"TX: {final[:32]}...\n\n"
                f"Aguarde ~1 minuto para confirmação\ne os resultados serão atualizados automaticamente."))

            # Recarregar após 65 segundos (tempo de 1 bloco)
            self.root.after(0, self.carregar_temas)
            self.root.after(65000, self.carregar_temas)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                T("aviso_titulo"), T("erro_voto", erro=str(e))))
        
        finally:
            self.root.after(0, lambda: self.btn_votar.config(
                state=tk.NORMAL,
                text=T("btn_votar")))

    def atualizar_resultados(self):
        self.texto_resultados.config(state=tk.NORMAL)
        self.texto_resultados.delete(1.0, tk.END)
        
        if not self.temas:
            self.texto_resultados.insert(tk.END, "\n  Nenhum tema disponível\n")
            self.texto_resultados.config(state=tk.DISABLED)
            return
        
        for tema in self.temas:
            status = "🔴 ENCERRADO" if tema.get('encerrado') else "🟢 EM VOTAÇÃO"
            self.texto_resultados.insert(tk.END,
                f"\n{'═'*60}\n"
                f"  📋 {tema['titulo']}\n"
                f"  ID: {tema['id']} | {status} | Prazo: {tema['prazo']}\n"
                f"  Total: {tema['total']} voto(s)\n"
                f"{'─'*60}\n")
            
            total = tema['total'] or 1
            for opcao in tema['opcoes']:
                count = tema['contagem'].get(opcao, 0)
                pct   = count / total * 100
                barra = '█' * int(pct / 5) + '░' * (20 - int(pct / 5))
                self.texto_resultados.insert(tk.END,
                    f"  {opcao:<15} {barra} {count:>4} ({pct:>5.1f}%)\n")
        
        self.texto_resultados.insert(tk.END, f"\n{'═'*60}\n")
        self.texto_resultados.config(state=tk.DISABLED)

    def remover_2fa(self):
        """Remove a configuração 2FA"""
        if not os.path.exists(ARQUIVO_2FA):
            messagebox.showinfo("2FA", T("2fa_nao_config"))
            return
        confirmar = messagebox.askyesno(T("remover_2fa_conf"),
            "Tem certeza que deseja remover a autenticação de dois fatores?\n\n"
            "⚠️ Suas transações ficarão menos protegidas!")
        if confirmar:
            os.remove(ARQUIVO_2FA)
            self.secret_2fa = None
            self.atualizar_status_2fa()
            messagebox.showinfo(T("2fa_removido"), T("2fa_removido_msg"))

    def salvar_config(self):
        global rpc_user, rpc_pass, rpc_port, datadir, cli_path
        
        rpc_user  = self.config_vars['rpc_user_var'].get()
        rpc_pass  = self.config_vars['rpc_pass_var'].get()
        rpc_port  = self.config_vars['rpc_port_var'].get()
        datadir   = self.config_vars['datadir_var'].get() or None
        cli_path  = self.config_vars['cli_var'].get() or None
        
        self.lbl_config_status.config(text=T("config_salvo"), fg=COR_VERDE)
        self.verificar_carteira()
        self.atualizar_status_2fa()

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    
    # Ícone (tenta carregar, ignora se não encontrar)
    try:
        root.iconbitmap("mulacoin.ico")
    except:
        pass
    
    app = MulacoinVoteApp(root)
    root.mainloop()
