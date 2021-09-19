from threading import Thread
from datetime import datetime
import random
import socket
import time
import sys

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


def listen():
    global dest
    global isLeader
    global isParticipant
    global leader
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
                    if str(pid) != op[1]:
                        try:
                            s.sendall(data)
                        except BrokenPipeError:
                            s.close()
                            find_node()
                    else:
                        print("MEU DEUS, O LÍDER MORREU!")
                        # eleição
                        isParticipant = True
                        try:
                            s.sendall(('el '+ str(pid) + ' ' + str(pid)).encode('UTF-8'))
                            print("Nova eleição iniciada")
                        except BrokenPipeError:
                            s.close()
                            find_node()
            elif op[0] == 'el':  
                if op[2] == str(pid):
                    leader = int(op[1])
                    isParticipant = False
                    if leader == pid:
                        isLeader = True
                    try:
                        s.sendall(('r2 '+ op[1] + ' ' + str(pid)).encode('UTF-8'))
                        print("Iniciando round 2")
                        print('----------------------')
                        print('Leader: ' + str(leader))
                        print('isLeader: ' + str(isLeader))
                        print('isParticipant:' + str(isParticipant))
                        print('----------------------')
                    except BrokenPipeError:
                        s.close()
                        find_node()                           
                elif op[1] > str(pid):
                    isParticipant = True
                    try:
                        s.sendall(data)
                        print("Definindo novo potencial líder")
                    except BrokenPipeError:
                        s.close()
                        find_node()
                elif op[1] < str(pid) and not isParticipant:
                    isParticipant = True
                    try:
                        s.sendall(('el '+ str(pid) + ' ' + op[2]).encode('UTF-8'))
                        print("Propagando pontencial líder")
                    except BrokenPipeError:
                        s.close()
                        find_node()
                
            elif op[0] == 'r2' and op[2] !=  str(pid):
                    leader = int(op[1])
                    isParticipant = False
                    if leader == pid:
                        isLeader = True
                    try:
                        s.sendall(data)
                        print('----------------------')
                        print('Leader: ' + str(leader))
                        print('isLeader :' + str(isLeader))
                        print('isParticipant :' + str(isParticipant))
                        print('----------------------')
                    except BrokenPipeError:
                        s.close()
                        find_node()


def send_periodically():
    while True:
        time.sleep(5)
        random.seed(datetime.now())
        if not isLeader and random.random() < 0.10:
            try:
                s.sendall(('hl ' + str(pid)).encode('UTF-8'))
                print("Procurando lider...")
            except BrokenPipeError:
                s.close()
                find_node()
        else:
            try:
                s.sendall('hc'.encode('UTF-8'))
            except BrokenPipeError:
                s.close()
                find_node()


def main():
    find_node()
    Thread(target=listen).start()
    Thread(target=send_periodically).start()


if __name__ == "__main__":
    main()
