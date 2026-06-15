# ═══════════════════════════════════════════════════════════
# ARQUIVO: main.py
# Responsabilidade: porta de entrada do programa
# apenas cria o jogo e inicia o loop principal
# ═══════════════════════════════════════════════════════════

# importa a classe Jogo do arquivo models/jogo.py
from models.jogo import Jogo

# ───────────────────────────────────────────────────────────
# PONTO DE ENTRADA
# "__name__ == '__main__'" garante que o jogo só inicia
# quando este arquivo é executado diretamente
# e não quando é importado por outro arquivo
# ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    jogo = Jogo()  # cria o objeto jogo
    jogo.rodar()   # inicia o loop principal