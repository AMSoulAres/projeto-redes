import numpy as np
import matplotlib.pyplot as plt

class ModulacaoDigital:
    def __init__(self, taxa_amostragem=1000, amplitude=1):
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
    
    def nrz_polar_decode(self, sinal):
        # Decodifica o sinal do padrão NRZ Polar
        bits = [-1 if componente < 0 else 0 for componente in sinal]

        return bits

    def manchester_decode(self, sinal):
        # Inicializa o vetor de bits
        bits = []

        tamanho_sinal = len(sinal)

        # Loop com metade do tamanho da array do sinal (interagir de dois em dois)
        for i in range(0, tamanho_sinal/2):
            if sinal[i] == -self.amplitude and sinal[i+1] == self.amplitude:  # Essa função depende de como vamos implementar o receptor e transmissor
                bits.append(0)                                                # O ideal nesse caso seria passar parametros iguais para inicializacao da
            elif sinal[i] == self.amplitude and sinal[i+1] == -self.amplitude:  # classe tanto no receptor como no transmissor
                bits.append(1)

        return bits

    def bipolar_decode(self, sinal):
        # Inicializa o vetor de bits
        bits = []

        for amplitude in sinal:
            if amplitude == 0: 
                bits.append(0)
            else:               # Tanto negativo quanto positivo equivalem ao bit 1
                bits.append(1)
        
        return bits


class ModulacaoPortadora:
    def __init__(self, taxa_amostragem=1000, amplitude=1):
        self.taxa_amostragem = taxa_amostragem
        self.amplitude = amplitude

    def ask(self, bits, freq_portadora=1):
        # Calcula o vetor do tempo
        tempo = np.linspace(0, len(bits), len(bits) * self.taxa_amostragem)

        # Inicializa o vetor de sinais
        sinal = []

        for bit in bits:
            if bit:
                # Gerar seno com a frequência dada e a amplitude
                t = np.linspace(0, 1, self.taxa_amostragem)  # Tempo para cada bit
                sinal.extend(self.amplitude * np.sin(2 * np.pi * freq_portadora * t))  # Sinal para bit "1"
            else:
                # Para bit "0", sinal é 0
                t = np.linspace(0, 1, self.taxa_amostragem)  # Tempo para cada bit
                sinal.extend(np.zeros_like(t))  # Sinal para bit "0"

        sinal_modulado = np.array(sinal)

        return tempo, sinal_modulado

    def fsk(self, bits, freq_low=1, freq_high=2):
        # Calcula o vetor do tempo
        tempo = np.linspace(0, len(bits), len(bits) * self.taxa_amostragem)

        # Inicializa o vetor de sinais
        sinal = []

        for bit in bits:
            if bit:
                # Gerar seno com a frequência maior dada e a amplitude
                t = np.linspace(0, 1, self.taxa_amostragem)  # Tempo para cada bit
                sinal.extend(self.amplitude * np.sin(2 * np.pi * freq_high * t))  # Sinal para bit "1"
            else:
                # Para bit "0", sinal é 0 com a frequência mais baixa
                t = np.linspace(0, 1, self.taxa_amostragem)  # Tempo para cada bit
                sinal.extend(self.amplitude * np.sin(2 * np.pi * freq_low * t))   # Sinal para bit "0"

        sinal_modulado = np.array(sinal)

        return tempo, sinal

    def qam8(self, bits):
        # Faz uma cópia dos bits para não modificar a entrada original
        bits_padded = bits.copy()
        
        # Calcula quantos bits faltam para completar um múltiplo de 3
        padding_needed = (3 - len(bits) % 3) % 3
        
        # Adiciona zeros como padding se necessário
        if padding_needed > 0:
            bits_padded.extend([0] * padding_needed)

        # Define os pontos da constelação 8-QAM
        # Formato: {(b2,b1,b0): (amplitude_I, amplitude_Q)}
        constelacao = {
            (0,0,0): (-self.amplitude, -self.amplitude),
            (0,0,1): (-self.amplitude, self.amplitude),
            (0,1,0): (self.amplitude, -self.amplitude),
            (0,1,1): (self.amplitude, self.amplitude),
            (1,0,0): (-2*self.amplitude, 0),
            (1,0,1): (0, -2*self.amplitude),
            (1,1,0): (2*self.amplitude, 0),
            (1,1,1): (0, 2*self.amplitude)
        }

        # Calcula o vetor do tempo
        tempo = np.linspace(0, len(bits_padded)//3, (len(bits_padded)//3) * self.taxa_amostragem)
        
        # Frequência da portadora (pode ser ajustada conforme necessário)
        freq_portadora = 1
        
        # Inicializa os vetores de sinal I e Q
        sinal_i = []
        sinal_q = []
        
        # Processa os bits em grupos de 3
        for i in range(0, len(bits_padded), 3):
            # Pega 3 bits para formar um símbolo
            simbolo = tuple(bits_padded[i:i+3])
            
            # Obtém as amplitudes I e Q do símbolo
            amp_i, amp_q = constelacao[simbolo]
            
            # Gera o tempo para um símbolo
            t = np.linspace(0, 1, self.taxa_amostragem)
            
            # Gera as componentes I e Q do sinal
            sinal_i.extend(amp_i * np.cos(2 * np.pi * freq_portadora * t))
            sinal_q.extend(amp_q * np.sin(2 * np.pi * freq_portadora * t))
        
        # Combina as componentes I e Q para formar o sinal modulado
        sinal_modulado = np.array(sinal_i) - np.array(sinal_q)
        
        return tempo, sinal_modulado

    def ask_decode(self, sinal):

        # Inicializa o vetor de bits
        bits = []

        for amplitude in sinal:
            if ampltiude == 0:
                bits.append(0)
            else:
                bits.append(1)

        return bits
    
    def fsk_decode(self, sinal, freq_low=1, freq_high=2):

        # Dividindo o sinal nos intervalos correspondentes a cada bit
        bits = []
        amostras_por_bit = self.taxa_amostragem  # Número de amostras por bit
        num_bits = len(sinal) // amostras_por_bit  # Total de bits no sinal

        for i in range(num_bits):
            # Extrai a parte do sinal correspondente ao bit atual
            segmento = sinal[i * amostras_por_bit:(i + 1) * amostras_por_bit]
            
            # Aplica a Transformada de Fourier para identificar a frequência predominante
            fft_result = np.fft.fft(segmento)
            fft_frequencies = np.fft.fftfreq(len(segmento), d=1/self.taxa_amostragem)
            
            # Identifica a frequência dominante (ignora a parte negativa das frequências)
            dominante = abs(fft_frequencies[np.argmax(abs(fft_result))])
            
            # Decodifica o bit com base na frequência dominante
            if abs(dominante - freq_high) < abs(dominante - freq_low):
                bits.append(1)
            else:
                bits.append(0)

        return bits

    def qam8_decode(self, sinal, freq_portadora=1):

        # Define os pontos da constelação 8-QAM
        constelacao = {
            (-self.amplitude, -self.amplitude): (0, 0, 0),
            (-self.amplitude, self.amplitude): (0, 0, 1),
            (self.amplitude, -self.amplitude): (0, 1, 0),
            (self.amplitude, self.amplitude): (0, 1, 1),
            (-2*self.amplitude, 0): (1, 0, 0),
            (0, -2*self.amplitude): (1, 0, 1),
            (2*self.amplitude, 0): (1, 1, 0),
            (0, 2*self.amplitude): (1, 1, 1)
        }

        # Número de amostras por símbolo
        amostras_por_simbolo = self.taxa_amostragem

        # Inicializa o vetor de bits decodificados
        bits = []

        # Itera sobre o sinal recebido, símbolo por símbolo
        for i in range(0, len(sinal), amostras_por_simbolo):
            # Extrai o segmento do sinal correspondente ao símbolo atual
            segmento = sinal[i:i+amostras_por_simbolo]
            
            # Gera o tempo para o símbolo
            t = np.linspace(0, 1, self.taxa_amostragem)

            # Reconstroi as componentes I e Q do sinal
            componente_i = 2 * np.mean(segmento * np.cos(2 * np.pi * freq_portadora * t))
            componente_q = -2 * np.mean(segmento * np.sin(2 * np.pi * freq_portadora * t))
            
            # Encontra o ponto da constelação mais próximo
            ponto_constelacao = min(constelacao.keys(), 
                                    key=lambda p: np.sqrt((componente_i - p[0])**2 + (componente_q - p[1])**2))

            # Adiciona os bits correspondentes ao símbolo decodificado
            bits.extend(constelacao[ponto_constelacao])

        return bits




"""
modulador = ModulacaoPortadora(taxa_amostragem=2000, amplitude=1)
bits = [1, 0, 1, 1, 0]
tempo, sinal_modulado = modulador.fsk(bits, freq_low=500, freq_high=1000)

# Decodificação do sinal
bits_decodificados = modulador.fsk_decode(sinal_modulado, freq_low=500, freq_high=1000)

print("Bits originais:", bits)
print("Bits decodificados:", bits_decodificados)

modulador = ModulacaoPortadora(amplitude=1, taxa_amostragem=100)
bits = [0, 0, 0, 0, 1, 1, 1, 1, 0]
tempo, sinal_modulado = modulador.qam8(bits)

# Decodificação do sinal
bits_decodificados = modulador.qam8_decode(sinal_modulado, freq_portadora=1)

print("Bits originais:", bits)
print("Bits decodificados:", bits_decodificados)

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



# Testando a modulação ASK com portadora
modulador = ModulacaoPortadora(taxa_amostragem=1000, amplitude=1)
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
modulador2 = ModulacaoPortadora(taxa_amostragem=1000,amplitude=1)
tempo2, sinal2 = modulador2.fsk(bits)

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

def plot_8qam_results(mod, bits):
    
    #Plota resultados completos da modulação 8-QAM com escalas corrigidas
    
    # Gera o sinal modulado
    tempo, sinal_modulado = mod.qam8(bits)
    
    # Configura o subplot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot do sinal modulado
    ax1.plot(tempo, sinal_modulado)
    ax1.set_title('Sinal 8-QAM Modulado')
    ax1.set_xlabel('Tempo (s)')
    ax1.set_ylabel('Amplitude')
    ax1.grid(True)
    ax1.set_ylim(-2.5, 2.5)  # Limita a escala vertical
    
    # Pontos da constelação teórica
    constelacao = {
        (0,0,0): (-1, -1),
        (0,0,1): (-1, 1),
        (0,1,0): (1, -1),
        (0,1,1): (1, 1),
        (1,0,0): (-2, 0),
        (1,0,1): (0, -2),
        (1,1,0): (2, 0),
        (1,1,1): (0, 2)
    }
    
    # Plot do diagrama de constelação
    I = [x[0] for x in constelacao.values()]
    Q = [x[1] for x in constelacao.values()]
    ax2.scatter(I, Q, c='red', marker='x', s=100, label='Pontos da Constelação')
    
    # Adiciona rótulos para cada ponto
    for bits, (i, q) in constelacao.items():
        ax2.annotate(f'{bits}', (i, q), xytext=(10, 10), textcoords='offset points')
    
    ax2.set_title('Diagrama de Constelação 8-QAM')
    ax2.set_xlabel('Em fase (I)')
    ax2.set_ylabel('Quadratura (Q)')
    ax2.grid(True)
    ax2.axis('equal')
    
    # Define os limites dos eixos explicitamente
    ax2.set_xlim(-2.5, 2.5)
    ax2.set_ylim(-2.5, 2.5)
    
    plt.tight_layout()
    plt.show()

# Teste com uma sequência específica
mod = ModulacaoPortadora(taxa_amostragem=1000, amplitude=1)
bits_teste = [1, 1, 0, 0, 0, 1, 1, 1, 0]
plot_8qam_results(mod, bits_teste)

"""