from threading import Thread
import random
import socket
import time
import sys

isLeader = False
pid = int(sys.argv[1])
print('Processo PID: ' + sys.argv[1])
dest = ('localhost', (pid + 1) % 5 + 9000)
r = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
r.bind(('0.0.0.0', pid))
r.listen(1)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if len(sys.argv) >= 3:
    if sys.argv[2] == 'lider':
        isLeader = True
        print('Sou o primeiro LÍDER')


def find_node():
    global dest
    global s
    attempt = 3
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(dest)
            break
        except ConnectionRefusedError:
            if attempt == 0:
                attempt = 3
                dest = ('localhost', (dest[1] + 1) % 5 + 9000)
            else:
                time.sleep(5)
                attempt -= 1


def listen():
    global dest
    while True:
        con, _ = r.accept()
        while True:
            data = con.recv(1024)
            if len(data) == 0:
                con.close()
                break
            res = data.decode('UTF-8')
            print(res)
            op = res.split(' ')
            if op[0] == 'hl':
                if not isLeader:
                    if str(pid) != op[1]:
                        try:
                            s.sendall(data)
                            print("PROPAGUEI")
                        except BrokenPipeError:
                            s.close()
                            find_node()
                    else:
                        print("VOTO IMPRESSO JÁ!")
                        # eleição


def send_periodically():
    while True:
        time.sleep(10)
        if random.random() < 0.10:
            try:
                s.sendall(('hl ' + str(pid)).encode('UTF-8'))
                print("ENVIEI")
            except BrokenPipeError:
                s.close()
                find_node()


def main():
    find_node()
    Thread(target=listen).start()
    Thread(target=send_periodically).start()


if __name__ == "__main__":
    main()
