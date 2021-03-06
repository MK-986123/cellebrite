"""
MMC     Dumper


Written By: Nir Zaltsman
23/08/11
"""


from IDumper import IDumper
from Mits.Utils.General import timed_xrange, get_dump_path


import time


class DumperMMC(IDumper):
    name = "MMC"
    def _dump_ram(self, start_address, end_address, blocks_per_read):
        step = self.block_size*blocks_per_read
        err_loop = 0
        # div and mul by 2 to support addresses > 0x7FFFFFFF
        for block_addr in xrange(start_address >> 1, end_address >> 1, step >> 1):
            while (True):
                try:
                    self.write_to_output(self.protocol.dump_ram(block_addr << 1, step))
                    err_loop = 0
                    break
                except KeyboardInterrupt, e:
                    raise e
                except Exception, e:
                    err_loop += 1
                    print "Error occured (dump_ram): %s" % repr(e)
                    if (err_loop > 10):
                        raise e


    def dump(self, start_block = 0 , end_block=None, ram_address=0x56C00000, chunk_size=20480, blocks_per_read=256, hw_version = 0, name=""):
        """
        Dump mmc using ram mapping
        """
        block_count, block_size = self.protocol.mmc_init(hw_version)
        self.block_size = block_size
        if (end_block == None):
            end_block = block_count
        self.open_output(name, "MMC", start_block, end_block)
        err_loop = 0
        try:
            current_block = 0
            blocks_step = chunk_size
            # factor chunk size is used to show the correct Kbps
            timed_xrange_addr = timed_xrange(start_block*block_size, end_block*block_size, blocks_step*block_size)
            while True :
                num_of_blocks_to_read = min(chunk_size, end_block - current_block, blocks_step)
                # iterate the timed_xrange
                if num_of_blocks_to_read == 0 :
                    try :
                        blocks_step = chunk_size
                        timed_xrange_addr.next()
                        continue
                    except StopIteration, e :
                        print "Dump end !"
                        break
                actual_block_read = self.protocol.mmc_read(current_block, num_of_blocks_to_read, ram_address)
                # backward compatible - when the btl return 0 --> success
                if (0 == actual_block_read):
                    actual_block_read = num_of_blocks_to_read
                elif (0 > actual_block_read): # new btl - returns the number of blocks read
                    raise Exception("mmc_read failed : result(%d) current_block (0x%x), block_size(0x%x)" % (actual_block_read, current_block, num_of_blocks_to_read))
                self._dump_ram(ram_address, ram_address+(actual_block_read * self.block_size), min(num_of_blocks_to_read,blocks_per_read))
                blocks_step -= actual_block_read
                current_block += actual_block_read
        except KeyboardInterrupt:
            print "User cancelled the dump"
            self.protocol.framer.flush()
            return


        finally:
            self.close_output()
