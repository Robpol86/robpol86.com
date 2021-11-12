/*
 * Enable OTG mode via max77818 i2c.
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


int main(void) {
    printf("Start\n");
    int ret, i2cFile;
    u_int16_t valU16;
    u_int8_t lsbU8, msbU8;

    if ((i2cFile = open("/dev/i2c-5", O_RDWR)) < 0) printf("open failed: %d\n", i2cFile);
    printf("Opened\n");

    if ((ret = ioctl(i2cFile, I2C_SLAVE_FORCE, 0x69)) < 0) printf("ioctl failed: %d\n", ret);
    printf("ioctl init done\n");

    ret = max77818_get_i2c_regU16(i2cFile, 0x69, 0xb7, &valU16, &lsbU8, &msbU8);
    printf("get done\n");

    printf("Read temp alert Register 0x%08x ret = %d, valU16=%d, lsbU8=0x%08x, msbU8=0x%08x\n", 0xb7, ret, valU16, lsbU8, msbU8);

    close(i2cFile);
    printf("Closed\n");

    return 0;
}
