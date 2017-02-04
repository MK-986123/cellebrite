from Mits.Connections.IConnection import IConnection
class IFramer(IConnection):
    name = "Null"
    def __init__(self, base):
    def connect(self):
    def close(self):
    def send(self, data):
    def recv(self, num_bytes = 1024):
    def recv_no_wait(self, num_bytes = 1024):
    def recv_wait(self, num_bytes = 1024, timeout = 10):
    #do not overload this function - so you can send raw data
    #do not overload this function - so you can send raw data
    def set_timeout(self, timeout):
    def get_timeout(self):
    def flush(self):
    #serial functions
    def set_baudrate(self, baud):
    def set_dtr(self, n):
    def set_rts(self, n):
    def set_byte_size(self, n):
    #usb functions
    def clear_halt(self, endpoint):