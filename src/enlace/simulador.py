import socket
import threading

from .enlace import CamadaEnlace
from ..fisica.modulacao import ModulacaoDigital
import sys
sys.path.append('../')



class Simulador:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.camada_fisica = ModulacaoDigital()
        self.camada_enlace = CamadaEnlace()
        self.conexoes = []
        
    def iniciar_servidor(self):
        """Inicia servidor TCP para receber conexões."""
        self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_servidor.bind((self.host, self.port))
        self.socket_servidor.listen(5)
        
        print(f"Servidor iniciado em {self.host}:{self.port}")
        
        while True:
            conn, addr = self.socket_servidor.accept()
            print(f"Nova conexão de {addr}")
            
            # Cria thread para lidar com a conexão
            thread = threading.Thread(target=self.manipular_conexao, 
                                   args=(conn, addr))
            thread.start()
            self.conexoes.append((conn, thread))
            
    def manipular_conexao(self, conn: socket.socket, addr: tuple):
        """Manipula uma conexão individual."""
        try:
            while True:
                # Recebe dados
                dados = conn.recv(1024)
                if not dados:
                    break
                    
                # Processa na camada de enlace
                quadro, sem_erros = self.camada_enlace.receber(dados)
                
                if sem_erros:
                    # Converte para bits
                    bits = [int(b) for byte in quadro 
                           for b in format(byte, '08b')]
                    
                    # Aplica modulação digital
                    tempo, sinal = self.camada_fisica.nrz_polar(bits)
                    
                    # Aqui você poderia enviar o sinal modulado
                    # ou salvá-lo para visualização
                    
                    # Por ora, vamos apenas ecoar os dados processados
                    resposta = self.camada_enlace.transmitir(quadro)
                    conn.sendall(resposta)
                else:
                    # Notifica erro
                    conn.sendall(b"ERRO: Dados corrompidos")
                    
        except Exception as e:
            print(f"Erro na conexão com {addr}: {e}")
        finally:
            conn.close()
            print(f"Conexão com {addr} encerrada")
            
    def parar(self):
        """Para o servidor e limpa as conexões."""
        for conn, thread in self.conexoes:
            conn.close()
            thread.join()
        self.socket_servidor.close()
        print("Servidor encerrado")