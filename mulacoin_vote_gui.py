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
from tkinter import ttk, messagebox, font
import subprocess
import json
import binascii
import threading
import urllib.request
import os
import sys

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
        self.root.title("🐴 Mulacoin Vote — Votação Descentralizada")
        self.root.geometry("700x600")
        self.root.configure(bg=COR_FUNDO)
        self.root.resizable(True, True)
        
        self.temas = []
        self.tema_selecionado = None
        self.opcao_var = tk.StringVar()
        
        self.criar_interface()
        self.verificar_carteira()
        self.iniciar_auto_refresh()

    def criar_interface(self):
        # Header
        header = tk.Frame(self.root, bg=COR_CARD, pady=16)
        header.pack(fill=tk.X)
        
        tk.Label(header, text="🐴 MULACOIN VOTE", 
                font=("Arial", 20, "bold"),
                fg=COR_DOURADO, bg=COR_CARD).pack()
        tk.Label(header, text="Votação descentralizada na blockchain",
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
        self.notebook.add(self.frame_votar, text="🗳️  Votar")
        self.criar_aba_votar()

        # Aba 2: Resultados
        self.frame_resultados = tk.Frame(self.notebook, bg=COR_FUNDO)
        self.notebook.add(self.frame_resultados, text="📊  Resultados")
        self.criar_aba_resultados()

        # Aba 3: Sugerir Tema
        self.frame_sugerir = tk.Frame(self.notebook, bg=COR_FUNDO)
        self.notebook.add(self.frame_sugerir, text="💡  Sugerir Tema")
        self.criar_aba_sugerir()

        # Aba 4: Configurações
        self.frame_config = tk.Frame(self.notebook, bg=COR_FUNDO)
        self.notebook.add(self.frame_config, text="⚙️  Configurações")
        self.criar_aba_config()

        # Footer
        footer = tk.Frame(self.root, bg=COR_CARD, pady=8)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Label(footer, text="mulacoin.com.br | Picanha Cumpanheiro! 🍖",
                font=("Arial", 9), fg=COR_MUTED, bg=COR_CARD).pack()

    def criar_aba_votar(self):
        # Lista de temas
        tk.Label(self.frame_votar, text="Selecione um tema:",
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
                text="← Selecione um tema acima",
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
                text="🗳️  REGISTRAR VOTO NA BLOCKCHAIN",
                font=("Arial", 12, "bold"),
                bg=COR_DOURADO, fg=COR_FUNDO,
                relief=tk.FLAT, padx=20, pady=10,
                cursor="hand2",
                command=self.ao_votar,
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
                text="🔄 Atualizar resultados",
                font=("Arial", 10),
                bg=COR_DOURADO, fg=COR_FUNDO,
                relief=tk.FLAT, padx=16, pady=6,
                cursor="hand2",
                command=self.atualizar_resultados).pack(pady=8)

    def criar_aba_sugerir(self):
        # Titulo
        tk.Label(self.frame_sugerir,
                text="💡 Sugerir Novo Tema de Votação",
                font=("Arial", 13, "bold"), fg=COR_DOURADO, bg=COR_FUNDO).pack(
                anchor=tk.W, padx=16, pady=(16, 4))

        tk.Label(self.frame_sugerir,
                text="O tema será gravado na blockchain e enviado para aprovação do administrador.",
                font=("Arial", 10), fg=COR_MUTED, bg=COR_FUNDO,
                wraplength=650, justify=tk.LEFT).pack(anchor=tk.W, padx=16, pady=(0, 16))

        # Título do tema
        frame_titulo = tk.Frame(self.frame_sugerir, bg=COR_FUNDO)
        frame_titulo.pack(fill=tk.X, padx=16, pady=4)
        tk.Label(frame_titulo, text="Título da votação:",
                font=("Arial", 10, "bold"), fg=COR_TEXTO, bg=COR_FUNDO).pack(anchor=tk.W)
        self.sugerir_titulo = tk.Entry(frame_titulo,
                font=("Arial", 11), bg=COR_CARD, fg=COR_TEXTO,
                insertbackground=COR_DOURADO, relief=tk.FLAT,
                borderwidth=6)
        self.sugerir_titulo.pack(fill=tk.X, pady=4)
        tk.Label(frame_titulo, text="Ex: Você merece picanha?",
                font=("Arial", 9), fg=COR_MUTED, bg=COR_FUNDO).pack(anchor=tk.W)

        # Opções
        frame_opcoes = tk.Frame(self.frame_sugerir, bg=COR_FUNDO)
        frame_opcoes.pack(fill=tk.X, padx=16, pady=8)
        tk.Label(frame_opcoes, text="Opções de voto (separe por vírgula):",
                font=("Arial", 10, "bold"), fg=COR_TEXTO, bg=COR_FUNDO).pack(anchor=tk.W)
        self.sugerir_opcoes = tk.Entry(frame_opcoes,
                font=("Arial", 11), bg=COR_CARD, fg=COR_TEXTO,
                insertbackground=COR_DOURADO, relief=tk.FLAT,
                borderwidth=6)
        self.sugerir_opcoes.pack(fill=tk.X, pady=4)
        tk.Label(frame_opcoes, text="Ex: Sim,Não,Talvez",
                font=("Arial", 9), fg=COR_MUTED, bg=COR_FUNDO).pack(anchor=tk.W)

        # Prazo
        frame_prazo = tk.Frame(self.frame_sugerir, bg=COR_FUNDO)
        frame_prazo.pack(fill=tk.X, padx=16, pady=8)
        tk.Label(frame_prazo, text="Prazo de votação (AAAA-MM-DD):",
                font=("Arial", 10, "bold"), fg=COR_TEXTO, bg=COR_FUNDO).pack(anchor=tk.W)
        self.sugerir_prazo = tk.Entry(frame_prazo,
                font=("Arial", 11), bg=COR_CARD, fg=COR_TEXTO,
                insertbackground=COR_DOURADO, relief=tk.FLAT,
                borderwidth=6, width=20)
        self.sugerir_prazo.insert(0, "2026-10-04")
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
                text="📤  ENVIAR SUGESTÃO PARA A BLOCKCHAIN",
                font=("Arial", 12, "bold"),
                bg=COR_DOURADO, fg=COR_FUNDO,
                relief=tk.FLAT, padx=20, pady=10,
                cursor="hand2",
                command=self.ao_sugerir_tema)
        self.btn_sugerir.pack(pady=16, padx=16, fill=tk.X)

        # Nota informativa
        nota = ("ℹ️  Ao enviar, o tema será gravado permanentemente na blockchain Mulacoin.\n"
                "Uma pequena taxa em FazoL será cobrada para registrar a transação.\n"
                "O tema ficará pendente até ser aprovado pelo administrador.")
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
            messagebox.showwarning("Atenção", "Digite o título da votação!")
            return
        if not opcoes or "," not in opcoes:
            messagebox.showwarning("Atenção", "Digite pelo menos 2 opções separadas por vírgula!")
            return
        if not prazo or len(prazo) != 10:
            messagebox.showwarning("Atenção", "Digite o prazo no formato AAAA-MM-DD!")
            return

        opcoes_fmt = "|".join([o.strip() for o in opcoes.split(",")])
        dados = f"MVOTE:1:CREATE:XXXXXXXX:{titulo}:{opcoes_fmt}:{prazo}"
        if len(dados.encode("utf-8")) > 200:
            messagebox.showwarning("Atenção",
                f"Dados muito longos! Reduza o título ou as opções.\n"
                f"Tamanho atual: {len(dados.encode())} bytes (máximo: 200)")
            return

        confirmar = messagebox.askyesno(
            "Confirmar sugestão",
            f"Enviar sugestão de votação?\n\n"
            f"Título: {titulo}\n"
            f"Opções: {opcoes}\n"
            f"Prazo: {prazo}\n\n"
            f"⚠️ Será gravado na blockchain e cobrada uma taxa em FazoL.\n"
            f"O tema ficará pendente até aprovação do administrador.\n\n"
            f"Confirmar?")

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
                raise Exception("Nenhum UTXO disponível. Certifique-se de ter FazoL na carteira.")

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

            self.root.after(0, lambda: messagebox.showinfo("Sugestão enviada!", msg))
            self.root.after(0, lambda: self.lbl_sugerir_status.config(
                text=f"✅ Tema {tema_id} enviado! Aguardando aprovação.",
                fg=COR_VERDE))
            self.root.after(0, lambda: self.sugerir_titulo.delete(0, tk.END))
            self.root.after(0, lambda: self.sugerir_opcoes.delete(0, tk.END))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Erro", f"Não foi possível enviar a sugestão:\n\n{str(e)}"))

        finally:
            self.root.after(0, lambda: self.btn_sugerir.config(
                state=tk.NORMAL,
                text="📤  ENVIAR SUGESTÃO PARA A BLOCKCHAIN"))

    def criar_aba_config(self):
        tk.Label(self.frame_config, text="Configuração RPC da Carteira",
                font=("Arial", 12, "bold"), fg=COR_DOURADO, bg=COR_FUNDO).pack(
                anchor=tk.W, padx=16, pady=16)

        campos = [
            ("Usuário RPC:", "rpc_user_var", "mula"),
            ("Senha RPC:", "rpc_pass_var", "picanha"),
            ("Porta RPC:", "rpc_port_var", "23560"),
            ("Datadir (opcional):", "datadir_var", ""),
            ("Caminho mulacoin-cli:", "cli_var", ""),
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
                text="💾 Salvar e reconectar",
                font=("Arial", 10, "bold"),
                bg=COR_DOURADO, fg=COR_FUNDO,
                relief=tk.FLAT, padx=16, pady=8,
                cursor="hand2",
                command=self.salvar_config).pack(pady=16)

        self.lbl_config_status = tk.Label(self.frame_config,
                text="", font=("Arial", 10), fg=COR_VERDE, bg=COR_FUNDO)
        self.lbl_config_status.pack()

        # Nota
        nota = ("⚠️ A carteira Mulacoin precisa estar aberta e rodando\n"
                "com as opções -server=1 -rpcuser=mula -rpcpassword=picanha")
        tk.Label(self.frame_config, text=nota,
                font=("Arial", 9), fg=COR_MUTED, bg=COR_FUNDO,
                justify=tk.LEFT, wraplength=600).pack(padx=16, pady=16, anchor=tk.W)

    # ── Lógica ────────────────────────────────────────────────────────────────
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
                text="🟢 Carteira conectada", fg=COR_VERDE))
            self.root.after(0, lambda: self.lbl_blocos.config(
                text=f"Bloco: {blocos:,}"))
            self.root.after(0, self.carregar_temas)
        except Exception as e:
            self.root.after(0, lambda: self.lbl_carteira.config(
                text="🔴 Carteira offline — abra o mulacoin-qt primeiro",
                fg=COR_VERMELHO))
            self.root.after(0, self.carregar_temas)

    def carregar_temas(self):
        self.lista_temas.delete(0, tk.END)
        self.lista_temas.insert(tk.END, "  Carregando temas...")
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
            self.lista_temas.insert(tk.END, "  Nenhum tema disponível")
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
            text=f"📋 {tema['titulo']}\nPrazo: {tema['prazo']} | {tema['total']} votos",
            fg=COR_DOURADO)

        # Limpar radio buttons anteriores
        for widget in self.frame_radio.winfo_children():
            widget.destroy()
        
        self.opcao_var.set("")
        
        tk.Label(self.frame_radio, text="Escolha sua opção:",
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
            texto = f"  {opcao}  ({count} votos — {pct:.1f}%)"

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
            text="🔒 Votação encerrada" if encerrado else "🗳️  REGISTRAR VOTO NA BLOCKCHAIN")

    def ao_votar(self):
        if not self.tema_selecionado:
            messagebox.showwarning("Atenção", "Selecione um tema primeiro!")
            return
        
        opcao = self.opcao_var.get()
        if not opcao:
            messagebox.showwarning("Atenção", "Selecione uma opção para votar!")
            return
        
        tema_id = self.tema_selecionado['id']
        titulo  = self.tema_selecionado['titulo']
        
        confirmar = messagebox.askyesno(
            "Confirmar voto",
            f"Você está prestes a registrar seu voto:\n\n"
            f"Tema: {titulo}\n"
            f"Opção: {opcao}\n\n"
            f"⚠️ Este voto será gravado PERMANENTEMENTE na blockchain!\n"
            f"Não é possível alterar depois.\n\n"
            f"Confirmar?")
        
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
                                    text="🗳️  REGISTRAR VOTO NA BLOCKCHAIN"))
                                return
                except:
                    continue

            # Criar e enviar transação
            dados     = f"{VOTE_PREFIX}:{VERSION}:VOTE:{tema_id}:{opcao}"
            dados_hex = to_hex(dados)

            utxos = rpc("listunspent")
            if not utxos:
                raise Exception("Nenhum UTXO disponível. Certifique-se de ter FazoL na carteira.")

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
                "✅ Voto registrado!",
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
                "Erro", f"Não foi possível registrar o voto:\n\n{str(e)}\n\n"
                "Verifique se a carteira Mulacoin está aberta."))
        
        finally:
            self.root.after(0, lambda: self.btn_votar.config(
                state=tk.NORMAL,
                text="🗳️  REGISTRAR VOTO NA BLOCKCHAIN"))

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

    def salvar_config(self):
        global rpc_user, rpc_pass, rpc_port, datadir, cli_path
        
        rpc_user  = self.config_vars['rpc_user_var'].get()
        rpc_pass  = self.config_vars['rpc_pass_var'].get()
        rpc_port  = self.config_vars['rpc_port_var'].get()
        datadir   = self.config_vars['datadir_var'].get() or None
        cli_path  = self.config_vars['cli_var'].get() or None
        
        self.lbl_config_status.config(text="✅ Configurações salvas!", fg=COR_VERDE)
        self.verificar_carteira()

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
