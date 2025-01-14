import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
import numpy as np
from typing import List, Tuple

class InterfaceGUI:
    def __init__(self, simulador):
        self.simulador = simulador
        self.window = Gtk.Window(title="Simulador de Comunicação Digital")
        self.window.set_default_size(800, 600)
        self.window.connect("destroy", Gtk.main_quit)

        # Layout principal
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.window.add(self.main_box)

        # Área de entrada de dados
        self.criar_area_entrada()
        
        # Área de configuração
        self.criar_area_configuracao()
        
        # Área de visualização
        self.criar_area_visualizacao()
        
        # Área de log
        self.criar_area_log()

        self.window.show_all()

    def criar_area_entrada(self):
        """Cria área para entrada de dados."""
        frame = Gtk.Frame(label="Entrada de Dados")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        frame.add(box)

        # Entrada de texto
        self.entrada_texto = Gtk.TextView()
        self.entrada_texto.set_wrap_mode(Gtk.WrapMode.WORD)
        scroll = Gtk.ScrolledWindow()
        scroll.add(self.entrada_texto)
        box.pack_start(scroll, True, True, 0)

        # Botões de ação
        bbox = Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)
        bbox.set_layout(Gtk.ButtonBoxStyle.END)
        
        btn_transmitir = Gtk.Button(label="Transmitir")
        btn_transmitir.connect("clicked", self.on_transmitir_clicked)
        bbox.add(btn_transmitir)
        
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

        # Detecção de Erros
        self.check_crc = Gtk.CheckButton(label="Usar CRC")
        self.check_crc.set_active(True)
        grid.attach(self.check_crc, 0, 2, 1, 1)

        # Correção de Erros
        self.check_hamming = Gtk.CheckButton(label="Usar Hamming")
        self.check_hamming.set_active(True)
        grid.attach(self.check_hamming, 1, 2, 1, 1)

        self.main_box.pack_start(frame, False, False, 0)

    def criar_area_visualizacao(self):
        """Cria área para visualização dos sinais."""
        frame = Gtk.Frame(label="Visualização")
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 6))
        
        # Configura os subplots
        self.ax1.set_title("Sinal Digital")
        self.ax2.set_title("Sinal Modulado")
        
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
        buffer = self.text_log.get_buffer()
        end_iter = buffer.get_end_iter()
        buffer.insert(end_iter, mensagem + "\n")
        # Auto-scroll para última mensagem
        mark = buffer.create_mark(None, buffer.get_end_iter(), False)
        self.text_log.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)

    def plotar_sinais(self, tempo: np.ndarray, sinal_digital: np.ndarray, 
                     sinal_modulado: np.ndarray):
        """Plota os sinais nas áreas de visualização."""
        self.ax1.clear()
        self.ax2.clear()
        
        self.ax1.plot(tempo, sinal_digital)
        self.ax1.set_title("Sinal Digital")
        self.ax1.grid(True)
        
        self.ax2.plot(tempo, sinal_modulado)
        self.ax2.set_title("Sinal Modulado")
        self.ax2.grid(True)
        
        self.fig.canvas.draw()

    def on_transmitir_clicked(self, button):
        """Manipula o evento de clique no botão transmitir."""
        buffer = self.entrada_texto.get_buffer()
        texto = buffer.get_text(buffer.get_start_iter(), 
                              buffer.get_end_iter(), True)
        
        if not texto:
            self.adicionar_log("Erro: Nenhum dado para transmitir")
            return

        try:
            # Converte texto para bytes
            dados = texto.encode('utf-8')
            
            # Processa na camada de enlace
            usar_crc = self.check_crc.get_active()
            usar_hamming = self.check_hamming.get_active()
            
            quadro = self.simulador.camada_enlace.transmitir(
                dados, usar_crc, usar_hamming)
            
            # Converte para bits
            bits = [int(b) for byte in quadro for b in format(byte, '08b')]
            
            # Aplica modulação digital selecionada
            modulacao = self.combo_modulacao.get_active_text()
            if modulacao == "NRZ-Polar":
                tempo, sinal_digital = self.simulador.camada_fisica.nrz_polar(bits)
            elif modulacao == "Manchester":
                tempo, sinal_digital = self.simulador.camada_fisica.manchester(bits)
            else:  # Bipolar
                tempo, sinal_digital = self.simulador.camada_fisica.bipolar(bits)
            
            # Aplica modulação por portadora selecionada
            modulacao_port = self.combo_portadora.get_active_text()
            if modulacao_port == "ASK":
                _, sinal_modulado = self.simulador.modulacao_portadora.ask(bits)
            elif modulacao_port == "FSK":
                _, sinal_modulado = self.simulador.modulacao_portadora.fsk(bits)
            else:  # 8-QAM
                _, sinal_modulado = self.simulador.modulacao_portadora.qam8(bits)
            
            # Atualiza visualização
            self.plotar_sinais(tempo, sinal_digital, sinal_modulado)
            
            self.adicionar_log(f"Dados transmitidos com sucesso usando {modulacao} e {modulacao_port}")
            
        except Exception as e:
            self.adicionar_log(f"Erro na transmissão: {str(e)}")

    def iniciar(self):
        """Inicia a interface gráfica."""
        Gtk.main()