from genesis.dbdict import *
from mud.world.defines import *

#--- Default gear

item = DBItemProto(name="Plain Helm")
item.skill = "Light Armor"
item.bitmap = "EQUIPMENT/HEAD/44"
item.model = "head/helmet.dts"
item.material="head/helmet"
item.slots = (RPG_SLOT_HEAD,)
item.flags=RPG_ITEM_SOULBOUND
item.armor = 2

item = DBItemProto()
item.itemType = ['UNIQUE']
item.name = "Magic Shield"
item.skill="Shields"
item.armor = 8
item.bitmap = "EQUIPMENT/SHIELDS/4"
item.model = "weapons/shield02.dts"
item.slots = (RPG_SLOT_SHIELD,)
item.flags = RPG_ITEM_ARTIFACT
item.addStat("agi",4)
item.addStat("dex",3)
item.addStat("maxHealth",25)
item.addStat("resistPoison",5)
item.addStat("defense",16)

item = DBItemProto()
item.itemType = ['COMMON','WEAPON']
item.name = "Longsword"
item.skill="1H Slash"
item.wpnDamage = 4
item.wpnRate = 11
item.wpnRange = 2
item.repairMax = 10
item.bitmap = "EQUIPMENT/SWORDS/24"
item.model = "weapons/sword01.dts"
item.worthCopper = 45
item.slots = (RPG_SLOT_PRIMARY,RPG_SLOT_SECONDARY)

item = DBItemProto()
item.itemType = ['COMMON','WEAPON']
item.name = "Broadsword"
item.skill="2H Slash"
item.wpnDamage = 8
item.wpnRate = 5
item.wpnRange = 4
item.repairMax = 10
item.flags=RPG_ITEM_COMMON
item.bitmap = "EQUIPMENT/SWORDS/25"
item.model = "weapons/fa_2hsh.dts"
item.worthCopper = 90
item.slots = (RPG_SLOT_PRIMARY,)

item = DBItemProto(name="Plain Shirt")
item.skill = "Light Armor"
item.bitmap = "EQUIPMENT/CHEST/9"
item.material = "tset_0_body"
item.slots = (RPG_SLOT_CHEST,)
item.flags=RPG_ITEM_SOULBOUND
item.armor = 1

item = DBItemProto(name="Plain Boots")
item.skill = "Light Armor"
item.bitmap = "EQUIPMENT/FEET/13"
item.material = "tset_0_feet"
item.slots = (RPG_SLOT_FEET,)
item.flags=RPG_ITEM_SOULBOUND
item.armor = 1


item = DBItemProto(name="Plain Arms")
item.skill = "Light Armor"
item.bitmap = "EQUIPMENT/ARMS/16"
item.material = "tset_0_arms"
item.slots = (RPG_SLOT_ARMS,)
item.flags=RPG_ITEM_SOULBOUND
item.armor = 1

item = DBItemProto(name="Plain Pants")
item.skill = "Light Armor"
item.bitmap = "EQUIPMENT/LEGS/16"
item.material = "tset_0_legs"
item.slots = (RPG_SLOT_LEGS,)
item.flags=RPG_ITEM_SOULBOUND
item.armor = 1

item = DBItemProto(name="Plain Gloves")
item.skill = "Light Armor"
item.bitmap = "EQUIPMENT/HANDS/2"
item.material = "tset_0_hands"
item.slots = (RPG_SLOT_HANDS,)
item.flags=RPG_ITEM_SOULBOUND
item.armor = 1


#---  Grey Wolf Hide
item = DBItemProto()
item.name = "Grey Wolf Hide"
item.desc = "This repugnant gray mass was once the skin of a fierce wolf."
item.bitmap = "EQUIPMENT/BACK/3"
item.flags = RPG_ITEM_SOULBOUND
item.stackMax = 20
item.stackDefault = 1

#--- Wolf Meat
item = DBItemProto(name="Wolf Meat")
item.desc = "The meaty parts of a wolf. Mmmm ... tastes like chicken."
item.stackMax = 100
item.stackDefault = 1
item.worthCopper = 10
item.bitmap = "STUFF/66"

#--- Foresting
item = DBItemProto() 
item.itemType = ['COMMON','TOOL'] 
item.name = "Small Wood Axe" 
item.skill="Foresting" 
item.wpnDamage = 4 
item.wpnRate = 11 
item.wpnRange = 2 
item.repairMax = 10 
item.bitmap = "EQUIPMENT/SWORDS/24" 
item.model = "weapons/sword01.dts" 
item.worthCopper = 45 
item.slots = (RPG_SLOT_PRIMARY,RPG_SLOT_SECONDARY)

#--- Mining
item = DBItemProto() 
item.itemType = ['COMMON','TOOL'] 
item.name = "Small Pick" 
item.skill="Mining" 
item.wpnDamage = 4 
item.wpnRate = 11 
item.wpnRange = 2 
item.repairMax = 10 
item.bitmap = "EQUIPMENT/SWORDS/24" 
item.model = "weapons/sword01.dts" 
item.worthCopper = 45 
item.slots = (RPG_SLOT_PRIMARY,RPG_SLOT_SECONDARY)
