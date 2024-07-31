import sys, os
from time import sleep
from threading import Thread
from .memory_adresses import (
    gta_sa as gta, 
    PLAYER_X, PLAYER_Y, PLAYER_Z, PLAYER_ANGLE_RADIANS,
    CAR_SPEED,
    GPS_BLIP_X, GPS_BLIP_Y, GPS_BLIP_Z,
    GPS_MARKER_X, GPS_MARKER_Y, GPS_MARKER_Z
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from resources.utils.vectors import Vector3



# Singleton instance
class GameData:
    _instance = None
    update_interval = 0.005

    gta_sa = None
    player_pos = None
    player_angle_radians = None
    car_speed = None
    blip_pos = None
    marker_pos = None

    def __new__(cls):
        if cls._instance:
            return
        
        cls._instance = super().__new__(cls)
        cls._instance.assign_values()
        Thread(target=cls._instance.update_values, daemon=True).start()


    def assign_values(self):
        if not gta:
            GameData.gta_sa = None
            return
        
        GameData.gta_sa = gta
        # Player
        GameData.player_pos = Vector3(gta.read_float(PLAYER_X),
                                              gta.read_float(PLAYER_Y),
                                              gta.read_float(PLAYER_Z))
        GameData.player_angle_radians = gta.read_float(PLAYER_ANGLE_RADIANS)

        # Car
        GameData.car_speed = gta.read_float(CAR_SPEED)

        # GPS Blip
        GameData.blip_pos = Vector3(gta.read_float(GPS_BLIP_X),
                                    gta.read_float(GPS_BLIP_Y),
                                    gta.read_float(GPS_BLIP_Z))
        
        # GPS Marker
        GameData.marker_pos = Vector3(gta.read_float(GPS_MARKER_X),
                                      gta.read_float(GPS_MARKER_Y),
                                      gta.read_float(GPS_MARKER_Z))

    def update_values(self):
        while True:
            try:
               self.assign_values()
            except:
                print('gta sa not found')
                GameData.gta_sa = None
            
            sleep(GameData.update_interval)

GameData()