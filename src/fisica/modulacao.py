import numpy as np
from typing import List, Tuple

class ModulacaoDigital:
    def __init__(self):
        self.taxa_amostragem = 100  # Amostras por bit
        self.amplitude = 1.0        # Amplitude do sinal
        self.max_bits = 1024       # Limite máximo de bits para prevenir overflow

    def gerar_tempo(self, num_bits: int) -> np.ndarray:
        """Gera array de tempo para o número de bits especificado."""
        # Garante que não exceda o limite máximo
        num_bits = min(num_bits, self.max_bits)
        return np.linspace(0, num_bits, num_bits * self.taxa_amostragem)

    def processar_bits(self, bits: List[int]) -> List[int]:
        """Processa e limita o número de bits."""
        if len(bits) > self.max_bits:
            bits = bits[:self.max_bits]
        return bits

    def nrz_polar(self, bits: List[int]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Implementa a modulação NRZ-Polar.
        
        Args:
            bits: Lista de bits (0s e 1s) a serem modulados
            
        Returns:
            Tuple contendo arrays de tempo e sinal modulado
        """
        bits = self.processar_bits(bits)
        tempo = self.gerar_tempo(len(bits))
        sinal = np.zeros(len(tempo))
        
        for i, bit in enumerate(bits):
            inicio = i * self.taxa_amostragem
            fim = (i + 1) * self.taxa_amostragem
            # Mapeia 0 para -amplitude e 1 para +amplitude
            sinal[inicio:fim] = self.amplitude if bit == 1 else -self.amplitude
            
        return tempo, sinal

    def manchester(self, bits: List[int]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Implementa a modulação Manchester.
        
        Args:
            bits: Lista de bits a serem modulados
            
        Returns:
            Tuple contendo arrays de tempo e sinal modulado
        """
        bits = self.processar_bits(bits)
        tempo = self.gerar_tempo(len(bits))
        sinal = np.zeros(len(tempo))
        
        for i, bit in enumerate(bits):
            inicio = i * self.taxa_amostragem
            meio = inicio + self.taxa_amostragem // 2
            fim = (i + 1) * self.taxa_amostragem
            
            if bit == 1:
                sinal[inicio:meio] = self.amplitude
                sinal[meio:fim] = -self.amplitude
            else:
                sinal[inicio:meio] = -self.amplitude
                sinal[meio:fim] = self.amplitude
                
        return tempo, sinal

    def bipolar(self, bits: List[int]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Implementa a modulação Bipolar (AMI).
        
        Args:
            bits: Lista de bits a serem modulados
            
        Returns:
            Tuple contendo arrays de tempo e sinal modulado
        """
        bits = self.processar_bits(bits)
        tempo = self.gerar_tempo(len(bits))
        sinal = np.zeros(len(tempo))
        ultimo_nivel = self.amplitude  # Alterna entre +amplitude e -amplitude
        
        for i, bit in enumerate(bits):
            inicio = i * self.taxa_amostragem
            fim = (i + 1) * self.taxa_amostragem
            
            if bit == 1:
                sinal[inicio:fim] = ultimo_nivel
                ultimo_nivel = -ultimo_nivel  # Alterna a polaridade
            # bit 0 permanece como zero
                
        return tempo, sinal

import numpy as np
from typing import List, Tuple

class ModulacaoPortadora:
    def __init__(self):
        self.taxa_amostragem = 100  # Amostras por bit
        self.freq_portadora = 10    # Frequência da portadora
        self.amplitude = 1.0        # Amplitude do sinal

    def gerar_portadora(self, tempo: np.ndarray, frequencia: float) -> np.ndarray:
        """Gera sinal portador na frequência especificada."""
        return np.sin(2 * np.pi * frequencia * tempo)

    def ask(self, bits: List[int]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Implementa a modulação ASK (Amplitude Shift Keying).
        
        Args:
            bits: Lista de bits a serem modulados
            
        Returns:
            Tuple contendo arrays de tempo e sinal modulado
        """
        tempo = np.linspace(0, len(bits), len(bits) * self.taxa_amostragem)
        portadora = self.gerar_portadora(tempo, self.freq_portadora)
        sinal = np.zeros(len(tempo))
        
        for i, bit in enumerate(bits):
            inicio = i * self.taxa_amostragem
            fim = (i + 1) * self.taxa_amostragem
            # Amplitude da portadora varia com o bit
            sinal[inicio:fim] = portadora[inicio:fim] * (self.amplitude if bit == 1 else 0.0)
            
        return tempo, sinal

    def fsk(self, bits: List[int]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Implementa a modulação FSK (Frequency Shift Keying).
        
        Args:
            bits: Lista de bits a serem modulados
            
        Returns:
            Tuple contendo arrays de tempo e sinal modulado
        """
        tempo = np.linspace(0, len(bits), len(bits) * self.taxa_amostragem)
        sinal = np.zeros(len(tempo))
        
        freq_0 = self.freq_portadora
        freq_1 = self.freq_portadora * 2  # Frequência para bit 1 é o dobro
        
        for i, bit in enumerate(bits):
            inicio = i * self.taxa_amostragem
            fim = (i + 1) * self.taxa_amostragem
            # Frequência varia com o bit
            freq = freq_1 if bit == 1 else freq_0
            sinal[inicio:fim] = self.amplitude * np.sin(2 * np.pi * freq * tempo[inicio:fim])
            
        return tempo, sinal

    def qam8(self, bits: List[int]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Implementa a modulação 8-QAM.
        
        Args:
            bits: Lista de bits a serem modulados (deve ser múltiplo de 3)
            
        Returns:
            Tuple contendo arrays de tempo e sinal modulado
        """
        if len(bits) % 3 != 0:
            raise ValueError("Número de bits deve ser múltiplo de 3 para 8-QAM")

        tempo = np.linspace(0, len(bits)/3, (len(bits)/3) * self.taxa_amostragem)
        sinal = np.zeros(len(tempo), dtype=complex)
        
        # Mapeamento 8-QAM para os 8 pontos da constelação
        constelacao = {
            (0,0,0): 1 + 1j,
            (0,0,1): 1 + 3j,
            (0,1,0): 3 + 1j,
            (0,1,1): 3 + 3j,
            (1,0,0): -1 - 1j,
            (1,0,1): -1 - 3j,
            (1,1,0): -3 - 1j,
            (1,1,1): -3 - 3j
        }
        
        for i in range(0, len(bits), 3):
            simbolo = tuple(bits[i:i+3])
            inicio = (i//3) * self.taxa_amostragem
            fim = ((i//3) + 1) * self.taxa_amostragem
            
            # Aplica o símbolo da constelação
            valor_complexo = constelacao[simbolo]
            sinal[inicio:fim] = valor_complexo
            
        # Separa as componentes em fase e quadratura
        sinal_i = np.real(sinal) * np.cos(2 * np.pi * self.freq_portadora * tempo)
        sinal_q = np.imag(sinal) * np.sin(2 * np.pi * self.freq_portadora * tempo)
        
        return tempo, sinal_i + sinal_q