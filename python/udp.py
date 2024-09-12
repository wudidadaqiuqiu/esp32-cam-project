import socket
import threading
import time
import cv2
import numpy as np
import queue

def udp_send(sock: socket.socket, server_address):
    while True:
        message = "vedioin".encode()
        # print("message:", message)
        # print("server_address: ", server_address)
        # print("sock: ", sock)
        sock.sendto(message, server_address)
        
        time.sleep(1)

q = queue.Queue()
recv_buffer, numdiv = [], [0, 0]
recv_buffer2 = b''
recv_queue = queue.Queue()
def reset_buf(data):
    global recv_buffer, numdiv
    numdiv[0] = int.from_bytes(data[0:4], byteorder='little')
    numdiv[1] = int.from_bytes(data[5:9], byteorder='little')
    recv_buffer = [[] for _ in range(numdiv[1])]
    # print(numdiv[0], numdiv[1])
    # print(recv_buffer)

def udp_receive2(sock):
    split_buffer = b''
    global recv_buffer2, recv_queue
    while True:
        print("wait for connection")
        connection, client_address = sock.accept()
        if not connection:
            print("wait for connection")
            continue
        else:
            print("connection accepted")
            break
    # connection, client_address = sock.accept()
    try:
        while True:
            # has_div = False
            data = connection.recv(4096)
            if not data: 
                continue
            assert(type(data) == bytes)
            # if len(t:=data.split(b'||||||||||')) == 1:
                
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
                # print(l)
                # print(len(l), len(f))
                if int.from_bytes(l, byteorder='little') == len(f):
                    q.put([f])
                    print("f len: " + str(len(f)))
                else:
                    print("f len: " + str(len(f)) + "  len: " + str(int.from_bytes(l, byteorder='little')))
                    print("data length error")
                    
            # if (data[-10:] == b'||||||||||' and data[-24:-14] == b'||||||||||'):
            #     if (int.from_bytes(data[-14:-10], byteorder='little') == len(recv_buffer2)-24):
            #         q.put([recv_buffer2[:-24]])
            #         print("recv_buffer2 len: " + str(len(recv_buffer2)))
            #     else:
            #         print(int.from_bytes(data[-14:-10], byteorder='little'), len(recv_buffer2)-24)
            #         print("data length error")

                recv_buffer2 = b''
    finally:
        connection.close()

def udp_receive(sock):
    while True:
        print("wait for connection")
        connection, client_address = sock.accept()
        if not connection:
            print("wait for connection")
            continue
        else:
            print("connection accepted")
            break
    try:
        while True:
            data = connection.recv(4096)
            if not data: 
                continue
            # print(f"Received {data} from {address}")
            # print(int.from_bytes(data[0:4], byteorder='little'), '/', int.from_bytes(data[5:9], byteorder='little'))
            if numdiv[0] == 0 and numdiv[1] == 0:
                reset_buf(data)
                # print("reset")
            # print(recv_buffer)
            if (numdiv[0] > int.from_bytes(data[0:4], byteorder='little')):
                if not [True for a in recv_buffer if not a]:
                    # complete jpg
                    q.put(recv_buffer)
                    print("complete jpg")
                else:
                    print("not complete jpg")
                reset_buf(data)
            elif numdiv[1] != int.from_bytes(data[5:9], byteorder='little'):
                # print("reset2")
                reset_buf(data)
            # print(numdiv[0], numdiv[1])
            # print(recv_buffer)
            numdiv[0] = int.from_bytes(data[0:4], byteorder='little')
            numdiv[1] = int.from_bytes(data[5:9], byteorder='little')
            recv_buffer[numdiv[0]] = data[9:]
    finally:
        connection.close()

def recv_process():
    while True:
        if (not q.empty()):
            img = recv_buf_process(q.get())
            if img is not None:
                cv2.imshow('img', img)
                cv2.waitKey(1)
            else:
                print("img is None")
        # time.sleep(0.001)
        
def recv_buf_process(recv_buffer: list[list[bytes]]):
    # 处理接收到的数据
    b = b''
    # print(type(recv_buffer[0]))
    for a in recv_buffer:
        b += a
    # 将jpg流转为NumPy数组
    nparr = np.frombuffer(b, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


# 创建 UDP 套接字
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# SOCK_STREAM:TCP
udp_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# hostname = socket.gethostname()  # 获取主机名
# local_ip = socket.gethostbyname(hostname)  # 获取本机 IP 地址
# print(local_ip)
# udp_socket2.accept()
# 绑定到本地地址以接收数据
udp_socket.bind(('0.0.0.0', 3333))
udp_socket2.bind(('0.0.0.0', 3334))
udp_socket2.listen(1)

# socket._Address
# 设置目标地址（用于发送）
server_address = ('10.250.243.217', 3333)

# 创建发送和接收的线程
send_thread = threading.Thread(target=udp_send, args=(udp_socket, server_address))
receive_thread = threading.Thread(target=udp_receive2, args=(udp_socket2,))
process_thread = threading.Thread(target=recv_process)
# 启动线程
send_thread.start()
receive_thread.start()
process_thread.start()

try:
    # 等待线程结束
    send_thread.join()
    receive_thread.join()
finally:
    # 关闭套接字
    udp_socket.close()
    udp_socket2.close()
    # process_thread.join()
process_thread.join()
