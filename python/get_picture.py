import socket
import threading
import time
import cv2
import numpy as np
import queue

import rc4

key = b'12345678'
r = rc4.RC4()
r.reset(key)

q = queue.Queue()
recv_buffer2 = b''
recv_queue = queue.Queue()

# SOCK_STREAM:TCP
udp_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

udp_socket2.bind(('0.0.0.0', 3334))
udp_socket2.listen(1)

# socket._Address
# 设置目标地址（用于发送）
# server_address = ('10.250.243.217', 3333)

def get_pic(sock: socket.socket):
    global recv_buffer2, recv_queue,q
    connection, client_address = sock.accept()
    while True:
        data = connection.recv(4096)
        if not data: 
            continue
        assert(type(data) == bytes)
        recv_buffer2 += data
        temp = recv_buffer2.split(b'||||||||||')
        for i in range(len(temp)):
            if (i == len(temp) - 1):
                recv_buffer2 = temp[i]
                break
            if i != b'':
                recv_queue.put(temp[i])
        while not recv_queue.empty() and recv_queue.qsize() % 2 == 0:
            f = recv_queue.get()
            l = recv_queue.get()
            if int.from_bytes(l, byteorder='little') == len(f):
                q.put([f])
                print("f len: " + str(len(f)))
            else:
                print("f len: " + str(len(f)) + "  len: " + str(int.from_bytes(l, byteorder='little')))
                print("data length error")
            if not q.empty():
                connection.close()
                return


def recv_process():
    while True:
        if (not q.empty()):
            img, bin = get_byte(q.get())
            if img is not None:
                with open('img.jpg', "wb") as f:
                    f.write(img)
                with open('bin.bin', "wb") as f:
                    f.write(bin)
                return
                # cv2.imshow('img', img)
                # cv2.waitKey(1)
            else:
                print("img is None")
        # time.sleep(0.001)

def get_byte(recv_buffer: list[list[bytes]]):
    # 处理接收到的数据
    b = b''
    # print(type(recv_buffer[0]))
    for a in recv_buffer:
        b += a
    return r.crypt(b), b


get_pic(udp_socket2)
recv_process()
udp_socket2.close()