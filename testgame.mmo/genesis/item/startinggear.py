from mud.world.defines import *
from genesis.dbdict import DBItemProto
from mud.world.character import StartingGear


RPG_REALM_DARKNESS_CLASSES =["Necromancer","Wizard","Cleric","Warrior","Barbarian","Tempest","Shaman","Assassin","Revealer","Thief","Doom Knight","Druid"]
RPG_REALM_LIGHT_CLASSES =["Shaman","Warrior","Paladin","Cleric","Tempest","Wizard","Monk","Barbarian","Thief","Druid","Bard","Ranger","Revealer"]

for cl in RPG_REALM_LIGHT_CLASSES:
    StartingGear(realm=RPG_REALM_LIGHT,classname=cl,items="Bottomless Pit,Key Ring,Drinking Water,Tasty Meal,Green Key,Red Key")

for cl in RPG_REALM_DARKNESS_CLASSES:
    StartingGear(realm=RPG_REALM_DARKNESS,classname=cl,items="Bottomless Pit,Key Ring,Drinking Water,Tasty Meal,Green Key,Red Key")
