import numpy as np
import matplotlib.pyplot as plt

class ModulacaoDigital:
    def __init__(self, taxa_amostragem=100, amplitude=1):
        self.taxa_amostragem = taxa_amostragem
        self.amplitude = amplitude

    def nrz_polar(self, bits):
        # Calcula o vetor de tempo
        tempo = np.linspace(0, len(bits), len(bits) * self.taxa_amostragem)
        # Inicializa o vetor de sinais
        sinal = np.repeat(bits, self.taxa_amostragem)
        sinal_modulado = np.where(sinal == 1, self.amplitude, -self.amplitude)
        return tempo, sinal_modulado

    def manchester(self, bits):
        # Calcula o vetor de tempo
        tempo = np.linspace(0, len(bits), len(bits) * self.taxa_amostragem)
        
        # Inicializa o vetor de sinais
        sinal = []
        
        for bit in bits:
            # Cada bit é representado por uma transição no meio do intervalo de tempo
            if bit:
                # Transição de +V para -V (bit 1), metade do sinal está em +V e a outra metade no -V
                sinal.extend([self.amplitude] * (self.taxa_amostragem // 2) + [-self.amplitude] * (self.taxa_amostragem // 2))
            else:
                # Transição de -V para +V (bit 0), etade do sinal está em -V e a outra metade no +V
                sinal.extend([-self.amplitude] * (self.taxa_amostragem // 2) + [self.amplitude] * (self.taxa_amostragem // 2))
        
        sinal_modulado = np.array(sinal)

        return tempo, sinal_modulado
        
    def bipolar(self, bits):
        # Calcula o vetor de tempo
        tempo = np.linspace(0, len(bits), len(bits) * self.taxa_amostragem)

        # Inicializa o vetor de sinais
        sinal = []
        last_sign = 1  # Começamos com +V para o primeiro bit 1

        for bit in bits:
            if bit:
                # Alterna entre +V e -V para os bits 1
                sinal.append(self.amplitude * last_sign)
                last_sign *= -1  # Alterna a polaridade para o próximo bit 1
            else:
                # Bit 0 é representado por 0
                sinal.append(0)
        
        # Agora, para representar o sinal na forma amostrada
        sinal_modulado = np.repeat(sinal, self.taxa_amostragem)
        
        return tempo, sinal_modulado
        

class ModulacaoPortadora:
    def __init__(self, freq_portadora=1000, taxa_amostragem=100, amplitude=1):
        self.freq_portadora = freq_portadora
        self.taxa_amostragem = taxa_amostragem
        self.amplitude = amplitude

    def ask(self, bits):
        # Calcula o vetor do tempo
        tempo = np.linspace(0, len(bits), len(bits) * self.taxa_amostragem)

        # Inicializa o vetor de sinais
        sinal = []

        for bit in bits:
            if bit:
                # Gerar seno com a frequência dada e a amplitude
                t = np.linspace(0, 1, self.taxa_amostragem)  # Tempo para cada bit
                sinal.extend(self.amplitude * np.sin(2 * np.pi * self.freq_portadora * t))  # Sinal para bit "1"
            else:
                # Para bit "0", sinal é 0
                t = np.linspace(0, 1, self.taxa_amostragem)  # Tempo para cada bit
                sinal.extend(np.zeros_like(t))  # Sinal para bit "0"

        sinal_modulado = np.array(sinal)

        return tempo, sinal_modulado




"""
modulador = ModulacaoDigital(taxa_amostragem=100)  # 100 amostras por bit
bits = [0, 1, 0, 1, 0, 0, 1, 1]  # Sequência de bits a ser modulada

# Gerando os sinais para cada tipo de modulação
tempo_nrz, sinal_nrz = modulador.nrz_polar(bits)
tempo_manchester, sinal_manchester = modulador.manchester(bits)
tempo_bipolar, sinal_bipolar = modulador.bipolar(bits)

# Criando uma figura com 3 subgráficos
fig, axs = plt.subplots(3, 1, figsize=(10, 8))

# Plotando o sinal NRZ Polar no primeiro subgráfico
axs[0].plot(tempo_nrz, sinal_nrz, label="NRZ Polar", color='b')
axs[0].set_title("Modulação NRZ Polar")
axs[0].set_xlabel("Tempo")
axs[0].set_ylabel("Nível de Sinal")
axs[0].grid(True)
axs[0].legend()

# Plotando o sinal Manchester no segundo subgráfico
axs[1].plot(tempo_manchester, sinal_manchester, label="Manchester", color='r')
axs[1].set_title("Modulação Manchester")
axs[1].set_xlabel("Tempo")
axs[1].set_ylabel("Nível de Sinal")
axs[1].grid(True)
axs[1].legend()

# Plotando o sinal Bipolar no terceiro subgráfico
axs[2].plot(tempo_bipolar, sinal_bipolar, label="Bipolar", color='g')
axs[2].set_title("Modulação Bipolar")
axs[2].set_xlabel("Tempo")
axs[2].set_ylabel("Nível de Sinal")
axs[2].grid(True)
axs[2].legend()

# Ajustando o layout para não sobrepor os gráficos
plt.tight_layout()
plt.show()
"""


# Testando a modulação ASK com portadora
modulador = ModulacaoPortadora(freq_portadora=1000, taxa_amostragem=2000, amplitude=1)
bits = [1, 0, 1, 1, 0]
tempo, sinal = modulador.ask(bits)

# Criando o gráfico
plt.figure(figsize=(10, 6))

# Plotando o primeiro gráfico com a modulação ASK
plt.subplot(2, 1, 1)  # 2 linhas, 1 coluna, 1º gráfico
plt.plot(tempo, sinal)
plt.title("Sinal Modulado em ASK com Portadora")
plt.xlabel("Tempo (s)")
plt.ylabel("Amplitude")
plt.grid(True)

# Plotando o segundo gráfico com a modulação ASK (para demonstrar com diferentes parâmetros)
modulador2 = ModulacaoPortadora(freq_portadora=1000, taxa_amostragem=1000, amplitude=1)
tempo2, sinal2 = modulador2.ask(bits)

plt.subplot(2, 1, 2)  # 2 linhas, 1 coluna, 2º gráfico
plt.plot(tempo2, sinal2)
plt.title("Sinal Modulado em ASK com Portadora - Frequência 1000Hz")
plt.xlabel("Tempo (s)")
plt.ylabel("Amplitude")
plt.grid(True)

# Ajuste para não sobrepor gráficos
plt.tight_layout()

# Exibindo o gráfico
plt.show()

