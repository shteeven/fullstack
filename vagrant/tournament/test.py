__author__ = 'Shtav'
import socket


# create an INET, STREAMing socket
serversocket = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a public host,
# and a well-known port
serversocket.bind(('localhost', 5432))
#become a server socket
serversocket.listen(5)