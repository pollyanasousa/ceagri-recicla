# ═══════════════════════════════════════════════════════════
# ARQUIVO: models/lixo.py
# Responsabilidade: representar um lixo que cai de cima
# ═══════════════════════════════════════════════════════════

import pygame
import random

import utils.constantes as constantes
from utils.constantes import PRETO, DOURADO

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
                        ("Garrafa PET",       "GARRAFA.png"),
                        ("Garrafa PET 2",     "GARRAFA_PLASTICO.png"),
                        ("Sacola",            "SACOLA.png"),
                        ("Copo Descartável",  "COPO.png"),
                        ("Colher Descartável","COLHER.png"),
                    ]},
        "vidro":    {"itens": [
                        ("Vidro",            "VIDRO.png"),
                        ("Vidro 2",          "VIDRO2.png"),
                        ("Vidro 3",          "VIDRO3.png"),
                        ("Vidro 4",          "VIDRO4.png"),
                        ("Vidro 5",          "VIDRO5.png"),
                        ("Pote de Vidro",    "POTE.png"),
                    ]},
        "metal":    {"itens": [
                        ("Lata",          "LATA.png"),
                        ("Lata de Refri", "LATA_REFRI.png"),
                        ("Lata 3",        "LATA3.png"),
                        ("Lata Amassada", "LATA_AMASSADA.png"),
                        ("Metal",         "METAL.png"),
                        ("Alicate",       "ALICATE.png"),
                        ("Chave",         "CHAVE.png"),
                        ("Tesoura",       "TESOURA.png"),
                    ]},
        "organico": {"itens": [
                        ("Casca de Banana",   "BANANA.png"),
                        ("Casca de Melancia", "MELANCIA.png"),
                        ("Casca de Maçã",     "MACA.png"),
                        ("Resto de Pizza",    "PIZZA.png"),
                        ("Espinha de Peixe",  "ESPINHA_DE_PEIXE.png"),
                        ("Casca de Abóbora",  "ABOBORA.png"),
                    ]},
        "madeira": {"itens": [
                        ("Madeira", "MADEIRA.png"),
                        ("Lápis",   "LAPIS.png"),
                    ]},
        "nao-reciclavel": {"itens": [
                        ("Fralda Descartável", "FRALDA_DESCARTAVEL.png"),
                        ("Absorvente",         "ABSORVENTE.png"),
                        ("Papel Higiênico",    "PAPEL_HIGIENICO.png"),
                        ("Rejeito",            "REJEITOS.png"),
                    ]},
        "hospitalar": {"itens": [
                        ("Seringa",           "SERINGA.png"),
                        ("Luva Descartável",  "LUVAS.png"),
                        ("Máscara",           "MASCARA.png"),
                        ("Gaze com Sangue",   "SANGUE.png"),
                        ("Gaze com Sangue 2", "TNT_COM_SANGUE.png"),
                        ("Bolsa de Sangue",   "BOLSA_DE_SANGUE.png"),
                        ("Soro",              "SORO.png"),
                        ("Remédio Vencido",   "REMEDIO.png"),
                        ("Comprimidos",       "COMPRIMIDOS.png"),
                        ("Prontuário Médico", "PRONTUARIO.png"),
                    ]},
        "radiotivo": {"itens": [
                        ("Barril Radioativo",     "BARRIL.png"),
                        ("Frasco com Isótopo",    "FRASCO_COM_ISOTOPO.png"),
                        ("Tubos de Ensaio",       "TUBOS_ENSAIO_PIPETAS.png"),
                    ]},
        "residuos-perigosos": {"itens": [
                        ("Produto Químico",          "PRODUTO_QUIMICO.png"),
                        ("Máscara de Gás",           "MASCARA_DE_GAS.png"),
                        ("Lata de Tinta",            "LATA_COM_TINTA.png"),
                        ("Termômetro com Mercúrio",  "TERMOMETRO.png"),
                        ("Lâmpada Fluorescente",     "LAMPADA.png"),
                        ("Pilha",                    "PILHA.png"),
                        ("Bateria",                  "BATERIA.png"),
                        ("Celular Velho",            "CELULAR.png"),
                        ("Monitor Velho",            "MONITOR.png"),
                        ("Câmera Antiga",            "CAMERA_FOTOGRAFICA.png"),
                    ]},
    }

    #construtor
    def __init__(self, fonte, multiplicador_velocidade=1.0, tipo_forcado=None):
        self.fonte = fonte

        # sorteia tipo de lixo — a menos que um tipo específico tenha
        # sido forçado (usado pelo LixoBonus, que precisa cair sempre
        # do MESMO tipo que a lixeira do jogador aceita; não faz sentido
        # um bônus de um tipo que o jogador nem está jogando)
        if tipo_forcado:
            self.tipo = tipo_forcado
        else:
            self.tipo = random.choice(list(self.TIPOS_DE_LIXO.keys()))

        # sorteia item (nome, arquivo) do tipo
        nome, arquivo = random.choice(self.TIPOS_DE_LIXO[self.tipo]["itens"])
        self.nome_item = nome

        self.largura    = 70
        self.altura     = 70
        self.posicao_x  = random.randint(0, constantes.LARGURA_TELA - self.largura)
        self.posicao_y  = -self.altura
        self.velocidade = random.randint(3, 6) * multiplicador_velocidade

        # carrega a imagem do item (com reserva caso o arquivo não exista ainda)
        caminho = f"assets/imagens/{arquivo}"
        cor_do_tipo = constantes.TIPOS_LIXEIRA[self.tipo]["cor"]
        self.imagem = constantes.carregar_imagem_ou_placeholder(
            caminho, self.largura, self.altura, cor=cor_do_tipo, texto=nome, fonte=self.fonte
        )

        # retângulo de colisão
        self.area_colisao = pygame.Rect(
            self.posicao_x,
            self.posicao_y,
            self.largura,
            self.altura
        )

        # ── NOVO: flag que diferencia um lixo comum de um lixo bônus ──
        # fica em False aqui e é sobrescrita como True na subclasse LixoBonus
        self.eh_bonus = False

    # MÉTODO: cair
    def cair(self):
        self.posicao_y      += self.velocidade
        self.area_colisao.y  = self.posicao_y

    # MÉTODO: saiu_da_tela
    def saiu_da_tela(self):
        return self.posicao_y > constantes.ALTURA_TELA

    # MÉTODO: desenhar
    # Desenha a imagem do item na tela com nome abaixo
    def desenhar(self, tela):
        # desenha a imagem do objeto
        tela.blit(self.imagem, (self.posicao_x, self.posicao_y))

        # desenha o nome do item abaixo da imagem
        imagem_nome = self.fonte.render(self.nome_item, True, PRETO)
        nome_x = self.posicao_x + (self.largura - imagem_nome.get_width()) // 2
        nome_y = self.posicao_y + self.altura + 2
        tela.blit(imagem_nome, (nome_x, nome_y))


# ═══════════════════════════════════════════════════════════
# CLASSE: LixoBonus
# Herda de Lixo (HERANÇA): reaproveita todo o comportamento de
# cair(), saiu_da_tela() e desenhar() da classe-mãe.
# IMPORTANTE: o tipo é FORÇADO para ser igual ao da lixeira do
# jogador (ver tipo_forcado) — não tem sentido um bônus de um
# tipo que o jogador nem está jogando, já que ele só consegue
# acertar (e só vale a pena) o tipo da lixeira escolhida.
# Erra a lixeira e perde vida normalmente, igual a qualquer
# outro lixo — a única diferença é que vale mais pontos e tem
# um destaque amarelo no fundo da imagem.
# ═══════════════════════════════════════════════════════════
class LixoBonus(Lixo):

    PONTOS_BONUS = 30  # vale 3x mais que um lixo comum (10 pontos)

    def __init__(self, fonte, tipo_forcado=None):
        # chama o construtor da classe-mãe (super) para sortear
        # um item normalmente — repassa tipo_forcado para garantir
        # que o bônus seja SEMPRE do mesmo tipo que a lixeira do
        # jogador aceita (não faz sentido um bônus de um tipo que
        # ele nem pode pegar)
        super().__init__(fonte, multiplicador_velocidade=1.3, tipo_forcado=tipo_forcado)

        # mantém o nome original do item (ex: "Papel", "Jornal") — sem
        # nenhum texto extra de "DOURADO"; o destaque é só visual, no desenhar()
        self.eh_bonus = True

    # MÉTODO: desenhar (POLIMORFISMO)
    # Sobrescreve o desenhar() do pai: desenha um fundo amarelo
    # simples, do tamanho exato da imagem (sem borda grossa nem
    # caixa "flutuando" por fora), e por cima chama o desenhar()
    # original do pai para reaproveitar o código de imagem/nome.
    def desenhar(self, tela):
        fundo = self.area_colisao.inflate(8, 8)
        pygame.draw.rect(tela, DOURADO, fundo, border_radius=10)

        super().desenhar(tela)  # reaproveita o desenhar() da classe Lixo