
import time
from Mits.Utils.BinUtils    import hex_print
class log:
        self.__f = open(self.logname,"wb")
        self.__f.write("Log Started at: %s\r\n\r\n"%(time.ctime()))
    def __write(self, text, buffer, prefix):

    def text(self, text, prefix="DEBUG"):
    def buffer(self, buffer, prefix="DEBUG"):
    def text_buffer(self, text, buffer, prefix="DEBUG"):
    def close(self):