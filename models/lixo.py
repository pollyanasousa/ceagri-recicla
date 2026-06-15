# ═══════════════════════════════════════════════════════════
# ARQUIVO: models/lixo.py
# Responsabilidade: representar um lixo que cai de cima
# ═══════════════════════════════════════════════════════════

import pygame
import random

import utils.constantes as constantes
from utils.constantes import PRETO

# ═══════════════════════════════════════════════════════════
# CLASSE: Lixo
# Representa cada item de lixo que cai de cima para baixo
# ═══════════════════════════════════════════════════════════
class Lixo:

    # ───────────────────────────────────────────────────────
    # Atributo de CLASSE — igual para todos os lixos
    # Define os tipos de lixo e suas imagens possíveis
    # ───────────────────────────────────────────────────────
    TIPOS_DE_LIXO = {
        "papel":    {"itens": [
                        ("Jornal",   "JORNAL.png"),
                        ("Caixa",    "CAIXA.png"),
                        ("Caixa 2",  "CAIXA2.png"),
                        ("Papel",    "PAPEL.png"),
                        ("Papel 2",  "PAPEL2.png"),
                    ]},
        "plastico": {"itens": [
                        ("Garrafa",  "GARRAF.png"),
                        ("Sacola",   "SACOLA.png"),
                        ("Copo",     "COPO.png"),
                        ("Colher",   "COLHER.png"),
                    ]},
        "vidro":    {"itens": [
                        ("Garrafa",  "GARRAFA.png"),
                        ("Vidro",    "VIDRO.png"),
                        ("Vidro 2",  "VIDRO2.png"),
                        ("Vidro 3",  "VIDRO3.png"),
                        ("Vidro 4",  "VIDRO4.png"),
                        ("Vidro 5",  "VIDRO5.png"),
                        ("Pote",     "POTE.png"),
                    ]},
        "metal":    {"itens": [
                        ("Lata",     "LATA.png"),
                        ("Lata R.",  "LATA-REFRI.png"),
                        ("Lata 3",   "LATA3.png"),
                        ("Lata Amass","LATA-AMASSADA.png"),
                        ("Metal",    "METAL.png"),
                        ("Alicate",  "ALICARTE.png"),
                        ("Chave",    "CHAVE.png"),
                        ("Tesoura",  "TESOURA.png"),
                    ]},
    }

    # ───────────────────────────────────────────────────────
    # __init__ = construtor
    # ───────────────────────────────────────────────────────
    def __init__(self, fonte, multiplicador_velocidade=1.0):
        self.fonte = fonte

        # sorteia tipo de lixo
        self.tipo = random.choice(list(self.TIPOS_DE_LIXO.keys()))

        # sorteia item (nome, arquivo) do tipo
        nome, arquivo = random.choice(self.TIPOS_DE_LIXO[self.tipo]["itens"])
        self.nome_item = nome

        self.largura    = 70
        self.altura     = 70
        self.posicao_x  = random.randint(0, constantes.LARGURA_TELA - self.largura)
        self.posicao_y  = -self.altura
        self.velocidade = random.randint(3, 6) * multiplicador_velocidade

        # carrega a imagem do item
        caminho = f"assets/imagens/{arquivo}"
        imagem_carregada = pygame.image.load(caminho).convert_alpha()
        self.imagem = pygame.transform.scale(imagem_carregada, (self.largura, self.altura))

        # retângulo de colisão
        self.area_colisao = pygame.Rect(
            self.posicao_x,
            self.posicao_y,
            self.largura,
            self.altura
        )

    # ───────────────────────────────────────────────────────
    # MÉTODO: cair
    # ───────────────────────────────────────────────────────
    def cair(self):
        self.posicao_y      += self.velocidade
        self.area_colisao.y  = self.posicao_y

    # ───────────────────────────────────────────────────────
    # MÉTODO: saiu_da_tela
    # ───────────────────────────────────────────────────────
    def saiu_da_tela(self):
        return self.posicao_y > constantes.ALTURA_TELA

    # ───────────────────────────────────────────────────────
    # MÉTODO: desenhar
    # Desenha a imagem do item na tela com nome abaixo
    # ───────────────────────────────────────────────────────
    def desenhar(self, tela):
        # desenha a imagem do objeto
        tela.blit(self.imagem, (self.posicao_x, self.posicao_y))

        # desenha o nome do item abaixo da imagem
        imagem_nome = self.fonte.render(self.nome_item, True, PRETO)
        nome_x = self.posicao_x + (self.largura - imagem_nome.get_width()) // 2
        nome_y = self.posicao_y + self.altura + 2
        tela.blit(imagem_nome, (nome_x, nome_y))