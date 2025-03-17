Advamation SD-card software
===========================

**Website:** http://www.advamation.de  
**Author:**  Advamation / Roland Freikamp \<support@advamation.de\>  
**Version:** 1.0.1 (2021-09-10)

Get information (CID, SMART) from microSD-/SD-cards.

Note:

- Retrieving information from a card only works for mmc-block-devices,
  e.g. on the Raspberry Pi, and needs appropriate permissions.
  It (at least currently) does not work with USB-cardreaders.
- Parsing the retrieved raw information of course works everywhere.

**Important:**
> We strongly recommend industrial (micro)SD-cards for computing
> and all other applications where reliability is important.
>
> Consumer (micro)SD-cards may be cheaper, but they do not specify
> any reliability and are neither made for nor suited for reliable
> applications!


Installation
------------

- for NixOS: see adva-sdcard.nix
- for Debian/Raspbian: use Debian-package
- for others:
  - make
  - make install


Usage
-----

### SD-card information

Generic information (via CID etc.):

- Manufacturer ID
- OEM/Application ID
- Product name
- Product revision
- Product serial number
- Manufacturing date
- CID
- CSD

Usage:

- see `adva_sdcard_info --help`:

      usage: adva_sdcard_info [-h] [-p | -j] [-d DEVICE] [--version] [cid]

      Get/parse microSD-/SD-cards-information from mmc-device.
      Version 1.0.0 by Advamation <support@advamation.de>.

      positional arguments:
      cid                   CID as hex string or file containing the CID, default: stdin

      optional arguments:
      -h, --help            show this help message and exit
      -p, --parsable        Print output in parsable format.
      -j, --json            Print output in JSON format.
      -d DEVICE, --device DEVICE
                            Retrieve CID directly from SD-card.
      --version             show program's version number and exit

      Examples:
          adva_sdcard_info 275048415...
          adva_sdcard_info -d /dev/mmcblk0
      Note that this does not work with USB-cardreaders.

- read raw CID-data as hex string: `cat /sys/block/mmcblk0/device/cid`
- parse + print CID-data: `adva_sdcard_info CID_AS_HEX_STRING`
- read, parse + print:

      adva_sdcard_info /sys/block/mmcblk0/device/
      # or
      adva_sdcard_info -d /dev/mmcblk0
      # or
      cat /sys/block/mmcblk0/device/ | adva_sdcard_info

- Examples:

      $ adva_sdcard_info -d /dev/mmcblk0
      CID:                   744a6055534455312030065689014c8d
      Manufacturer ID:       0x74
      OEM/Application ID:    J`
      Product name:          USDU1
      Product revision:      2.0
      Product serial number: 0x30065689
      Manufacturing date:    2020-12
      Checksum:              0x46

      $ adva_sdcard_info -p -d /dev/mmcblk0
      cid: 0x744a6055534455312030065689014c8d
      manfid: 0x74
      oemid: J`
      name: USDU1
      rev: 2.0
      serial: 0x30065689
      date: 2020-12
      crc: 0x46

### SMART information

Several industrial microSD-/SD-cards contain SMART-like information;
this program can read them from some industrial cards from Apacer
and Transcend (more may follow).

Supported cards:

- Apacer H1-M  / AP-MSD...-1HTM
- Apacer H2-M  / AP-MSD...-1RTM
- Apacer H1-SL / AP-MSD...-2HTM
- Apacer H2-SL / AP-MSD...-2RTM
- Apacer CV110-MSD / AK6.112...
- Apacer CH110-MSD / AK6.118...
- Transcend 230I
- Transcend 240I

Notes:

- Reading the (raw) SMART-information from the card requires full access
  to the block-device of the card, so `adva_sdcard_smart_get` is usually run
  as root. SETUID may be useful.
- `adva_sdcard_smart_get` is CPU-architecture-dependent, and may have to be
  recompiled for the desired architecture.
- `adva_sdcard_smart` can be run as user and is architecture-independent.

Permissions:

- `adva_sdcard_smart_get` currently needs to run as root.

Usage:

- `adva_sdcard_smart_get`:
  - read raw SMART-information as hex string (as root)
  - example: `adva_sdcard_smart_get /dev/mmcblk0`
  - `adva_sdcard_smart_get --help`:

        usage: adva_sdcard_smart_get DEVICE

        Get raw SMART-information from industrial microSD-/SD-cards.
        Version 1.0.0 by Advamation <support@advamation.de>.

        Example: adva_sdcard_smart_get /dev/mmcblk0
        Note that this does not work with USB-cardreaders.

- `adva_sdcard_smart`:
  - parse raw SMART-information (as user)
  - optionally incl. call to `adva_sdcard_smart_get`
  - examples:

        # print all SMART data
        echo SMART_RAW_DATA_AS_HEX_STRING | adva_sdcard_smart -a
        # get + print all SMART data
        adva_sdcard_smart -a -d /dev/mmcblk0
        # get endurance
        adva_sdcard_smart -e -d /dev/mmcblk0

  - `adva_sdcard_smart --help`:

        usage: adva_sdcard_smart [-h] (-a | -e) [-p | -j] [-d DEVICE] [--version] [smartdata]

        Parse raw SMART-information from industrial microSD-/SD-cards.
        Version 1.0.0 by Advamation <support@advamation.de>.

        positional arguments:
          smartdata             file containing raw SMART-data, default: stdin

        optional arguments:
          -h, --help            show this help message and exit
          -a, --all             Show all SMART-data.
          -e, --endurance       Show only remaining endurance (in percent).
          -p, --parsable        Print output in parsable format.
          -j, --json            Print output in JSON format.
          -d DEVICE, --device DEVICE
                                Retrieve raw SMART-data directly from SD-card via adva_sdcard_smart_get (instead of 'smartdata').
          --version             show program's version number and exit

        Note that this does not work with USB-cardreaders.

- monitoring via cron:

      TODO

- Examples:

      # Transcend 230I, 16GB:
      $ sudo adva_sdcard_smart_get /dev/mmcblk0
      T-5472616e7363656e64000000000000001000040304000000000b002d000000010000039500000419001d171d000003ee00000249000002bb00007a12000002b600003c3003e862000000000000000024453e98b3766b7400534d32373037454e00000000000000000fa00000000000010000000ad7b052d10000000000000000543034303820000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

      $ sudo adva_sdcard_smart -a -d /dev/mmcblk0
      Type:                     T
      Flash ID:                 0x000000453e98b3766b
      IC version:               SM2707EN
      FW version:               T0408
      Product marker:           Transcend
      Power on count:           36
      Power off abnormal count: 1
      Endurance:                98.00 %
      Erase count min.:         917
      Erase count avg.:         1006
      Erase count max.:         1049
      Blocks, bad:              0

      $ sudo adva_sdcard_smart_get /dev/mmcblk0 | adva_sdcard_smart_get -a -p
      type: T
      flash_id: 76135152186987
      ic_version: SM2707EN
      fw_version: T0408
      product_marker: Transcend
      power_on_count: 36
      power_off_abnormal_count: 1
      endurance: 98
      erase_count_min: 917
      erase_count_avg: 1006
      erase_count_max: 1049
      blocks_bad: 0

      $ sudo adva_sdcard_smart -e -d /dev/mmcblk0
      98
      $ sudo adva_sdcard_smart_get /dev/mmcblk0 | adva_sdcard_smart -e
      98

      # Apacer:
      TODO

