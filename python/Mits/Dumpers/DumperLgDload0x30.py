from IDumper import IDumper
from Mits.Utils.General import timed_xrange, get_dump_path
from Mits.Utils.upy import upy


"""
STEP_SIZE represents the number of blocks to read per iteration
 the maximum STEP_SIZE for this devices is 8, the bootloader validates it


"""


class DumperLgDload0x30(IDumper):    
    name = "DumperLgDload0x30"
    def __init__(self, protocol):
        super(DumperLgDload0x30, self).__init__(protocol)


    def dump(self, start, end, step, bytes_per_iteration):
        print "[+] Dump loop starts\n"
        # STEP_SIZE = 8 , each 8 steps we get 4kb data
        self.open_output('', "MMCx30", start, end)
        for i in timed_xrange(start, end, step, bytes_per_iteration/step):
            raw = self.protocol.read_mem(i, step, bytes_per_iteration)
            self.write_to_output(raw)
            if len(raw) < bytes_per_iteration :
                break
                
        upy.target_add_desc_set("ExtractionMethod", "ANDROID_ADB", "Image")
        self.close_output()
        print "[+] Dump loop ends\n"
        if float(i) / end > 0.85 :
            return 
        raise RuntimeError("Failed to read phone memory")
            
