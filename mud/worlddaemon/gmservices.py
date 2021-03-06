# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from twisted.internet import reactor
from twisted.spread import pb
from twisted.cred.credentials import UsernamePassword

from mud.gamesettings import *
from mud.common.permission import User

from md5 import md5
import traceback



class GMServices(pb.Root):
    
    def __init__(self, worldName):
        self.perspective = None
        self.worldName = worldName
        self.avatars = []
    
    
    def connected(self, perspective):
        self.perspective = perspective
    
    
    def failure(self, reason):
        print reason.getErrorMessage()
    
    
    def connect(self):
        factory = pb.PBClientFactory()
        
        try:
            reactor.connectTCP(GMSERVER_IP,GMSERVER_PORT,factory)
            
            password = md5(WORLDNAMES[self.worldName]).digest()
            
            d = factory.login(UsernamePassword("%s-WorldDaemon"% \
                self.worldName,password),self)
            d.addCallback(self.connected)
            d.addErrback(self.failure)
        except KeyError:
            print "World Daemon couldn't connect to GM server, password not found."
        except:
            print "Error connecting World Daemon to GM server!"
    
    
    def disconnect(self):
        if self.perspective:
            self.perspective.broker.transport.loseConnection()
            self.perspective = None
    
    
    def registerZoneClusterAvatars(self, avatars):
        self.zoneClusterAvatars = avatars
    
    
    def remote_receiveGMChat(self, name, msg):
        for avatar in self.zoneClusterAvatars:
            try:
                avatar.mind.callRemote("receiveGMChat",name,msg)
            except:
                traceback.print_exc()
    
    
    def remote_sendGuildMsg(self, name, msg, guildName):
        for avatar in self.zoneClusterAvatars:
            try:
                avatar.mind.callRemote("sendGuildMsg",name,msg,guildName)
            except:
                traceback.print_exc()


