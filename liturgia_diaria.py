import requests
import textwrap
import tkinter as tk

def impressao_formatada(elementos={},refrao=False):
   for elemento in elementos:
      print(f"\n{elemento["referencia"]}")
      print(f"{elemento["refrao"] if refrao else elemento["titulo"]}\n") 
  
      elemento_formatado = textwrap.wrap(elemento["texto"], width=120)
      for linha in elemento_formatado:
          print(f"{linha}")

def liturgia_diaria():
    try:       
       response = requests.get("https://liturgia.up.railway.app/v2/",timeout=5)
       response.raise_for_status()
       dados = response.json()
        
       print(f"{dados["data"]}")
       print(f"{dados["liturgia"]}")
       print(f"{dados["cor"]}")
        
       impressao_formatada(dados["leituras"]["primeiraLeitura"]["texto"])
       impressao_formatada(dados["leituras"]["salmo"],True)
       impressao_formatada(dados["leituras"]["segundaLeitura"])
       impressao_formatada(dados["leituras"]["evangelho"])

    except requests.exceptions.HTTPError as erro_http:
        print(f"Erro de conexão: {erro_http}")
        print(f"Código de Status: {erro_http.response.status_code}")

    except requests.exceptions.Timeout:
        print("A requisição demorou muito (TimeOut) e foi cancelada.")

    except requests.exceptions.ConnectionError:
       print("Erro de conexão. Verifique sua conexão com a internet.")

    except request.exceptions.RequestException as erro:
       print(f"Ocorreu um erro inesperado: {erro}")

janela = tk.Tk()
janela.title("Liturgia Diária")
janela.geometry("500x500")

primeira_leitura= tk.StringVar(value="Primeira Leitura")

frame_primeira_leitura = tk.Frame(janela)
frame_primeira_leitura.grid(row=0,column=0,padx=10,pady=10)

label_primeira_leitura = tk.Label(frame_primeira_leitura, textvariable=primeira_leitura)
label_primeira_leitura.grid(row=1,column=1,padx=10,pady=10)

janela.mainloop()
