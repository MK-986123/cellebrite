import socket
from Mits.Connections import IConnection
class ConnectionSocket(IConnection.IConnection):
        if to_open_connection==True:
    def __del__(self):
    def __repr__(self):
    def get_port(self):
    def connect(self, blocking=False):
    def close(self):

    def send(self, data):
    def recv(self, num_bytes = 1024):

    def get_timeout(self):
    