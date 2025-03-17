/**** SD-card: get raw SMART-information

Get SMART-information from (industrial) SD-/microSD-card.

Getting SMART-information is split into two parts:

- A minimal program, to get the raw SMART-information and output it
  in hexadecimal; this needs access to the device or must be run
  as root / SUID.
  (this part)
- A program to parse/interpret the raw information.
  (e.g in C or Python)

Supported cards:

- Apacer CV110-MSD / AK6.112* (not yet tested)
- Apacer CH110-MSD / AK6.118* (not yet tested)
- Apacer H1-M  / AP-*-1HTM (only microSD tested)
- Apacer H2-M  / AP-*-1RTM (only microSD tested)
- Apacer H1-SL / AP-*-2HTM (only microSD tested)
- Apacer H2-SL / AP-*-2RTM (only microSD tested)
- maybe more Apacer AP-*-* (not tested)
- Transcend 230I
- Transcend 240I

Works on Raspberry Pi with /dev/mmcblk*,
does not work with USB-cardreaders.

:Usage:
    see --help or USAGE-string

:Returns:
    exitcode:
    - 0: success
    - -1: invalid commandline-parameters
    - >0: error, see errno

prints:
    - to stdout: SMART-information as TYPE + '-' + 512 hexadecimal bytes on success
    - to stderr: usage-information and/or error-message on error

:Author:    Advamation / Roland Freikamp <support@advamation.de>
:Version:   2025-03-17
:Copyright: Advamation <info@advamation.de>
:License:   MIT
***/

#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/ioctl.h>

#include <linux/mmc/ioctl.h>    // for struct mmc_ioc_cmd
#include <linux/major.h>        // for MMC_IOC_CMD

/* from linux/mmc/core.h */
#define MMC_RSP_PRESENT (1 << 0)
//#define MMC_RSP_136 (1 << 1)
#define MMC_RSP_CRC (1 << 2)
//#define MMC_RSP_BUSY (1 << 3)
#define MMC_RSP_OPCODE (1 << 4)
//#define MMC_CMD_AC (0 << 5)
#define MMC_CMD_ADTC (1 << 5)
#define MMC_RSP_SPI_S1 (1 << 7)
//#define MMC_RSP_SPI_BUSY (1 << 10)
#define MMC_RSP_SPI_R1 (MMC_RSP_SPI_S1)
//#define MMC_RSP_SPI_R1B (MMC_RSP_SPI_S1 | MMC_RSP_SPI_BUSY)
//#define MMC_RSP_NONE	(0)
#define MMC_RSP_R1 (MMC_RSP_PRESENT | MMC_RSP_CRC | MMC_RSP_OPCODE)
//#define MMC_RSP_R1B (MMC_RSP_PRESENT | MMC_RSP_CRC | MMC_RSP_OPCODE | MMC_RSP_BUSY)

//----------------------------------------
#define SECTOR_SIZE 512

/****
Get SMART-information.

:Parameters:
    - fd: filedescriptor of opened device
    - type: 'A' for Apacer, 'T' for Transcend
    - smart: output, length SECTOR_SIZE
:Returns:
    0:  success
    -1: ioctl failed, see errno for details
    -2: card not supported / no SMART
    -3: card not supported / no SMART / invalid SMART-data
***/
int smart_get(int fd, char* type, unsigned char *smart)
{
    int ret;
    struct mmc_ioc_cmd idata;

    memset(smart, 0, SECTOR_SIZE);

    //----------------------------------------
    // Apacer
    if(type[0] == 'A') {
        // 1st command: "Pre-Load SMART Command Information"
        memset(&idata, 0, sizeof(idata));
        idata.write_flag = 1;
        idata.opcode = 56;
        idata.arg = 0x10;
        idata.flags = MMC_RSP_SPI_R1 | MMC_RSP_R1 | MMC_CMD_ADTC;
        idata.blksz = SECTOR_SIZE;
        idata.blocks = 1;
        mmc_ioc_cmd_set_data(idata, smart);
        ret = ioctl(fd, MMC_IOC_CMD, &idata);
        if(ret < 0)
            return -1;

        // 2nd command: "GetSMART Command Information"
        memset(&idata, 0, sizeof(idata));
        idata.write_flag = 0;
        idata.opcode = 56;
        idata.arg = 0x21;
        idata.flags = MMC_RSP_SPI_R1 | MMC_RSP_R1 | MMC_CMD_ADTC;
        idata.blksz = SECTOR_SIZE;
        idata.blocks = 1;
        mmc_ioc_cmd_set_data(idata, smart);
        ret = ioctl(fd, MMC_IOC_CMD, &idata);
        if(ret < 0)
            return -1;
    }
    
    //----------------------------------------
    // Transcend
    else if(type[0] == 'T') {
        memset(&idata, 0, sizeof(idata));
        idata.write_flag = 0;
        idata.opcode = 56;
        idata.arg = 0x110005F9;
        idata.flags = MMC_RSP_SPI_R1 | MMC_RSP_R1 | MMC_CMD_ADTC;
        idata.blksz = SECTOR_SIZE;
        idata.blocks = 1;
        mmc_ioc_cmd_set_data(idata, smart);
        ret = ioctl(fd, MMC_IOC_CMD, &idata);
        if(ret < 0)
            return -1;
    }
    //----------------------------------------
    // unknown card
    else {
        return -2;
    }
    //----------------------------------------
    // check
    int i;
    for(i=0; i<SECTOR_SIZE; i++) {
        if(smart[i] != 0xff)
            break;
    }
    if(i >= 500)
        return -3;

    return 0;
}

//========================================
const char *USAGE="\
usage: adva-sdcard-smart-get DEVICE\n\
\n\
Get raw SMART-information from industrial microSD-/SD-card.\n\
Version 1.0.0 by Advamation <support@advamation.de>.\n\
\n\
Example: adva-sdcard-smart-get /dev/mmcblk0\n\
Note that this does not work with USB-cardreaders.\n\
Supported cards:\n\
    - Apacer CV110-MSD / AK6.112*\n\
    - Apacer CH110-MSD / AK6.118*\n\
    - Apacer H1-M  / AP-*-1HTM\n\
    - Apacer H2-M  / AP-*-1RTM\n\
    - Apacer H1-SL / AP-*-2HTM\n\
    - Apacer H2-SL / AP-*-2RTM\n\
    - Transcend 230I\n\
    - Transcend 240I\n\
";

int main(int argc, char *argv[])
{
    char *device;
    char type[10];
    struct stat st;
    int fd, ret, i;
    FILE *f;

    // Usage
    if(argc == 1 || strcmp(argv[1], "--help") == 0 || strcmp(argv[1], "-h") == 0) {
        fprintf(stderr, "%s", USAGE);
        return 0;
    }
    if(argc != 2) {
        fprintf(stderr, "ERROR: Invalid arguments.\n");
        fprintf(stderr, "%s", USAGE);
        return -1;
    }
    device = argv[1];

    // restrict DEVICE to /dev/mmcblk* (for SUID security)
    // TODO: also allow /dev/disk/... or /dev/sd* ?
    if(strncmp(device, "/dev/mmcblk", 11) != 0 || strchr(device+5, '/') != 0) {
        fprintf(stderr, "ERROR: Only devices /dev/mmcblk* allowed.\n");
        return -1;
    }

    // restrict to block-devices
    if(stat(device, &st) == 0 && !(st.st_mode & S_IFBLK)) {
        fprintf(stderr, "ERROR: Invalid device '%s', must be a block-device.\n", device);
        return ENOTBLK;
    }

    // get TYPE
    char manfid_path[64];
    unsigned int manfid;
    ret = snprintf(manfid_path, 64, "/sys/block/%s/device/manfid", device+5);
    if(ret >= 64) {
        fprintf(stderr, "ERROR: Invalid arguments: DEVICE too long.\n");
        return -1;
    }
    f = fopen(manfid_path, "r");
    if(f == NULL) {
        // check errno
        if(errno == ENOENT || errno == ENODEV || errno == ENXIO) {
            fprintf(stderr, "ERROR: File '%s' does not exist.\n", manfid_path);
        }
        if(errno == EACCES || errno == EROFS) {
            fprintf(stderr, "ERROR: Permission denied for '%s'.\n", manfid_path);
        }
        else {
            fprintf(stderr, "ERROR: %s for '%s'. (%d)\n", strerror(errno), manfid_path, errno);
        }
        return errno;
    }
    ret = fscanf(f, "%x", &manfid);
    fclose(f);
    if(ret != 1) {
        fprintf(stderr, "ERROR: Unexpected '%s' contents.\n", manfid_path);
        return ENOTSUP;
    }
    if(     manfid == 0x27) type[0] = 'A';
    else if(manfid == 0x74) type[0] = 'T';
    else {
        fprintf(stderr, "ERROR: Device not supported.\n");
        return ENOTSUP;
    }
    type[1] = '\0';

    // try to open the device
    fd = open(device, O_RDWR);
    if(fd < 0) {
        // check errno
        if(errno == ENOENT || errno == ENODEV || errno == ENXIO) {
            fprintf(stderr, "ERROR: Device '%s' does not exist.\n", device);
        }
        if(errno == EACCES || errno == EROFS) {
            fprintf(stderr, "ERROR: Permission denied.\n");
        }
        else {
            fprintf(stderr, "ERROR: %s. (%d)\n", strerror(errno), errno);
        }
        return errno;
    }

    // get smart-information
    unsigned char smart[SECTOR_SIZE];
    ret = smart_get(fd, type, smart);
    close(fd);
    if(ret == -2) {
        fprintf(stderr, "ERROR: Device not supported. (type: %s)\n", type);
        return ENOTSUP;
    }
    if(ret == -3) {
        fprintf(stderr, "ERROR: Device not supported. (ff..ff)\n");
        return ENOTSUP;
    }
    if(ret) {
        fprintf(stderr, "ERROR: Failed. (%s, %d)\n", strerror(errno), errno);
        return errno;
    }
    // print smart-information-data
    printf("%s-", type);
    for(i=0; i<SECTOR_SIZE; i++)
        printf("%02x", smart[i]);
    printf("\n");

    return 0;
}

//========================================
