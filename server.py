import socket
import threading

server_ip = '127.0.0.1'  # Endereço IP do servidor
server_port = 9999  # Porta do servidor

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Cria um socket UDP
server_socket.bind((server_ip, server_port))  # Vincula o socket ao endereço e à porta do servidor
dufgygs
clients = []

def receber_mensagens(client_socket, client_address):
    while True:
        try:
            data = client_socket.recv(1024)  # Recebe dados do cliente
            if not data:
                break
            print(f"Cliente {client_address}: {data.decode('utf-8')}")
            
            # Enviar mensagem recebida para todos os clientes conectados (exceto para o remetente)
            enviar_para_outros(client_socket, data, client_address)
        except ConnectionResetError:
            break


def enviar_para_outros(sender_socket, message, sender_address):
    for client in clients:
        if client != sender_socket:
            try:
                client.sendto(message, sender_address)
            except ConnectionResetError:
                clients.remove(client)


while True:
    client_data, client_address = server_socket.recvfrom(1024)  # Recebe dados e endereço do cliente
    print(f"Conexão estabelecida com {client_address}")
    
    # Adiciona o novo cliente à lista de clientes
    clients.append(client_address)
    
    # Inicia uma thread para receber mensagens do cliente
    receive_thread = threading.Thread(target=receber_mensagens, args=(server_socket, client_address))
    receive_thread.start()
