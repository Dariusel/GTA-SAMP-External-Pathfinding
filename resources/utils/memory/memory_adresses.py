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
        elif module.name == 'SAMPFUNCS.asi':
            sampfuncs_asi_base_address = module.lpBaseOfDll


# If gta_sa exists assign addresses
if gta_sa:
    # Variables
    PLAYER_X = gta_sa_base_adress + 0x76FF74 
    PLAYER_Y = gta_sa_base_adress + 0x76FF7C 
    PLAYER_Z = gta_sa_base_adress + 0x76FF78
    PLAYER_ANGLE_RADIANS = gta_sa_base_adress + 0x76FAB0

    GPS_BLIP_X = get_address_from_offsets(sampfuncs_asi_base_address + 0x115850, [0x18, 0xAC, 0x158, 0x194])
    GPS_BLIP_Y = get_address_from_offsets(sampfuncs_asi_base_address + 0x115850, [0x18, 0xAC, 0x158, 0x19C])
    GPS_BLIP_Z = get_address_from_offsets(sampfuncs_asi_base_address + 0x115850, [0x18, 0xAC, 0x158, 0x198])

    GPS_MARKER_X = get_address_from_offsets(samp_dll_base_address + 0x21A10C, [0xC])
    GPS_MARKER_Y = get_address_from_offsets(samp_dll_base_address + 0x21A10C, [0x14])
    GPS_MARKER_Z = get_address_from_offsets(samp_dll_base_address + 0x21A10C, [0x10])
    
    CAR_SPEED = gta_sa_base_adress + 0x76F270