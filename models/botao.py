# ═══════════════════════════════════════════════════════════
# ARQUIVO: models/botao.py
# Responsabilidade: representar um botão clicável na tela
# ═══════════════════════════════════════════════════════════

import pygame

from utils.constantes import PRETO, CINZA

# ═══════════════════════════════════════════════════════════
# CLASSE: Botao
# Um botão tem posição, tamanho, texto e cor
# e sabe quando foi clicado
# ═══════════════════════════════════════════════════════════
class Botao:

    def __init__(self, posicao_x, posicao_y, largura, altura, texto, cor=CINZA, fonte=None):
        self.posicao_x = posicao_x   # posição horizontal na tela
        self.posicao_y = posicao_y   # posição vertical na tela
        self.largura   = largura     # largura do botão em pixels
        self.altura    = altura      # altura do botão em pixels
        self.texto     = texto       # texto escrito no botão
        self.cor       = cor         # cor normal do botão
        self.fonte     = fonte       # fonte do texto

        # cor quando o mouse passa por cima — clareia cada canal RGB
        # min() garante que o valor não ultrapasse 255
        self.cor_selecionada = (
            min(self.cor[0] + 40, 255),  # clareia o vermelho
            min(self.cor[1] + 40, 255),  # clareia o verde
            min(self.cor[2] + 40, 255)   # clareia o azul
        )

        # retângulo que representa a área do botão
        # usado para detectar se o mouse está em cima ou clicou
        self.area_clique = pygame.Rect(
            self.posicao_x,
            self.posicao_y,
            self.largura,
            self.altura
        )

    # Desenha o botão na tela
    def desenhar(self, tela):
        # pega a posição atual do mouse
        posicao_mouse = pygame.mouse.get_pos()

        # verifica se o mouse está dentro da área do botão
        if self.area_clique.collidepoint(posicao_mouse):
            cor_atual = self.cor_selecionada  # mouse em cima: clareia
        else:
            cor_atual = self.cor              # mouse fora: cor normal

        # desenha o fundo do botão com bordas arredondadas
        pygame.draw.rect(tela, cor_atual, self.area_clique, border_radius=10)

        # desenha a borda escura ao redor do botão
        pygame.draw.rect(tela, PRETO, self.area_clique, 2, border_radius=10)

        # desenha o texto centralizado dentro do botão
        if self.fonte:
            # render transforma o texto em uma imagem desenhável
            imagem_texto = self.fonte.render(self.texto, True, PRETO)

            # calcula a posição para centralizar o texto no botão
            texto_posicao_x = self.posicao_x + (self.largura - imagem_texto.get_width())  // 2
            texto_posicao_y = self.posicao_y + (self.altura  - imagem_texto.get_height()) // 2

            # blit = desenha a imagem do texto na tela
            tela.blit(imagem_texto, (texto_posicao_x, texto_posicao_y))

    # Verifica se o botão foi clicado
    # retorna True se sim, False se não
    def foi_clicado(self, evento):
        # MOUSEBUTTONDOWN = evento de clique do mouse
        if evento.type == pygame.MOUSEBUTTONDOWN:
            # verifica se o clique foi dentro da área do botão
            if self.area_clique.collidepoint(evento.pos):
                return True   # foi clicado!
        return False           # não foi clicado