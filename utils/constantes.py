# ═══════════════════════════════════════════════════════════
# ARQUIVO: utils/constantes.py
# Responsabilidade: guardar todos os valores fixos do jogo
# ═══════════════════════════════════════════════════════════

import pygame

# ───────────────────────────────────────────────────────────
# TAMANHO DA TELA
# ───────────────────────────────────────────────────────────
LARGURA_TELA  = 800   # largura da janela em pixels
ALTURA_TELA   = 600   # altura da janela em pixels
LIMITE_FPS    = 60    # frames por segundo

# ───────────────────────────────────────────────────────────
# CORES — formato (Vermelho, Verde, Azul) de 0 a 255
# ───────────────────────────────────────────────────────────
BRANCO        = (255, 255, 255)  # textos claros / lixeira hospitalar
PRETO         = (0,   0,   0  )  # bordas e textos escuros / lixeira madeira
CINZA         = (140, 140, 140)  # botões neutros / lixeira não-reciclável
CINZA_ESCURO  = (100, 100, 100)  # textos secundários
AZUL_PAPEL    = (30,  144, 255)  # cor da lixeira de papel
VERMELHO_PLASTICO = (220, 50, 50)  # cor da lixeira de plástico
VERDE_VIDRO   = (34,  139, 34 )  # cor da lixeira de vidro
AMARELO_METAL = (255, 200, 0  )  # cor da lixeira de metal
VERDE_VIDA    = (0,   200, 80 )  # cor do ícone de vida
DOURADO       = (255, 215, 0  )  # cor de brilho do item bônus
MARROM_ORGANICO       = (101, 67,  33 )  # cor da lixeira de orgânico
ROXO_RADIOATIVO       = (128, 0,   128)  # cor da lixeira radioativo
LARANJA_PERIGOSO      = (255, 140, 0  )  # cor da lixeira de resíduos perigosos

# ───────────────────────────────────────────────────────────
# TIPOS DE LIXEIRA
# Fonte única de verdade: para adicionar uma lixeira nova no jogo
# só é preciso acrescentar uma linha aqui e os itens dela em
# Lixo.TIPOS_DE_LIXO (models/lixo.py) — o resto do jogo (botões,
# ícones de vida, telas) se ajusta automaticamente.
# As chaves abaixo seguem exatamente o nome dos arquivos de imagem
# que você tem: lixeira-{chave}.png
# ───────────────────────────────────────────────────────────
TIPOS_LIXEIRA = {
    "papel":               {"cor": AZUL_PAPEL,        "nome": "PAPEL"},
    "plastico":            {"cor": VERMELHO_PLASTICO, "nome": "PLASTICO"},
    "vidro":               {"cor": VERDE_VIDRO,       "nome": "VIDRO"},
    "metal":               {"cor": AMARELO_METAL,     "nome": "METAL"},
    "organico":            {"cor": MARROM_ORGANICO,   "nome": "ORGANICO"},
    "madeira":             {"cor": PRETO,             "nome": "MADEIRA"},
    "nao-reciclavel":      {"cor": CINZA,             "nome": "NAO RECICLAVEL"},
    "hospitalar":          {"cor": BRANCO,            "nome": "HOSPITALAR"},
    "radiotivo":           {"cor": ROXO_RADIOATIVO,   "nome": "RADIOATIVO"},
    "residuos-perigosos":  {"cor": LARANJA_PERIGOSO,  "nome": "PERIGOSOS"},
}

# ───────────────────────────────────────────────────────────
# IMAGEM COM RESERVA
# Tenta carregar uma imagem do disco; se o arquivo não existir
# (ex: ainda não há imagem para a lixeira de eletrônico), gera
# um ícone substituto colorido com a inicial do nome, para que
# o jogo nunca trave por falta de um arquivo de imagem.
#
# IMPORTANTE: a imagem real é redimensionada PRESERVANDO A
# PROPORÇÃO original (sem esticar) e depois centralizada numa
# superfície transparente do tamanho exato pedido (largura x
# altura). Isso evita que imagens retangulares (ex: a seringa,
# bem mais alta que larga) fiquem deformadas ao forçar para um
# tamanho quadrado — o resultado sempre cabe no espaço pedido
# sem distorcer o desenho original.
# ───────────────────────────────────────────────────────────
def carregar_imagem_ou_placeholder(caminho, largura, altura, cor=CINZA, texto="?", fonte=None):
    try:
        imagem = pygame.image.load(caminho).convert_alpha()

        # calcula o maior tamanho que cabe em (largura, altura)
        # mantendo a proporção original da imagem (letterbox)
        largura_original, altura_original = imagem.get_size()
        escala = min(largura / largura_original, altura / altura_original)
        nova_largura  = max(1, round(largura_original * escala))
        nova_altura   = max(1, round(altura_original  * escala))

        imagem_redimensionada = pygame.transform.smoothscale(imagem, (nova_largura, nova_altura))

        # cola a imagem redimensionada centralizada numa superfície
        # transparente do tamanho exato pedido — assim quem usa essa
        # função continua recebendo sempre um retângulo (largura x altura)
        # consistente para posicionamento e colisão, sem esticar o desenho
        superficie_final = pygame.Surface((largura, altura), pygame.SRCALPHA)
        pos_x = (largura - nova_largura) // 2
        pos_y = (altura  - nova_altura)  // 2
        superficie_final.blit(imagem_redimensionada, (pos_x, pos_y))

        return superficie_final
    except (pygame.error, FileNotFoundError):
        placeholder = pygame.Surface((largura, altura), pygame.SRCALPHA)
        pygame.draw.rect(placeholder, cor, placeholder.get_rect(), border_radius=12)
        pygame.draw.rect(placeholder, PRETO, placeholder.get_rect(), 3, border_radius=12)
        if fonte:
            letra = fonte.render(texto[:1].upper(), True, BRANCO)
            placeholder.blit(
                letra,
                (largura // 2 - letra.get_width() // 2, altura // 2 - letra.get_height() // 2)
            )
        return placeholder

# ───────────────────────────────────────────────────────────
# FONTES
# Ficam numa função pois só podem ser criadas
# depois do pygame.init() que está no jogo.py
# ───────────────────────────────────────────────────────────
def carregar_fontes():
    return {
        "titulo":  pygame.font.SysFont("Arial", 52, bold=True),  # título grande
        "media":   pygame.font.SysFont("Arial", 30, bold=True),  # textos médios
        "pequena": pygame.font.SysFont("Arial", 20)               # textos pequenos
    }