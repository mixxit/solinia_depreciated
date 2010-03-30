# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

import os,sys,imp
from ConfigParser import SafeConfigParser

#Game Defaults...Change these only if you are instructed to via the instructions
GAMENAME = "Testgame MMO"
GAMEROOT = "testgame.mmo"
DEFAULT_GAME_CONFIG = "testgame"

MASTERIP = 'world.soliniaonline.com'
MASTERPORT = 2007

#GMSERVER_IP = "minions.prairiegames.com"
#GMSERVER_IP = "127.0.0.1"
GMSERVER_IP = "127.0.0.1"
GMSERVER_PORT = 1998

AHSERVER_IP = "127.0.0.1"
AHSERVER_PORT = 1999

MAILSERVER_IP = "127.0.0.1"
MAILSERVER_PORT = 2000

GLOBAL_IMMORTALS = ["mixxit","Kylethedarkn","HawkStorm"]
GLOBAL_GUARDIANS = []

IRC_SERVER = "world.soliniaonline.com"
IRC_PORT = 6667
IRC_CHANNEL_OFF_TOPIC = "#solinia_ot"
IRC_CHANNEL_GLOBAL = "#solinia"
IRC_CHANNEL_HELP = "#solinia_help"

DO_LAN_SERVER_FIX = 0
DO_WAN_SERVER_FIX = 1
GL_ANNOUNCE_IP = "world.soliniaonline.com"

USE_PNG_SVN = 1

DEFAULT_GAMENAME = "Solinia Online"
DEFAULT_GAMEROOT = GAMEROOT
DEFAULT_MASTERIP = MASTERIP
DEFAULT_MASTERPORT = MASTERPORT
DEFAULT_GMSERVER_IP = GMSERVER_IP
DEFAULT_GMSERVER_PORT = GMSERVER_PORT

SERVER_WORLD_USERNAME = "starter"
SERVER_WORLD_PASSWORD = "mmo"
SERVER_WORLD_SVN = "patchfiles"
SERVER_SVN_WORKING_REPO = "C:\\mygame\\" + SERVER_WORLD_SVN
SERVER_DEFAULT_PORT = 2006

SERVER_MANHOLE_USERNAME = "starter"
SERVER_MANHOLE_PASSWORD = "mmo"
SERVER_MANHOLE_PORT = 8192

SERVER_CSERVER_PASSWORD = "startermmo"


SERVER_EMAIL_ADDRESS = "michaelbollanduk@gmail.com"
SERVER_EMAIL_ACCOUNT = "michaelbollanduk@gmail.com"
SERVER_EMAIL_PASSWORD = "yu5itatm3whsj1982i4862110!"
SERVER_EMAIL_SERVER = "smtp.gmail.com"
SERVER_EMAIL_PORT = 587
SERVER_EMAIL_USE_GMAIL = 1

SERVER_MYSQL_USER = "myusername"
SERVER_MYSQL_PASSWORD = "mypassword"

SERVER_PATCH_PREMIUM = SERVER_WORLD_USERNAME + ":" + SERVER_WORLD_PASSWORD + "@http://" + MASTERIP + "/svn/" + SERVER_WORLD_SVN
SERVER_PATCH_DEMO = SERVER_WORLD_USERNAME + ":" + SERVER_WORLD_PASSWORD + "@http://" + MASTERIP + "/svn/" + SERVER_WORLD_SVN

CLUSTERNAMES = [
("base",),
]

WORLDNAMES = {"Premium_MMORPG": "TestDaemon"}

def main_is_frozen():
   return (hasattr(sys, "frozen") or # new py2exe
           hasattr(sys, "importers") # old py2exe
           or imp.is_frozen("__main__")) # tools/freeze


#IDE
def LoadGameConfiguration():
    global GAMENAME,GAMEROOT,MASTERIP,MASTERPORT

    if main_is_frozen():
        from binarygameconfig import GAMECONFIG
        sys.argv.append(GAMECONFIG)
    
    for arg in sys.argv:
        if arg.startswith("gameconfig="):
            config = arg[11:]
            
            if config != ".cfg":
                if os.path.exists('./projects'):
                    parser = SafeConfigParser()
                    parser.read("./projects/%s"%config)
            
                    GAMENAME = parser.get("Game Settings","Game Name")
                    GAMEROOT = parser.get("Game Settings","Game Root")
                    MASTERIP = parser.get("Game Settings","Master IP")
                    MASTERPORT = int(parser.get("Game Settings","Master Port"))
                    GMSERVER_IP = parser.get("Game Settings","GMServer IP")
                    GMSERVER_PORT = int(parser.get("Game Settings","GMServer Port"))
                return

    GAMENAME = DEFAULT_GAMENAME
    GAMEROOT = DEFAULT_GAMEROOT
    MASTERIP = DEFAULT_MASTERIP
    MASTERPORT = DEFAULT_MASTERPORT
    GMSERVER_IP = DEFAULT_GMSERVER_IP
    GMSERVER_PORT = DEFAULT_GMSERVER_PORT
    print "Using Defaults, to specify an alternative config: gameconfig=myconfig.cfg"
            

LoadGameConfiguration()
