/*
 * Enable OTG mode via max77818 i2c.
 *
 * Datasheet: https://datasheets.maximintegrated.com/en/ds/MAX77818.pdf
 *      All registers are 16 bits wide and are read and written as 2-byte values. When the MSB of a register is read, the MSB
 *      and LSB are latched simultaneously and held for the duration of the Read Data command.
 *
 * WSL2 Debian prerequisites:
 *      sudo apt-get install 'gcc-arm*'
 *
 * Build:
 *      arm-linux-gnueabi-gcc -Wall t9_enable_otg.c -o enable_otg
 *
 * Resources:
 *      https://www.reddit.com/r/RemarkableTablet/comments/k6ir7s/experiencing_issue_with_charging_my_remarkable_2/
 *      https://www.reddit.com/user/Andrey_Dmitriev/
 *      https://github.com/Devin-Alexander/MAX17330_MAX77958_MAX77818_REFDES/blob/d04e1faa/MAX77818.py
 */

#include <sys/fcntl.h>
#include <sys/stat.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

#include <linux/i2c-dev.h>
#include <linux/i2c.h>


int max77818_get_i2c_regU16(int file, unsigned char addr, unsigned char reg, unsigned short *val, unsigned char *lsb, unsigned char *msb) {
    unsigned char inbuf[2], outbuf;
    struct i2c_rdwr_ioctl_data packets;
    struct i2c_msg messages[2];

    outbuf = reg;
    messages[0].addr  = addr;
    messages[0].flags = 0;
    messages[0].len   = sizeof(outbuf);
    messages[0].buf   = &outbuf;

    messages[1].addr  = addr;
    messages[1].flags = I2C_M_RD;
    messages[1].len   = sizeof(inbuf);
    messages[1].buf   = inbuf;

    packets.msgs      = messages;
    packets.nmsgs     = 2;
    if(ioctl(file, I2C_RDWR, &packets) < 0) {
        return 0;
    }
    *lsb = inbuf[0];
    *msb = inbuf[1];
    *val =  (inbuf[0] << 8) | inbuf[1];

    return 1;
}


int max77818_set_i2c_regU16(int file, unsigned char addr, unsigned char reg, unsigned char lsb, unsigned char msb) {
    unsigned char outbuf[3];
    struct i2c_rdwr_ioctl_data packets;
    struct i2c_msg messages[1];

    messages[0].addr  = addr; //Warn - address swapped, for example, B6 is 6D
    messages[0].flags = 0;
    messages[0].len   = sizeof(outbuf);
    messages[0].buf   = outbuf;

    outbuf[0] = reg;
    outbuf[1] = lsb;
    outbuf[2] = msb;

    packets.msgs  = messages;
    packets.nmsgs = 1;

    if(ioctl(file, I2C_RDWR, &packets) < 0) return 0;

    return 1;
}


int main(void) {
    printf("Start\n");
    int ret, i2cFile;
    u_int16_t valU16;
    u_int8_t lsbU8, msbU8;

    // Open i2c connection.
    if ((i2cFile = open("/dev/i2c-5", O_RDWR)) < 0) {
        printf("ERROR: open /dev/i2c-5 failed: %d\n", i2cFile);
        return -i2cFile;
    }
    if ((ret = ioctl(i2cFile, I2C_SLAVE_FORCE, 0x69)) < 0) {
        printf("ERROR: ioctl failed: %d\n", ret);
        close(i2cFile);
        return -ret;
    }

    // Current config.
    valU16 = lsbU8 = msbU8 = 0;
    ret = max77818_get_i2c_regU16(i2cFile, 0x69, 0xb7, &valU16, &lsbU8, &msbU8);
    printf("Current config @ register 0x%02x ret = %d, valU16=%d, lsbU8=0x%02x, msbU8=0x%02x\n", 0xb7, ret, valU16, lsbU8, msbU8);

    // Change mode to 0x0f.
    // TODO.

    // Did it work?
    valU16 = lsbU8 = msbU8 = 0;
    ret = max77818_get_i2c_regU16(i2cFile, 0x69, 0xb7, &valU16, &lsbU8, &msbU8);
    printf("Current config @ register 0x%02x ret = %d, valU16=%d, lsbU8=0x%02x, msbU8=0x%02x\n", 0xb7, ret, valU16, lsbU8, msbU8);

    close(i2cFile);
    printf("Closed\n");

    return 0;
}
