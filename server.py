import socket
import threading

# Configurações do servidor
SERVER_HOST = '192.168.0.113'
SERVER_PORT = 65432
ADDRESS = (SERVER_HOST, SERVER_PORT)
BUFFER_SIZE = 1024


# Estado inicial do tabuleiro (8x8) com peças iniciais
board = [[' ' for _ in range(8)] for _ in range(8)]
board[3][3] = 'W'
board[3][4] = 'B'
board[4][3] = 'B'
board[4][4] = 'W'

# Lista de clientes conectados e jogadores
clients = []
players = {}
current_turn = 'B'  # 'B' para preto, 'W' para branco

# Função para enviar o estado do tabuleiro para todos os clientes
def broadcast_board():
    for client in clients:
        try:
            client.sendall(f"BOARD:{str(board)}".encode())
        except:
            clients.remove(client)
            client.close()

# Função para enviar uma mensagem para todos os clientes
def broadcast_message(message):
    for client in clients:
        try:
            client.sendall(f"MSG:{message}".encode())
        except:
            clients.remove(client)
            client.close()

# Função para validar uma jogada
def is_valid_move(x, y, color):
    if board[y][x] != ' ':
        return False
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    valid = False
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        pieces_to_flip = []
        while 0 <= nx < 8 and 0 <= ny < 8 and board[ny][nx] != ' ' and board[ny][nx] != color:
            pieces_to_flip.append((nx, ny))
            nx += dx
            ny += dy
        if 0 <= nx < 8 and 0 <= ny < 8 and board[ny][nx] == color and pieces_to_flip:
            valid = True
            break
    return valid

# Função para executar uma jogada
def make_move(x, y, color):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    board[y][x] = color
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        pieces_to_flip = []
        while 0 <= nx < 8 and 0 <= ny < 8 and board[ny][nx] != ' ' and board[ny][nx] != color:
            pieces_to_flip.append((nx, ny))
            nx += dx
            ny += dy
        if 0 <= nx < 8 and 0 <= ny < 8 and board[ny][nx] == color:
            for fx, fy in pieces_to_flip:
                board[fy][fx] = color

# Função para verificar se um jogador tem jogadas válidas
def has_valid_moves(color):
    for y in range(8):
        for x in range(8):
            if is_valid_move(x, y, color):
                return True
    return False

# Função para lidar com um cliente
def handle_client(client_socket, player_color):
    global current_turn
    client_socket.sendall(f"BOARD:{str(board)}".encode())
    while True:
        try:
            message = client_socket.recv(BUFFER_SIZE).decode()
            if not message:
                break

            if message.startswith("MOVE:"):
                x, y = map(int, message[5:].split(','))
                if current_turn == player_color and is_valid_move(x, y, player_color):
                    make_move(x, y, player_color)
                    current_turn = 'W' if current_turn == 'B' else 'B'
                    broadcast_board()
                    broadcast_message(f"Player {player_color} made a move.")
                else:
                    client_socket.sendall("MSG:Invalid move or not your turn.".encode())
            elif message.startswith("CHAT:"):
                broadcast_message(f"Player {player_color}: {message[5:]}")
            elif message.startswith("QUIT:"):
                broadcast_message(f"Player {player_color} has quit the game.")
                client_socket.close()
                clients.remove(client_socket)
                break

        except Exception as e:
            print(f"Erro: {e}")
            clients.remove(client_socket)
            client_socket.close()
            break

# Configuração do socket do servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(ADDRESS)
server_socket.listen(2)

print(f"Servidor iniciado em {SERVER_HOST}:{SERVER_PORT}")

# Aceitar conexões dos clientes
while len(clients) < 2:
    client_socket, client_address = server_socket.accept()
    clients.append(client_socket)
    player_color = 'B' if len(clients) == 1 else 'W'
    players[client_socket] = player_color
    client_socket.sendall(f"MSG:You are player {player_color}".encode())
    client_socket.sendall(f"BOARD:{str(board)}".encode())

    broadcast_board() 

    print(f"Conexão aceita de {client_address}, atribuído ao jogador {player_color}")
    # Criar uma nova thread para lidar com o cliente
    thread = threading.Thread(target=handle_client, args=(client_socket, player_color))
    thread.start()

# Fechar o socket do servidor
server_socket.close()