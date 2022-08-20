#!/usr/bin/env python3
"""

    subghz_decode_presets.py

    Decodes CC1101 settings from Flipper setting_user file or saved sameple file

    Warning:   this is total trash code, use at own risk

    Written By: Peter Shipley github.com/evilpete

    From pkg https://github.com/evilpete/flipper_toolbox

"""

# import sys
# import os
# import pprint
import argparse

from subghz_decode_presets import CC_Config    # CC_REG

# ppylint: disable=no-member

_DEBUG = 0

rf_presets = {
    # PresetOok270Async
    "AM270": ("Custom_preset_data: 02 0d 03 47 08 32 0b 06 14 00 "
              "13 00 12 30 11 32 10 67 18 18 19 18 1d 40 1c 00 1b "
              "03 20 fb 22 11 21 b6 00 00 00 C0 00 00 00 00 00 00"),

    # PresetOok650Async
    "AM650": ("Custom_preset_data: 02 0d 03 07 08 32 0b 06 14 00 13 "
              "00 12 30 11 32 10 17 18 18 19 18 1d 91 1c 00 1b 07 20 "
              "fb 22 11 21 b6 00 00 00 C0 00 00 00 00 00 00"),

    # Preset2FSKDev238Async
    "FM238": ("Custom_preset_data: 02 0d 0b 06 08 32 07 04 14 00 13 02 "
              "12 04 11 83 10 67 15 04 18 18 19 16 1d 91 1c 00 1b 07 20 "
              "fb 22 10 21 56 00 00 C0 00 00 00 00 00 00 00"),
    # Preset2FSKDev476Async
    "FM476": ("Custom_preset_data: 02 0d 0b 06 08 32 07 04 14 00 13 02 12 "
              "04 11 83 10 67 15 47 18 18 19 16 1d 91 1c 00 1b 07 20 fb 22 "
              "10 21 56 00 00 C0 00 00 00 00 00 00 00"),
}


# Intermediate_freq:        152343.75 Hz
# Modulations:              2FSK
# Data_Rate:                4797.94 Hz
# Bit_Width:                208.42 ms
# Channel_Bandwidth:        270833.33 Hz
# Deviation:                2380.37 Hz
# Sync_Mode:                SYNCM_CARRIER
# Channel_spacing:          101562.50 Hz
# Manchester:               0
# Variable_length_packet:   Infinite packet length
# Enable_Pkt_CRC:           0
# Preamble_Quality_Threshold: 0
# Pkt_DataWhitening         0
# Min_TX_Preamble:          0
# PA_Table:                 [192, 0, 0, 0, 0, 0, 0, 0]

MOD_2FSK = 0x00
MOD_GFSK = 0x10
MOD_ASK_OOK = 0x30
MOD_4FSK = 0x40
MOD_MSK = 0x70

# pkt_fmt = {
#     "Normal": 0x03,
#     "Sync":  0x01,
#     "Random":  0x02,
#     "Async":  0x03,
# }

mods = {
    "2FSK": 0x00,   # MOD_2FSK,
    "GFSK": 0x10,    # MOD_GFSK,
    "OOK": 0x30,     # MOD_ASK_OOK
    "4FSK": 0x40,    # MOD_4FSK  note: radio doesn't support Manchester encoding in 4FSK
    "MSK": 0x70,     # MOD_MSK
}

sync_modes = ['SYNCM_NONE', 'SYNCM_15_of_16', 'SYNCM_16_of_16', 'SYNCM_30_of_32',
              'SYNCM_CARRIER', 'SYNCM_CARRIER_15_of_16', 'SYNCM_CARRIER_16_of_16',
              'SYNCM_CARRIER_30_of_32']

sync_help = """
    SYNCM_NONE                      = 0
    SYNCM_15_of_16                  = 1
    SYNCM_16_of_16                  = 2
    SYNCM_30_of_32                  = 3
    SYNCM_CARRIER                   = 4
    SYNCM_CARRIER_15_of_16          = 5
    SYNCM_CARRIER_16_of_16          = 6
    SYNCM_CARRIER_30_of_32          = 7
"""


def _interpret_val(opt):
    opt = opt.upper()

    if opt in ["ON", "TRUE", "T", "YES", "Y", "1"]:
        return 1

    if opt in ["OFF", "FALSE", "F", "NO", "N", "0"]:
        return 0

    if opt.isdigit():
        return int(opt)

    return None


def arg_opts():
    """argument parse"""

    preset_namelist = sorted(rf_presets.keys())
    modulation_namelist = sorted(CC_Config.mod_num.values())
    length_namelist = sorted(CC_Config.PKT_LENGTH_CONF.keys())
    # pkt_fmt_namelist = sorted(pkt_fmt.keys())
    # modulation_namelist = sorted(mods.keys())
    # length_namelist = sorted(length_conf.keys())

    parser = argparse.ArgumentParser(add_help=True, allow_abbrev=True,
                        formatter_class=argparse.RawDescriptionHelpFormatter)
                        # argument_default=argparse.SUPPRESS,

    parser.add_argument("-p", "--preset", dest="preset_profile",
                        choices=preset_namelist,
                        default=None,
                        help="preset profile")

    parser.add_argument("-pr", "--print", dest="print_profile",
                        action='store_true',
                        default=None,
                        help="Print Profile Description")

    parser.add_argument("-sw", "--syncword", dest="sync_word",
                        type=int,
                        # choices=sync_modes,
                        default=None,
                        help="Sync Word")

    parser.add_argument("-sm", "--syncmode", dest="sync_mode",
                        type=int,
                        # choices=sync_modes,
                        default=None,
                        help=sync_help)

    parser.add_argument("-mod", "--modulation", dest="modulation",
                        choices=modulation_namelist,
                        default=None,
                        help="Modulation")

    parser.add_argument("-lc", "--length_conf", dest="length_conf",
                        choices=length_namelist,
                        default=None,
                        help="Length Config")

    # parser.add_argument("-pf", "--pktfmt", dest="pkt_fmt",
    #                     choices=length_namelist,
    #                     default=None,
    #                     help="Packet Format")

    parser.add_argument("-pl", "--pkt_len", dest="pkt_len",
                        type=int,
                        default=None,
                        help="Packet Length")

    parser.add_argument('-v', '--verbose', dest="verbose",
                        default=0,
                        help='Increase debug verbosity', action='count')

    parser.add_argument("-n", "--name", dest="conf_name",
                        default="NewPreset",
                        help="Name For Preset")

    parser.add_argument("-if", "--IntermediateFreq", dest="intermediate_freq",
                        type=int,
                        default=None,
                        help="Intermediate frequency")

    parser.add_argument("-dr", "--datarate", dest="data_rate",
                        type=int,
                        default=None,
                        help="Date Rate")

    parser.add_argument("-fr", "--frequency", dest="frequency",
                        type=int,
                        default=None,
                        help="frequency")

    parser.add_argument("-bw", "--bandwidth", dest="band_width",
                        type=int,
                        default=None,
                        help="Band Width")

    parser.add_argument("-np", "--numpreamble", dest="num_preamble",
                        type=int,
                        default=None,
                        help="Minimum number of preamble bytes to be transmitted\n"
                             "0=2bytes 1=3b 2=4b 3=6b 4=8b 5=12b 6=15b 7=24b"
                        )

    parser.add_argument("-dev", "--deviation", dest="deviation",
                        type=int,
                        default=None,
                        help="FM Deviation")

    parser.add_argument("-cs", "--channelspacing", "--spacing", dest="channel_spacing",
                        type=int,
                        default=None,
                        help="Channel Spacing")

    parser.add_argument("-man", "--manchester", dest="manchester",
                        default=False, action='store_true',
                        help="Manchester Encoding")

    # crc_grp = parser.add_mutually_exclusive_group()

    parser.add_argument("-crc", "--enable_crc", dest="enable_crc",
                        choices=['on', 'off'],
                        default=None,
                        help="Enable/Disable CRC")

    parser.add_argument("-dw", "--datawhitening", "--datawhite", dest="data_whiten",
                        choices=['on', 'off'],
                        default=None,
                        help="Enable/DisableData Whitening")


#    data_grp.add_argument("-c", "--cmd-file", dest="cmd_file",
#                          type=argparse.FileType('r', encoding='UTF-8'),
#                          default=None,
#                          help="Command File")

    return parser.parse_known_args()


def main():

    # print(rf_presets)

    reg_conf = CC_Config()

    args, u = arg_opts()

    # print(f"args: {args}\n")
    # print(f"u: {u}\n")

    if args.preset_profile:
        reg_conf.load_str(rf_presets[args.preset_profile])

    if args.deviation is not None:
        reg_conf.set_Deviatn(args.deviation)

    if args.modulation is not None:
        reg_conf.set_Modulation(args.modulation)

    if args.manchester is not None:
        reg_conf.set_Manchester(args.manchester)

    if args.length_conf is not None:
        reg_conf.set_Pktlen_conf(args.length_conf)

    if args.pkt_len is not None:
        if args.pkt_len > 255:
            raise ValueError("Max Packet Length 255")
        reg_conf.set_pktlen(args.pkt_len)

    if args.intermediate_freq is not None:
        reg_conf.set_FsIF(args.intermediate_freq)

    if args.data_rate is not None:
        reg_conf.set_DRate(args.set_DRate)

    if args.channel_spacing is not None:
        reg_conf.set_ChanSpc(args.channel_spacing)

    if args.enable_crc is not None:
        if args.enable_crc == 'on':
            reg_conf.set_Enable_CRC(enable=True)
        else:
            reg_conf.set_Enable_CRC(enable=False)

    if args.data_whiten is not None:
        if args.data_whiten == 'yes':
            reg_conf.set_PktDataWhitening(1)
        else:
            reg_conf.set_PktDataWhitening(1)

    if args.num_preamble is not None:
        reg_conf.set_NumPreamble(args.num_preamble)

    if args.band_width is not None:
        if args.band_width < 54170:
            raise ValueError("Bandwith must me over 54kHz")
        reg_conf.set_ChanBW(args.band_width)

    if args.frequency is not None:
        reg_conf.set_Freq(args.frequency)
        print("Warning: frequency is set in subghz flipper file")

    # if args.pkt_fmt is not None:

    mod = reg_conf.get_Modulation()
    manch = reg_conf.get_Manchester()

    if mod == 0x30 and args.deviation:
        print("Warning: Deviation value is ignored when modulation is 'OOK'")

    if mod is not None and manch is not None:
        if args.modulation == 0x40 and manch:
            print("Warning: radio doesn't support Manchester encoding in 4FSK")

    # print("as_preset_tuples:\n", pprint.pformat(reg_conf.as_preset_data_tuples(), compact=True))

    print("\n")
    print(f"Custom_preset_name: {args.conf_name}\n"
          "Custom_preset_module: CC1101\n"
          "Custom_preset_data:", reg_conf.as_preset_data())
    print("\n")

    if args.print_profile:
        for a, b in reg_conf.rf_conf():
            print(f"    {a:<28s} {b:<10s}")


if __name__ == '__main__':
    main()
