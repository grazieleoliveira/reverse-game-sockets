import socket
import threading
import pygame
import constants as CONSTANTS
from pygame_setup import pygame_setup

# Configurações do cliente
SERVER_HOST = '192.168.0.113'
SERVER_PORT = 65432
BUFFER_SIZE = 1024

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))

window, font = pygame_setup()
square_size = CONSTANTS.WIDTH // 8
pieces = []
messages = []  # Store messages for display in chat
player_color = None
input_text = ''  # Store player's typed message

RESIGN_BUTTON = pygame.Rect(10, 550, 100, 30)  # Position (10, 550) and size (100x30)


def draw_initial_pieces():
    pieces.extend([(3, 3, CONSTANTS.WHITE), (3, 4, CONSTANTS.BLACK), (4, 3, CONSTANTS.BLACK), (4, 4, CONSTANTS.WHITE)])


def draw_board():
    window.fill(CONSTANTS.WHITE)
    # Draw board
    for row in range(8):
        for col in range(8):
            square_rect = pygame.Rect(col * square_size, row * square_size, square_size, square_size)
            pygame.draw.rect(window, CONSTANTS.GREEN, square_rect)
            pygame.draw.rect(window, CONSTANTS.WHITE, square_rect, 2)

    # Draw pieces
    for piece in pieces:
        draw_piece(piece[0], piece[1], piece[2])

    # Draw chat area below the board
    chat_area_start = 410  # Start drawing chat below the board
    chat_height = 20
    for idx, msg in enumerate(messages[-8:]):  # Show only last 8 messages
        text_surface = font.render(msg, True, CONSTANTS.BLACK)
        window.blit(text_surface, (10, chat_area_start + idx * chat_height))

    # Draw the typing text line
    typing_surface = font.render(input_text, True, CONSTANTS.BLACK)
    window.blit(typing_surface, (10, chat_area_start + len(messages[-8:]) * chat_height))

    window.fill(CONSTANTS.WHITE)
    # Draw board and pieces
    for row in range(8):
        for col in range(8):
            square_rect = pygame.Rect(col * square_size, row * square_size, square_size, square_size)
            pygame.draw.rect(window, CONSTANTS.GREEN, square_rect)
            pygame.draw.rect(window, CONSTANTS.WHITE, square_rect, 2)

    for piece in pieces:
        draw_piece(piece[0], piece[1], piece[2])

    # Draw chat area
    chat_area_start = 410
    chat_height = 20
    for idx, msg in enumerate(messages[-8:]):  # Last 8 messages
        text_surface = font.render(msg, True, CONSTANTS.BLACK)
        window.blit(text_surface, (10, chat_area_start + idx * chat_height))

    # Draw input box
    input_box = pygame.Rect(10, 600, CONSTANTS.WIDTH - 20, 30)
    pygame.draw.rect(window, CONSTANTS.GRAY, input_box)
    text_surface = font.render(input_text, True, CONSTANTS.BLACK)
    window.blit(text_surface, (input_box.x + 5, input_box.y + 5))

    pygame.draw.rect(window, CONSTANTS.RED, RESIGN_BUTTON)
    button_text = font.render("Resign", True, CONSTANTS.WHITE)
    window.blit(button_text, (RESIGN_BUTTON.x + 10, RESIGN_BUTTON.y + 5))


def draw_piece(square_col, square_row, color):
    center_x = square_col * square_size + square_size // 2
    center_y = square_row * square_size + square_size // 2
    pygame.draw.circle(window, color, (center_x, center_y), 20)

def update_board(board_state):
    global pieces
    pieces = []
    for row in range(8):
        for col in range(8):
            if board_state[row][col] == 'W':
                pieces.append((col, row, CONSTANTS.WHITE))
            elif board_state[row][col] == 'B':
                pieces.append((col, row, CONSTANTS.BLACK))

def receive_updates():
    global player_color
    while True:
        try:
            message = client_socket.recv(BUFFER_SIZE).decode()
            if message.startswith("BOARD:"):
                update_board(eval(message[6:]))  # Board update (internal)
            elif message.startswith("MSG:"):
                msg_content = message[4:]
                if "You are player" in msg_content:
                    player_color = msg_content[-1]
                messages.append(msg_content)  # Display only external messages
        except Exception as e:
            print(f"Error: {e}")
            client_socket.close()
            break

thread = threading.Thread(target=receive_updates)
thread.start()

draw_initial_pieces()
running = True
while running:
    chat_area_y_start = 410  # Chat area starts at y=410

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            client_socket.sendall("QUIT:".encode())
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and player_color:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
        # Check if the resign button is clicked
            if RESIGN_BUTTON.collidepoint(mouse_x, mouse_y):
                client_socket.sendall("RESIGN:".encode())
            else:
                clicked_col = mouse_x // square_size
                clicked_row = mouse_y // square_size
                
                # Check if the click is within the game board (e.g., 8x8 grid)
                if 0 <= clicked_col < 8 and 0 <= clicked_row < 8:
                    if mouse_y < 400:  # Ignore clicks in the chat area
                        client_socket.sendall(f"MOVE:{clicked_col},{clicked_row}".encode())
                else:
                    print("Click is outside the board.")
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                client_socket.sendall(f"CHAT:{input_text}".encode())
                messages.append(f"You: {input_text}")
                input_text = ''
            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                input_text += event.unicode

    window.fill(CONSTANTS.WHITE)
    draw_board()

    pygame.display.update()

pygame.quit()