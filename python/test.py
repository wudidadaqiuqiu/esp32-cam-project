# import socket

# udp_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# udp_socket2.bind(('0.0.0.0', 3334))

# udp_socket2.listen(100)
# connection, client_address = udp_socket2.accept()

# while True:
#     data = connection.recv(1024)
#     print(data)

a = b'aaa||'
b = a.split(b'||||')
print(len(b))