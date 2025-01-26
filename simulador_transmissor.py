import socket
import json
import struct
from CamadaFisica import ModulacaoDigital, ModulacaoPortadora
from CamadaEnlace import CamadaEnlace

class Simulador:
    def __init__(self):
        self.mod_digital = ModulacaoDigital()
        self.mod_portadora = ModulacaoPortadora()
        self.camada_enlace = CamadaEnlace([])
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

    def configurar_camada_enlace(self, metodos):
        self.camada_enlace = CamadaEnlace(metodos)

    def conectar(self, ip, port):
        try:
            self.socket.connect((ip, port))
            self.connected = True
            return True, f"Conectado ao receptor em {ip}:{port}"
        except Exception as e:
            return False, f"Erro na conexão: {str(e)}"

    def desconectar(self):
        try:
            self.socket.close()
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connected = False
            return True, "Desconectado do receptor"
        except Exception as e:
            return False, f"Erro ao desconectar: {str(e)}"
        
    def simular_erro(self, quadros: list[str]):
        bit = quadros[0][0].split()[0]
        bit = '1' if bit == '0' else '0'
        quadros[0] = bit + quadros[0][1:]
        return quadros

    def transmitir(self, texto, mod_digital, mod_portadora, enquadramento, deteccao, correcao):
        try:
            # Gera bits a partir do texto
            bits = ''.join(format(byte, '08b') for byte in texto.encode('utf-8'))

            # Configuração da camada de enlace
            self.camada_enlace.set_detection_correction(deteccao)
            self.camada_enlace.set_hamming(correcao)
            
            # Enquadramento dos dados
            if enquadramento == "Contagem de Caracteres":
                quadros = self.camada_enlace.enquadrar_contagem(bits, 16)
            elif enquadramento == "Inserção de Bytes":
                quadros = self.camada_enlace.enquadrar_insercao(bits, 16)
            else:
                raise ValueError("Uma forma de enquadramento deve ser selecionada.")
            
            
            # Enquadramento dos dados com chance de erro
            if enquadramento == "Contagem de Caracteres":
                quadros_erro = self.camada_enlace.enquadrar_contagem(bits, 16)
            elif enquadramento == "Inserção de Bytes":
                quadros_erro = self.camada_enlace.enquadrar_insercao(bits, 16)
            else:
                raise ValueError("Uma forma de enquadramento deve ser selecionada.")

            # Aplica modulação digital selecionada
            if mod_digital == "NRZ-Polar":
                tempo, sinal = self.mod_digital.nrz_polar(quadros)
            elif mod_digital == "Manchester":
                tempo, sinal = self.mod_digital.manchester(quadros)
            elif mod_digital == "Bipolar":
                tempo, sinal = self.mod_digital.bipolar(quadros)
            else:
                raise ValueError("Uma forma de modulação digital deve ser selecionada.")
            
            # Aplica a modulação da portadora
            if mod_portadora == "ASK":
                tempo_carrier, sinal_carrier = self.mod_portadora.ask(quadros)
            elif mod_portadora == "FSK":
                tempo_carrier, sinal_carrier = self.mod_portadora.fsk(quadros)
            elif mod_portadora == "8-QAM":
                tempo_carrier, sinal_carrier = self.mod_portadora.qam8(quadros)
            else:
                raise ValueError("Uma forma de modulação digital deve ser selecionada.")
            
            print(f"ANTES DA FUNÇÃO de erro {quadros}")
            # Simular erro no pacote
            quadros_erro = self.simular_erro(quadros)
            print(f"DEPOIS DA FUNÇÃO de erro {quadros_erro}")
            
            # Aplica modulação digital selecionada em quadro com chance de erro
            if mod_digital == "NRZ-Polar":
                tempo_erro, sinal_erro = self.mod_digital.nrz_polar(quadros_erro)
            elif mod_digital == "Manchester":
                tempo_erro, sinal_erro = self.mod_digital.manchester(quadros_erro)
            elif mod_digital == "Bipolar":
                tempo_erro, sinal_erro = self.mod_digital.bipolar(quadros_erro)
            else:
                raise ValueError("Uma forma de modulação digital deve ser selecionada.")
 
            # Aplica a modulação da portadora em quadro com chance de erro
            if mod_portadora == "ASK":
                tempo_erro_carrier, sinal_erro_carrier = self.mod_portadora.ask(quadros_erro)
            elif mod_portadora == "FSK":
                tempo_erro_carrier, sinal_erro_carrier = self.mod_portadora.fsk(quadros_erro)
            elif mod_portadora == "8-QAM":
                tempo_erro_carrier, sinal_erro_carrier = self.mod_portadora.qam8(quadros_erro)
            else:
                raise ValueError("Uma forma de modulação digital deve ser selecionada.")
            
            # Prepara os dados para transmissão
            dados = {
                'enquadramento': enquadramento,
                'deteccao': deteccao,
                'correcao': correcao,
                'modulacao_digital': mod_digital,
                'modulacao_portadora': mod_portadora,
                'sinal_digital': sinal.tolist(),
                'tempo_sinal_digital': tempo.tolist(),
                'sinal_portadora': sinal_carrier.tolist(),
                'tempo_sinal_portadora': tempo_carrier.tolist(),
                'sinal_digital_erro': sinal_erro.tolist(),
                'tempo_sinal_digital_erro': tempo_erro.tolist(),
                'sinal_portadora_erro': sinal_erro_carrier.tolist(),
                'tempo_sinal_portadora_erro': tempo_erro_carrier.tolist()
            }

            # Envia os dados
            dados_json = json.dumps(dados)
            tamanho = len(dados_json)
            self.socket.sendall(struct.pack('!I', tamanho))  # Envia o tamanho primeiro
            self.socket.sendall(dados_json.encode('utf-8'))  # Depois envia os dados

            return True, (tempo, sinal, tempo_carrier, sinal_carrier)
        except Exception as e:
            return False, f"Erro na transmissão: {str(e)}"