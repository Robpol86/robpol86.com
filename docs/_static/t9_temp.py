# Basic operations for MAX77818

from smbus2 import SMBus


bus = SMBus(1)


class MAX77818:
    def __init__(self, top=0x66, chg=0x69, fg=0x36):
        try:
            bus.write_byte(0x36, 0x0)
            self.connected = True
        except IOError:
            self.connected = False
        if (self.read(0xbd) & 0xC >> 2) == 3:
            self.unlocked = True
            print("Self.unlocked = {}".format(self.unlocked))
        else:
            self.unlocked = False
        self.top = top
        self.chg = chg
        self.fg = fg

    @staticmethod
    def read(reg_address, length=1, slave=0x69):
        if length == 1:
            return bus.read_byte_data(slave, reg_address)
        else:
            return bus.read_i2c_block_data(slave, reg_address, length)

    @staticmethod
    def write(address, data, length=1, slave=0x69):
        if (length == 1) or (type(data) is not list):
            bus.write_byte_data(slave, address, data)
        else:
            bus.write_i2c_block_data(slave, address, data)

    def set_mode(self, mode):
        chg_cnfg_00 = self.read(0xb7)
        self.write(0xb7, (chg_cnfg_00 & 0xF0) | min(0xF, mode))

    def show_chg_details(self):
        dtls0 = self.read(0xb3)
        dtls1 = self.read(0xb4)
        dtls2 = self.read(0xb5)
        if dtls0 & 0x60 == 0x60:
            print("MAX77818 VBUS Valid")
        if dtls0 & 0x1 == 1:
            print("MAX77818 BATT Presence detected")

        print("CHG_DTLS = " + "   ".join(map(hex, [dtls0, dtls1, dtls2])))

    def get_chg_stat(self):
        data = self.read(0xb4)
        return data & 0xF
