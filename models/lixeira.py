# ═══════════════════════════════════════════════════════════
# ARQUIVO: models/lixeira.py
# Responsabilidade: representar a lixeira que o jogador controla
# ═══════════════════════════════════════════════════════════

import pygame

import utils.constantes as constantes
from utils.constantes import PRETO, BRANCO

class Lixeira:

    def __init__(self, tipo_aceito, cor_lixeira, fonte):
        self.tipo_aceito  = tipo_aceito    # tipo de lixo que aceita
        self.cor_lixeira  = cor_lixeira    # cor da lixeira
        self.fonte        = fonte          # fonte para escrever o tipo

        self.largura    = constantes.LARGURA_TELA // 8   # largura proporcional à tela
        self.altura     = constantes.ALTURA_TELA  // 5   # altura proporcional à tela
        self.velocidade = 7                # velocidade de movimento

        # posição inicial centralizada na parte inferior da tela
        self.posicao_x = constantes.LARGURA_TELA // 2 - self.largura // 2
        self.posicao_y = constantes.ALTURA_TELA - self.altura - 10

        # retângulo de colisão
        self.area_colisao = pygame.Rect(
            self.posicao_x,
            self.posicao_y,
            self.largura,
            self.altura
        )

        # ── carrega a imagem da lixeira ──
        # o nome do arquivo segue o padrão: lixeira-{tipo}.png
        caminho_imagem = f"assets/imagens/lixeira-{tipo_aceito}.png"

        # carrega a imagem do disco
        imagem_carregada = pygame.image.load(caminho_imagem)

        # redimensiona a imagem para o tamanho da lixeira
        self.imagem_lixeira = pygame.transform.scale(
            imagem_carregada, (self.largura, self.altura)
        )

    # MÉTODO: mover
    # Move a lixeira com as teclas seta esquerda e direita
    def mover(self):
        teclas_pressionadas = pygame.key.get_pressed()

        if teclas_pressionadas[pygame.K_LEFT]:
            self.posicao_x -= self.velocidade   # move para esquerda

        if teclas_pressionadas[pygame.K_RIGHT]:
            self.posicao_x += self.velocidade   # move para direita

        # impede sair pela esquerda
        if self.posicao_x < 0:
            self.posicao_x = 0

        # impede sair pela direita
        if self.posicao_x > constantes.LARGURA_TELA - self.largura:
            self.posicao_x = constantes.LARGURA_TELA - self.largura

        # atualiza o retângulo de colisão
        self.area_colisao.x = self.posicao_x
        self.area_colisao.y = self.posicao_y

    # MÉTODO: desenhar
    # Desenha a imagem da lixeira na tela
    def desenhar(self, tela):
        # desenha a imagem na posição atual da lixeira
        tela.blit(self.imagem_lixeira, (self.posicao_x, self.posicao_y))