import socket
import threading
import pygame
import constants as CONSTANTS
from pygame_setup import pygame_setup

# Configurações do cliente
SERVER_HOST = '192.168.0.113'
SERVER_PORT = 65432
BUFFER_SIZE = 1024

# Conectar ao servidor
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))

# Configuração do Pygame
window, font = pygame_setup()
square_size = CONSTANTS.WIDTH // 8
pieces = []

# Variável para controlar a comunicação
messages = []
player_color = None

def draw_initial_pieces():
    pieces.append((3, 3, CONSTANTS.WHITE))
    pieces.append((3, 4, CONSTANTS.BLACK))
    pieces.append((4, 3, CONSTANTS.BLACK))
    pieces.append((4, 4, CONSTANTS.WHITE))

# Função para desenhar o tabuleiro
def draw_board():
    for row in range(8):
        for col in range(8):
            square_rect = pygame.Rect(col * square_size, row * square_size, square_size, square_size)
            pygame.draw.rect(window, CONSTANTS.GREEN, square_rect)
            pygame.draw.rect(window, CONSTANTS.WHITE, square_rect, 2)

# Função para desenhar uma peça
def draw_piece(square_col, square_row, color):
    center_x = square_col * square_size + square_size // 2
    center_y = square_row * square_size + square_size // 2
    pygame.draw.circle(window, color, (center_x, center_y), 20)

# Função para atualizar o tabuleiro a partir do estado recebido do servidor
def update_board(board_state):
    global pieces
    pieces = []
    for row in range(8):
        for col in range(8):
            if board_state[row][col] == 'W':
                pieces.append((col, row, CONSTANTS.WHITE))
            elif board_state[row][col] == 'B':
                pieces.append((col, row, CONSTANTS.BLACK))

# Função para receber atualizações do servidor
def receive_updates():
    global player_color
    while True:
        try:
            message = client_socket.recv(BUFFER_SIZE).decode()
            if message.startswith("BOARD:"):
                update_board(eval(message[6:]))
            elif message.startswith("MSG:"):
                messages.append(message[4:])
                print(message[4:])
                if "You are player" in message:
                    player_color = message[-1]
        except Exception as e:
            print(f"Erro: {e}")
            client_socket.close()
            break

# Thread para receber atualizações do servidor
thread = threading.Thread(target=receive_updates)
thread.start()

draw_initial_pieces()
# Loop principal do jogo
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            client_socket.sendall("QUIT:".encode())
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and player_color:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            clicked_col = mouse_x // square_size
            clicked_row = mouse_y // square_size
            client_socket.sendall(f"MOVE:{clicked_col},{clicked_row}".encode())
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                msg = input("Digite sua mensagem: ")
                client_socket.sendall(f"CHAT:{msg}".encode())

    window.fill(CONSTANTS.WHITE)
    draw_board()
    for piece in pieces:
        draw_piece(piece[0], piece[1], piece[2])
    pygame.display.update()

pygame.quit()