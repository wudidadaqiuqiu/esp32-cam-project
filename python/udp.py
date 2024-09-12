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

def reset_buf(data):
    global recv_buffer, numdiv
    numdiv[0] = int.from_bytes(data[0:4], byteorder='little')
    numdiv[1] = int.from_bytes(data[5:9], byteorder='little')
    recv_buffer = [[] for _ in range(numdiv[1])]
    # print(numdiv[0], numdiv[1])
    # print(recv_buffer)

def udp_receive(sock):
    while True:
        data, address = sock.recvfrom(4096)
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

# 绑定到本地地址以接收数据
udp_socket.bind(('0.0.0.0', 3333))

# 设置目标地址（用于发送）
server_address = ('10.250.243.217', 3333)

# 创建发送和接收的线程
send_thread = threading.Thread(target=udp_send, args=(udp_socket, server_address))
receive_thread = threading.Thread(target=udp_receive, args=(udp_socket,))
# process_thread = threading.Thread(target=recv_process)
# 启动线程
send_thread.start()
receive_thread.start()
# process_thread.start()

# 等待线程结束
send_thread.join()
receive_thread.join()
# process_thread.join()
