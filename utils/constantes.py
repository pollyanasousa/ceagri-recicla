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
BRANCO        = (255, 255, 255)  # textos claros
PRETO         = (0,   0,   0  )  # bordas e textos escuros
CINZA         = (180, 180, 180)  # botões neutros
CINZA_ESCURO  = (100, 100, 100)  # textos secundários
AZUL_PAPEL    = (30,  144, 255)  # cor da lixeira de papel
VERMELHO_PLASTICO = (220, 50, 50)  # cor da lixeira de plástico
VERDE_VIDRO   = (34,  139, 34 )  # cor da lixeira de vidro
AMARELO_METAL = (255, 200, 0  )  # cor da lixeira de metal
VERDE_VIDA    = (0,   200, 80 )  # cor do ícone de vida

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