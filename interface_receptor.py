import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
import threading
from simulador_receptor import SimuladorReceptor

class ReceptorGUI:
    def __init__(self):
        self.simulador = SimuladorReceptor()
        self.window = Gtk.Window(title="Receptor de Comunicação Digital")
        self.window.set_default_size(800, 600)
        self.window.connect("destroy", Gtk.main_quit)

        # Layout principal
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.window.add(self.main_box)

        self.criar_area_servidor()
        self.criar_area_recebidos()
        self.criar_area_visualizacao()
        self.criar_area_log()

        self.window.show_all()

    def criar_area_servidor(self):
        frame = Gtk.Frame(label="Servidor")
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

        self.btn_start = Gtk.Button(label="Iniciar Servidor")
        self.btn_start.connect("clicked", self.on_start_clicked)
        box.pack_start(self.btn_start, False, False, 0)

        self.main_box.pack_start(frame, False, False, 0)

    def criar_area_recebidos(self):
        frame = Gtk.Frame(label="Dados Recebidos")
        scroll = Gtk.ScrolledWindow()
        frame.add(scroll)

        self.text_received = Gtk.TextView()
        self.text_received.set_editable(False)
        self.text_received.set_wrap_mode(Gtk.WrapMode.WORD)
        scroll.add(self.text_received)

        self.main_box.pack_start(frame, True, True, 0)

    def criar_area_visualizacao(self):
        frame = Gtk.Frame(label="Visualização")
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 6))
        self.ax1.set_title("Sinal Digital Recebido")
        self.ax2.set_title("Sinal da Portadora Recebido")
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

    def adicionar_dados_recebidos(self, texto: str):
        def append_text():
            buffer = self.text_received.get_buffer()
            end_iter = buffer.get_end_iter()
            buffer.insert(end_iter, texto + "\n")
            mark = buffer.create_mark(None, buffer.get_end_iter(), False)
            self.text_received.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)
        GLib.idle_add(append_text)

    def atualizar_visualizacao(self, texto: str, mod_digital: str, mod_portadora: str, bits_recebidos: list):
        def update():
            t = np.linspace(0, len(bits_recebidos), len(bits_recebidos))
            
            self.ax1.clear()
            self.ax2.clear()
            
            self.ax1.step(t, bits_recebidos)
            self.ax1.set_title(f"Sinal Digital Recebido ({mod_digital})")
            self.ax1.grid(True)
            
            if mod_portadora == "ASK":
                carrier_freq = 10
                t_dense = np.linspace(0, len(bits_recebidos), len(bits_recebidos) * 20)
                carrier = np.sin(2 * np.pi * carrier_freq * t_dense)
                signal = np.repeat(bits_recebidos, 20) * carrier
            elif mod_portadora == "FSK":
                t_dense = np.linspace(0, len(bits_recebidos), len(bits_recebidos) * 20)
                f0, f1 = 5, 10
                signal = np.zeros(len(t_dense))
                for i, bit in enumerate(bits_recebidos):
                    freq = f1 if bit else f0
                    signal[i*20:(i+1)*20] = np.sin(2 * np.pi * freq * t_dense[i*20:(i+1)*20])
            else:
                t_dense = np.linspace(0, len(bits_recebidos), len(bits_recebidos) * 20)
                signal = np.sin(2 * np.pi * 10 * t_dense) * np.repeat(bits_recebidos, 20)
            
            self.ax2.plot(t_dense, signal)
            self.ax2.set_title(f"Sinal Modulado Recebido ({mod_portadora})")
            self.ax2.grid(True)
            
            self.fig.canvas.draw()
            
        GLib.idle_add(update)

    def on_start_clicked(self, button):
        if button.get_label() == "Iniciar Servidor":
            ip = self.entry_ip.get_text()
            port = int(self.entry_port.get_text())
            success, message = self.simulador.iniciar_servidor(ip, port)
            self.adicionar_log(message)
            if success:
                button.set_label("Parar Servidor")
                threading.Thread(target=self.aceitar_conexoes, daemon=True).start()
        else:
            success, message = self.simulador.parar_servidor()
            self.adicionar_log(message)
            if success:
                button.set_label("Iniciar Servidor")

    def aceitar_conexoes(self):
        while self.simulador.running:
            success, message = self.simulador.aceitar_conexoes()
            self.adicionar_log(message)
            if success:
                threading.Thread(target=self.receber_dados, daemon=True).start()

    def receber_dados(self):
        while self.simulador.running:
            success, result = self.simulador.receber_dados()
            if success:
                texto, mod_digital, mod_portadora, bits_recebidos = result
                self.adicionar_dados_recebidos(f"Recebido:\n{texto}")
                self.atualizar_visualizacao(texto, mod_digital, mod_portadora, bits_recebidos)
                self.adicionar_log(f"Dados recebidos usando {mod_digital} e {mod_portadora}")
            else:
                self.adicionar_log(result)
                break

    def iniciar(self):
        Gtk.main()

if __name__ == "__main__":
    receiver = ReceptorGUI()
    receiver.iniciar()