"""
"""
from Mits.Utils.SerialScan import WinScan

def get_serial_port():
    while(True):
        ports = WinScan().comports()
        print "\t" + "\r\n\t".join(ports_txt)
        except SyntaxError, e:
    return port