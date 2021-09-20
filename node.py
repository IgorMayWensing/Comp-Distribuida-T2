from datetime import datetime
from threading import Thread
import random
import socket
import time
import sys

# Inicializações globais
isLeader = False
leader = -1
isParticipant = False
pid = int(sys.argv[1])
print('Processo PID: ' + sys.argv[1])
dest = ('localhost', (pid + 1) % 5 + 9000)
r = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
r.bind(('0.0.0.0', pid))
r.listen(1)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# Mostra informações sobre a eleição
def show_info():
    print('----------------------')
    print('Leader: ' + str(leader))
    print('isLeader: ' + str(isLeader))
    print('isParticipant: ' + str(isParticipant))
    print('----------------------')


# Encontra o próximo nodo sem falha para completar o anel
def find_node():
    global dest
    global s
    attempt = 3

    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(dest)
            print("Anel restaurado")
            break
        except ConnectionRefusedError:
            if attempt == 0:
                attempt = 3
                dest = ('localhost', (dest[1] + 1) % 5 + 9000)
            else:
                time.sleep(1)
                attempt -= 1


# Envia uma mensagem para o próximo nodo
def send_message(msg):
    try:
        s.sendall(msg.encode('UTF-8'))
    except BrokenPipeError:
        s.close()
        find_node()


# Sempre escuta por mensagens
# Trata as requisições feitas pelos nodos
# Dicionário de requisições:
# hc: healthcheck
# hl: have leader?
# el: election
# r2: round 2
def listen():
    global isParticipant
    global isLeader
    global leader
    global dest

    while True:
        con, _ = r.accept()
        while True:
            data = con.recv(1024)
            if len(data) == 0:
                con.close()
                break
            res = data.decode('UTF-8')
            op = res.split(' ')

            if op[0] != 'hc':
                print('Mensagem recebida: ' + res)
            if op[0] == 'hl':
                if not isLeader:
                    if pid != int(op[1]):
                        send_message(res)
                    else:
                        print("MEU DEUS, O LÍDER MORREU!")
                        isParticipant = True
                        send_message('el ' + str(pid) + ' ' + str(pid))
                        print("Nova eleição iniciada")
            elif op[0] == 'el':
                # Round 1
                if int(op[2]) == pid:
                    leader = int(op[1])
                    isParticipant = False
                    if leader == pid:
                        isLeader = True
                    send_message('r2 ' + op[1] + ' ' + str(pid))
                    show_info()
                elif int(op[1]) > pid:
                    isParticipant = True
                    send_message(res)
                    print("Definindo novo potencial líder")
                elif int(op[1]) < pid and not isParticipant:
                    isParticipant = True
                    send_message('el ' + str(pid) + ' ' + op[2])
                    print("Propagando pontencial líder")
            elif op[0] == 'r2' and int(op[2]) != pid:
                # Round 2
                leader = int(op[1])
                isParticipant = False
                if leader == pid:
                    isLeader = True
                send_message(res)
                show_info()


# Envia healthchecks a cada 5 segundos
# e tem 10% de chance de verificar se o líder está online
def send_periodically():
    while True:
        time.sleep(5)
        random.seed(datetime.now())
        if not isLeader and random.random() < 0.10:
            send_message('hl ' + str(pid))
            print("Procurando líder...")
        else:
            send_message('hc')


# Instaura o anel e executa as duas threads
def main():
    find_node()
    Thread(target=listen).start()
    Thread(target=send_periodically).start()


if __name__ == "__main__":
    main()
