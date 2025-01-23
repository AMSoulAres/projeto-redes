import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
import numpy as np
import socket
import threading
import json

class ReceptorGUI:
    def __init__(self):
        #TODO: descomentar quando implementar a modulação
        #  # Inicializa módulos de modulação
        # self.mod_digital = ModulacaoDigital(taxa_amostragem=100)
        # self.mod_portadora = ModulacaoPortadora(freq_portadora=1000, taxa_amostragem=100)

        self.window = Gtk.Window(title="Receptor de Comunicação Digital")
        self.window.set_default_size(800, 600)
        self.window.connect("destroy", Gtk.main_quit)

        # Socket setup
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket = None
        self.running = True

        # Layout principal
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.window.add(self.main_box)

        self.criar_area_servidor()
        self.criar_area_recebidos()
        self.criar_area_visualizacao()
        self.criar_area_log()

        self.window.show_all()

    def criar_area_servidor(self):
        """Cria área para configuração do servidor."""
        frame = Gtk.Frame(label="Servidor")
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        frame.add(box)

        # IP
        box.pack_start(Gtk.Label(label="IP:"), False, False, 0)
        self.entry_ip = Gtk.Entry()
        self.entry_ip.set_text("127.0.0.1")
        box.pack_start(self.entry_ip, True, True, 0)

        # Porta
        box.pack_start(Gtk.Label(label="Porta:"), False, False, 0)
        self.entry_port = Gtk.Entry()
        self.entry_port.set_text("65432")
        box.pack_start(self.entry_port, True, True, 0)

        # Botão Iniciar
        self.btn_start = Gtk.Button(label="Iniciar Servidor")
        self.btn_start.connect("clicked", self.on_start_clicked)
        box.pack_start(self.btn_start, False, False, 0)

        self.main_box.pack_start(frame, False, False, 0)

    def criar_area_recebidos(self):
        """Cria área para exibição dos dados recebidos."""
        frame = Gtk.Frame(label="Dados Recebidos")
        scroll = Gtk.ScrolledWindow()
        frame.add(scroll)

        self.text_received = Gtk.TextView()
        self.text_received.set_editable(False)
        self.text_received.set_wrap_mode(Gtk.WrapMode.WORD)
        scroll.add(self.text_received)

        self.main_box.pack_start(frame, True, True, 0)


    def criar_area_visualizacao(self):
        """Cria área para visualização dos sinais."""
        frame = Gtk.Frame(label="Visualização")
        
        # Ajusta a figura para ter dois subplots lado a lado
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 6))  # 1 linha, 2 colunas
        self.ax1.set_title("Sinal Digital Recebido")
        self.ax2.set_title("Sinal da Portadora Recebido")
        
        self.ax1.grid(True)
        self.ax2.grid(True)
        
        # Adiciona o canvas para exibir os gráficos na interface GTK
        canvas = FigureCanvas(self.fig)
        frame.add(canvas)
        
        self.main_box.pack_start(frame, True, True, 0)

    def criar_area_log(self):
        """Cria área para exibição de logs."""
        frame = Gtk.Frame(label="Log")
        scroll = Gtk.ScrolledWindow()
        scroll.set_min_content_height(50)  # Altura mínima do log
        scroll.set_size_request(-1, 100)   # Ajusta o tamanho inicial
        frame.add(scroll)

        self.text_log = Gtk.TextView()
        self.text_log.set_editable(False)
        self.text_log.set_wrap_mode(Gtk.WrapMode.WORD)
        scroll.add(self.text_log)

        frame.set_vexpand(False)  # Log não cresce verticalmente
        self.main_box.pack_start(frame, False, False, 0)

    def adicionar_log(self, mensagem: str):
        """Adiciona mensagem ao log."""
        def append_text():
            buffer = self.text_log.get_buffer()
            end_iter = buffer.get_end_iter()
            buffer.insert(end_iter, mensagem + "\n")
            mark = buffer.create_mark(None, buffer.get_end_iter(), False)
            self.text_log.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)
        GLib.idle_add(append_text)

    def adicionar_dados_recebidos(self, texto: str):
        """Adiciona dados recebidos à área de texto."""
        def append_text():
            buffer = self.text_received.get_buffer()
            end_iter = buffer.get_end_iter()
            buffer.insert(end_iter, texto + "\n")
            mark = buffer.create_mark(None, buffer.get_end_iter(), False)
            self.text_received.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)
        GLib.idle_add(append_text)

    #TODO: descomentar quando implementar a modulação
    # def atualizar_visualizacao(self, texto: str, mod_digital: str, mod_portadora: str):
    #     """Atualiza a visualização dos sinais."""
    #     def update():
    #         # Gera bits a partir do texto
    #         bits = [int(b) for byte in texto.encode('utf-8') for b in format(byte, '08b')]
            
    #         # Aplica modulação digital
    #         if mod_digital == "NRZ-Polar":
    #             tempo, sinal_digital = self.mod_digital.nrz_polar(bits)
    #         elif mod_digital == "Manchester":
    #             tempo, sinal_digital = self.mod_digital.manchester(bits)
    #         else:  # Bipolar
    #             tempo, sinal_digital = self.mod_digital.bipolar(bits)
            
    #         # Aplica modulação por portadora
    #         if mod_portadora == "ASK":
    #             tempo_mod, sinal_modulado = self.mod_portadora.ask(bits)
    #         elif mod_portadora == "FSK":
    #             tempo_mod, sinal_modulado = self.mod_portadora.fsk(bits)
    #         else:  # 8-QAM
    #             tempo_mod, sinal_modulado = self.mod_portadora.qam8(bits)
            
    #         # Atualiza gráficos
    #         self.ax1.clear()
    #         self.ax2.clear()
            
    #         self.ax1.plot(tempo, sinal_digital)
    #         self.ax1.set_title(f"Sinal Digital Recebido ({mod_digital})")
    #         self.ax1.grid(True)
            
    #         self.ax2.plot(tempo_mod, sinal_modulado)
    #         self.ax2.set_title(f"Sinal Modulado Recebido ({mod_portadora})")
    #         self.ax2.grid(True)
            
    #         self.fig.canvas.draw()
            
    #     GLib.idle_add(update)
    
    def atualizar_visualizacao(self, texto: str, mod_digital: str, mod_portadora: str):
        """Atualiza a visualização dos sinais."""
        def update():
            bits = [int(b) for byte in texto.encode('utf-8') for b in format(byte, '08b')]
            t = np.linspace(0, len(bits), len(bits))
            
            # Limpa os gráficos
            self.ax1.clear()
            self.ax2.clear()
            
            # Plota sinal digital
            self.ax1.step(t, bits)
            self.ax1.set_title(f"Sinal Digital Recebido ({mod_digital})")
            self.ax1.grid(True)
            
            # Simula sinal modulado (exemplo simplificado)
            if mod_portadora == "ASK":
                # Amplitude Shift Keying
                carrier_freq = 10
                t_dense = np.linspace(0, len(bits), len(bits) * 20)
                carrier = np.sin(2 * np.pi * carrier_freq * t_dense)
                signal = np.repeat(bits, 20) * carrier
            elif mod_portadora == "FSK":
                # Frequency Shift Keying
                t_dense = np.linspace(0, len(bits), len(bits) * 20)
                f0, f1 = 5, 10  # Duas frequências diferentes
                signal = np.zeros(len(t_dense))
                for i, bit in enumerate(bits):
                    freq = f1 if bit else f0
                    signal[i*20:(i+1)*20] = np.sin(2 * np.pi * freq * t_dense[i*20:(i+1)*20])
            else:  # 8-QAM (simplified)
                t_dense = np.linspace(0, len(bits), len(bits) * 20)
                signal = np.sin(2 * np.pi * 10 * t_dense) * np.repeat(bits, 20)
            
            self.ax2.plot(t_dense, signal)
            self.ax2.set_title(f"Sinal Modulado Recebido ({mod_portadora})")
            self.ax2.grid(True)
            
            self.fig.canvas.draw()
            
        GLib.idle_add(update)

    def on_start_clicked(self, button):
        """Manipula o evento de clique no botão iniciar servidor."""
        if button.get_label() == "Iniciar Servidor":
            try:
                ip = self.entry_ip.get_text()
                port = int(self.entry_port.get_text())
                self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.server_socket.bind((ip, port))
                self.server_socket.listen(1)
                
                # Inicia thread para aceitar conexões
                threading.Thread(target=self.accept_connections, daemon=True).start()
                
                button.set_label("Parar Servidor")
                self.adicionar_log(f"Servidor iniciado em {ip}:{port}")
                
            except Exception as e:
                self.adicionar_log(f"Erro ao iniciar servidor: {str(e)}")
        else:
            try:
                self.running = False
                self.server_socket.close()
                if self.client_socket:
                    self.client_socket.close()
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                button.set_label("Iniciar Servidor")
                self.adicionar_log("Servidor parado")
            except Exception as e:
                self.adicionar_log(f"Erro ao parar servidor: {str(e)}")

    def accept_connections(self):
        """Thread para aceitar conexões de clientes."""
        while self.running:
            try:
                self.client_socket, address = self.server_socket.accept()
                self.adicionar_log(f"Cliente conectado de {address}")
                
                # Inicia thread para receber dados
                threading.Thread(target=self.receive_data, args=(address,), daemon=True).start()
                
            except Exception as e:
                if self.running:
                    self.adicionar_log(f"Erro na conexão: {str(e)}")
                break

    def receive_data(self, address):
        """Thread para receber dados de um cliente."""
        while self.running:
            try:
                data = self.client_socket.recv(4096)
                if not data:
                    break
                
                # Processa os dados recebidos
                dados = json.loads(data.decode('utf-8'))
                texto = dados['texto']
                mod_digital = dados['modulacao_digital']
                mod_portadora = dados['modulacao_portadora']
                
                # Atualiza interface
                self.adicionar_dados_recebidos(f"Recebido de {address}:\n{texto}")
                self.atualizar_visualizacao(texto, mod_digital, mod_portadora)
                self.adicionar_log(f"Dados recebidos de {address} usando {mod_digital} e {mod_portadora}")
                
            except Exception as e:
                if self.running:
                    self.adicionar_log(f"Erro ao receber dados: {str(e)}")
                break
        
        if self.running:
            self.adicionar_log(f"Cliente {address} desconectado")

    def iniciar(self):
        """Inicia a interface gráfica."""
        Gtk.main()

if __name__ == "__main__":
    receiver = ReceptorGUI()
    receiver.iniciar()