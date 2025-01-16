import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
import numpy as np
import socket
import threading
import json

class TransmissorGUI:
    def __init__(self):
        self.window = Gtk.Window(title="Transmissor de Comunicação Digital")
        self.window.set_default_size(800, 600)
        self.window.connect("destroy", Gtk.main_quit)

        # Socket setup
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

        # Layout principal
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.window.add(self.main_box)

        self.criar_area_conexao()
        self.criar_area_entrada()
        self.criar_area_configuracao()
        self.criar_area_visualizacao()
        self.criar_area_log()

        self.window.show_all()

    def criar_area_conexao(self):
        """Cria área para configuração de conexão."""
        frame = Gtk.Frame(label="Conexão")
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

        # Botão Conectar
        self.btn_connect = Gtk.Button(label="Conectar")
        self.btn_connect.connect("clicked", self.on_connect_clicked)
        box.pack_start(self.btn_connect, False, False, 0)

        self.main_box.pack_start(frame, False, False, 0)

    def criar_area_entrada(self):
        """Cria área para entrada de dados."""
        frame = Gtk.Frame(label="Entrada de Dados")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        frame.add(box)

        self.entrada_texto = Gtk.TextView()
        self.entrada_texto.set_wrap_mode(Gtk.WrapMode.WORD)
        scroll = Gtk.ScrolledWindow()
        scroll.add(self.entrada_texto)
        box.pack_start(scroll, True, True, 0)

        bbox = Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)
        bbox.set_layout(Gtk.ButtonBoxStyle.END)
        
        self.btn_transmitir = Gtk.Button(label="Transmitir")
        self.btn_transmitir.connect("clicked", self.on_transmitir_clicked)
        self.btn_transmitir.set_sensitive(False)
        bbox.add(self.btn_transmitir)
        
        box.pack_start(bbox, False, False, 0)
        self.main_box.pack_start(frame, True, True, 0)

    def criar_area_configuracao(self):
        """Cria área de configuração dos parâmetros."""
        frame = Gtk.Frame(label="Configurações")
        grid = Gtk.Grid(column_spacing=12, row_spacing=6)
        frame.add(grid)

        # Modulação Digital
        label = Gtk.Label(label="Modulação Digital:")
        grid.attach(label, 0, 0, 1, 1)
        
        self.combo_modulacao = Gtk.ComboBoxText()
        for mod in ["NRZ-Polar", "Manchester", "Bipolar"]:
            self.combo_modulacao.append_text(mod)
        self.combo_modulacao.set_active(0)
        grid.attach(self.combo_modulacao, 1, 0, 1, 1)

        # Modulação Portadora
        label = Gtk.Label(label="Modulação Portadora:")
        grid.attach(label, 0, 1, 1, 1)
        
        self.combo_portadora = Gtk.ComboBoxText()
        for mod in ["ASK", "FSK", "8-QAM"]:
            self.combo_portadora.append_text(mod)
        self.combo_portadora.set_active(0)
        grid.attach(self.combo_portadora, 1, 1, 1, 1)

        self.main_box.pack_start(frame, False, False, 0)

    def criar_area_visualizacao(self):
        """Cria área para visualização dos sinais."""
        frame = Gtk.Frame(label="Visualização")
        self.fig, self.ax1 = plt.subplots(1, 1, figsize=(8, 4))
        
        self.ax1.set_title("Sinal Digital")
        canvas = FigureCanvas(self.fig)
        frame.add(canvas)
        self.main_box.pack_start(frame, True, True, 0)

    def criar_area_log(self):
        """Cria área para exibição de logs."""
        frame = Gtk.Frame(label="Log")
        scroll = Gtk.ScrolledWindow()
        frame.add(scroll)

        self.text_log = Gtk.TextView()
        self.text_log.set_editable(False)
        self.text_log.set_wrap_mode(Gtk.WrapMode.WORD)
        scroll.add(self.text_log)

        self.main_box.pack_start(frame, True, True, 0)

    def adicionar_log(self, mensagem: str):
        """Adiciona mensagem ao log."""
        def append_text():
            buffer = self.text_log.get_buffer()
            end_iter = buffer.get_end_iter()
            buffer.insert(end_iter, mensagem + "\n")
            mark = buffer.create_mark(None, buffer.get_end_iter(), False)
            self.text_log.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)
        GLib.idle_add(append_text)

    def on_connect_clicked(self, button):
        """Manipula o evento de clique no botão conectar."""
        if not self.connected:
            try:
                ip = self.entry_ip.get_text()
                port = int(self.entry_port.get_text())
                self.socket.connect((ip, port))
                self.connected = True
                self.btn_connect.set_label("Desconectar")
                self.btn_transmitir.set_sensitive(True)
                self.adicionar_log(f"Conectado ao receptor em {ip}:{port}")
            except Exception as e:
                self.adicionar_log(f"Erro na conexão: {str(e)}")
        else:
            try:
                self.socket.close()
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connected = False
                self.btn_connect.set_label("Conectar")
                self.btn_transmitir.set_sensitive(False)
                self.adicionar_log("Desconectado do receptor")
            except Exception as e:
                self.adicionar_log(f"Erro ao desconectar: {str(e)}")

    def on_transmitir_clicked(self, button):
        """Manipula o evento de clique no botão transmitir."""
        if not self.connected:
            self.adicionar_log("Erro: Não conectado ao receptor")
            return

        buffer = self.entrada_texto.get_buffer()
        texto = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
        
        if not texto:
            self.adicionar_log("Erro: Nenhum dado para transmitir")
            return

        try:
            # Prepara os dados para transmissão
            dados = {
                'texto': texto,
                'modulacao_digital': self.combo_modulacao.get_active_text(),
                'modulacao_portadora': self.combo_portadora.get_active_text()
            }
            
            # Envia os dados
            self.socket.sendall(json.dumps(dados).encode('utf-8'))
            
            # Simula sinal digital para visualização
            bits = [int(b) for byte in texto.encode('utf-8') for b in format(byte, '08b')]
            t = np.linspace(0, len(bits), len(bits))
            
            # Plota o sinal
            self.ax1.clear()
            self.ax1.step(t, bits, where='post')
            self.ax1.set_title("Sinal Digital Transmitido")
            self.ax1.grid(True)
            self.fig.canvas.draw()
            
            self.adicionar_log("Dados transmitidos com sucesso")
            
        except Exception as e:
            self.adicionar_log(f"Erro na transmissão: {str(e)}")

    def iniciar(self):
        """Inicia a interface gráfica."""
        Gtk.main()

if __name__ == "__main__":
    transmissor = TransmissorGUI()
    transmissor.iniciar()