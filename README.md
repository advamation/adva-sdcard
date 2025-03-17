Advamation SD-card software
===========================

**Website:** http://www.advamation.de  
**Author:**  Advamation / Roland Freikamp \<support@advamation.de\>  
**Version:** 1.0.1 (2025-03-17)

Get information (CID, SMART) from microSD-/SD-cards.

Mainly intended to get SMART-/endurance-information from industrial
microSD-cards, e.g. on a Raspberry Pi.

Supported cards for SMART:

- Transcend industrial (micro)SD-cards, especially 230I and 240I
- Apacer industrial (micro)SD-cards (only "newer" ones, see below for a detailed list)

Note:

- Retrieving information from a card only works for mmc-block-devices,
  e.g. on the Raspberry Pi, and needs appropriate permissions.

  It does not (yet) work with USB-cardreaders, but it might work with
  some cardreaders in the future.  
  (For the Transcend cards, the SMART-information can currently be read
  with Transcend's ScopePro software with their RDF-cardreaders.)
- Parsing the retrieved raw information of course works everywhere.

**Important:**
> We strongly recommend industrial (micro)SD-cards for computing
> (e.g. Raspberry Pi) and all other applications, where reliability
> is important.
>
> We can especially recommend the **pSLC** ("pseudo SLC") types, since
> they have a much higher endurance than MLC and TLC, and are much
> cheaper than SLC.
>
> Consumer (micro)SD-cards may be cheaper, but they do not specify
> any reliability and are neither made for nor suited for reliable
> applications, and may die rather quickly e.g. on a Raspberry Pi!


Installation
------------

- for NixOS: see `adva-sdcard.nix`
- for Debian/Raspbian: use/build Debian-package
- for others:
  - make
  - make install

SD-card information
-------------------

Generic information:

- Manufacturer ID
- OEM/Application ID
- Product name
- Product revision
- Product serial number
- Manufacturing date
- CID
- CSD

This can be retrieved from `/sys/block/mmc*/device/`, or with `adva-sdcard-info`.

Usage:

- see `adva-sdcard-info --help`:

      usage: adva-sdcard-info [-h] [-p | -j] [-d DEVICE] [--version] [cid]

      Get/parse microSD-/SD-cards-information from mmc-device.
      Version 1.0.0 by Advamation <support@advamation.de>.

      positional arguments:
        cid                   CID as hex string or file containing the CID, default:
                              stdin

      optional arguments:
        -h, --help            show this help message and exit
        -p, --parsable        Print output in parsable format.
        -j, --json            Print output in JSON format.
        -d DEVICE, --device DEVICE
                              Retrieve CID directly from SD-card.
        --version             show program's version number and exit

      Examples:
          adva-sdcard-info 275048415...
          adva-sdcard-info -d /dev/mmcblk0
      Note that this does not work with USB-cardreaders.

- read raw CID-data as hex string:

      cat /sys/block/mmcblk0/device/cid

- parse + print CID-data:

      adva-sdcard-info CID_AS_HEX_STRING

- read, parse + print:

      adva-sdcard-info /sys/block/mmcblk0/device/cid
      # or
      adva-sdcard-info -d /dev/mmcblk0
      # or
      cat /sys/block/mmcblk0/device/cid | adva-sdcard-info -

- Examples with data:

      $ adva-sdcard-info -d /dev/mmcblk0
      CID:                   744a6055534455312030065689014c8d
      Manufacturer ID:       0x74
      OEM/Application ID:    J`
      Product name:          USDU1
      Product revision:      2.0
      Product serial number: 0x30065689
      Manufacturing date:    2020-12
      Checksum:              0x46

      $ adva-sdcard-info -p -d /dev/mmcblk0
      cid: 0x744a6055534455312030065689014c8d
      manfid: 0x74
      oemid: J`
      name: USDU1
      rev: 2.0
      serial: 0x30065689
      date: 2020-12
      crc: 0x46

SMART information
-----------------

Several industrial microSD-/SD-cards contain SMART-like information, which
can be read via CMD56. This software can read them from some industrial
cards from Transcend and Apacer (more may follow).

Supported cards:

- Transcend 240I
- Transcend 230I
- Apacer CH110-MSD / AK6.118...
- Apacer CV110-MSD / AK6.112...
- Apacer H2-SL / AP-MSD...-2RTM
- Apacer H1-SL / AP-MSD...-2HTM
- Apacer H2-M  / AP-MSD...-1RTM
- Apacer H1-M  / AP-MSD...-1HTM

Notes:

- Reading the (raw) SMART-information from the card requires full access
  to the block-device of the card, so `adva-sdcard-smart-get` is usually run
  as root. SETUID may be useful.
- `adva-sdcard-smart-get` is CPU-architecture-dependent, and may have to be
  recompiled for the desired architecture.
- `adva-sdcard-smart` can be run as user and is architecture-independent.

Permissions:

- `adva-sdcard-smart-get` currently needs to run as root.

Usage:

- `adva-sdcard-smart-get`:
  - read raw SMART-information as hex string (as root)
  - `adva-sdcard-smart-get --help`:

        usage: adva-sdcard-smart-get DEVICE

        Get raw SMART-information from industrial microSD-/SD-cards.
        Version 1.0.0 by Advamation <support@advamation.de>.

        Example: adva-sdcard-smart-get /dev/mmcblk0
        Note that this does not work with USB-cardreaders.
        ...

  - Example:

        $ adva-sdcard-smart-get /dev/mmcblk0
        T-5472616e7363656e64000000000000001000040305...

- `adva-sdcard-smart`:
  - parse raw SMART-information (as user)
  - optionally incl. reading it via `adva-sdcard-smart-get`
  - `adva-sdcard-smart --help`:

        usage: adva-sdcard-smart [-h] (-a | -e) [-p | -j] [-d DEVICE] [--version] [smartdata]

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
                                Retrieve raw SMART-data directly from SD-card via adva-sdcard-smart-get (instead of 'smartdata').
          --version             show program's version number and exit

        Note that this does not work with USB-cardreaders.
        ...

  - Examples:

        # print all SMART data
        echo SMART_RAW_DATA_AS_HEX_STRING | adva-sdcard-smart -a
        # get + print all SMART data
        adva-sdcard-smart -a -d /dev/mmcblk0
        # get endurance
        adva-sdcard-smart -e -d /dev/mmcblk0

- monitoring via cron:

      TODO

- Examples with data:

  - Transcend 240I, 20GB:

        $ sudo adva-sdcard-smart -a -d /dev/mmcblk0
        Type:                     T
        Flash ID:                 0x000000453e9803766c
        IC version:               SM2706AB
        FW version:               V1201
        Product marker:           Transcend
        Power on count:           21
        Power off abnormal count: 245
        Endurance:                100.00 %
        Erase count min.:         0
        Erase count avg.:         0
        Erase count max.:         1
        Blocks, bad:              0

  - Transcend 230I, 16GB:

        $ sudo adva-sdcard-smart-get /dev/mmcblk0
        T-5472616e7363656e64000000000000001000040304000000000b002d000000010000039500000419001d171d000003ee00000249000002bb00007a12000002b600003c3003e862000000000000000024453e98b3766b7400534d32373037454e00000000000000000fa00000000000010000000ad7b052d10000000000000000543034303820000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

        $ sudo adva-sdcard-smart -a -d /dev/mmcblk0
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

        $ sudo adva-sdcard-smart-get /dev/mmcblk0 | adva-sdcard-smart -a -p
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

        $ sudo adva-sdcard-smart -e -d /dev/mmcblk0
        98
        $ sudo adva-sdcard-smart-get /dev/mmcblk0 | adva-sdcard-smart -e
        98

  - Apacer MLC 8GB:

        $ sudo adva-sdcard-smart -a -d /dev/mmcblk0
        Type:                     A
        Flash ID:                 0x98de94937651080400
        IC version:               32.18
        FW version:               28.15
        CE number:                1
        Product marker:           0x0000000000000000
        Power up count:           49
        Power off abnormal count: 1
        Endurance:                99.94 %
        Blocks, good rate:        98.46 %
        Blocks, spare count:      16
        Blocks, bad, initial:     33 ([0, 33, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        Blocks, bad, later:       0 ([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        Erase count total:        2160
        Erase count min.:         2
        Erase count avg.:         2
        Erase count max.:         3
        Refresh count total:      0

