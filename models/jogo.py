# ═══════════════════════════════════════════════════════════
# ARQUIVO: models/jogo.py
# Responsabilidade: controlar todas as telas e a lógica geral
# ═══════════════════════════════════════════════════════════

# pygame: biblioteca principal — janela, imagens, sons, teclado, colisão
# sys: usado para fechar o programa com sys.exit()
# random: sorteia os tipos e itens de lixo que caem
# json + os: salvam e leem o ranking em arquivo no disco
import pygame
import sys
import random
import json
import os
import math

import utils.constantes as constantes
from utils.constantes import (
    LIMITE_FPS,
    BRANCO, PRETO, CINZA,
    AZUL_PAPEL, VERMELHO_PLASTICO, VERDE_VIDRO, AMARELO_METAL, DOURADO,
    TIPOS_LIXEIRA,
    carregar_fontes
)
from models.botao   import Botao
from models.lixeira import Lixeira
from models.lixo     import Lixo, LixoBonus

# arquivo onde o ranking é salvo entre sessões
ARQUIVO_RECORDE = "recorde.json"

# quantidade de melhores pontuações guardadas no ranking (NOVO)
TAMANHO_RANKING = 5

# chance (8%) de um lixo sorteado ser o item bônus em vez de um lixo comum
CHANCE_LIXO_BONUS = 0.08

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

        # ── NOVO: sons de efeito de acerto e erro ──
        # usamos try/except porque esses arquivos podem não existir ainda;
        # assim o jogo continua funcionando (sem som) em vez de travar
        try:
            self.som_acerto = pygame.mixer.Sound("assets/sons/acerto.mp3")
            self.som_erro   = pygame.mixer.Sound("assets/sons/erro.mp3")
        except (pygame.error, FileNotFoundError):
            self.som_acerto = None
            self.som_erro   = None

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

        # ÍCONES DE VIDA  (gerado a partir de TIPOS_LIXEIRA — escala
        # automaticamente para qualquer quantidade de lixeiras cadastradas)
        # dicionário com um ícone 40x40 para cada tipo de lixeira
        # exibidos no canto superior esquerdo durante o jogo
        #
        # IMPORTANTE: o nome do arquivo usa a CHAVE do tipo (ex: "nao-reciclavel"),
        # não o nome de exibição (ex: "NAO RECICLAVEL", que tem espaço e não
        # existe como arquivo) — isso casa com os arquivos reais em assets/imagens:
        # VIDA-PAPEL.png, VIDA-NAO-RECICLAVEL.png, VIDA-RADIOTIVO.png, etc.
        # Exceção: "residuos-perigosos" usa VIDA-PERIGOSOS.png (nome mais curto).
        nomes_arquivo_vida = {"residuos-perigosos": "PERIGOSOS"}

        self.icones_vida = {}
        for tipo, dados in TIPOS_LIXEIRA.items():
            nome_arquivo = nomes_arquivo_vida.get(tipo, tipo.upper())
            self.icones_vida[tipo] = self._carregar_imagem(
                f"VIDA-{nome_arquivo}.png", 40, 40, cor=dados["cor"], texto=dados["nome"]
            )

        # IMAGENS DA TELA DE ESCOLHA  (NOVO: idem, a partir de TIPOS_LIXEIRA)
        # imagens maiores (200x200) usadas nos botões de seleção de lixeira
        self.imagens_escolha = {}
        for tipo, dados in TIPOS_LIXEIRA.items():
            self.imagens_escolha[tipo] = self._carregar_imagem(
                f"lixeira-{tipo}.png", 200, 200, cor=dados["cor"], texto=dados["nome"]
            )

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

        # ── NOVO: sistema de combo/multiplicador de pontos ──
        # combo conta acertos seguidos; zera quando o jogador erra
        # maior_combo guarda o melhor combo da partida (mostrado no game over)
        self.combo       = 0
        self.maior_combo = 0

        # ── NOVO: guarda em qual tela estava antes de pausar ──
        self.tela_antes_da_pausa = None

        # VELOCIDADE PROGRESSIVA
        # velocidade_base começa em 1.0 e aumenta 30% por nível
        # aviso_nivel_timer conta frames para exibir o aviso de nível na tela
        self.velocidade_base      = 1.0
        self.pontos_ultimo_nivel  = 0
        self.nivel_atual          = 0
        self.aviso_nivel_timer    = 0

        # RANKING (substituiu o recorde único)
        # lê o top 5 salvo no arquivo ao iniciar
        self.ranking  = self._carregar_ranking()
        self.recorde  = self.ranking[0] if self.ranking else 0

        # BOTÃO START (tela de menu)
        self.botao_iniciar = Botao(
            self.LARGURA // 2 - 100, self.ALTURA - 150,
            200, 55, "START", VERDE_VIDRO, self.fontes["media"]
        )

        # ── NOVO: BOTÃO RANKING (tela de menu) ──
        self.botao_ranking = Botao(
            self.LARGURA // 2 - 100, self.ALTURA - 80,
            200, 45, "RANKING", CINZA, self.fontes["pequena"]
        )

        # ── NOVO: BOTÃO VOLTAR (tela de ranking) ──
        self.botao_voltar_ranking = Botao(
            self.LARGURA // 2 - 100, self.ALTURA - 100,
            200, 50, "VOLTAR", CINZA, self.fontes["media"]
        )

        # BOTÕES DE ESCOLHA DE LIXEIRA  (grid fixo: 2 colunas)
        # Em vez de "até 4 por linha" — que com 10 lixeiras gera
        # 4 + 4 + 2 e deixa a última linha incompleta e desalinhada —
        # usamos SEMPRE 2 colunas. Assim o grid fica simétrico nas
        # duas metades da tela, e cada item ganha um CARD (fundo +
        # borda) por trás, em vez da imagem ficar solta no fundo escuro.
        tipos_lixeira = list(TIPOS_LIXEIRA.keys())
        quantidade    = len(tipos_lixeira)
        colunas       = 2
        linhas        = math.ceil(quantidade / colunas)

        # espaço reservado no topo (título + instrução) e na base (botão JOGAR,
        # que fica em ALTURA - 120 — reservamos um pouco mais para dar folga)
        topo_reservado    = 170
        base_reservada    = 140
        espaco_disponivel = self.ALTURA - topo_reservado - base_reservada

        # ── tamanho do card é CALCULADO a partir do espaço disponível,
        # não fixo — assim, com muitas linhas (ex: 5), os cards encolhem
        # o suficiente para caber sem sobrepor o título ou o botão JOGAR.
        # tenta primeiro com a margem "confortável"; se não couber, usa
        # uma margem menor entre as linhas (o card sempre cede espaço
        # primeiro à margem, e só depois ao próprio tamanho).
        margem_y_confortavel = 20
        margem_y_minima      = 10

        def altura_card_para(margem_y_teste):
            return (espaco_disponivel - (linhas - 1) * margem_y_teste) / linhas

        margem_y   = margem_y_confortavel
        card_altura = altura_card_para(margem_y)
        if card_altura < 110:
            # com a margem confortável o card ficaria pequeno demais:
            # reduz a margem para sobrar mais altura pro card
            margem_y    = margem_y_minima
            card_altura = altura_card_para(margem_y)

        # nunca deixa o card maior que 160 (fica desproporcional com poucas linhas)
        # nem permite ultrapassar o espaço disponível mesmo no caso extremo
        card_altura = max(70, min(160, int(card_altura)))

        # o ícone ocupa a maior parte do card; o restante é margem + nome
        tam_icone    = int(card_altura * 0.62)
        card_largura = 280
        margem_x     = 50

        total_largura = colunas * card_largura + (colunas - 1) * margem_x
        total_altura  = linhas  * card_altura  + (linhas  - 1) * margem_y

        ini_x = (self.LARGURA - total_largura) // 2
        ini_y = topo_reservado + max(0, (espaco_disponivel - total_altura) // 2)

        # guarda as dimensões do card para reaproveitar no desenho
        self.tam_icone_escolha    = tam_icone
        self.card_largura_escolha = card_largura
        self.card_altura_escolha  = card_altura

        self.botoes_escolha = {}
        for indice, tipo in enumerate(tipos_lixeira):
            coluna = indice % colunas
            linha  = indice // colunas
            x = ini_x + coluna * (card_largura + margem_x)
            y = ini_y + linha  * (card_altura  + margem_y)
            cor = TIPOS_LIXEIRA[tipo]["cor"]
            # a área de clique do botão agora é o CARD inteiro (não só o ícone)
            self.botoes_escolha[tipo] = Botao(x, y, card_largura, card_altura, "", cor, self.fontes["media"])

        # BOTÃO JOGAR (aparece após escolher lixeira) 
        self.botao_jogar = Botao(
            self.LARGURA // 2 - 100, self.ALTURA - 120,
            200, 55, "JOGAR!", VERDE_VIDRO, self.fontes["media"]
        )

    # ── NOVO: ranking (substitui _carregar_recorde / _salvar_recorde) ──
    # Lê e grava o TOP 5 no arquivo recorde.json.
    # Mantém compatibilidade com o formato antigo {"recorde": N},
    # convertendo automaticamente para o novo formato em lista.
    def _carregar_ranking(self):
        if os.path.exists(ARQUIVO_RECORDE):
            with open(ARQUIVO_RECORDE, "r") as f:
                dados = json.load(f)
                if "ranking" in dados:
                    return dados["ranking"]
                elif "recorde" in dados:          # arquivo no formato antigo
                    return [dados["recorde"]]
        return []

    def _salvar_ranking(self):
        with open(ARQUIVO_RECORDE, "w") as f:
            json.dump({"ranking": self.ranking}, f)

    # Insere a pontuação da partida no ranking, reordena do maior
    # para o menor e mantém só os TAMANHO_RANKING melhores
    def _atualizar_ranking(self, pontos):
        self.ranking.append(pontos)
        self.ranking.sort(reverse=True)
        self.ranking = self.ranking[:TAMANHO_RANKING]
        self._salvar_ranking()
        self.recorde = self.ranking[0]

    # Método auxiliar que evita repetição de código.
    # Sempre que precisamos carregar e redimensionar uma imagem,
    # chamamos ele passando nome do arquivo, largura e altura.
    # NOVO: usa carregar_imagem_ou_placeholder, então se o arquivo
    # não existir (ex: lixeira nova sem imagem ainda), gera um
    # ícone substituto em vez de travar o jogo.
    def _carregar_imagem(self, nome_arquivo, largura, altura, cor=CINZA, texto="?"):
        caminho = f"assets/imagens/{nome_arquivo}"
        return constantes.carregar_imagem_ou_placeholder(
            caminho, largura, altura, cor=cor, texto=texto, fonte=self.fontes["pequena"]
        )

    # Desenha os ícones de vida no canto superior esquerdo.
    # Antes de escolher lixeira: mostra um ícone de cada tipo.
    # Após a escolha: mostra só o ícone da lixeira escolhida.
    def desenhar_vidas(self):
        if not self.tipo_escolhido:
            tipos = list(TIPOS_LIXEIRA.keys())
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
        self.botao_ranking.desenhar(self.tela)  # NOVO

        for evento in lista_eventos:
            if self.botao_iniciar.foi_clicado(evento):
                self.tela_atual = "escolha"   # avança para a próxima tela
            if self.botao_ranking.foi_clicado(evento):  # NOVO
                self.tela_atual = "ranking"

    # ── NOVO: tela de ranking ──
    # Mostra as 5 melhores pontuações já registradas.
    # Botão VOLTAR retorna ao menu.
    def tela_ranking(self, lista_eventos):
        self.tela.fill((30, 30, 30))

        titulo = self.fontes["titulo"].render("TOP 5 RECORDES", True, AMARELO_METAL)
        self.tela.blit(titulo, (self.LARGURA // 2 - titulo.get_width() // 2, 60))

        if not self.ranking:
            vazio = self.fontes["media"].render(
                "Nenhum recorde ainda. Jogue para começar!", True, CINZA
            )
            self.tela.blit(vazio, (self.LARGURA // 2 - vazio.get_width() // 2, 220))
        else:
            for posicao, pontos in enumerate(self.ranking, start=1):
                # o primeiro lugar ganha destaque dourado e o ícone de troféu
                if posicao == 1:
                    texto = self.fontes["media"].render(f"1º lugar — {pontos} pontos", True, DOURADO)
                    y = 170
                    self.tela.blit(self.icone_trofeu, (self.LARGURA // 2 - texto.get_width() // 2 - 50, y - 5))
                else:
                    texto = self.fontes["media"].render(f"{posicao}º lugar — {pontos} pontos", True, BRANCO)
                    y = 170 + (posicao - 1) * 55
                self.tela.blit(texto, (self.LARGURA // 2 - texto.get_width() // 2, y))

        self.botao_voltar_ranking.desenhar(self.tela)

        for evento in lista_eventos:
            if self.botao_voltar_ranking.foi_clicado(evento):
                self.tela_atual = "menu"

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

        tam_icone = self.tam_icone_escolha

        for tipo, botao in self.botoes_escolha.items():
            x          = botao.posicao_x
            y          = botao.posicao_y
            card_larg  = botao.largura
            card_alt   = botao.altura
            area_card  = pygame.Rect(x, y, card_larg, card_alt)

            selecionado = (self.tipo_escolhido == tipo)

            # ── sombra leve por trás do card (dá profundidade) ──
            sombra = area_card.move(4, 4)
            pygame.draw.rect(self.tela, (20, 20, 20), sombra, border_radius=16)

            # ── fundo do card: mais claro e com leve tom da cor do tipo
            # quando selecionado, para dar feedback visual sem perder contraste ──
            cor_fundo = (70, 70, 70) if not selecionado else (60, 90, 60)
            pygame.draw.rect(self.tela, cor_fundo, area_card, border_radius=16)

            # borda do card — branca e mais grossa quando selecionado
            cor_borda = BRANCO if selecionado else CINZA
            espessura_borda = 4 if selecionado else 2
            pygame.draw.rect(self.tela, cor_borda, area_card, espessura_borda, border_radius=16)

            # ── ícone da lixeira, centralizado na metade superior do card ──
            icone = pygame.transform.smoothscale(self.imagens_escolha[tipo], (tam_icone, tam_icone))
            icone_x = x + (card_larg - tam_icone) // 2
            icone_y = y + max(8, int(card_alt * 0.08))
            self.tela.blit(icone, (icone_x, icone_y))

            # ── nome do tipo, sempre em branco (legível em qualquer card) ──
            imagem_nome = self.fontes["pequena"].render(
                TIPOS_LIXEIRA[tipo]["nome"], True, BRANCO
            )
            nome_x = x + (card_larg - imagem_nome.get_width()) // 2
            nome_y = icone_y + tam_icone + 8
            self.tela.blit(imagem_nome, (nome_x, nome_y))

            # área de clique do botão = o card inteiro
            botao.area_clique = area_card

        # botão JOGAR só aparece depois que uma lixeira foi escolhida
        if self.tipo_escolhido:
            self.botao_jogar.desenhar(self.tela)

        for evento in lista_eventos:
            for tipo, botao in self.botoes_escolha.items():
                if botao.foi_clicado(evento):
                    self.tipo_escolhido = tipo

            if self.tipo_escolhido and self.botao_jogar.foi_clicado(evento):
                # cria o objeto Lixeira com o tipo escolhido pelo jogador
                self.lixeira_jogador = Lixeira(
                    self.tipo_escolhido,
                    TIPOS_LIXEIRA[self.tipo_escolhido]["cor"],
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
    #   1. Verifica se o jogador pediu pausa (tecla P)
    #   2. Calcula o nível e ajusta velocidade e spawn
    #   3. Cria novos lixos no intervalo definido (chance de ser Lixo Bônus)
    #   4. Move e desenha cada lixo da lista
    #   5. Detecta colisão: tipo certo = +pontos com combo, errado = -1 vida
    #   6. Remove lixos que saíram da tela
    #   7. Move e desenha a lixeira
    #   8. Exibe pontuação, recorde, nível, combo e aviso de nível
    #   9. Verifica se acabaram as vidas -> game over
    def tela_jogo(self, lista_eventos):
        # ── NOVO: pausa o jogo ao pressionar P ──
        for evento in lista_eventos:
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_p:
                self.tela_atual = "pausado"
                return  # não processa o resto do frame como jogo

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
            # pequena chance de cair um Lixo Bônus em vez de um lixo comum.
            # IMPORTANTE: o bônus é forçado a ser do MESMO tipo da lixeira
            # do jogador — não faz sentido sortear um bônus de um tipo que
            # ele não está jogando, já que ele não tem como acertar.
            if random.random() < CHANCE_LIXO_BONUS:
                novo_lixo = LixoBonus(self.fontes["pequena"], tipo_forcado=self.tipo_escolhido)
            else:
                novo_lixo = Lixo(self.fontes["pequena"], self.velocidade_base)
            self.lista_lixos.append(novo_lixo)
            self.contador_lixo = 0

        # ── processa cada lixo na lista ──
        for lixo_atual in self.lista_lixos[:]:
            lixo_atual.cair()           # move o lixo para baixo
            lixo_atual.desenhar(self.tela)

            # colisão com a lixeira
            if lixo_atual.area_colisao.colliderect(self.lixeira_jogador.area_colisao):
                self.lista_lixos.remove(lixo_atual)

                # acertou a lixeira certa? (o lixo bônus também precisa
                # ser jogado na lixeira certa — só muda o quanto vale)
                if lixo_atual.tipo == self.lixeira_jogador.tipo_aceito:
                    # sistema de combo — a cada 5 acertos seguidos
                    # o multiplicador de pontos sobe 0.5x (10 -> 15 -> 20...)
                    self.combo += 1
                    self.maior_combo = max(self.maior_combo, self.combo)

                    if lixo_atual.eh_bonus:
                        # item dourado: pontos fixos e maiores
                        self.pontuacao += LixoBonus.PONTOS_BONUS
                    else:
                        multiplicador_combo = 1 + (self.combo // 5) * 0.5
                        self.pontuacao += int(10 * multiplicador_combo)

                    if self.som_acerto:
                        self.som_acerto.play()
                else:
                    self.combo = 0   # erro zera o combo (vale para o bônus também)
                    self.quantidade_vidas -= 1
                    if self.som_erro:
                        self.som_erro.play()

            # remove lixo que passou da tela sem ser capturado
            elif lixo_atual.saiu_da_tela():
                self.lista_lixos.remove(lixo_atual)
                self.combo = 0   # deixar passar zera o combo

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

        # ── NOVO: mostra o combo atual quando maior que 1 ──
        if self.combo > 1:
            multiplicador_combo = 1 + (self.combo // 5) * 0.5
            texto_combo = self.fontes["pequena"].render(
                f"Combo x{self.combo}  (pontos x{multiplicador_combo:.1f})", True, DOURADO
            )
            self.tela.blit(texto_combo, (self.LARGURA - 220, 96))

        # ── dica de pausa no canto inferior ──
        dica_pausa = self.fontes["pequena"].render("P = pausar", True, CINZA)
        self.tela.blit(dica_pausa, (10, self.ALTURA - 30))

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
            self._atualizar_ranking(self.pontuacao)  # NOVO: atualiza o top 5
            self.tela_atual = "gameover"    

    # ── NOVO: tela de pausa ──
    # Desenha um overlay escurecido sobre o último frame do jogo
    # (a tela não é limpa, então o jogo continua visível por baixo).
    # Pressionar P de novo retoma exatamente de onde parou.
    def tela_pausa(self, lista_eventos):
        overlay = pygame.Surface((self.LARGURA, self.ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.tela.blit(overlay, (0, 0))

        texto_pausa = self.fontes["titulo"].render("PAUSADO", True, BRANCO)
        self.tela.blit(texto_pausa, (self.LARGURA // 2 - texto_pausa.get_width() // 2, self.ALTURA // 2 - 80))

        texto_dica = self.fontes["media"].render("Pressione P para continuar", True, CINZA)
        self.tela.blit(texto_dica, (self.LARGURA // 2 - texto_dica.get_width() // 2, self.ALTURA // 2))

        for evento in lista_eventos:
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_p:
                self.tela_atual = "jogando"

    # Exibe o placar final, o recorde e o maior combo da partida.
    # Se bateu o recorde: mostra "NOVO RECORDE!" com troféu em amarelo.
    # R -> chama __init__ novamente reiniciando tudo (preserva o ranking).
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

        # ── NOVO: mostra o maior combo feito na partida ──
        imagem_combo = self.fontes["pequena"].render(
            f"Maior combo: x{self.maior_combo}", True, DOURADO
        )
        self.tela.blit(imagem_combo, (self.LARGURA // 2 - imagem_combo.get_width() // 2, self.ALTURA // 2 + 40))

        imagem_reiniciar = self.fontes["media"].render(
            "Pressione R para jogar de novo", True, CINZA
        )
        posicao_reiniciar_x = self.LARGURA // 2 - imagem_reiniciar.get_width() // 2
        self.tela.blit(imagem_reiniciar, (posicao_reiniciar_x, self.ALTURA // 2 + 80))

        for evento in lista_eventos:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    ranking_atual = self.ranking    # salva o ranking antes de reiniciar
                    self.__init__()                 # reinicia todos os atributos
                    self.ranking = ranking_atual     # restaura o ranking preservado
                    self.recorde = self.ranking[0] if self.ranking else 0
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
            elif self.tela_atual == "ranking":       # NOVO
                self.tela_ranking(lista_eventos)
            elif self.tela_atual == "escolha":
                self.tela_escolha(lista_eventos)
            elif self.tela_atual == "jogando":
                self.tela_jogo(lista_eventos)
            elif self.tela_atual == "pausado":       # NOVO
                self.tela_pausa(lista_eventos)
            elif self.tela_atual == "gameover":
                self.tela_gameover(lista_eventos)

            pygame.display.flip()          # atualiza tudo que foi desenhado
            self.relogio.tick(LIMITE_FPS)  # limita a 60 frames por segundo