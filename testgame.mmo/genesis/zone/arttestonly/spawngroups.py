from mud.world.defines import *
from genesis.dbdict import DBSpawnInfo,DBSpawnGroup

#--- wolf
wolf = DBSpawnInfo(spawn="Grey Wolf")
sg = DBSpawnGroup(zone="arttestonly",groupName="GREYWOLF")
sg.addSpawnInfo(wolf)
