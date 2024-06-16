from typing import List
from pymem import Pymem



def try_get_gta_sa():
    try:
        gta_sa = Pymem('gta_sa.exe')
        return gta_sa
    except Exception:
        gta_sa = None
        return gta_sa
    


gta_sa = try_get_gta_sa()
def get_address_from_offsets(base: int, offsets: List[int]):
    address = gta_sa.read_int(base)
    for i in offsets:
        if i != offsets[-1]:
            address = gta_sa.read_int(address + i)
    
    return address + offsets[-1]
