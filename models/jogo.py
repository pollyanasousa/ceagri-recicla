# ═══════════════════════════════════════════════════════════
# ARQUIVO: models/jogo.py
# Responsabilidade: controlar todas as telas e a lógica geral
# ═══════════════════════════════════════════════════════════

# pygame: biblioteca principal — janela, imagens, sons, teclado, colisão
# sys: usado para fechar o programa com sys.exit()
# random: sorteia os tipos e itens de lixo que caem
# json + os: salvam e leem o recorde em arquivo no disco
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

# arquivo onde o recorde é salvo entre sessões
ARQUIVO_RECORDE = "recorde.json"

class Jogo:

    # CONSTRUTOR
    # Inicializa o pygame, cria a janela, carrega imagens, sons,
    # define todas as variáveis de controle e cria os botões.
    def __init__(self):
        pygame.init()

        # SOM 
        # mixer.init() ativa o sistema de áudio do pygame
        pygame.mixer.init()
        self.som_gameover = pygame.mixer.Sound("assets/sons/game-over.mp3")
        self.musica_tocando = False

        # TELA CHEIA 
        # set_mode com FULLSCREEN abre em tela cheia
        # get_size() lê a resolução real do monitor e atualiza as constantes
        self.tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("CEAGRI Recicla")

        constantes.LARGURA_TELA, constantes.ALTURA_TELA = self.tela.get_size()
        self.LARGURA = constantes.LARGURA_TELA
        self.ALTURA  = constantes.ALTURA_TELA

        # relogio controla os FPS — garante 60 frames por segundo
        self.relogio = pygame.time.Clock()
        self.fontes  = carregar_fontes()

        # IMAGEM DE FUNDO DO MENU 
        # carrega e redimensiona para preencher a tela inteira
        imagem_carregada = pygame.image.load("assets/imagens/IMAGEM-JOGO.png")
        self.imagem_fundo_menu = pygame.transform.scale(
            imagem_carregada, (self.LARGURA, self.ALTURA)
        )

        # ÍCONES DE VIDA 
        # dicionário com um ícone 40x40 para cada tipo de lixeira
        # exibidos no canto superior esquerdo durante o jogo
        self.icones_vida = {
            "papel":    self._carregar_imagem("VIDA-PAPEL.png",    40, 40),
            "plastico": self._carregar_imagem("VIDA-PLASTICO.png", 40, 40),
            "vidro":    self._carregar_imagem("VIDA-VIDRO.png",    40, 40),
            "metal":    self._carregar_imagem("VIDA-METAL.png",    40, 40),
        }

        # IMAGENS DA TELA DE ESCOLHA 
        # imagens maiores (200x200) usadas nos botões de seleção de lixeira
        self.imagens_escolha = {
            "papel":    self._carregar_imagem("lixeira-papel.png",    200, 200),
            "plastico": self._carregar_imagem("lixeira-plastico.png", 200, 200),
            "vidro":    self._carregar_imagem("lixeira-vidro.png",    200, 200),
            "metal":    self._carregar_imagem("lixeira-metal.png",    200, 200),
        }

        # ÍCONE DO TROFÉU
        # aparece ao lado do recorde no menu e na tela de game over
        self.icone_trofeu = self._carregar_imagem("TROFEU.png", 40, 40)

        # VARIÁVEIS DE CONTROLE
        # tela_atual define qual método de tela é chamado no loop principal
        # lista_lixos guarda todos os objetos Lixo que estão caindo
        # contador_lixo conta frames para controlar quando spawnar novo lixo
        self.tela_atual       = "menu"
        self.pontuacao        = 0
        self.quantidade_vidas = 4
        self.lixeira_jogador  = None
        self.lista_lixos      = []
        self.contador_lixo    = 0
        self.tipo_escolhido   = None

        # VELOCIDADE PROGRESSIVA
        # velocidade_base começa em 1.0 e aumenta 30% por nível
        # aviso_nivel_timer conta frames para exibir o aviso de nível na tela
        self.velocidade_base      = 1.0
        self.pontos_ultimo_nivel  = 0
        self.nivel_atual          = 0
        self.aviso_nivel_timer    = 0

        # RECORDE
        # lê o recorde salvo no arquivo ao iniciar
        self.recorde = self._carregar_recorde()

        # BOTÃO START (tela de menu)
        self.botao_iniciar = Botao(
            self.LARGURA // 2 - 100, self.ALTURA - 120,
            200, 55, "START", VERDE_VIDRO, self.fontes["media"]
        )

        # BOTÕES DE ESCOLHA DE LIXEIRA 
        # 4 botões centralizados horizontalmente na tela
        # cálculo de ini_x garante que o conjunto fique centralizado
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

        # BOTÃO JOGAR (aparece após escolher lixeira) 
        self.botao_jogar = Botao(
            self.LARGURA // 2 - 100, self.ALTURA - 120,
            200, 55, "JOGAR!", VERDE_VIDRO, self.fontes["media"]
        )

    # _carregar_recorde e _salvar_recorde
    # Lê e grava o recorde no arquivo recorde.json
    # json.load lê o dicionário salvo; json.dump grava de volta
    # os.path.exists verifica se o arquivo já existe antes de abrir
    def _carregar_recorde(self):
        if os.path.exists(ARQUIVO_RECORDE):
            with open(ARQUIVO_RECORDE, "r") as f:
                dados = json.load(f)
                return dados.get("recorde", 0)
        return 0

    def _salvar_recorde(self):
        with open(ARQUIVO_RECORDE, "w") as f:
            json.dump({"recorde": self.recorde}, f)

    # Método auxiliar que evita repetição de código.
    # Sempre que precisamos carregar e redimensionar uma imagem,
    # chamamos ele passando nome do arquivo, largura e altura.
    def _carregar_imagem(self, nome_arquivo, largura, altura):
        caminho = f"assets/imagens/{nome_arquivo}"
        imagem  = pygame.image.load(caminho)
        return pygame.transform.scale(imagem, (largura, altura))

    # Desenha os ícones de vida no canto superior esquerdo.
    # Antes de escolher lixeira: mostra um ícone de cada tipo.
    # Após a escolha: mostra só o ícone da lixeira escolhida.
    def desenhar_vidas(self):
        if not self.tipo_escolhido:
            tipos = ["papel", "plastico", "vidro", "metal"]
            for i, tipo in enumerate(tipos[:self.quantidade_vidas]):
                self.tela.blit(self.icones_vida[tipo], (10 + i * 48, 10))
        else:
            icone = self.icones_vida[self.tipo_escolhido]
            for i in range(self.quantidade_vidas):
                self.tela.blit(icone, (10 + i * 48, 10))

    # Desenha a tela inicial com imagem de fundo, título,
    # recorde com troféu no canto superior direito e botão START.
    # Quando START é clicado, muda tela_atual para "escolha".  
    def tela_menu(self, lista_eventos):
        # desenha a imagem de fundo cobrindo toda a tela
        self.tela.blit(self.imagem_fundo_menu, (0, 0))

        # fundo semitransparente atrás do título (SRCALPHA = suporta transparência)
        fundo_titulo = pygame.Surface((500, 80), pygame.SRCALPHA)
        fundo_titulo.fill((0, 0, 0, 150))
        self.tela.blit(fundo_titulo, (self.LARGURA // 2 - 250, 30))

        imagem_titulo = self.fontes["titulo"].render("CEAGRI RECICLA", True, BRANCO)
        posicao_titulo_x = self.LARGURA // 2 - imagem_titulo.get_width() // 2
        self.tela.blit(imagem_titulo, (posicao_titulo_x, 40))

        # recorde no canto superior direito com ícone de troféu
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
                self.tela_atual = "escolha"   # avança para a próxima tela

    # Desenha os 4 botões com imagens das lixeiras.
    # Lixeira selecionada ganha borda branca.
    # Botão JOGAR só aparece após uma lixeira ser escolhida.
    # Ao clicar JOGAR: cria o objeto Lixeira e inicia a música.   
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

            # borda branca na lixeira selecionada
            if self.tipo_escolhido == tipo:
                pygame.draw.rect(self.tela, BRANCO,
                    pygame.Rect(x - 6, y - 6, tam + 12, tam + 12), 4, border_radius=14)

            self.tela.blit(self.imagens_escolha[tipo], (x, y))

            imagem_nome = self.fontes["media"].render(tipo.upper(), True, cores_tipo[tipo])
            self.tela.blit(imagem_nome, (x + (tam - imagem_nome.get_width()) // 2, y + tam + 8))

            botao.area_clique = pygame.Rect(x, y, tam, tam)

        # botão JOGAR só aparece depois que uma lixeira foi escolhida
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
                # cria o objeto Lixeira com o tipo escolhido pelo jogador
                self.lixeira_jogador = Lixeira(
                    self.tipo_escolhido,
                    cores_por_tipo[self.tipo_escolhido],
                    self.fontes["pequena"]
                )
                # inicia a música de fundo em loop infinito (-1)
                pygame.mixer.music.load("assets/sons/game-start.mp3")
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0.5)
                self.musica_tocando = True
                self.tela_atual = "jogando"

    # Aqui o jogo acontece de fato, frame a frame.
    # A cada frame:
    #   1. Calcula o nível e ajusta velocidade e spawn
    #   2. Cria novos lixos no intervalo definido
    #   3. Move e desenha cada lixo da lista
    #   4. Detecta colisão: tipo certo = +10pts, errado = -1 vida
    #   5. Remove lixos que saíram da tela
    #   6. Move e desenha a lixeira
    #   7. Exibe pontuação, recorde, nível e aviso de nível
    #   8. Verifica se acabaram as vidas -> game over
    def tela_jogo(self, lista_eventos):
        self.tela.fill((200, 220, 200))

        # ── nível sobe a cada 50 pontos; velocidade aumenta 30% por nível ──
        nivel = self.pontuacao // 50
        self.velocidade_base = 1.0 + nivel * 0.3

        # ── detecta mudança de nível e ativa o aviso na tela por 3 segundos ──
        if nivel > self.nivel_atual:
            self.nivel_atual       = nivel
            self.aviso_nivel_timer = 180  # 180 frames = 3 segundos a 60fps

        # ── intervalo de spawn diminui com o nível (mínimo 20 frames) ──
        intervalo_spawn = max(20, 60 - nivel * 5)

        # ── cria novo lixo quando o contador atinge o intervalo ──
        self.contador_lixo += 1
        if self.contador_lixo >= intervalo_spawn:
            novo_lixo = Lixo(self.fontes["pequena"], self.velocidade_base)
            self.lista_lixos.append(novo_lixo)
            self.contador_lixo = 0

        # ── processa cada lixo na lista ──
        for lixo_atual in self.lista_lixos[:]:
            lixo_atual.cair()           # move o lixo para baixo
            lixo_atual.desenhar(self.tela)

            # colisão com a lixeira: tipo certo soma pontos, errado perde vida
            if lixo_atual.area_colisao.colliderect(self.lixeira_jogador.area_colisao):
                self.lista_lixos.remove(lixo_atual)
                if lixo_atual.tipo == self.lixeira_jogador.tipo_aceito:
                    self.pontuacao += 10
                else:
                    self.quantidade_vidas -= 1

            # remove lixo que passou da tela sem ser capturado
            elif lixo_atual.saiu_da_tela():
                self.lista_lixos.remove(lixo_atual)

        self.lixeira_jogador.mover()
        self.lixeira_jogador.desenhar(self.tela)
        self.desenhar_vidas()

        # ── textos de pontuação, recorde e nível no canto superior direito ──
        imagem_pontuacao = self.fontes["media"].render(
            f"Pontos: {self.pontuacao}", True, PRETO
        )
        self.tela.blit(imagem_pontuacao, (self.LARGURA - 220, 10))

        imagem_recorde = self.fontes["pequena"].render(
            f"Recorde: {self.recorde}", True, PRETO
        )
        self.tela.blit(imagem_recorde, (self.LARGURA - 220, 48))

        imagem_nivel = self.fontes["pequena"].render(
            f"Nivel: {nivel + 1}", True, PRETO
        )
        self.tela.blit(imagem_nivel, (self.LARGURA - 220, 72))

        # ── aviso de novo nível com fade out suave ──
        if self.aviso_nivel_timer > 0:
            self.aviso_nivel_timer -= 1

            fundo = pygame.Surface((500, 100), pygame.SRCALPHA)
            alpha = min(255, self.aviso_nivel_timer * 3)  # alpha diminui com o timer
            fundo.fill((0, 0, 0, alpha))
            self.tela.blit(fundo, (self.LARGURA // 2 - 250, self.ALTURA // 2 - 50))

            surf_nivel = self.fontes["titulo"].render(f"NIVEL {self.nivel_atual + 1}!", True, AMARELO_METAL)
            surf_sub   = self.fontes["media"].render("Ficou mais rapido!", True, BRANCO)
            self.tela.blit(surf_nivel, (self.LARGURA // 2 - surf_nivel.get_width() // 2, self.ALTURA // 2 - 40))
            self.tela.blit(surf_sub,   (self.LARGURA // 2 - surf_sub.get_width()   // 2, self.ALTURA // 2 + 20))

        # ── verifica game over ──
        if self.quantidade_vidas <= 0:
            pygame.mixer.music.stop()       # para a música de fundo
            self.som_gameover.play()        # toca o efeito de game over
            if self.pontuacao > self.recorde:
                self.recorde = self.pontuacao
                self._salvar_recorde()      # grava novo recorde no arquivo
            self.tela_atual = "gameover"    
  
    # Exibe o placar final e o recorde.
    # Se bateu o recorde: mostra "NOVO RECORDE!" com troféu em amarelo.
    # R -> chama __init__ novamente reiniciando tudo (preserva o recorde).
    # ESC -> fecha o programa.   
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

        # cor e texto do recorde mudam conforme bateu ou não o recorde
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
                    recorde_atual = self.recorde  # salva o recorde antes de reiniciar
                    self.__init__()               # reinicia todos os atributos
                    self.recorde = recorde_atual  # restaura o recorde preservado
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    # O loop principal do jogo — roda indefinidamente.
    # A cada iteração:
    #   1. Coleta todos os eventos do frame (teclado, mouse, fechar janela)
    #   2. Verifica se o jogador fechou a janela ou pressionou ESC
    #   3. Chama o método da tela_atual
    #   4. display.flip() atualiza a tela com tudo que foi desenhado
    #   5. relogio.tick(60) limita a 60 frames por segundo
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

            # chama o método da tela atual
            if self.tela_atual == "menu":
                self.tela_menu(lista_eventos)
            elif self.tela_atual == "escolha":
                self.tela_escolha(lista_eventos)
            elif self.tela_atual == "jogando":
                self.tela_jogo(lista_eventos)
            elif self.tela_atual == "gameover":
                self.tela_gameover(lista_eventos)

            pygame.display.flip()          # atualiza tudo que foi desenhado
            self.relogio.tick(LIMITE_FPS)  # limita a 60 frames por segundo