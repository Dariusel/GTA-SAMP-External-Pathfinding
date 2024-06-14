from pymem import Pymem

def try_get_gta_sa():
    try:
        gta_sa = Pymem('gta_sa.exe')
        gta_sa_base_adress = gta_sa.base_address
        return gta_sa
    except Exception:
        gta_sa = None
        return None


# Get gta_sa base adress if gta_sa exists
gta_sa = try_get_gta_sa()
gta_sa_base_adress = gta_sa.base_address if gta_sa else None

if gta_sa:
    # Variables
    PLAYER_X = gta_sa_base_adress + 0x76FF74
    PLAYER_Y = gta_sa_base_adress + 0x76FF7C
    PLAYER_Z = gta_sa_base_adress + 0x76FF78
    
    PLAYER_ANGLE_RADIANS = gta_sa_base_adress + 0x76FAB0
    
    CAR_SPEED = gta_sa_base_adress + 0x76F270