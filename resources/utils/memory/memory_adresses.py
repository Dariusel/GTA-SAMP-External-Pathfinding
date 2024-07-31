import win32gui, win32process
from pymem import Pymem
from resources.utils.memory.utils.memory_utils import *



# Get gta_sa base adress if gta_sa exists
gta_sa = try_get_gta_sa()
gta_sa_base_adress = gta_sa.base_address if gta_sa else None

# Get 'samp.dll' base address from all modules
if gta_sa:
    modules = gta_sa.list_modules()
    for module in modules:
        if module.name == 'samp.dll':
            samp_dll_base_address = module.lpBaseOfDll


# If gta_sa exists assign addresses
if gta_sa:
    # Variables
    PLAYER_X = gta_sa_base_adress + 0x76FF74 
    PLAYER_Y = gta_sa_base_adress + 0x76FF7C 
    PLAYER_Z = gta_sa_base_adress + 0x76FF78
    PLAYER_ANGLE_RADIANS = gta_sa_base_adress + 0x76FAB0

    GPS_BLIP_X = get_address_from_offsets(gta_sa_base_adress + 0x690750, [0x0, 0x0, 0x0, 0x0, 0x3C])
    GPS_BLIP_Y = get_address_from_offsets(gta_sa_base_adress + 0x690750, [0x0, 0x0, 0x0, 0x0, 0x44])
    GPS_BLIP_Z = get_address_from_offsets(gta_sa_base_adress + 0x690750, [0x0, 0x0, 0x0, 0x0, 0x40])

    GPS_MARKER_X = get_address_from_offsets(samp_dll_base_address + 0x21A10C, [0xC])
    GPS_MARKER_Y = get_address_from_offsets(samp_dll_base_address + 0x21A10C, [0x14])
    GPS_MARKER_Z = get_address_from_offsets(samp_dll_base_address + 0x21A10C, [0x10])
    
    CAR_SPEED = gta_sa_base_adress + 0x76F270
else:
    PLAYER_X = None
    PLAYER_Y = None
    PLAYER_Z = None
    PLAYER_ANGLE_RADIANS = None

    GPS_BLIP_X = None
    GPS_BLIP_Y = None
    GPS_BLIP_Z = None

    GPS_MARKER_X = None
    GPS_MARKER_Y = None
    GPS_MARKER_Z = None

    CAR_SPEED = None