# ═══════════════════════════════════════════════════════════
# ARQUIVO: models/jogo.py
# Responsabilidade: controlar todas as telas e a lógica geral
# ═══════════════════════════════════════════════════════════

import pygame
import sys
import random
import json
import os

import utils.constantes as constantes
from utils.constantes import (
    LIMITE_FPS,
    BRANCO, PRETO, CINZA,
    AZUL_PAPEL, VERMELHO_PLASTICO, VERDE_VIDRO, AMARELO_METAL,
    carregar_fontes
)
from models.botao   import Botao
from models.lixeira import Lixeira
from models.lixo    import Lixo

# arquivo onde o recorde é salvo
ARQUIVO_RECORDE = "recorde.json"

class Jogo:

    def __init__(self):
        pygame.init()

        # ── SOM ──
        pygame.mixer.init()
        self.som_gameover = pygame.mixer.Sound("assets/sons/game-over.mp3")
        self.musica_tocando = False

        # ── TELA CHEIA ──
        self.tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("CEAGRI Recicla")

        constantes.LARGURA_TELA, constantes.ALTURA_TELA = self.tela.get_size()
        self.LARGURA = constantes.LARGURA_TELA
        self.ALTURA  = constantes.ALTURA_TELA

        self.relogio = pygame.time.Clock()
        self.fontes  = carregar_fontes()

        # ── imagem de fundo do menu ──
        imagem_carregada = pygame.image.load("assets/imagens/IMAGEM-JOGO.png")
        self.imagem_fundo_menu = pygame.transform.scale(
            imagem_carregada, (self.LARGURA, self.ALTURA)
        )

        # ── ícones de vida ──
        self.icones_vida = {
            "papel":    self._carregar_imagem("VIDA-PAPEL.png",    40, 40),
            "plastico": self._carregar_imagem("VIDA-PLASTICO.png", 40, 40),
            "vidro":    self._carregar_imagem("VIDA-VIDRO.png",    40, 40),
            "metal":    self._carregar_imagem("VIDA-METAL.png",    40, 40),
        }

        # ── imagens das lixeiras para a tela de escolha (200x200) ──
        self.imagens_escolha = {
            "papel":    self._carregar_imagem("lixeira-papel.png",    200, 200),
            "plastico": self._carregar_imagem("lixeira-plastico.png", 200, 200),
            "vidro":    self._carregar_imagem("lixeira-vidro.png",    200, 200),
            "metal":    self._carregar_imagem("lixeira-metal.png",    200, 200),
        }

        # ── ícone do troféu ──
        self.icone_trofeu = self._carregar_imagem("TROFEU.png", 40, 40)

        # ── variáveis de controle ──
        self.tela_atual       = "menu"
        self.pontuacao        = 0
        self.quantidade_vidas = 4
        self.lixeira_jogador  = None
        self.lista_lixos      = []
        self.contador_lixo    = 0
        self.tipo_escolhido   = None

        # ── velocidade progressiva ──
        self.velocidade_base      = 1.0   # multiplicador inicial
        self.pontos_ultimo_nivel  = 0     # pontuação na última vez que subiu de nível
        self.nivel_atual          = 0     # nível atual
        self.aviso_nivel_timer    = 0     # timer do aviso na tela (frames)

        # ── recorde ──
        self.recorde = self._carregar_recorde()

        # ── botão START ──
        self.botao_iniciar = Botao(
            self.LARGURA // 2 - 100, self.ALTURA - 120,
            200, 55, "START", VERDE_VIDRO, self.fontes["media"]
        )

        # ── botões de escolha centralizados na tela ──
        tam     = 200
        margem  = 40
        total   = 4 * tam + 3 * margem
        ini_x   = (self.LARGURA - total) // 2
        ini_y   = self.ALTURA // 2 - tam // 2

        self.botoes_escolha = {
            "papel":    Botao(ini_x,                       ini_y, tam, tam, "", AZUL_PAPEL,        self.fontes["media"]),
            "plastico": Botao(ini_x + (tam + margem),     ini_y, tam, tam, "", VERMELHO_PLASTICO, self.fontes["media"]),
            "vidro":    Botao(ini_x + (tam + margem) * 2, ini_y, tam, tam, "", VERDE_VIDRO,       self.fontes["media"]),
            "metal":    Botao(ini_x + (tam + margem) * 3, ini_y, tam, tam, "", AMARELO_METAL,     self.fontes["media"]),
        }

        self.botao_jogar = Botao(
            self.LARGURA // 2 - 100, self.ALTURA - 120,
            200, 55, "JOGAR!", VERDE_VIDRO, self.fontes["media"]
        )

    # ───────────────────────────────────────────────────────
    # RECORDE: carregar e salvar
    # ───────────────────────────────────────────────────────
    def _carregar_recorde(self):
        if os.path.exists(ARQUIVO_RECORDE):
            with open(ARQUIVO_RECORDE, "r") as f:
                dados = json.load(f)
                return dados.get("recorde", 0)
        return 0

    def _salvar_recorde(self):
        with open(ARQUIVO_RECORDE, "w") as f:
            json.dump({"recorde": self.recorde}, f)

    # ───────────────────────────────────────────────────────
    # MÉTODO AUXILIAR: _carregar_imagem
    # ───────────────────────────────────────────────────────
    def _carregar_imagem(self, nome_arquivo, largura, altura):
        caminho = f"assets/imagens/{nome_arquivo}"
        imagem  = pygame.image.load(caminho)
        return pygame.transform.scale(imagem, (largura, altura))

    # ───────────────────────────────────────────────────────
    # MÉTODO: desenhar_vidas
    # ───────────────────────────────────────────────────────
    def desenhar_vidas(self):
        if not self.tipo_escolhido:
            tipos = ["papel", "plastico", "vidro", "metal"]
            for i, tipo in enumerate(tipos[:self.quantidade_vidas]):
                self.tela.blit(self.icones_vida[tipo], (10 + i * 48, 10))
        else:
            icone = self.icones_vida[self.tipo_escolhido]
            for i in range(self.quantidade_vidas):
                self.tela.blit(icone, (10 + i * 48, 10))

    # ───────────────────────────────────────────────────────
    # MÉTODO: tela_menu
    # ───────────────────────────────────────────────────────
    def tela_menu(self, lista_eventos):
        self.tela.blit(self.imagem_fundo_menu, (0, 0))

        fundo_titulo = pygame.Surface((500, 80), pygame.SRCALPHA)
        fundo_titulo.fill((0, 0, 0, 150))
        self.tela.blit(fundo_titulo, (self.LARGURA // 2 - 250, 30))

        imagem_titulo = self.fontes["titulo"].render("CEAGRI RECICLA", True, BRANCO)
        posicao_titulo_x = self.LARGURA // 2 - imagem_titulo.get_width() // 2
        self.tela.blit(imagem_titulo, (posicao_titulo_x, 40))

        # mostra recorde no canto superior direito com troféu
        texto_recorde = self.fontes["media"].render(f"Recorde: {self.recorde} pts", True, AMARELO_METAL)
        largura_total = self.icone_trofeu.get_width() + 8 + texto_recorde.get_width()
        fundo_rec = pygame.Surface((largura_total + 24, 50), pygame.SRCALPHA)
        fundo_rec.fill((0, 0, 0, 160))
        pos_x = self.LARGURA - largura_total - 30
        self.tela.blit(fundo_rec,        (pos_x - 4, 8))
        self.tela.blit(self.icone_trofeu,(pos_x, 13))
        self.tela.blit(texto_recorde,    (pos_x + self.icone_trofeu.get_width() + 8, 18))

        self.desenhar_vidas()
        self.botao_iniciar.desenhar(self.tela)

        for evento in lista_eventos:
            if self.botao_iniciar.foi_clicado(evento):
                self.tela_atual = "escolha"

    # ───────────────────────────────────────────────────────
    # MÉTODO: tela_escolha
    # ───────────────────────────────────────────────────────
    def tela_escolha(self, lista_eventos):
        self.tela.fill((40, 40, 40))

        imagem_titulo = self.fontes["titulo"].render("Escolha sua lixeira!", True, BRANCO)
        self.tela.blit(imagem_titulo, (self.LARGURA // 2 - imagem_titulo.get_width() // 2, 50))

        imagem_instrucao = self.fontes["pequena"].render(
            "Clique na lixeira e depois em JOGAR", True, CINZA
        )
        self.tela.blit(imagem_instrucao, (self.LARGURA // 2 - imagem_instrucao.get_width() // 2, 120))

        cores_tipo = {
            "papel":    AZUL_PAPEL,
            "plastico": VERMELHO_PLASTICO,
            "vidro":    VERDE_VIDRO,
            "metal":    AMARELO_METAL,
        }

        for tipo, botao in self.botoes_escolha.items():
            x = botao.posicao_x
            y = botao.posicao_y
            tam = botao.largura

            if self.tipo_escolhido == tipo:
                pygame.draw.rect(self.tela, BRANCO,
                    pygame.Rect(x - 6, y - 6, tam + 12, tam + 12), 4, border_radius=14)

            self.tela.blit(self.imagens_escolha[tipo], (x, y))

            imagem_nome = self.fontes["media"].render(tipo.upper(), True, cores_tipo[tipo])
            self.tela.blit(imagem_nome, (x + (tam - imagem_nome.get_width()) // 2, y + tam + 8))

            botao.area_clique = pygame.Rect(x, y, tam, tam)

        if self.tipo_escolhido:
            self.botao_jogar.desenhar(self.tela)

        for evento in lista_eventos:
            for tipo, botao in self.botoes_escolha.items():
                if botao.foi_clicado(evento):
                    self.tipo_escolhido = tipo

            if self.tipo_escolhido and self.botao_jogar.foi_clicado(evento):
                cores_por_tipo = {
                    "papel":    AZUL_PAPEL,
                    "plastico": VERMELHO_PLASTICO,
                    "vidro":    VERDE_VIDRO,
                    "metal":    AMARELO_METAL
                }
                self.lixeira_jogador = Lixeira(
                    self.tipo_escolhido,
                    cores_por_tipo[self.tipo_escolhido],
                    self.fontes["pequena"]
                )
                # toca música em loop
                pygame.mixer.music.load("assets/sons/game-start.mp3")
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0.5)
                self.musica_tocando = True
                self.tela_atual = "jogando"

    # ───────────────────────────────────────────────────────
    # MÉTODO: tela_jogo
    # ───────────────────────────────────────────────────────
    def tela_jogo(self, lista_eventos):
        self.tela.fill((200, 220, 200))

        # ── velocidade progressiva: sobe a cada 50 pontos ──
        nivel = self.pontuacao // 50
        self.velocidade_base = 1.0 + nivel * 0.3  # +30% por nível

        # ── detecta mudança de nível e ativa aviso ──
        if nivel > self.nivel_atual:
            self.nivel_atual       = nivel
            self.aviso_nivel_timer = 180  # mostra por 3 segundos (60fps x 3)

        # ── intervalo de spawn diminui com o nível (mínimo 20 frames) ──
        intervalo_spawn = max(20, 60 - nivel * 5)

        self.contador_lixo += 1
        if self.contador_lixo >= intervalo_spawn:
            novo_lixo = Lixo(self.fontes["pequena"], self.velocidade_base)
            self.lista_lixos.append(novo_lixo)
            self.contador_lixo = 0

        for lixo_atual in self.lista_lixos[:]:
            lixo_atual.cair()
            lixo_atual.desenhar(self.tela)

            if lixo_atual.area_colisao.colliderect(self.lixeira_jogador.area_colisao):
                self.lista_lixos.remove(lixo_atual)
                if lixo_atual.tipo == self.lixeira_jogador.tipo_aceito:
                    self.pontuacao += 10
                else:
                    self.quantidade_vidas -= 1

            elif lixo_atual.saiu_da_tela():
                self.lista_lixos.remove(lixo_atual)

        self.lixeira_jogador.mover()
        self.lixeira_jogador.desenhar(self.tela)
        self.desenhar_vidas()

        # ── pontuação ──
        imagem_pontuacao = self.fontes["media"].render(
            f"Pontos: {self.pontuacao}", True, PRETO
        )
        self.tela.blit(imagem_pontuacao, (self.LARGURA - 220, 10))

        # ── recorde durante o jogo ──
        imagem_recorde = self.fontes["pequena"].render(
            f"Recorde: {self.recorde}", True, PRETO
        )
        self.tela.blit(imagem_recorde, (self.LARGURA - 220, 48))

        # ── nível atual ──
        imagem_nivel = self.fontes["pequena"].render(
            f"Nivel: {nivel + 1}", True, PRETO
        )
        self.tela.blit(imagem_nivel, (self.LARGURA - 220, 72))

        # ── desenha aviso de nível ──
        if self.aviso_nivel_timer > 0:
            self.aviso_nivel_timer -= 1

            # fundo semitransparente centralizado
            fundo = pygame.Surface((500, 100), pygame.SRCALPHA)
            alpha = min(255, self.aviso_nivel_timer * 3)  # fade out suave
            fundo.fill((0, 0, 0, alpha))
            self.tela.blit(fundo, (self.LARGURA // 2 - 250, self.ALTURA // 2 - 50))

            # texto do nível com fade out
            cor_aviso = (255, 220, 0, alpha)
            surf_nivel = self.fontes["titulo"].render(f"NIVEL {self.nivel_atual + 1}!", True, AMARELO_METAL)
            surf_sub   = self.fontes["media"].render("Ficou mais rapido!", True, BRANCO)
            self.tela.blit(surf_nivel, (self.LARGURA // 2 - surf_nivel.get_width() // 2, self.ALTURA // 2 - 40))
            self.tela.blit(surf_sub,   (self.LARGURA // 2 - surf_sub.get_width()   // 2, self.ALTURA // 2 + 20))

        if self.quantidade_vidas <= 0:
            # para a música e toca game over
            pygame.mixer.music.stop()
            self.som_gameover.play()
            # salva recorde se bateu
            if self.pontuacao > self.recorde:
                self.recorde = self.pontuacao
                self._salvar_recorde()
            self.tela_atual = "gameover"

    # ───────────────────────────────────────────────────────
    # MÉTODO: tela_gameover
    # ───────────────────────────────────────────────────────
    def tela_gameover(self, lista_eventos):
        self.tela.fill(PRETO)

        imagem_gameover = self.fontes["titulo"].render("GAME OVER", True, VERMELHO_PLASTICO)
        posicao_x = self.LARGURA // 2 - imagem_gameover.get_width() // 2
        self.tela.blit(imagem_gameover, (posicao_x, self.ALTURA // 2 - 150))

        imagem_pontuacao_final = self.fontes["media"].render(
            f"Você fez {self.pontuacao} pontos!", True, BRANCO
        )
        posicao_pontuacao_x = self.LARGURA // 2 - imagem_pontuacao_final.get_width() // 2
        self.tela.blit(imagem_pontuacao_final, (posicao_pontuacao_x, self.ALTURA // 2 - 60))

        # ── mostra recorde ──
        cor_recorde = AMARELO_METAL if self.pontuacao >= self.recorde else CINZA
        texto_recorde = "NOVO RECORDE!" if self.pontuacao >= self.recorde else f"Recorde: {self.recorde} pts"
        imagem_recorde = self.fontes["media"].render(texto_recorde, True, cor_recorde)
        if self.pontuacao >= self.recorde:
            largura_total = self.icone_trofeu.get_width() + 8 + imagem_recorde.get_width()
            pos_x = self.LARGURA // 2 - largura_total // 2
            self.tela.blit(self.icone_trofeu, (pos_x, self.ALTURA // 2 - 5))
            self.tela.blit(imagem_recorde,    (pos_x + self.icone_trofeu.get_width() + 8, self.ALTURA // 2))
        else:
            posicao_recorde_x = self.LARGURA // 2 - imagem_recorde.get_width() // 2
            self.tela.blit(imagem_recorde, (posicao_recorde_x, self.ALTURA // 2))

        imagem_reiniciar = self.fontes["media"].render(
            "Pressione R para jogar de novo", True, CINZA
        )
        posicao_reiniciar_x = self.LARGURA // 2 - imagem_reiniciar.get_width() // 2
        self.tela.blit(imagem_reiniciar, (posicao_reiniciar_x, self.ALTURA // 2 + 70))

        for evento in lista_eventos:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    recorde_atual = self.recorde  # preserva o recorde ao reiniciar
                    self.__init__()
                    self.recorde = recorde_atual
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    # ───────────────────────────────────────────────────────
    # MÉTODO: rodar
    # ───────────────────────────────────────────────────────
    def rodar(self):
        while True:
            lista_eventos = pygame.event.get()

            for evento in lista_eventos:
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            if self.tela_atual == "menu":
                self.tela_menu(lista_eventos)
            elif self.tela_atual == "escolha":
                self.tela_escolha(lista_eventos)
            elif self.tela_atual == "jogando":
                self.tela_jogo(lista_eventos)
            elif self.tela_atual == "gameover":
                self.tela_gameover(lista_eventos)

            pygame.display.flip()
            self.relogio.tick(LIMITE_FPS)