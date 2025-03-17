#!/usr/bin/env python3
"""SD-card: Parse SMART-information.

Parse raw SMART-information from (industrial) SD-/microSD-card.

Getting SMART-information is split into two parts:

- A minimal program, to get the raw SMART-information and output it
  in hexadecimal; this needs access to the device or must be run
  as root / SUID.
- A program to parse/interpret the raw information.
  (this part)

Supported cards:

- Transcend 240I
- Transcend 230I
- Apacer CH110-MSD / AK6.118* (not yet tested)
- Apacer CV110-MSD / AK6.112* (not yet tested)
- Apacer H2-SL / AP-*-2RTM (only microSD tested)
- Apacer H1-SL / AP-*-2HTM (only microSD tested)
- Apacer H2-M  / AP-*-1RTM (only microSD tested)
- Apacer H1-M  / AP-*-1HTM (only microSD tested)
- maybe more Apacer AP-*-* (not tested)

Works on Raspberry Pi with /dev/mmcblk*,
does not work with USB-cardreaders.

:Usage:
    see --help

:Exit code:
    0:   success
    2:   invalid commandline-parameters
    5:   cannot read from device (EIO)
    22:  invalid CID data (EINVAL)
    130: aborted (e.g. via Ctrl-C) (ECONNABORTED)
    errno: from adva-sdcard-smart-get

:Author:    Advamation / Roland Freikamp <support@advamation.de>
:Version:   2025-03-17
:Copyright: Advamation <info@advamation.de>
:License:   MIT
"""

__version__ = "1.0.0"
__author__ = "Advamation <support@advamation.de>"

import sys
import argparse
import subprocess
import json

# raw SMART data consists of 512 bytes:
#
# Apacer:
# ========= =======================================
# byte      contents
# ========= =======================================
# 0..8      Flash ID
# 9..10     IC version
# 11..12    FW version
# 14        CE number
# 16..17    bad block replace maximum
# 32..63    bad block count per die
# 64..65    good block rate (%) (TODO: overall or spare block rate?)
# 80..83    total erase count
# 96..97    endurance (remain life) (%)
# 98..99    average erase count L
# 100..101  minimum erase count L
# 102..103  maximum erase count L
# 104..105  average erase count H
# 106..107  minimum erase count H
# 108..109  maximum erase count H
# 112..115  power up count
# 128..129  abnormal power off count
# 160..161  total refresh count
# 176..183  product "marker"
# 184..215  bad block count per die
# --------- ---------------------------------------
# TODO
# 15        10
# 19        02
# 86        0b b8
# 144       2a 1f
# 164       01
# 216       01 01 10 10
# 284       02
# 297       01 05
# 496..510  CID[:-1]
# 511       chksum?
# ========= =======================================

# Transcend 2GB/4GB:
# ========= =======================================
# byte      contents
# ========= =======================================
# 0..8      Flash ID
# 9..10     IC version
# 11..12    Firmware version
# 14        CE number
# 32..35    total bad block count
# 64..65    spare block rate = (total_spare_block - new_bad_block)/total_spare_block)
# 80..83    total erase count
# 96..97    health status = (flash_endurance - avg_erase_count) / flash_endurance
# 98..99    avg. erase count, low byte
# 100..101  min. erase-count, low byte
# 102..103  max. erase-count, low byte
# 104..105  avg. erase-count, high byte
# 106..107  min. erase-count, high byte
# 108..109  max. erase-count, high byte
# 112..115  power off/on count
# 128..129  suddenly power off count
# 176..184  "Transcend"
# ========= =======================================

# Transcend >=8GB:
# ========= =======================================
# byte      contents
# ========= =======================================
# 0..15     "Transcend"
# (17)      in/not in secured mode
# (18)      speed class
# (19)      UHS speed class
# 26        new bad block count
# 28..31    abnormal power loss when reading/writing data
# 32..35    min. erase count
# 36..39    max. erase count
# 44..47    avg. erase count
# 70        remaining card life = (flash_endurance - avg_erase_count) / flash_endurance
# (72..75)  total write CRC count
# 76..79    power on/off count
# 80..85    NAND Flash ID
# 88..95    IC version (TODO: format?)
# (111)     sd card speed mode
# 128..133  firmware version
# ========= =======================================

def smart_parse(raw):
    """Parse raw SMART-data.

    :Parameters:
        - raw: raw smart-data
    :Returns:
        smart-information: empty dict, or dict with:
        - type (A for Apacer, T for Transcend)
        - flash_id
        - ic_version
        - fw_version
        - ce_number (only Apacer, Transcend 2/4GB)
        - product_marker

        - power_on_count
        - power_off_abnormal_count
        - endurance (0.0..100.0, in %)

        - erase_count_min
        - erase_count_avg
        - erase_count_max
        - erase_count_total (only Apacer, Transcend 2/4GB)
        - refresh_count_total (only Apacer)

        - blocks_bad
        - blocks_good_rate   (only Apacer)
        - blocks_spare       (only Apacer)
        - blocks_spare_rate  (only Transcend 2/4GB)
        - blocks_bad_later_per_die (only Apacer)
        - blocks_bad_initial_per_die (only Apacer)
        - blocks_bad_initial (only Apacer)
    """
    typ, data = raw.split("-", 1)
    b = bytes.fromhex(data)
    smart = {}
    # Apacer
    if typ == 'A':
        smart["type"] = 'A'
        smart["flash_id"]                   = int.from_bytes(b[0:9], "big")
        smart["ic_version"]                 = "%02d.%02d" % (b[9], b[10])
        smart["fw_version"]                 = "%02d.%02d" % (b[11], b[12])
        smart["ce_number"]                  = b[14]
        smart["product_marker"]             = int.from_bytes(b[176:184], "big")
        smart["power_on_count"]             = int.from_bytes(b[112:116], "big")
        smart["power_off_abnormal_count"]   = int.from_bytes(b[128:130], "big")
        smart["endurance"]                  = int.from_bytes(b[96:98], "big") / 100.0
        smart["erase_count_min"]            = int.from_bytes(b[106:108] + b[100:102], "big")
        smart["erase_count_avg"]            = int.from_bytes(b[104:106] + b[ 98:100], "big")
        smart["erase_count_max"]            = int.from_bytes(b[108:110] + b[102:104], "big")
        smart["erase_count_total"]          = int.from_bytes(b[80:84], "big")
        smart["refresh_count_total"]        = int.from_bytes(b[160:162], "big")

        smart["blocks_bad"]                 = None
        smart["blocks_good_rate"]           = int.from_bytes(b[64:66], "big") / 100.0
        smart["blocks_spare"]               = int.from_bytes(b[16:18], "big")
        smart["blocks_bad_later_per_die"]   = [b[i] for i in range(184,216)]
        smart["blocks_bad"]                 = sum(smart["blocks_bad_later_per_die"])
        smart["blocks_bad_initial_per_die"] = [b[i] for i in range(32,64)]
        smart["blocks_bad_initial"]         = sum(smart["blocks_bad_initial_per_die"])
    # Transcend 2GB/4GB
    elif typ == 'T' and b[0:9] != b'Transcend':
        smart["type"] = 'T'
        smart["flash_id"]                   = int.from_bytes(b[0:9], "big")
        smart["ic_version"]                 = "%02d.%02d" % (b[9], b[10])
        smart["fw_version"]                 = "%02d.%02d" % (b[11], b[12])
        smart["ce_number"]                  = b[14]
        smart["product_marker"]             = b[176:185].decode("latin-1")
        smart["power_on_count"]             = int.from_bytes(b[112:116], "big")
        smart["power_off_abnormal_count"]   = int.from_bytes(b[128:130], "big")
        smart["endurance"]                  = int.from_bytes(b[96:98], "big") / 100.0
        smart["erase_count_min"]            = int.from_bytes(b[106:108] + b[100:102], "big")
        smart["erase_count_avg"]            = int.from_bytes(b[104:106] + b[ 98:100], "big")
        smart["erase_count_max"]            = int.from_bytes(b[108:110] + b[102:104], "big")
        smart["erase_count_total"]          = int.from_bytes(b[80:84], "big")
        smart["blocks_bad"]                 = int.from_bytes(b[32:36], "big")
        smart["blocks_spare_rate"]          = int.from_bytes(b[64:66], "big") / 100.0
    # Transcend >=8GB
    elif typ == 'T':
        smart["type"] = 'T'
        smart["flash_id"]                   = int.from_bytes(b[80:86], "big")
        smart["ic_version"]                 = b[88:96].decode("latin-1").strip()
        smart["fw_version"]                 = b[128:134].decode("latin-1").strip()
        smart["product_marker"]             = b[0:16].decode("latin-1").rstrip('\x00')
        smart["power_on_count"]             = int.from_bytes(b[76:80], "big")
        smart["power_off_abnormal_count"]   = int.from_bytes(b[28:32], "big")
        smart["endurance"]                  = b[70]
        smart["erase_count_min"]            = int.from_bytes(b[32:36], "big")
        smart["erase_count_avg"]            = int.from_bytes(b[44:48], "big")
        smart["erase_count_max"]            = int.from_bytes(b[36:40], "big")
        smart["blocks_bad"]                 = b[26]

    return smart

def smart_print(smart):
    """Print SMART-information.
    """
    print("Type:                     %s" % smart["type"])
    print("Flash ID:                 0x%018x" % smart["flash_id"])
    print("IC version:               %s" % smart["ic_version"])
    print("FW version:               %s" % smart["fw_version"])
    if "ce_number" in smart:
        print("CE number:                %d" % smart["ce_number"])
    if isinstance(smart["product_marker"], int):
        print("Product marker:           0x%016x" % smart["product_marker"])
    else:
        print("Product marker:           %s" % smart["product_marker"])

    print("Power on count:           %d" % smart["power_on_count"])
    print("Power off abnormal count: %d" % smart["power_off_abnormal_count"])
    print("Endurance:                %.2f %%" % smart["endurance"])

    print("Erase count min.:         %d" % smart["erase_count_min"])
    print("Erase count avg.:         %d" % smart["erase_count_avg"])
    print("Erase count max.:         %d" % smart["erase_count_max"])
    if "erase_count_total" in smart:
        print("Erase count total:        %d" % smart["erase_count_total"])
    if "refresh_count_total" in smart:
        print("Refresh count total:      %d" % smart["refresh_count_total"])

    print("Blocks, bad:              %d" % smart["blocks_bad"])
    if smart["type"] == "A":
        print("Blocks, good rate:        %05.02f %%" % smart["blocks_good_rate"])
        print("Blocks, spare count:      %d" % smart["blocks_spare"])
        print("Blocks, bad, initial:     %d (%s)" % (smart["blocks_bad_initial"], smart["blocks_bad_initial_per_die"]))
        print("Blocks, bad, later:       %d (%s)" % (smart["blocks_bad"], smart["blocks_bad_later_per_die"]))
    if "blocks_spare_rate" in smart:
        print("Blocks, spare rate:       %.2f %%" % smart["blocks_spare_rate"])

#=========================================

def main(arglist=None):
    """Parse raw smart data and print result.

    See module doctring for exit codes.
    """
    # parse arguments
    parser = argparse.ArgumentParser(
        description="""Parse raw SMART-information from industrial microSD-/SD-card.
Version %s by %s.""" % (__version__, __author__),
        formatter_class=argparse.RawDescriptionHelpFormatter,   # for keeping newlines in description
        epilog="""
Note that this does not work with USB-cardreaders.\n\
Supported cards:\n\
    - Transcend 240I\n\
    - Transcend 230I\n\
    - Apacer CH110-MSD / AK6.118*\n\
    - Apacer CV110-MSD / AK6.112*\n\
    - Apacer H2-SL / AP-*-2RTM\n\
    - Apacer H1-SL / AP-*-2HTM\n\
    - Apacer H2-M  / AP-*-1RTM\n\
    - Apacer H1-M  / AP-*-1HTM\n\
""")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-a", "--all",  action='store_true', help="Show all SMART-data.")
    group.add_argument("-e", "--endurance", action='store_true', help="Show only remaining endurance (as integer in percent).")
    #parser.add_argument("-f", "--field", action='store_true', help="Show only this field.")

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("-p", "--parsable", action='store_true', help="Print output in parsable format.")
    group.add_argument("-j", "--json",     action='store_true', help="Print output in JSON format.")

    parser.add_argument("-d", "--device", action='store', help="Retrieve raw SMART-data directly from SD-card via adva-sdcard-smart-get (instead of 'smartdata').")
    parser.add_argument("smartdata", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help='file containing raw SMART-data, default: stdin')
    parser.add_argument("--version", action='version', version="%(prog)s " + __version__)

    if arglist is None  and  len(sys.argv) <= 1:
        parser.print_help(sys.stderr)
        return 0
    args = parser.parse_args(arglist)

    # retrieve raw SMART-data
    if args.device:
        try:
            p = subprocess.run(["adva-sdcard-smart-get", args.device], capture_output=True, encoding='utf-8')
            if p.returncode == 0:
                raw = p.stdout.strip()
            else:
                print(p.stderr)
                return p.returncode
        except Exception as err:
            print("ERROR: Cannot get SMART-data from device. (%s)" % (err,), file=sys.stderr)
            return 5
    else:
        raw = args.smartdata.read(1500).strip()

    # check raw SMART-data
    if len(raw) == 1024:    # for backwards compatibility
        raw = "A-" + raw
    if len(raw) != 1026 or raw[1] != '-':
        print("ERROR: Invalid SMART raw data.", file=sys.stderr)
        return 22

    # parse raw SMART-data
    try:
        smart = smart_parse(raw)
    except ValueError as err:
        print("ERROR: Invalid SMART raw data. (%s)" % err, file=sys.stderr)
        return 22

    # print SMART-data
    if args.all:
        if   args.json:
            print(json.dumps(smart))
        elif args.parsable:
            for key,val in smart.items():
                print("%s: %s" % (key, val))
        else:
            smart_print(smart)
    elif args.endurance:
        print("%d" % smart["endurance"])
    return 0

#=========================================
if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(130)

#=========================================
