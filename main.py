import pygame
import random
import time
import sqlite3

# Inicializar o pygame
pygame.init()

# Definir as dimensões da tela
LARGURA = 800
ALTURA = 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo de Adivinhação")

# Definir as cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
VERDE = (0, 255, 0)
AMARELO = (255, 255, 0)
VERMELHO = (255, 0, 0)

# Fonte para o texto
fonte = pygame.font.SysFont(None, 50)
fonte_menor = pygame.font.SysFont(None, 30)

# Função para desenhar o texto na tela
def desenhar_texto(texto, cor, x, y, fonte):
    imagem = fonte.render(texto, True, cor)
    tela.blit(imagem, (x, y))

# Função para exibir a tela inicial
def tela_inicial():
    tela.fill(PRETO)
    desenhar_texto("Jogo de Adivinhação!", BRANCO, LARGURA//4, ALTURA//3, fonte)
    desenhar_texto("Pressione Enter para começar", BRANCO, LARGURA//4, ALTURA//2, fonte_menor)
    pygame.display.update()

    espera = True
    while espera:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                quit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:  # Pressionou Enter
                    espera = False

# Função para dar dicas de quão perto ou longe o jogador está
def dar_dica(numero_secreto, numero_digitado, min_num, max_num):
    diferenca = abs(numero_secreto - numero_digitado)

    if diferenca == 0:
        return "Você acertou!", VERDE

    # Dicas de proximidade
    if diferenca <= 5:
        return f"Você está muito perto! O número secreto é {'menor' if numero_digitado > numero_secreto else 'maior'} que o seu palpite.", VERDE
    elif diferenca <= 10:
        return f"Você está perto! O número secreto é {'menor' if numero_digitado > numero_secreto else 'maior'} que o seu palpite.", AMARELO
    elif diferenca <= 20:
        return f"Você está um pouco longe! O número secreto é {'menor' if numero_digitado > numero_secreto else 'maior'} que o seu palpite.", AMARELO
    else:
        # Dica de faixa: Quando a diferença é muito grande
        return f"Você está muito longe! O número secreto está entre {min_num} e {max_num}.", VERMELHO

# Função para jogar uma fase
def jogar_fase(fase, nome_jogador, numero_secreto):
    tentativas = 2  # Limite fixo de 2 tentativas por fase
    max_numero = 50 + fase * 20  # Limite do número aumenta a cada fase
    min_numero = 1
    pontos = 0
    acertou = False  # Variável para saber se acertou em alguma fase

    while tentativas > 0:
        tela.fill(PRETO)
        desenhar_texto(f"Fase {fase} - Adivinhe o número!", BRANCO, 100, 100, fonte)
        desenhar_texto(f"Tentativas restantes: {tentativas}", BRANCO, 100, 200, fonte_menor)

        pygame.display.update()

        # Esperar o jogador digitar um número
        numero_digitado = None
        texto_digitado = ""
        while numero_digitado is None:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_BACKSPACE:
                        texto_digitado = texto_digitado[:-1]
                    elif evento.key == pygame.K_RETURN:
                        if texto_digitado.isdigit():
                            numero_digitado = int(texto_digitado)
                    else:
                        texto_digitado += evento.unicode

            tela.fill(PRETO)
            desenhar_texto(f"Fase {fase} - Adivinhe o número!", BRANCO, 100, 100, fonte)
            desenhar_texto(f"Tentativas restantes: {tentativas}", BRANCO, 100, 200, fonte_menor)
            desenhar_texto(f"Digite o número: {texto_digitado}", BRANCO, 100, 250, fonte)

            pygame.display.update()

        # Verificar se o jogador acertou
        if numero_digitado == numero_secreto:
            pontos += 10  # Ganha pontos ao acertar
            acertou = True
            break  # Não precisa continuar a fase se acertar

        tentativas -= 1

    # Exibir dica após cada fase (independente de ter acertado ou não)
    dica, cor_dica = dar_dica(numero_secreto, numero_digitado, min_numero, max_numero)
    tela.fill(PRETO)
    desenhar_texto(f"Fase {fase} - O número secreto era {numero_secreto}", BRANCO, 100, 100, fonte)
    desenhar_texto(dica, cor_dica, 100, 200, fonte_menor)
    pygame.display.update()
    time.sleep(2)

    if not acertou:
        pontos = 0  # Se não acertou em nenhuma fase, zera os pontos

    return pontos

# Função para criar ou conectar ao banco de dados SQLite
def conectar_banco():
    conn = sqlite3.connect("ranking.db")  # Banco de dados persistente
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS ranking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT,
                    pontos INTEGER)''')
    conn.commit()
    return conn, c

# Função para salvar a pontuação no banco de dados
def salvar_ranking(nome_jogador, pontos):
    conn, c = conectar_banco()
    c.execute("INSERT INTO ranking (nome, pontos) VALUES (?, ?)", (nome_jogador, pontos))
    conn.commit()
    conn.close()

# Função para exibir o ranking
def exibir_ranking():
    conn, c = conectar_banco()
    c.execute("SELECT nome, pontos FROM ranking ORDER BY pontos DESC LIMIT 5")
    ranking = c.fetchall()
    tela.fill(PRETO)
    desenhar_texto("Ranking:", BRANCO, 100, 100, fonte)
    y = 200
    for i, (nome, pontos) in enumerate(ranking):
        desenhar_texto(f"{i+1}. {nome} - {pontos} pontos", BRANCO, 100, y, fonte_menor)
        y += 50
    pygame.display.update()
    time.sleep(3)
    conn.close()

# Função para obter o nome do jogador
def obter_nome_jogador():
    texto_digitado = ""
    nome_jogador = None
    while nome_jogador is None:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                quit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_BACKSPACE:
                    texto_digitado = texto_digitado[:-1]
                elif evento.key == pygame.K_RETURN:
                    if texto_digitado.strip():
                        nome_jogador = texto_digitado
                else:
                    texto_digitado += evento.unicode

        tela.fill(PRETO)
        desenhar_texto("Digite seu nome:", BRANCO, 100, 100, fonte)
        desenhar_texto(f"Nome: {texto_digitado}", BRANCO, 100, 200, fonte)
        pygame.display.update()

    return nome_jogador

# Função principal
def game():
    tela_inicial()

    nome_jogador = obter_nome_jogador()

    # Gerar o número secreto uma única vez, na fase 1
    numero_secreto = random.randint(1, 50)  # Número secreto gerado na fase 1

    pontos_totais = 0
    for fase in range(1, 4):  # Três fases
        pontos_totais += jogar_fase(fase, nome_jogador, numero_secreto)

    # Se o jogador não acertou, pontuação será zerada
    if pontos_totais == 0:
        salvar_ranking(nome_jogador, 0)  # Armazena no banco com 0 pontos
    else:
        salvar_ranking(nome_jogador, pontos_totais)
    
    # Exibir o ranking
    exibir_ranking()
    
    # Finalizar o jogo
    pygame.quit()
    quit()

if __name__ == "__main__":
    game()
