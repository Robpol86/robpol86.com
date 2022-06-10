#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable-all
"""
Originally from: https://gist.github.com/jkinred/73689e463a08af963c45c137df6646d0

(c) B.Kerler 2019 under MIT license
If you use my code, make sure you refer to [B.Kerler]
If you want to use in a commercial product, ask [B.Kerler] before integrating it

C7 = 7 0		0	2	7		5 0
C6 = 3 1		7	0	3		0 1
C5 = 0 2		5	3	0		3 2
C8 = 1 3		3	1	5		7 3
C4 = 5 4		1	4	1		1 4
"""
import sys
import argparse
from binascii import hexlify, unhexlify

PROD_TABLE = {
    "MDM8200":    dict(openlock=0, openmep=1, opencnd=0, clen=8, init=[1,3,5,7,0], run="resultbuffer[i]=self.SierraAlgo(challenge[i], 2, 4, 1, 3, 0, 3, 4, 0)"), # MC878XC_F1.2.3.15 verified, key may be stored in nvitem 0x4e21;MC8700 M3.0.9.0 verified
    "MDM9200":    dict(openlock=0, openmep=1, opencnd=0, clen=8, init=[7,3,0,1,5], run="resultbuffer[i]=self.SierraAlgo(challenge[i], 4, 2, 1, 0, 3, 2, 0, 0)"),  # AC881U, EM8805 SWI9X15C_05.05.58.00, at!openlock?6A1F1CEA298A14B0 => AT!OPENLOCK="3A9EA70D86FEE58C"
    "MDM9200_V1": dict(openlock=2, openmep=1, opencnd=0, clen=8, init=[7,3,0,1,5], run="resultbuffer[i]=self.SierraAlgo(challenge[i], 4, 2, 1, 0, 3, 2, 0, 0)"),  # AC710
    "MDM9200_V2": dict(openlock=3, openmep=1, opencnd=0, clen=8, init=[7,3,0,1,5], run="resultbuffer[i]=self.SierraAlgo(challenge[i], 4, 2, 1, 0, 3, 2, 0, 0)"),  # AC775
    "MDM9200_V3": dict(openlock=8, openmep=1, opencnd=8, clen=8, init=[7,3,0,1,5], run="resultbuffer[i]=self.SierraAlgo(challenge[i], 4, 2, 1, 0, 3, 2, 0, 0)"),  # AC775
    #"MDM9x15":    dict(openlock=0, openmep=1, opencnd=0, clen=8, init=[5,0,3,7,1], run="resultbuffer[i]=self.SierraCalc9x15(challenge[i])"), # 9x15C 06.03.32.02, AC340U 1.13.12.14 verified, #AT!CUSTOM=\"ADBENABLE\",1
    "MDM9x15":    dict(openlock=0, openmep=1, opencnd=0, clen=8, init=[7,3,0,1,5], run="resultbuffer[i]=self.SierraAlgo(challenge[i], 4, 2, 1, 0, 3, 2, 0, 0)"), # 9x15C 06.03.32.02, AC340U 1.13.12.14 verified, #AT!CUSTOM=\"ADBENABLE\",1

    #"MDM9x28":    dict(openlock=9, openmep=10, opencnd=9, clen=8, init=[5,0,3,7,1], run="resultbuffer[i]=self.SierraAlgo(challenge[i], 0, 1, 2, 3, 4, 3, 1, 0)"),  # SWI9X07Y_02.25.02.01
    "MDM9x28":    dict(openlock=9, openmep=10, opencnd=9, clen=8, init=[7,3,0,1,5], run="resultbuffer[i]=self.SierraAlgo(challenge[i], 4, 2, 1, 0, 3, 2, 0, 0)"),  # SWI9X07Y_02.25.02.01
    #"MDM9x30":    dict(openlock=0, openmep=1, opencnd=0, clen=8, init=[0,7,5,3,1], run="resultbuffer[i]=self.SierraCalc9x30(challenge[i])"), # MC7455_2.30.01.01 #4
    "MDM9x30":    dict(openlock=5, openmep=4, opencnd=5, clen=8, init=[7,3,0,1,5], run="resultbuffer[i]=self.SierraAlgo(challenge[i], 4, 2, 1, 0, 3, 2, 0, 0)"),  # MC7455_2.30.01.01 #4
    "MDM9x30_V1":    dict(openlock=18, openmep=16, opencnd=18, clen=8, init=[7,3,0,1,5], run="resultbuffer[i]=self.SierraAlgo(challenge[i], 4, 2, 1, 0, 3, 2, 0, 0)"),  # AC791L/AC790S NTG9X35C_02.08.29.00

    #"MDM9x40":    dict(openlock=11, openmep=1, opencnd=11, clen=8, init=[0,7,5,3,1], run="resultbuffer[i]=self.MDM9x40(challenge[i], 2, 0, 3, 1, 4, 1, 0, 0)"),
    "MDM9x40": dict(openlock=11, openmep=12, opencnd=11, clen=8, init=[7,3,0,1,5], run="resultbuffer[i]=self.SierraAlgo(challenge[i], 4, 2, 1, 0, 3, 2, 0, 0)"),  # AC815s
    "MDM9x50_V1": dict(openlock=11, openmep=12, opencnd=11, clen=8, init=[7,3,0,1,5], run="resultbuffer[i]=self.SierraAlgo(challenge[i], 4, 2, 1, 0, 3, 2, 0, 0)"),

    #"MDM9x50":    dict(openlock=7, openmep=6, opencnd=7, clen=8, init=[7,0,1,3,5], run="resultbuffer[i]=self.SierraCalc9x50(challenge[i])"),
    "MDM9x50": dict(openlock=7, openmep=6, opencnd=7, clen=8, init=[7,3,0,1,5], run="resultbuffer[i]=self.SierraAlgo(challenge[i], 4, 2, 1, 0, 3, 2, 0, 0)"),  # EM7565

}

INFO_TABLE = {
    "MDM8200": ["M81A", "M81B", "AC880", "AC881", "MC8780", "MC8781", "AC880E", "AC881E", "EM8780", "EM8781",
                "MC8780V", "MC8781V", "MC8700", "AC308U"],
    "MDM9200": ["AC710", "MC8775", "MC8775V", "AC875", "MC8700", "AC313U", "MC8801", "MC7700", "MC7750", "MC7710",
                "EM7700"],
    "MDM9200_V1": ["AC710", "MC8775", "MC8775V", "AC875", "MC8700", "AC313U", "MC8801", "MC7700", "MC7750",
                   "MC7710", "EM7700"],
    "MDM9200_V2": ["AC775", "PC7200"],
    "MDM9x28": ["SWI9X07Y", "WP76xx"],
    "MDM9x15": ["SWI9X15C", "AR7550", "AR7552", "AR7554", "EM7355", "EM7655", "MC7354", "WP7100", "WP7102", "WP7104",
                "MC7305", "EM7305", "MC8805", "EM8805", "MC7350", "MC7350-L", "MC7802", "MC7304", "AR7556", "AR7558",
                "WP75xx", "WP85xx", "WP8548", "WP8548G", "AC340U"],
    "MDM9x30": ["EM7455", "MC7455", "EM7430", "MC7430"],
    "MDM9x30_V1" : ["Netgear AC790/MDM9230"],
    "MDM9x40": ["AC815s"],
    "MDM9x50": ["EM7565", "EM7565-9", "EM7511"],
    "MDM9x50_V1" : ["Netgear MR1100"]
}

KEY_TABLE = bytearray([0xF0, 0x14, 0x55, 0x0D, 0x5E, 0xDA, 0x92, 0xB3, 0xA7, 0x6C, 0xCE, 0x84, 0x90, 0xBC, 0x7F, 0xED,  #0 MC8775_H2.0.8.19 !OPENLOCK, !OPENCND .. MC8765V,MC8765,MC8755V,MC8775,MC8775V,MC8775,AC850,AC860,AC875,AC881,AC881U,AC875, AC340U 1.13.12.14
                       0x61, 0x94, 0xCE, 0xA7, 0xB0, 0xEA, 0x4F, 0x0A, 0x73, 0xC5, 0xC3, 0xA6, 0x5E, 0xEC, 0x1C, 0xE2,  #1 MC8775_H2.0.8.19 AC340U, OPENMEP default
                       0x39, 0xC6, 0x7B, 0x04, 0xCA, 0x50, 0x82, 0x1F, 0x19, 0x63, 0x36, 0xDE, 0x81, 0x49, 0xF0, 0xD7,  #2 AC750,AC710,AC7XX,SB750A,SB750,PC7000,AC313u OPENMEP
                       0xDE, 0xA5, 0xAD, 0x2E, 0xBE, 0xE1, 0xC9, 0xEF, 0xCA, 0xF9, 0xFE, 0x1F, 0x17, 0xFE, 0xED, 0x3B,  #3 AC775,PC7200
                       0xFE, 0xD4, 0x40, 0x52, 0x2D, 0x4B, 0x12, 0x5C, 0xE7, 0x0D, 0xF8, 0x79, 0xF8, 0xC0, 0xDD, 0x37,  #4 MC7455_02.30.01.01 OPENMEP
                       0x3B, 0x18, 0x99, 0x6B, 0x57, 0x24, 0x0A, 0xD8, 0x94, 0x6F, 0x8E, 0xD9, 0x90, 0xBC, 0x67, 0x56,  #5 MC7455_02.30.01.01 OPENLOCK
                       0x47, 0x4F, 0x4F, 0x44, 0x4A, 0x4F, 0x42, 0x44, 0x45, 0x43, 0x4F, 0x44, 0x49, 0x4E, 0x47, 0x2E,  #6 SWI9x50 Openmep Key SWI9X50C_01.08.04.00
                       0x4F, 0x4D, 0x41, 0x52, 0x20, 0x44, 0x49, 0x44, 0x20, 0x54, 0x48, 0x49, 0x53, 0x2E, 0x2E, 0x2E,  #7 SWI9x50 Openlock Key SWI9X50C_01.08.04.00
                       0x8F, 0xA5, 0x85, 0x05, 0x5E, 0xCF, 0x44, 0xA0, 0x98, 0x8B, 0x09, 0xE8, 0xBB, 0xC6, 0xF7, 0x65,  #8 MDM8200 Special
                       0x4D, 0x42, 0xD8, 0xC1, 0x25, 0x44, 0xD8, 0xA0, 0x1D, 0x80, 0xC4, 0x52, 0x8E, 0xEC, 0x8B, 0xE3,  #9 SWI9x07 Openlock Key 02.25.02.01
                       0xED, 0xA9, 0xB7, 0x0A, 0xDB, 0x85, 0x3D, 0xC0, 0x92, 0x49, 0x7D, 0x41, 0x9A, 0x91, 0x09, 0xEE,  #10 SWI9x07 Openmep Key 02.25.02.01
                       0x8A, 0x56, 0x03, 0xF0, 0xBB, 0x9C, 0x13, 0xD2, 0x4E, 0xB2, 0x45, 0xAD, 0xC4, 0x0A, 0xE7, 0x52,  #11 NTG9X40C_11.14.08.11 / mdm9x40r11_core AC815s / SWI9x50 MR1100 Openlock Key
                       0x2A, 0xEF, 0x07, 0x2B, 0x19, 0x60, 0xC9, 0x01, 0x8B, 0x87, 0xF2, 0x6E, 0xC1, 0x42, 0xA8, 0x3A,  #12 SWI9x50 MR1100 Openmep Key
                       0x28, 0x55, 0x48, 0x52, 0x24, 0x72, 0x63, 0x37, 0x14, 0x26, 0x37, 0x50, 0xBE, 0xFE, 0x00, 0x00,  #13 SWI9x50 Unknown key
                       0x22, 0x63, 0x48, 0x02, 0x24, 0x72, 0x27, 0x37, 0x19, 0x26, 0x37, 0x50, 0xBE, 0xEF, 0xCA, 0xFE,  #14 SWI9x50 IMEI nv key
                       0x98, 0xE1, 0xC1, 0x93, 0xC3, 0xBF, 0xC3, 0x50, 0x8D, 0xA1, 0x35, 0xFE, 0x50, 0x47, 0xB3, 0xC4,  #15 NTG9X35C_02.08.29.00 Openmep Key AC791L/AC790S Old
                       0x61, 0x94, 0xCE, 0xA7, 0xB0, 0xEA, 0x4F, 0x0A, 0x73, 0xC5, 0xC3, 0xA6, 0x5E, 0xEC, 0x1C, 0xE2,  #16 NTG9X35C_02.08.29.00 Openmep Key AC791/AC790S
                       0xC5, 0x50, 0x40, 0xDA, 0x23, 0xE8, 0xF4, 0x4C, 0x29, 0xE9, 0x07, 0xDE, 0x24, 0xE5, 0x2C, 0x1D,  #17 NTG9X35C_02.08.29.00 Openlock Key AC791/AC790S Old
                       0xF0, 0x14, 0x55, 0x0D, 0x5E, 0xDA, 0x92, 0xB3, 0xA7, 0x6C, 0xCE, 0x84, 0x90, 0xBC, 0x7F, 0xED,  #18 NTG9X35C_02.08.29.00 Openlock Key AC791/AC790S
                       ])


class SierraGenerator:
    tbl = bytearray()
    rtbl = bytearray()

    def __init__(self):
        for i in range(0, 0x14):
            self.rtbl.append(0x0)
        for i in range(0, 0x100):
            self.tbl.append(0x0)

    def run(self, devicegeneration, challenge, type):
        challenge = bytearray(unhexlify(challenge))

        self.devicegeneration = devicegeneration
        if not devicegeneration in PROD_TABLE:
            print("Sorry, " + devicegeneration + " not supported.")
            exit(0)

        mepid = PROD_TABLE[devicegeneration]["openmep"]
        cndid = PROD_TABLE[devicegeneration]["opencnd"]
        lockid = PROD_TABLE[devicegeneration]["openlock"]
        clen = PROD_TABLE[devicegeneration]["clen"]
        if len(challenge) < clen:
            for i in range(0, clen - len(challenge)):
                challenge.append(0)

        challengelen = len(challenge)
        if type == 0:  # lockkey
            idf = lockid
        elif type == 1:  # mepkey
            idf = mepid
        elif type == 2:  # cndkey
            idf = cndid

        key = KEY_TABLE[idf * 16 : (idf * 16) + 16]
        resp = self.SierraKeygen(challenge, key, challengelen, 16)[:challengelen]
        resp = hexlify(resp).decode("utf-8").upper()
        return resp

    def SierraPreInit(self, counter, key, keylen, challengelen, mcount):
        if counter != 0:
            tmp2 = 0
            i = 1
            while i < counter:
                i = 2 * i + 1

            while True:
                tmp = mcount
                mcount = tmp + 1
                challengelen = (key[tmp & 0xFF] + self.tbl[(challengelen & 0xFF)]) & 0xFF
                if mcount >= keylen:
                    mcount = 0
                    challengelen = ((challengelen & 0xFF) + keylen) & 0xFF
                tmp2 = tmp2 + 1
                tmp3 = ((challengelen & 0xFF) & i) & 0xFF
                if tmp2 >= 0xB:
                    tmp3 = counter % tmp3
                if tmp3 <= counter:
                    break
            counter = tmp3 & 0xFF
        return [counter, challengelen, mcount]

    def SierraInit(self, key, keylen):
        if keylen == 0 or keylen > 0x20:
            retval = [0, keylen]
        elif 1 <= keylen <= 0x20:
            for i in range(0, 0x100):
                self.tbl[i] = i & 0xFF
            mcount = 0
            cl = keylen & 0xFFFFFF00
            i = 0xFF
            while i > -1:
                t, cl, mcount = self.SierraPreInit(i, key, keylen, cl, mcount)
                m = self.tbl[i]
                self.tbl[i] = self.tbl[(t & 0xFF)]
                i = i - 1
                self.tbl[(t & 0xFF)] = m
            self.rtbl[0] = (
                self.tbl[PROD_TABLE[self.devicegeneration]["init"][0]]
                if PROD_TABLE[self.devicegeneration]["init"][0] != 0
                else self.tbl[(cl & 0xFF)]
            )
            self.rtbl[1] = (
                self.tbl[PROD_TABLE[self.devicegeneration]["init"][1]]
                if PROD_TABLE[self.devicegeneration]["init"][1] != 0
                else self.tbl[(cl & 0xFF)]
            )
            self.rtbl[2] = (
                self.tbl[PROD_TABLE[self.devicegeneration]["init"][2]]
                if PROD_TABLE[self.devicegeneration]["init"][2] != 0
                else self.tbl[(cl & 0xFF)]
            )
            self.rtbl[3] = (
                self.tbl[PROD_TABLE[self.devicegeneration]["init"][3]]
                if PROD_TABLE[self.devicegeneration]["init"][3] != 0
                else self.tbl[(cl & 0xFF)]
            )
            self.rtbl[4] = (
                self.tbl[PROD_TABLE[self.devicegeneration]["init"][4]]
                if PROD_TABLE[self.devicegeneration]["init"][4] != 0
                else self.tbl[(cl & 0xFF)]
            )
            retval = [1, keylen]
        return retval

    def SierraAlgo(self, challenge, a=0, b=1, c=2, d=3, e=4, ret=3, ret2=1, flag=1):  # M9x15
        v6 = self.rtbl[e]
        v0 = (v6 + 1) & 0xFF
        self.rtbl[e] = v0
        self.rtbl[c] = (self.tbl[v6 + flag & 0xFF] + self.rtbl[c]) & 0xFF
        v4 = self.rtbl[c] & 0xFF
        v2 = self.rtbl[b] & 0xFF
        v1 = self.tbl[(v2 & 0xFF)]
        self.tbl[(v2 & 0xFF)] = self.tbl[(v4 & 0xFF)]
        v5 = self.rtbl[d] & 0xFF
        self.tbl[(v4 & 0xFF)] = self.tbl[(v5 & 0xFF)]
        self.tbl[(v5 & 0xFF)] = self.tbl[(v0 & 0xFF)]
        self.tbl[v0] = v1 & 0xFF
        u = self.tbl[
            (
                self.tbl[
                    (
                        self.tbl[((self.rtbl[a] + self.tbl[(v1 & 0xFF)]) & 0xFF)]
                        + self.tbl[(v5 & 0xFF)]
                        + self.tbl[(v2 & 0xFF)]
                        & 0xFF
                    )
                ]
                & 0xFF
            )
        ]
        v = self.tbl[((self.tbl[(v4 & 0xFF)] + v1) & 0xFF)]
        self.rtbl[ret] = u ^ v ^ challenge
        self.rtbl[a] = (self.tbl[(v1 & 0xFF)] + self.rtbl[a]) & 0xFF
        self.rtbl[ret2] = challenge & 0xFF
        return self.rtbl[ret] & 0xFF

    def SierraFinish(self):
        for i in range(0, 0x100):
            self.tbl[i] = 0
        self.rtbl[0] = 0
        self.rtbl[1] = 0
        self.rtbl[2] = 0
        self.rtbl[3] = 0
        self.rtbl[4] = 0
        return 1

    def SierraKeygen(self, challenge, key, challengelen, keylen):
        resultbuffer = bytearray()
        for i in range(0, 0x100 + 1):
            resultbuffer.append(0x0)
        ret, keylen = self.SierraInit(key, keylen)
        if ret:
            for i in range(0, challengelen):
                exec(PROD_TABLE[self.devicegeneration]["run"])
            self.SierraFinish()
        return resultbuffer


def main(argv):
    version = "1.0"
    info = "Sierra Wireless Generator " + version + " (c) B. Kerler 2019"

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=info)
    parser.add_argument("-openlock", "-l", help="AT!OPENLOCK? modem response", default="")
    parser.add_argument("-openmep", "-m", help="AT!OPENMEP? modem response", default="")
    parser.add_argument("-opencnd", "-c", help="AT!OPENCND? modem response", default="")
    parser.add_argument("-devicegeneration", "-d", help="Device devicegeneration generation", default="")
    parser.add_argument("-port", "-p", help="use com port for auto unlock", default="")
    parser.add_argument("-unlock", "-u", help="use com port for auto unlock", default=False, action="store_true")
    args = parser.parse_args(args=argv)

    openlock = args.openlock
    openmep = args.openmep
    opencnd = args.opencnd
    devicegeneration = args.devicegeneration

    if (devicegeneration == "" or (openlock == "" and openmep == "" and opencnd == "")) and not args.unlock:
        print(info)
        print("------------------------------------------------------------\n")
        print("Usage: ./sierrakeygen [-l,-m,-c] [challenge] -d [devicegeneration]")
        print("Example: ./sierrakeygen.py -l BE96CBBEE0829BCA -d MDM9200")
        print("or: ./sierrakeygen.py -u for auto unlock")
        print("or: ./sierrakeygen.py -u -p [portname] for auto unlock with given portname")
        print("Supported devicegenerations :")
        for key in INFO_TABLE:
            info = f"\t{key}:\t\t"
            count = 0
            for item in INFO_TABLE[key]:
                count += 1
                if count > 15:
                    info += "\n\t\t\t\t\t"
                    count = 0
                info += item + ","

            info = info[:-1]
            print(info)
        exit(0)

    if devicegeneration == "" and not args.unlock:
        print("You need to specific a device generation as well. Option -d")
        exit(0)

    keygen = SierraGenerator()
    if args.unlock:
        raise NotImplementedError
    else:
        if openlock != "":
            resp = keygen.run(devicegeneration, openlock, 0)
            print('AT!OPENLOCK="' + resp + '"')
            # -l BE96CBBEE0829BCA -d MDM9x40 ==> AT!OPENLOCK="1033773720F6EE66"
        elif openmep != "":
            resp = keygen.run(devicegeneration, openmep, 1)
            print('AT!OPENMEP="' + resp + '"')
        elif opencnd != "":
            resp = keygen.run(devicegeneration, opencnd, 2)
            print('AT!OPENCND="' + resp + '"')


if __name__ == "__main__":
    main(sys.argv[1:])
