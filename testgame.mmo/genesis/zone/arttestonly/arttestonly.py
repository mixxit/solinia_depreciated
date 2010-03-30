from mud.world.defines import *
from genesis.dbdict import DBZone
from mud.world.zone import ZoneLink

zone = DBZone()
zone.name = "arttestonly"
zone.niceName = "arttestonly"
zone.missionFile = "arttestonly.mis"
zone.climate = RPG_CLIMATE_TROPICAL
zone.immTransform = "31.7615 -274.927 115.2 0 0 -1 4.20118"

import spawns
import spawngroups
import items
import quests
