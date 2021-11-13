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
        if (self.read(0xBD) & 0xC >> 2) == 3:
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

    @staticmethod
    def rw(reg, s=0x36):
        data = bus.read_word_data(s, reg)
        return data

    def set_lock(self, lock):
        lock_reg = self.read(0xBD)
        if lock in ["unlock", "Unlock", "U", "u", 0, True]:
            self.write(0xBD, (lock_reg & 0xF3) | 0xC)
            self.unlocked = True
        else:
            self.write(0xBD, lock_reg & 0xF3)
            self.unlocked = False

    def set_cv(self, voltage):
        # locks = self.unlocked
        # if not self.unlocked:
        self.set_lock("unlock")
        chg_cnfg_04 = self.read(0xBB)
        if type(voltage) is float or type(voltage) is int:
            if voltage < 4.33999:
                v = max(0, int(((voltage * 1000) - 3650) / 25))
            elif voltage < 4.34999:
                v = 0x1C
            else:
                v = min(0x2B, max(0x1D, 0x1D + int(((voltage * 1000) - 4350) / 25)))
        elif voltage in ["up", "Up", "UP", "u", "U"]:
            v = min((chg_cnfg_04 & 0x3F) + 1, 0x2B)
        elif voltage in ["d", "down", "Down", "D"]:
            v = max((chg_cnfg_04 & 0x3F) - 1, 0x0)
        else:
            v = min(0x2B, max(0, int(voltage, 16)))
        print("Voltage = {}, hex = {}".format(voltage, hex(v)))
        self.write(0xBB, (chg_cnfg_04 & 0xC0) | v)
        # self.set_lock(locks)

    def set_cc(self, curr):
        locks = self.unlocked
        if not self.unlocked:
            self.set_lock("unlock")
        chg_cnfg_02 = self.read(0xB9)
        if type(curr) is float or type(curr) is int:
            if curr < 4.0:  # Amps to mA
                curr = curr * 1000.0
            c = min(max(0, int(curr / 50)), 0x3F)
        else:
            try:
                curr = int(curr, 16)
                c = min(max(0, int(curr)), 0x3F)
            except IOError:
                print("Invalid CC value")
                return
        self.write(0xB9, ((chg_cnfg_02 & 0xC0) | c))
        self.set_lock(locks)

    def set_input_lim(self, curr):
        if type(curr) is float or type(curr) is int:
            if curr < 6.0:  # Amps to mA
                curr = curr * 1000.0
            c = min(max(0, int(curr / 33)), 0x7F)
        else:
            try:
                curr = int(curr, 16)
                c = min(max(0, int(curr)), 0x7F)
            except IOError:
                print("Invalid input current limit value")
                return
        # print("Current = {}     Reg = {}".format(curr, hex(c)))
        self.write(0xC0, c)

    def set_mode(self, mode):
        chg_cnfg_00 = self.read(0xB7)
        self.write(0xB7, (chg_cnfg_00 & 0xF0) | min(0xF, mode))

    def show_chg_details(self):
        dtls0 = self.read(0xB3)
        dtls1 = self.read(0xB4)
        dtls2 = self.read(0xB5)
        if dtls0 & 0x60 == 0x60:
            print("MAX77818 VBUS Valid")
        if dtls0 & 0x1 == 1:
            print("MAX77818 BATT Presence detected")

        print("CHG_DTLS = " + "   ".join(map(hex, [dtls0, dtls1, dtls2])))

    def get_chg_stat(self):
        data = self.read(0xB4)
        return data & 0xF
