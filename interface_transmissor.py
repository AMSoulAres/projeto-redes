import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from simulador_transmissor import Simulador

class TransmissorGUI:
    def __init__(self):
        self.simulador = Simulador()
        self.window = Gtk.Window(title="Transmissor de Comunicação Digital")
        self.window.set_default_size(800, 600)
        self.window.connect("destroy", Gtk.main_quit)

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
        frame = Gtk.Frame(label="Conexão")
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        frame.add(box)

        box.pack_start(Gtk.Label(label="IP:"), False, False, 0)
        self.entry_ip = Gtk.Entry()
        self.entry_ip.set_text("127.0.0.1")
        box.pack_start(self.entry_ip, True, True, 0)

        box.pack_start(Gtk.Label(label="Porta:"), False, False, 0)
        self.entry_port = Gtk.Entry()
        self.entry_port.set_text("65432")
        box.pack_start(self.entry_port, True, True, 0)

        self.btn_connect = Gtk.Button(label="Conectar")
        self.btn_connect.connect("clicked", self.on_connect_clicked)
        box.pack_start(self.btn_connect, False, False, 0)

        self.main_box.pack_start(frame, False, False, 0)

    def criar_area_entrada(self):
        frame = Gtk.Frame(label="Entrada de Dados")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        frame.add(box)

        self.entrada_texto = Gtk.TextView()
        self.entrada_texto.set_wrap_mode(Gtk.WrapMode.WORD)
        scroll = Gtk.ScrolledWindow()
        scroll.set_min_content_height(50)
        scroll.set_size_request(-1, 100)
        scroll.add(self.entrada_texto)
        box.pack_start(scroll, True, True, 0)

        bbox = Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)
        bbox.set_layout(Gtk.ButtonBoxStyle.END)

        self.btn_transmitir = Gtk.Button(label="Transmitir")
        self.btn_transmitir.connect("clicked", self.on_transmitir_clicked)
        self.btn_transmitir.set_sensitive(False)
        bbox.add(self.btn_transmitir)

        box.pack_start(bbox, False, False, 0)
        frame.set_vexpand(False)
        self.main_box.pack_start(frame, False, False, 0)

    def criar_area_configuracao(self):
        frame = Gtk.Frame(label="Configurações")
        grid = Gtk.Grid(column_spacing=12, row_spacing=6)
        frame.add(grid)

        label = Gtk.Label(label="Modulação Digital:")
        grid.attach(label, 0, 0, 1, 1)

        self.combo_modulacao = Gtk.ComboBoxText()
        for mod in ["NRZ-Polar", "Manchester", "Bipolar"]:
            self.combo_modulacao.append_text(mod)
        self.combo_modulacao.set_active(0)
        grid.attach(self.combo_modulacao, 1, 0, 1, 1)

        label = Gtk.Label(label="Modulação Portadora:")
        grid.attach(label, 0, 1, 1, 1)

        self.combo_portadora = Gtk.ComboBoxText()
        for mod in ["ASK", "FSK", "8-QAM"]:
            self.combo_portadora.append_text(mod)
        self.combo_portadora.set_active(0)
        grid.attach(self.combo_portadora, 1, 1, 1, 1)

        label = Gtk.Label(label="Correção de Erros:")
        grid.attach(label, 0, 2, 1, 1)

        self.check_crc32 = Gtk.CheckButton(label="CRC-32")
        grid.attach(self.check_crc32, 1, 2, 1, 1)

        self.check_paridade = Gtk.CheckButton(label="Paridade")
        grid.attach(self.check_paridade, 1, 3, 1, 1)

        self.check_hamming = Gtk.CheckButton(label="Hamming")
        grid.attach(self.check_hamming, 1, 4, 1, 1)

        self.main_box.pack_start(frame, False, False, 0)

    def criar_area_visualizacao(self):
        frame = Gtk.Frame(label="Visualização")
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 6))
        self.ax1.set_title("Sinal Digital")
        self.ax2.set_title("Sinal da Portadora")
        self.ax1.grid(True)
        self.ax2.grid(True)
        canvas = FigureCanvas(self.fig)
        frame.add(canvas)
        self.main_box.pack_start(frame, True, True, 0)

    def criar_area_log(self):
        frame = Gtk.Frame(label="Log")
        scroll = Gtk.ScrolledWindow()
        scroll.set_min_content_height(50)
        scroll.set_size_request(-1, 100)
        frame.add(scroll)

        self.text_log = Gtk.TextView()
        self.text_log.set_editable(False)
        self.text_log.set_wrap_mode(Gtk.WrapMode.WORD)
        scroll.add(self.text_log)

        frame.set_vexpand(False)
        self.main_box.pack_start(frame, False, False, 0)

    def adicionar_log(self, mensagem: str):
        def append_text():
            buffer = self.text_log.get_buffer()
            end_iter = buffer.get_end_iter()
            buffer.insert(end_iter, mensagem + "\n")
            mark = buffer.create_mark(None, buffer.get_end_iter(), False)
            self.text_log.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)
        GLib.idle_add(append_text)

    def on_connect_clicked(self, button):
        if not self.simulador.connected:
            ip = self.entry_ip.get_text()
            port = int(self.entry_port.get_text())
            success, message = self.simulador.conectar(ip, port)
            self.adicionar_log(message)
            if success:
                self.btn_connect.set_label("Desconectar")
                self.btn_transmitir.set_sensitive(True)
        else:
            success, message = self.simulador.desconectar()
            self.adicionar_log(message)
            if success:
                self.btn_connect.set_label("Conectar")
                self.btn_transmitir.set_sensitive(False)

    def on_transmitir_clicked(self, button):
        if not self.simulador.connected:
            self.adicionar_log("Erro: Não conectado ao receptor")
            return

        buffer = self.entrada_texto.get_buffer()
        texto = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)

        if not texto:
            self.adicionar_log("Erro: Nenhum dado para transmitir")
            return

        mod_digital = self.combo_modulacao.get_active_text()
        mod_portadora = self.combo_portadora.get_active_text()

        metodos_correcoes = []
        if self.check_crc32.get_active():
            metodos_correcoes.append("CRC-32")
        if self.check_paridade.get_active():
            metodos_correcoes.append("Paridade")
        if self.check_hamming.get_active():
            metodos_correcoes.append("Hamming")

        self.simulador.configurar_camada_enlace(metodos_correcoes)

        success, result = self.simulador.transmitir(texto, mod_digital, mod_portadora)
        if success:
            tempo, sinal, tempo_carrier, sinal_carrier = result

            self.ax1.clear()
            self.ax1.step(tempo, sinal, where='post')
            self.ax1.set_title(f"Sinal Digital ({mod_digital})")
            self.ax1.grid(True)

            self.ax2.clear()
            self.ax2.step(tempo_carrier, sinal_carrier, where='post')
            self.ax2.set_title(f"Sinal da Portadora ({mod_portadora})")
            self.ax2.grid(True)

            self.fig.canvas.draw()
            self.adicionar_log(f"Dados transmitidos usando {mod_digital} e {mod_portadora}")
        else:
            self.adicionar_log(result)

    def iniciar(self):
        Gtk.main()

if __name__ == "__main__":
    transmissor = TransmissorGUI()
    transmissor.iniciar()