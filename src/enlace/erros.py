from typing import List, Tuple

import numpy as np


class CorrecaoErros:
    def __init__(self):
        self.max_bits = 1024  # Limite máximo de bits para prevenir overflow
        self.matriz_paridade = None
        self.k = 4  # Número de bits de dados padrão

    def _gerar_matriz_paridade(self, k: int) -> np.ndarray:
        """Gera matriz de paridade para código Hamming."""
        n = 2**k - 1  # Comprimento total da palavra código
        r = k         # Número de bits de paridade
        
        H = np.zeros((r, n), dtype=int)
        # Preenche a matriz conforme regras do código Hamming
        for i in range(n):
            binario = format(i + 1, f'0{r}b')
            H[:, i] = [int(b) for b in binario]
            
        return H

    def _inicializar_matriz_se_necessario(self, tamanho_dados: int):
        """Inicializa a matriz de paridade se necessário."""
        if self.matriz_paridade is None or tamanho_dados > 2**self.k - self.k - 1:
            # Ajusta k para acomodar os dados
            while tamanho_dados > 2**self.k - self.k - 1 and self.k < 8:
                self.k += 1
            self.matriz_paridade = self._gerar_matriz_paridade(self.k)

    def hamming_encode(self, dados: List[int]) -> List[int]:
        """
        Codifica dados usando código Hamming.
        
        Args:
            dados: Lista de bits a serem codificados
            
        Returns:
            Lista de bits codificados
        """
        # Limita o tamanho dos dados
        dados = dados[:self.max_bits]
        
        # Inicializa a matriz de paridade apropriada
        self._inicializar_matriz_se_necessario(len(dados))
        
        # Calcula o tamanho da palavra código
        n = self.matriz_paridade.shape[1]
        k = n - self.matriz_paridade.shape[0]
        
        # Prepara os dados
        dados_ajustados = dados[:k]  # Limita aos primeiros k bits
        if len(dados_ajustados) < k:
            dados_ajustados.extend([0] * (k - len(dados_ajustados)))  # Padding com zeros
            
        # Gera palavra código
        palavra_codigo = np.zeros(n, dtype=int)
        palavra_codigo[:k] = dados_ajustados
        
        # Calcula bits de paridade
        sindromo = np.dot(self.matriz_paridade, palavra_codigo) % 2
        palavra_codigo[k:] = sindromo
        
        return palavra_codigo.tolist()

    def hamming_decode(self, palavra_codigo: List[int]) -> Tuple[List[int], bool]:
        """
        Decodifica e corrige erros usando código Hamming.
        
        Args:
            palavra_codigo: Lista de bits codificados
            
        Returns:
            Tuple com dados decodificados e flag indicando se houve correção
        """
        # Garante que a matriz de paridade está inicializada
        self._inicializar_matriz_se_necessario(len(palavra_codigo))
        
        palavra = np.array(palavra_codigo)
        if len(palavra) > self.matriz_paridade.shape[1]:
            palavra = palavra[:self.matriz_paridade.shape[1]]
            
        sindromo = np.dot(self.matriz_paridade, palavra) % 2
        
        # Verifica se há erro
        posicao_erro = 0
        for i, bit in enumerate(sindromo):
            posicao_erro += bit * (2**i)
            
        corrigido = False
        if posicao_erro > 0 and posicao_erro <= len(palavra):
            # Corrige o erro
            palavra[posicao_erro-1] ^= 1
            corrigido = True
            
        k = len(palavra_codigo) - len(self.matriz_paridade)
        return palavra[:k].tolist(), corrigido