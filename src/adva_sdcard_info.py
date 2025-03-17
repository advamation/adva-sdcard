#!/usr/bin/env python3
"""SD-card: Get card information.

Get/parse SD-card information from CID/CSD.

:Usage:
    see --help

:Exit code:
    0:   success
    2:   invalid commandline-parameters
    19:  device not found (ENODEV)
    5:   cannot read from device (EIO)
    22:  invalid CID data (EINVAL)
    130: aborted (e.g. via Ctrl-C) (ECONNABORTED)

:Author:    Advamation / Roland Freikamp <support@advamation.de>
:Version:   2021-09-10
:Copyright: Advamation <info@advamation.de>
:License:   MIT
"""

__version__ = "1.0.0"
__author__ = "Advamation <support@advamation.de>"

import os
import sys
import argparse
import json

#=========================================

def cid_get(dev="/dev/mmcblk0/"):
    """Get CID from (micro)SD-card.

    This currently only works for devices with mmc_host,
    esp. Raspberry Pi. It does not work with USB-cardreaders.

    :Returns:
        The CID as hexadecimal string.
    :Raises:
        ValueError for invalid arguments,
        FileNotFoundError if device cannot be found,
        IOError if device cannot be opened/read.
    """
    if not dev.startswith("/dev/"):
        raise ValueError("'dev' must start with '/dev/'")
    if not os.path.exists(dev):
        raise FileNotFoundError("'%s' does not exist." % dev)
    dev = os.path.realpath(dev)
    if not dev.startswith("/dev/") or "/" in dev[5:]:
        raise ValueError("'dev' link destination must be '/dev/...'")
    path = "/sys/block/%s/device/cid" % dev[5:]
    if not os.path.exists(path):
        raise FileNotFoundError("'%s' does not exist." % path)

    with open(path, 'r', encoding="utf-8") as f:
        return f.read(100).strip()

def cid_parse(cid):
    """Parse CID-information.

    :Parameters:
        - cid: CID-data as hexadecimal string
    :Returns:
        SD-card info dict, with:
        - cid
        - manfid (MID, Manufacturer ID)
        - oemid  (OID, OEM/Application ID)
        - name   (PNM, Product Name)
        - rev    (PRV, Product Revision)
        - serial (PSN, Serial Number)
        - date   (MDT, Manufacture Date)
        - crc    (CRC, checksum)
    """
    i = int(cid, 16)
    info = {}
    info["cid"] = i
    info["manfid"] =  (i>>120) & 0xFF
    info["oemid"]  = ((i>>104) & 0xFFFF).to_bytes(2, "big").decode("latin-1")
    info["name"]   = ((i>> 64) & 0xFFFFFFFFFF).to_bytes(5, "big").decode("latin-1")
    info["rev"]    = "%d.%d" % ((i >> 60)&0xF, (i>>56)&0xF)
    info["serial"] =  (i>> 24) & 0xFFFFFFFF
    info["date"]   = "%04d-%02d" % (2000+((i>>12)&0xFF), (i>>8)&0xF)
    #TODO: check checksum?
    info["crc"]    =  (i>>  1) & 0x7F
    return info

def cid_print(info):
    """Print parsed CID-information.

    :Parameters:
        - info: CID-info, parsed by cid_parse()
    """
    print("CID:                   %032x" % info["cid"])
    print("Manufacturer ID:       0x%02x" % info["manfid"])
    print("OEM/Application ID:    %s" % info["oemid"])
    print("Product name:          %s" % info["name"])
    print("Product revision:      %s" % info["rev"])
    print("Product serial number: 0x%08x" % info["serial"])
    print("Manufacturing date:    %s" % info["date"])
    print("Checksum:              0x%02x" % info["crc"])

#----------------------
def csd_parse(csd):
    """Parse CSD-information.

    :Parameters:
        - csd: CSD-data as hexadecimal string
    :Returns:
        SD-card info dict, with:
        - csd
        - CSD_STRUCTURE
        - TAAC
        - NSAC
        - TRAN_SPEED
        - CCC
        - READ_BL_LEN
        - READ_BL_PARTIAL
        - WRITE_BLK_MISALIGN
        - READ_BLK_MISALIGN
        - DSR_IMP
        - C_SIZE
        - ERASE_BLK_EN
        - SECTOR_SIZE
        - WP_GRP_SIZE
        - WP_GRP_ENABLE
        - R2W_FACTOR
        - WRITE_BL_LEN
        - WRITE_BL_PARTIAL
        - FILE_FORMAT_GRP
        - COPY
        - PERM_WRITE_PROTECT
        - TMP_WRITE_PROTECT
        - FILE_FORMAT
        - CRC
    """
    i = int(csd, 16)
    info = {}
    info["csd"] = i
    info["CSD_STRUCTURE"]      = (i>>126) & 0x03
    info["TAAC"]               = (i>>112) & 0xFF
    info["NSAC"]               = (i>>104) & 0xFF
    info["TRAN_SPEED"]         = (i>> 96) & 0xFF
    info["CCC"]                = (i>> 84) & 0x7FF
    info["READ_BL_LEN"]        = (i>> 80) & 0x0F
    info["READ_BL_PARTIAL"]    = (i>> 79) & 0x01
    info["WRITE_BLK_MISALIGN"] = (i>> 78) & 0x01
    info["READ_BLK_MISALIGN"]  = (i>> 77) & 0x01
    info["DSR_IMP"]            = (i>> 76) & 0x01
    if info["CSD_STRUCTURE"] == 0:
        info["C_SIZE"]         = (i>> 62) & 0x7FF
        #VDD_R_CURR_MIN
        #VDD_R_CURR_MAX
        #VDD_W_CURR_MIN
        #VDD_W_CURR_MAX
        #C_SIZE_MULT
    else:
        info["C_SIZE"]         = (i>> 48) & 0x3FFFFF
    info["ERASE_BLK_EN"]       = (i>> 46) & 0x01
    info["SECTOR_SIZE"]        = (i>> 39) & 0x7F
    info["WP_GRP_SIZE"]        = (i>> 32) & 0x7F
    info["WP_GRP_ENABLE"]      = (i>> 31) & 0x01
    info["R2W_FACTOR"]         = (i>> 26) & 0x07
    info["WRITE_BL_LEN"]       = (i>> 22) & 0x0F
    info["WRITE_BL_PARTIAL"]   = (i>> 21) & 0x01
    info["FILE_FORMAT_GRP"]    = (i>> 15) & 0x01
    info["COPY"]               = (i>> 14) & 0x01
    info["PERM_WRITE_PROTECT"] = (i>> 13) & 0x01
    info["TMP_WRITE_PROTECT"]  = (i>> 12) & 0x01
    info["FILE_FORMAT"]        = (i>> 10) & 0x03
    #TODO: check checksum?
    info["CRC"]                = (i>>  1) & 0x7F
    return info

#=========================================

def main(arglist=None):
    """Get/parse CID and print result.

    See module docsting for exit codes.
    """
    # parse arguments
    parser = argparse.ArgumentParser(
        description="""Get/parse microSD-/SD-card-information from mmc-device.
Version %s by %s.""" % (__version__, __author__),
        formatter_class=argparse.RawDescriptionHelpFormatter,   # for keeping newlines in description
        epilog="""
Examples:
    adva_sdcard_info 275048415...
    adva_sdcard_info -d /dev/mmcblk0
Note that this does not work with USB-cardreaders.\n""")

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("-p", "--parsable", action='store_true', help="Print output in parsable format.")
    group.add_argument("-j", "--json",     action='store_true', help="Print output in JSON format.")

    parser.add_argument("-d", "--device", action='store', help="Retrieve CID directly from SD-card.")
    parser.add_argument("cid", nargs='?', type=str, help='CID as hex string or file containing the CID, default: stdin')
    parser.add_argument("--version", action='version', version="%(prog)s " + __version__)

    if arglist is None  and  len(sys.argv) <= 1:
        parser.print_help(sys.stderr)
        return 0
    args = parser.parse_args(arglist)

    # retrieve CID
    cid = None
    if args.device:
        try:
            cid = cid_get(args.device)
        except ValueError as err:
            print("ERROR: %s" % str(err).replace('dev', 'DEVICE'))
            return 2
        except FileNotFoundError as err:
            print("ERROR: %s" % str(err).replace('dev', 'DEVICE'))
            return 19   # ENODEV
        except IOError as err:
            print("ERROR: %s" % str(err).replace('dev', 'DEVICE'))
            return 5    # EIO
    elif args.cid:
        if len(args.cid) == 32:
            try:
                int(args.cid, 16)
                cid = args.cid
            except ValueError:
                pass
        if not cid:
            if not os.path.isfile(args.cid):
                print("ERROR: Invalid arguments, 'cid' must be hex or a regular file. (%s)" % args.cid)
                return 2
            try:
                with open(args.cid, 'r', encoding="utf-8") as f:
                    cid = f.read(100).strip()
            except IOError as err:
                print("ERROR: Cannot open '%s' (%s)." % (args.cid, err), file=sys.stderr)
                return 5    # EIO
    else:
        cid = sys.stdin.read(100).strip()

    # parse CID
    try:
        info = cid_parse(cid)
    except ValueError as err:
        print("ERROR: Invalid CID data. (%s)" % err, file=sys.stderr)
        return 22   # EINVAL

    # print CID-data
    if   args.json:
        print(json.dumps(info))
    elif args.parsable:
        for key,val in info.items():
            if isinstance(val, int):
                print("%s: 0x%x" % (key, val))
            else:
                print("%s: %s" % (key, val))
    else:
        cid_print(info)

    return 0

#=========================================
if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(130)   # ECONNABORTED

#=========================================
