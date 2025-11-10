import requests
import tkinter as tk
import tkinter.scrolledtext as st
from tkinter import ttk

class LiturgiaApp:
    def __init__(self, root):
        """
        Construtor da aplicação.
        Configura a janela principal e os widgets base (scroll, canvas).
        """
        self.root = root
        self.root.title("Liturgia Diária")
        self.root.geometry("690x710")

        # --- 1. Configuração da Área Rolável (Scrollable Area) ---
        # Este é o setup padrão para um frame rolável
        
        # Frame principal que preenche a janela
        frame_principal = ttk.Frame(self.root)
        frame_principal.pack(fill='both', expand=True)

        # Canvas e Scrollbar
        self.canvas = tk.Canvas(frame_principal)
        scrollbar = ttk.Scrollbar(frame_principal, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Layout do Canvas e Scrollbar
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # --- 2. Frame de Conteúdo (Onde TUDO vai) ---
        # Este é o frame que VAI rolar, ele vive DENTRO do canvas
        self.frame_conteudo = ttk.Frame(self.canvas)
        
        # Insere o frame de conteúdo dentro do canvas
        self.canvas.create_window((0, 0), window=self.frame_conteudo, anchor="nw")

        # --- 3. Ligações de Eventos (Binds) ---
        
        # Atualiza a região de scroll quando o tamanho do frame_conteudo muda
        self.frame_conteudo.bind("<Configure>", self.on_frame_configure)
        
        # Liga o scroll do rato (mousewheel)
        self._bind_mousewheel(self.root) # Ligar à janela inteira

        # --- 4. Configuração da Grelha (Grid) ---
        # Configura as colunas NO FRAME DE CONTEÚDO (não na janela)
        self.frame_conteudo.columnconfigure(0, weight=1)
        self.frame_conteudo.columnconfigure(1, weight=1)
        self.frame_conteudo.columnconfigure(2, weight=1)
        self.frame_conteudo.columnconfigure(3, weight=1)

        # --- 5. Carregar os Dados ---
        self.carregar_dados_liturgia()


    def on_frame_configure(self, event):
        """Atualiza a região de scroll do canvas."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # --- Funções de Scroll do Rato ---
    def _on_mousewheel(self, event):
        """Move o canvas para cima ou para baixo."""
        # No Windows/macOS usa-se event.delta. No Linux, o número do botão.
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")

    def _bind_mousewheel(self, widget):
        """Aplica o bind do scroll do rato a um widget e seus filhos."""
        # Aplica o bind ao widget principal
        widget.bind_all("<MouseWheel>", self._on_mousewheel)
        widget.bind_all("<Button-4>", self._on_mousewheel)
        widget.bind_all("<Button-5>", self._on_mousewheel)


    def carregar_dados_liturgia(self):
        """
        Busca os dados da API e chama as funções para construir a UI.
        """
        url = "https://liturgia.up.railway.app/v2/"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            dados = response.json()
            
            # Limpa qualquer conteúdo antigo (caso seja um "refresh")
            self.limpar_conteudo()
            
            # Constrói a UI com os novos dados
            self.construir_ui(dados)

        except requests.exceptions.HTTPError as erro_http:
            self.mostrar_erro(f"Erro de conexão: {erro_http}\nCódigo de Status: {erro_http.response.status_code}")
        except requests.exceptions.Timeout:
            self.mostrar_erro("A requisição demorou muito (TimeOut) e foi cancelada.")
        except requests.exceptions.ConnectionError:
            self.mostrar_erro("Erro de conexão. Verifique sua conexão com a internet.")
        except requests.exceptions.RequestException as erro:
            self.mostrar_erro(f"Ocorreu um erro inesperado: {erro}")
        except tk.TclError:
            # Acontece se a janela for fechada durante o request
            pass

    def construir_ui(self, dados):
        """
        Cria os widgets da UI com base nos dados da API.
        """
        # --- Cabeçalho ---
        # Separa a criação do widget do .grid()
        data_label = ttk.Label(self.frame_conteudo, text=dados["data"], anchor='w')
        liturgia_label = ttk.Label(self.frame_conteudo, text=dados["liturgia"], anchor='center')
        cor_label = ttk.Label(self.frame_conteudo, text=dados["cor"], anchor='e')
        
        # sticky='EW' faz o label preencher a coluna
        data_label.grid(row=0, column=0, sticky='EW')
        liturgia_label.grid(row=0, column=1, columnspan=2, sticky='EW')
        cor_label.grid(row=0, column=3, sticky='EW')

        # --- Leituras ---
        # A função de impressão agora é um método da classe
        linha_atual = 1 # Começa na linha 1 (abaixo do cabeçalho)
        
        linha_atual = self.imprimir_bloco_leitura(dados["leituras"]["primeiraLeitura"], linha_atual)
        linha_atual = self.imprimir_bloco_leitura(dados["leituras"]["salmo"], linha_atual, refrao=True)
        linha_atual = self.imprimir_bloco_leitura(dados["leituras"]["segundaLeitura"], linha_atual)
        linha_atual = self.imprimir_bloco_leitura(dados["leituras"]["evangelho"], linha_atual)

    def imprimir_bloco_leitura(self, elementos, linha_inicio, refrao=False):
        """
        Cria um bloco de widgets (título, texto) para uma leitura.
        Retorna a próxima linha livre.
        """
        linha = linha_inicio
        
        # 'elementos' pode ser uma lista (como no Salmo) ou um dict (outras)
        # Vamos garantir que seja sempre uma lista para unificar o loop
        if not isinstance(elementos, list):
            elementos = [elementos]

        for elemento in elementos:
            if not elemento: # Pula se o elemento for vazio (ex: segunda leitura)
                continue
                
            # --- Linha de Espaçamento ---
            # Um frame vazio é melhor que um label vazio para espaçamento
            ttk.Frame(self.frame_conteudo, height=10).grid(row=linha, column=0)
            linha += 1
            
            # --- Referência ---
            referencia_label = ttk.Label(self.frame_conteudo, text=elemento["referencia"], anchor='center', style='Header.TLabel')
            referencia_label.grid(row=linha, column=0, columnspan=4, sticky='EW')
            linha += 1

            # --- Título / Refrão ---
            titulo_texto = elemento["refrao"] if refrao else elemento["titulo"]
            titulo_label = ttk.Label(self.frame_conteudo, text=titulo_texto, anchor='center', style='Title.TLabel')
            titulo_label.grid(row=linha, column=0, columnspan=4, sticky='EW')
            linha += 1
            
            # --- Caixa de Texto ---
            caixa_texto = st.ScrolledText(self.frame_conteudo, wrap='word', height=10)
            caixa_texto.grid(row=linha, column=0, columnspan=4, padx=5, sticky='EW')
            
            caixa_texto.config(state='normal')
            caixa_texto.delete('1.0', 'end')
            caixa_texto.insert('1.0', elemento["texto"])
            caixa_texto.config(state='disabled')
            
            linha += 1
            
        return linha # Retorna a próxima linha disponível

    def mostrar_erro(self, mensagem):
        """Mostra uma mensagem de erro no frame de conteúdo."""
        self.limpar_conteudo() # Limpa TUDO
        erro_label = ttk.Label(self.frame_conteudo, text=mensagem, style='Error.TLabel')
        erro_label.grid(row=0, column=0, padx=10, pady=10)

    def limpar_conteudo(self):
        """Remove todos os widgets do frame de conteúdo."""
        for widget in self.frame_conteudo.winfo_children():
            widget.destroy()

    def definir_estilos(self):
        """Define estilos personalizados para os widgets."""
        style = ttk.Style()
        style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))
        style.configure('Title.TLabel', font=('Helvetica', 10, 'italic'))
        style.configure('Error.TLabel', font=('Helvetica', 12), foreground='red')


# --- Ponto de Entrada da Aplicação ---
if __name__ == "__main__":
    root = tk.Tk()
    app = LiturgiaApp(root)
    root.mainloop()
