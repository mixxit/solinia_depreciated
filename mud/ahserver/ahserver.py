# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

import sys,os
sys.path.append(os.getcwd())

if sys.platform == "win32":
    from twisted.internet.iocpreactor import install
else:
    from twisted.internet.threadedselectreactor import install
install()

from twisted.internet import reactor
from mud.server.app import Server
from mud.server.config import ConfigureServer
from mud.common.permission import Role, User
from mud.common.avatar import Avatar,RoleAvatar
from mud.world.defines import *
from mud.common.persistent import Persistent,PersistentGhost
from sqlobject import *
from mud.gamesettings import *
from random import randint
from mud.world.item import ItemInstanceReceive
from mud.world.itemvariants import ItemVariantsAHSave,ItemVariantsAHLoad
from copy import copy
import shutil
from twisted.spread import pb
from twisted.cred.credentials import UsernamePassword

from md5 import md5
from time import strftime,time

from sqlite3 import dbapi2 as sqlite
#http://pypi.python.org/pypi/pylzma/0.3.0 - This is needed if it is not installed already!
import pylzma
import zlib
import traceback

AHSERVER_AVATAR_GLOBAL = None

print "\nAuction House Server"
print "->Initializing"

"""
DB Use Information
----------------------------------------
 ItemList - Information sent out to the player.  It is also used by the server to validate the item exists in the DB.  Items once finished are deleted.

 ItemTransactionDB - History DB for all transactions in the DB.  It keeps track of ItemList to ItemInstance matches, key values such as ending timestamp, seller,
                     inplay(still in DB, but will not be shortly).  Also some historical values such as the protoID, bid values, and purchased flag is kept so it
                     can be used to query that information while in play or use later if you wish to post the information online for economy tracking purposes.  This
                     DB does not delete its items and should never be sent to the players
  
 ItemInstance - Contains Instance information that pertains to the auction item such as stack, quality, repair, etc.  Used to create an instance of the item for both
                buying and selling
                
 ItemCharacterMapping - Unique IDs to map a Character to an ID
 
 ItemVarient - Contains an identical table to the item_variant table for items on the world side
----------------------------------------
"""
            
#Clear out the player IDs in the buffer
def clean_player_IDs():       
    count = 0
    shutil.copyfile("./data/character/character.db","./data/character/character.bak")
    #Open up the Character DB...isolation_level is needed if you wish to write to it
    dbconn = sqlite.connect("./data/character/character.db",isolation_level = None)
    dcursor = dbconn.cursor()
    dcursor.execute("BEGIN TRANSACTION;")
    #Going to get the buffer and the name of the character
    dcursor.execute("SELECT character_name, buffer from character_buffer;")
    #Loop through the results
    for name,buffer in dcursor.fetchall():
        try:
            #Decompress it using zlib
            dbuffer = zlib.decompress(buffer)
            #Write to a file so we can open it up as a DB
            f = file("./data/tmp/abuffer","wb")
            f.write(dbuffer)
            f.close()
            
            #Open that file up as a sqLite DB so we can work with it.  At this point it is decompressed
            bconn = sqlite.connect("./data/tmp/abuffer",isolation_level = None)
            bcursor = bconn.cursor()
            #Update the Auction IDN
            bcursor.execute("UPDATE character SET auction_id_n = 0")
            #Close DB and Cursor
            bcursor.close()
            bconn.close()
            
            #Going to open the file again this time to dump it into a buffer
            f = file("./data/tmp/abuffer","rb")
            dbuffer = f.read()
            f.close()
            
            #Compress the file and make sure it is binary
            dbuffer = zlib.compress(dbuffer)
            dbuffer = sqlite.Binary(dbuffer)
            #Values passed via the ? below.  Used to make SQLite happy about the BLOB value for the buffer
            values = (dbuffer,name)
            #Update the Character DB with the new buffer
            dcursor.execute("UPDATE character_buffer SET buffer = ? WHERE character_name = ?",values)   
            count += 1
        except:
            traceback.print_stack()
            print "AhServer: %s did not get an update to his/her character buffer"%name
            continue         
            
    dcursor.execute("END TRANSACTION;")
    dcursor.close()
    dbconn.close()
    print "Character IDs Cleaned: %d"%count
    
#FLUSH the DB, only do this if you want to delete everything!
if "dbreset" in sys.argv:
    dbconn = sqlite.connect("./data/ahserver/ahmaster.db",isolation_level = None)
    dcursor = dbconn.cursor()
    try:
        dcursor.execute("drop table ItemList")
        dcursor.execute("drop table ItemTransactionDB")
        dcursor.execute("drop table ItemInstance")
        dcursor.execute("drop table ItemCharacterMapping")
        dcursor.execute("drop table ItemVariant")
        dcursor.execute("vacuum ItemList")
        dcursor.execute("vacuum ItemTransactionDB")
        dcursor.execute("vacuum ItemInstance")
        dcursor.execute("vacuum ItemCharacterMapping")
        dcursor.execute("vacuum ItemVariant")
    except:
        pass
    dcursor.execute("BEGIN TRANSACTION;")
    dcursor.execute("create table ItemList(id INTEGER PRIMARY KEY AUTOINCREMENT, buyout_cost INTEGER, cost INTEGER, item_id INTEGER, time_left INTEGER, char_id INTEGER, bidder_id INTEGER);")
    dcursor.execute("create table ItemTransactionDB(id INTEGER PRIMARY KEY AUTOINCREMENT, item_list_id INTEGER, item_id INTEGER, time_end TIMESTAMP, seller TEXT, inplay BOOLEAN, \
                                                    item_proto_id INTEGER, last_bid INTEGER, last_bidder TEXT, purchased BOOLEAN, realm INTEGER);")
    dcursor.execute("create table ItemInstance(id INTEGER PRIMARY KEY AUTOINCREMENT, item_list_id INTEGER, stackCount INTEGER, useCharges INTEGER, quality INTEGER, food INTEGER, drink INTEGER, repairMax INTEGER, \
                                               repair INTEGER, lifeTime INTEGER, descOverride TEXT, levelOverride INTEGER, spellenhanceLevel INTEGER, bitmap TEXT, \
                                               hasVariants BOOLEAN, crafted BOOLEAN, name TEXT);")
    dcursor.execute("create table ItemCharacterMapping(id INTEGER PRIMARY KEY AUTOINCREMENT, charname TEXT UNIQUE COLLATE NOCASE);") 
    dcursor.execute("create table ItemVariant(id INTEGER PRIMARY KEY AUTOINCREMENT, code INTEGER, svalue TEXT, value INTEGER, item_list_id INTEGER, \
                                              value2 INTEGER, value3 INTEGER, value4 INTEGER, value5 INTEGER);") 
    
    dcursor.execute("create index index_item_list_trans ON ItemTransactionDB(item_list_id ASC);")                                         
    dcursor.execute("create index index_item_list_variant ON ItemVariant(item_list_id ASC);")
    dcursor.execute("create index index_item_list_instance ON ItemInstance(item_list_id ASC);")
    dcursor.execute("create index index_item_list_timestamp ON ItemTransactionDB(time_end ASC);")
    dcursor.execute("create index index_item_list_realm on ItemTransactionDB(realm ASC);")
    """
    for x in range(1,10000):
        cnt = randint(1,1500)
        bo = cnt*5000
        co = cnt*4000
        tl = randint(1,3)
        uni=0
        if (cnt >= 490):
            uni=1
        dcursor.execute("insert into ItemList values(NULL,%d,%d,%d,%d,%d);"%(bo,co,cnt,tl,uni))
        dcursor.execute("insert into ItemTransactionDB values(NULL, %d, %d, %f,'Xerves',1, %d, 0, '',0);"%(x,x,time()+7200,cnt))
        dcursor.execute("insert into ItemInstance values(NULL, %d, 1, 0, 1, 0, 0, 0, 0, 0, '', 0, 0, '', 0, 0);"%x)
    """
    dcursor.execute("END TRANSACTION;")
    dcursor.close()
    dbconn.close()
    clean_player_IDs()
    print "***Database is reset and cleaned***\n***Make sure to run upgrade.bat before launching the server***"
    sys.exit(0)
                  
#Auction House Master.  This is connected to via the proxies from the World Daemon.  We can only have 1 connection to the DB so this is needed -- X
class AhMaster():
    #Init the AH Master
    def __init__(self):
        global AHSERVER_AVATAR_GLOBAL
        self.MailServerPerspective = None
        self.ConnectToMailServer()
        #Connect the master DB up to the class so we can call it from a single source.  isolation_level is needed to write
        dbconn = sqlite.connect("./data/ahserver/ahmaster.db",isolation_level = None)
        self.dbconn = dbconn
        self.conn = dbconn.cursor()
        #Flush empty space
        self.conn.execute("vacuum ItemList")
        self.conn.execute("vacuum ItemTransactionDB")
        self.conn.execute("vacuum ItemInstance")
        self.conn.execute("vacuum ItemCharacterMapping")
        self.conn.execute("vacuum ItemVariant")
        #Begin Transaction process.  BE CAREFUL it writes every 10 seconds and transactions can be lost if server is shut down improperly
        self.conn.execute("BEGIN TRANSACTION;")
        #Expire auctions and change remaining time flags if needed
        self.checkTimeStamps()
        #Preps a client DB to be sent over the wire and updates the transaction processes.  Function recalls itself every 10 seconds
        self.clientDBUpdate()
        AHSERVER_AVATAR_GLOBAL = self
        self.tickSync = None
        self.timeStampSync = None
        
    #AH Sell failed post adding an item...lets revoke it so players aren't "duping"    
    def perspective_revokeAHSell(self,auctionID):
        self.conn.execute("UPDATE ItemTransactionDB set inplay=0 WHERE item_list_id=%d;"%auctionID) 
        self.conn.execute("DELETE from ItemList WHERE id = %s;"%auctionID)
        self.conn.execute("DELETE from ItemInstance WHERE item_list_id = %s;"%auctionID)
        self.conn.execute("DELETE from ItemVariant WHERE item_list_id = %s;"%auctionID)
        
    #Return Character Auction ID back to world/character
    def perspective_getCharacterAHID(self, charname):
        self.conn.execute("SELECT id FROM ItemCharacterMapping WHERE charname = '%s';"%charname)
        try:
            charid = self.conn.fetchone()[0]
            return charid
        except:
            self.conn.execute("INSERT INTO ItemCharacterMapping values (NULL, '%s');"%charname)
            charid = self.conn.execute("SELECT id FROM ItemCharacterMapping WHERE charname = '%s';"%charname).fetchone()[0]
            return charid
            
    #Revokes an item placed for sale if there is not a bid.  Returns it to the owner
    def perspective_checkRevoke(self, auctionID,charName):
        try:
            iid, bidder_id = self.conn.execute("SELECT item_id, bidder_id FROM ItemList WHERE id = %s;"%auctionID).fetchone()
            
            if not iid:
                return (None,None)
                
            if bidder_id:
                return (None,None)                         
            
            #Create an ItemInstance.  ItemInstanceReceive is a wrapper to send it to the Mail Server
            item = ItemInstanceReceive(None, True)
            #Populate the item with instance values
            item.setItemAH(self.conn,auctionID)
            #Set Auction values to be used by the world server and client
            item.auctionID = auctionID
            item.auctionItemID = iid
            self.MailServerPerspective.callRemote("MailProxyAvatar","sendRevoke",item,charName)
            self.perspective_revokeAHSell(auctionID)
            return (auctionID,item.name)
        except:
            return (None,None)

    #Place item for sale
    def perspective_placeForSale(self, item,bidTin,buyTin,charname,protoID,duration,slot,realm):
        #If for some reason something fails it will Fail out
        try:
            if duration == 1:
                durtime = 14400 #4 hours
            elif duration == 2:
                durtime = 28800 #8 hours
            else:
                durtime = 86400 #24 hours
                
            tstring = "datetime(%f, 'unixepoch', 'localtime')"%(time()+durtime)
            self.conn.execute("SELECT id FROM ItemCharacterMapping WHERE charname = '%s';"%charname)
            try:
                charid = self.conn.fetchone()[0]
            except:
                self.conn.execute("INSERT INTO ItemCharacterMapping values (NULL, '%s');"%charname)
                charid = self.conn.execute("SELECT id FROM ItemCharacterMapping WHERE charname = '%s';"%charname).fetchone()[0]
                
            self.conn.execute("insert into ItemList values(NULL,%d,%d,%d,%d,%d,0);"%(buyTin,bidTin,protoID,duration,charid))
            maxItemList = self.conn.execute("select MAX(id) from ItemList;").fetchone()[0]
            self.conn.execute("insert into ItemInstance values(NULL, %d, %d, %d, %d, %d, %d, %d, %d, %d, '%s', %d, %d, '%s', %d, %d, '%s');"%(maxItemList,item.stackCount,item.useCharges,item.quality,item.food,item.drink,item.repairMax,item.repair,item.lifeTime,item.descOverride,item.levelOverride,item.spellEnhanceLevel,item.bitmap,item.hasVariants,item.crafted,item.name))
            maxItemInstance = self.conn.execute("select MAX(id) from ItemInstance;").fetchone()[0]
            self.conn.execute("insert into ItemTransactionDB values(NULL, %d, %d, %s,'%s',1, %d, 0, '', 0, %d);"%(maxItemList,maxItemInstance,tstring,charname,protoID,realm))
            ItemVariantsAHSave(item, self.conn, maxItemList)
            return (maxItemList,charid)
        except:
            return (False,False)       
      
    #gets the Item Information from the DB and sends it to the client.  Used to view items in the Auction when you right click on it  
    def perspective_getItemInfo(self, id, iid):
        item = ItemInstanceReceive(None, True)
        item.setItemAH(self.conn,id)
        item.auctionID = id
        item.auctionItemID = iid
        return item        

    #All was good after the item was created on the buyout and the player was checked again, so clean up the DB
    def perspective_finishAHBuyout(self, cost,auctionID, iid, charname,seller,bidder_id,bid_cost):
        #Create an ItemInstance.  ItemInstanceReceive is a wrapper to send it to the Mail Server
        item = ItemInstanceReceive(None, True)
        #Populate the item with instance values
        item.setItemAH(self.conn,auctionID)
        #Set Auction values to be used by the world server and client
        item.auctionID = auctionID
        item.auctionItemID = iid
        self.MailServerPerspective.callRemote("MailProxyAvatar","sendWinnings",item,cost,charname,seller)
        
        if bidder_id:
            self.conn.execute("SELECT charname FROM ItemCharacterMapping WHERE id = %s;"%bidder_id)
            lastbidder = self.conn.fetchone()[0]  
            self.MailServerPerspective.callRemote("MailProxyAvatar","refundBidBuyout",bid_cost,lastbidder,item.name) 
        #Update Tables
        self.conn.execute("DELETE from ItemList WHERE id = %s;"%auctionID)
        self.conn.execute("DELETE from ItemInstance WHERE item_list_id = %s;"%auctionID)
        self.conn.execute("DELETE from ItemVariant WHERE item_list_id = %s;"%auctionID)
        # Transaction DB is historic and is not deleted
        self.conn.execute("UPDATE ItemTransactionDB set purchased=1 WHERE item_list_id=%d;"%auctionID) 
        return (auctionID,seller,item.name)
  
    #Not enough money on the player...blarg revoke the inplay flag      
    def perspective_revokeAHBuyout(self, auctionID):
        self.conn.execute("UPDATE ItemTransactionDB set inplay=1 WHERE item_list_id=%d;"%auctionID) 
        
    #Initial pass on the buyout.  Checking to make sure the purchase is valid and returning information to valid and sent to the mail server
    def perspective_buyout(self, auctionID, tin,playerID,prealm):
        try:           
            char_id, iid,buyout_cost,bidder_id,bid_cost = self.conn.execute("SELECT char_id, item_id, buyout_cost, bidder_id,cost FROM ItemList WHERE id = %s;"%auctionID).fetchone()
            
            if not char_id:
                return (0,0,0,None,0,0)
                
            if char_id == playerID:
                return (0,0,0,None,0,0)
                
            if (tin < buyout_cost):
                return (0,0,0,None,0,0)
            
            #Make sure the item is in play.  First come first serve
            r,seller,realm = self.conn.execute("SELECT inplay,seller,realm FROM ItemTransactionDB WHERE item_list_id = %s AND purchased = 0;"%auctionID).fetchone()  
            if r == None:
                return (0,0,0,None,0,0)
            
            if r <= 0:
                return (0,0,0,None,0,0)
                
            if not realm or prealm != realm:
                return (0,0,0,None,0,0)
                
        except:
            return (0,0,0,None,0,0)
            
        #Set item as out of play so it cannot be snatched
        self.conn.execute("UPDATE ItemTransactionDB set inplay=0 WHERE item_list_id=%d;"%auctionID) 
        return (buyout_cost,auctionID,iid,seller,bidder_id,bid_cost)        

    #All was good after the item was created on the buyout and the player was checked again, so clean up the DB
    def perspective_finishAHBid(self, cost,auctionID,charID,origcost,charname):   
        try:
            lastbidder = None
            self.conn.execute("SELECT bidder_id FROM ItemList WHERE id = %s;"%auctionID)
            bidder_id = self.conn.fetchone()[0]  
            
            self.conn.execute("SELECT name FROM ItemInstance WHERE item_list_id = %s;"%auctionID)
            item_name = self.conn.fetchone()[0]  
            
            if bidder_id:
                self.conn.execute("SELECT charname FROM ItemCharacterMapping WHERE id = %s;"%bidder_id)
                lastbidder = self.conn.fetchone()[0]  
                self.MailServerPerspective.callRemote("MailProxyAvatar","refundBid",origcost,lastbidder,item_name)   
            
            self.conn.execute("UPDATE ItemList set cost = %s,bidder_id = %s WHERE id=%d;"%(cost,charID,auctionID)) 
            self.conn.execute("UPDATE ItemTransactionDB set last_bidder = '%s', last_bid = %d WHERE item_list_id = %d;"%(charname, cost, auctionID))
            return (auctionID,lastbidder,item_name,cost)
        except:
            return (0,None,None,0)
        
    #Initial pass on the bid.  Checking to make sure the purchase is valid and returning the item in ItemInstance form
    def perspective_bid(self, auctionID, tin, playerID,prealm):
        try:
            char_id, bidder_id, cost =  self.conn.execute("SELECT char_id,bidder_id,cost FROM ItemList WHERE id = %s;"%auctionID).fetchone()
            
            if not char_id:
                return (0,0,0)
                
            if char_id == playerID or bidder_id == playerID:
                return (0,0,0)
            
            origcost = cost
            
            if bidder_id > 0:
                cost = int(cost * RPG_AUCTION_BIDCOST)
                
            if (tin < cost):
                return (0,0,0)
            
            #Make sure the item is in play.  First come first serve
            r,seller,realm = self.conn.execute("SELECT inplay,seller,realm FROM ItemTransactionDB WHERE item_list_id = %s AND purchased = 0;"%auctionID).fetchone()  
            if r == None:
                return (0,0,0)
            
            if r <= 0:
                return (0,0,0)
                
            if not realm or prealm != realm:
                return (0,0,0)
        except:
            return (0,0,0)
            
        return (cost,auctionID,origcost)
       
    #Called from the client to grab a DB.  The client DB is part of the main db that is client and realm information only. 
    def perspective_refreshAuctionList(self,realm):
        #Open the buffer to read the DB.  Keep in mind the DB was compressed earlier
        f = file("./data/ahserver/%s"%RPG_AUCTION_DBNAME[realm],"rb")
        cbuffer = f.read()
        f.close()
        return cbuffer
        
    #Checks for expired auctions and ones that need to be reflagged for duration.  Fairly high cost here if there are a lot of items.
    def checkTimeStamps(self):
        #Check to make sure Mail Server Connection is up
        if not self.MailServerPerspective:
            self.timeStampSync = reactor.callLater(5,self.checkTimeStamps)
            return
            
        count = 0   
        #Send some mails
        for auctionID,itemProtoID,seller,cost,buyer in self.conn.execute("select item_list_id,item_proto_id,seller,last_bid,last_bidder from ItemTransactionDB WHERE inplay = 1 AND time_end < datetime('now','localtime');"):
            item = ItemInstanceReceive(None, True)
            #Populate the item with instance values
            item.setItemAH(self.conn,auctionID)
            #Set Auction values to be used by the world server and client
            item.auctionID = auctionID
            item.auctionItemID = itemProtoID
            count += 1
            
            #If there was a bid send the item and winnings, if not sent the item back to the seller
            if cost:
                self.MailServerPerspective.callRemote("MailProxyAvatar","sendWinnings",item,cost,buyer,seller)
            else:               
                self.MailServerPerspective.callRemote("MailProxyAvatar","auctionTimeLimit",item,seller)  
        
        if count <= 0:
            self.timeStampSync = reactor.callLater(60,self.checkTimeStamps)
            return
            
        #Update Tables
        self.conn.execute("DELETE from ItemList WHERE id IN (select item_list_id from ItemTransactionDB WHERE inplay = 1 AND time_end < datetime('now','localtime'))" )
        self.conn.execute("DELETE from ItemInstance WHERE item_list_id IN (select item_list_id from ItemTransactionDB WHERE inplay = 1 AND time_end < datetime('now','localtime'))" )
        self.conn.execute("DELETE from ItemVariant WHERE item_list_id IN (select item_list_id from ItemTransactionDB WHERE inplay = 1 AND time_end < datetime('now','localtime'))" )
            
        #Remove the items from being in play
        self.conn.execute("UPDATE ItemTransactionDB set inplay=0 WHERE inplay = 1 AND time_end < datetime('now','localtime');") 
        #Calls itself again in 60 seconds.  Change accordingly if needed.
        self.timeStampSync = reactor.callLater(60,self.checkTimeStamps)
        
    #Character was deleted, so lets remove all references...
    def perspective_deleteCharacter(self,cname):
        try:
            self.conn.execute("SELECT id FROM ItemCharacterMapping WHERE charname = '%s';"%cname)
            charID = self.conn.fetchone()[0]  
            self.conn.execute('SELECT cost,bidder_id, id from ItemList WHERE char_id = %d;'%charID)
            for cost,bidderID, AHID in self.conn.fetchall():
                #Bidder found...Refund coins
                if bidderID > 0:
                    self.conn.execute("SELECT name FROM ItemInstance WHERE item_list_id = %s;"%AHID)
                    item_name = self.conn.fetchone()[0]             
                    self.conn.execute("SELECT charname FROM ItemCharacterMapping WHERE id = %s;"%bidderID)                    
                    lastbidder = self.conn.fetchone()[0]                      
                    self.MailServerPerspective.callRemote("MailProxyAvatar","refundBidDelete",cost,lastbidder,item_name)
                
                self.conn.execute('DELETE from ItemList WHERE id = %d;'%AHID)
                self.conn.execute('DELETE from ItemInstance WHERE item_list_id = %d;'%AHID)
                self.conn.execute('DELETE from ItemVariant WHERE item_list_id = %d;'%AHID)  
            self.conn.execute("DELETE FROM ItemCharacterMapping WHERE charname = '%s';"%cname)
        except:
            pass
            
            
    #Generate and clean client DBs based on the list in defines.py
    def generateClientDB(self,realm,realmDB):
        try:
            #Copy the master DB to the client DB
            shutil.copyfile("./data/ahserver/ahmaster.db","./data/ahserver/%s"%realmDB)
                        
            #Connecting to the client DB to flush out the extra tables we do not need to send over
            dbconn = sqlite.connect("./data/ahserver/%s"%realmDB,isolation_level = None)
            dcursor = dbconn.cursor()
            dcursor.execute("BEGIN TRANSACTION;")
            dcursor.execute("DELETE from ItemList WHERE id IN (select item_list_id FROM ItemTransactionDB WHERE realm != %d);"%realm)    
            dcursor.execute("drop table ItemTransactionDB")
            dcursor.execute("drop table ItemInstance")
            dcursor.execute("drop table ItemCharacterMapping")
            dcursor.execute("drop table ItemVariant")
            dcursor.execute("END TRANSACTION;")  
            dcursor.execute("vacuum ItemTransactionDB")
            dcursor.execute("vacuum ItemInstance")
            dcursor.execute("vacuum ItemCharacterMapping")
            dcursor.execute("vacuum ItemVariant")
            dcursor.close()
            dbconn.close()        
        
            #Compress the client DB.  Better to do this once every 10 seconds than a bunch of times under heavy load of client requests
            f = file("./data/ahserver/%s"%realmDB,"rb")
            cbuffer = f.read()
            cbuffer = pylzma.compress(cbuffer,algorithm=0)      
            cbuffer = sqlite.Binary(cbuffer)
            f.close()
            f = file("./data/ahserver/%s"%realmDB,"wb")
            f.write(cbuffer)
            f.close()     
        except:
            print "Failed to write %s to disk"%realmDB                           
        
    #Updates the DB with all changes by committing the transactions.  It also creates the client databases to be sent to the clients during this time
    def clientDBUpdate(self):
        try:
            #Ends the transaction and forces the changes to the master database
            self.conn.execute("END TRANSACTION;")
        except:
            print "Error: Failed to Commit Transaction.  Make sure you don't have the DB open and locked"
            
        #Generate client DBs per realm.  Realm can be anything, just don't go nuts.
        for realm,realmDB in RPG_AUCTION_DBNAME.iteritems():
            self.generateClientDB(realm,realmDB)            
            
        try:
            #Start the transaction process back up
            self.conn.execute("BEGIN TRANSACTION;")
        except:
            print "Error: Failed to Begin Transaction.  Make sure you don't have the DB open and locked"

        #Calls itself again in 10 seconds.  Change accordingly if needed.
        self.tickSync = reactor.callLater(10,self.clientDBUpdate)  
        
    #Below 3 functions create a connection to the mail server and tie the perspective to this class    
    def MSConnected(self, perspective):
        self.MailServerPerspective = perspective
        
    def MSFailure(self, error):
        print "Mail Server Connection Error",error
        
    def ConnectToMailServer(self):
        print "Connecting to Mail Server Proxy at: %s"%MAILSERVER_IP
        factory = pb.PBClientFactory()
        reactor.connectTCP(MAILSERVER_IP,MAILSERVER_PORT,factory)
        password = md5("MSP").digest()
        
        factory.login(UsernamePassword("MSP-MSP", password),pb.Root()).addCallbacks(self.MSConnected, self.MSFailure)
  
    #Close databases, rather important when the world daemon reboots
    def logout(self):
        self.conn.execute("END TRANSACTION;")
        self.conn.close()
        self.dbconn.close()
        if self.tickSync:
            try:
                self.tickSync.cancel()
            except:
                pass
            self.tickSync = None
            
        if self.timeStampSync:
            try:
                self.timeStampSync.cancel()
            except:
                pass
            self.timeStampSync = None
            
        print "Logout from the Auction Server is Complete"

#Auction House Class.  This is a proxy to push commands back up to the master so we can have multiple connections from World Clusters
class AHAvatar(Avatar):
    #Init the AH Avatar.  
    def __init__(self, username, role, mind):
        global AHSERVER_AVATAR_GLOBAL
        #Avatar information used by system to system communication (AH <--> World)
        Avatar.__init__(self,username,role,mind)
        self.username = username
        self.role = role
        self.mind = mind
        self.masterConn = None
        if not AHSERVER_AVATAR_GLOBAL:
            #Start the master connection to the DB
            AhMaster()
        
    def checkProxyConn(self):
        global AHSERVER_AVATAR_GLOBAL
        if not self.masterConn:
            if not AHSERVER_AVATAR_GLOBAL:
                print "FATAL ERROR CONNECTING WORLD PROXY TO AUCTION SERVER!!!"
                return False
            else:
                self.masterConn = AHSERVER_AVATAR_GLOBAL 
                
        return True        
        
    #AH Sell failed post adding an item...lets revoke it so players aren't "duping"    
    def perspective_revokeAHSell(self,auctionID):
        if not self.checkProxyConn():
            return
        
        return self.masterConn.perspective_revokeAHSell(auctionID)
        
    #Return Character Auction ID back to world/character
    def perspective_getCharacterAHID(self, charname):
        if not self.checkProxyConn():
            return
        
        return self.masterConn.perspective_getCharacterAHID(charname)
            
    #Revokes an item placed for sale if there is not a bid.  Returns it to the owner
    def perspective_checkRevoke(self, auctionID,charName):
        if not self.checkProxyConn():
            return
        
        return self.masterConn.perspective_checkRevoke(auctionID,charName)

    #Place item for sale
    def perspective_placeForSale(self, item,bidTin,buyTin,charname,protoID,duration,slot,realm):
        if not self.checkProxyConn():
            return
        
        return self.masterConn.perspective_placeForSale(item,bidTin,buyTin,charname,protoID,duration,slot,realm)      
      
    #gets the Item Information from the DB and sends it to the client.  Used to view items in the Auction when you right click on it  
    def perspective_getItemInfo(self, id, iid):
        if not self.checkProxyConn():
            return
        
        return self.masterConn.perspective_getItemInfo(id, iid)     

    #All was good after the item was created on the buyout and the player was checked again, so clean up the DB
    def perspective_finishAHBuyout(self, cost,auctionID, iid, charname,seller,bidder_id,bid_cost):
        if not self.checkProxyConn():
            return
        
        return self.masterConn.perspective_finishAHBuyout(cost,auctionID, iid, charname,seller,bidder_id,bid_cost)
  
    #Not enough money on the player...blarg revoke the inplay flag      
    def perspective_revokeAHBuyout(self, auctionID):
        if not self.checkProxyConn():
            return
        
        return self.masterConn.perspective_revokeAHBuyout(auctionID)
        
    #Initial pass on the buyout.  Checking to make sure the purchase is valid and returning information to valid and sent to the mail server
    def perspective_buyout(self, auctionID, tin,playerID,prealm):
        if not self.checkProxyConn():
            return
        
        return self.masterConn.perspective_buyout(auctionID, tin,playerID,prealm)

    #All was good after the item was created on the buyout and the player was checked again, so clean up the DB
    def perspective_finishAHBid(self, cost,auctionID,charID,origcost,charname):   
        if not self.checkProxyConn():
            return
        
        return self.masterConn.perspective_finishAHBid(cost,auctionID,charID,origcost,charname)
        
    #Initial pass on the bid.  Checking to make sure the purchase is valid and returning the item in ItemInstance form
    def perspective_bid(self, auctionID, tin, playerID,prealm):
        if not self.checkProxyConn():
            return
        
        return self.masterConn.perspective_bid(auctionID, tin, playerID,prealm)
       
    #Called from the client to grab a DB.  The client DB is part of the main db that is client and realm information only. 
    def perspective_refreshAuctionList(self,realm):
        if not self.checkProxyConn():
            return
        
        return self.masterConn.perspective_refreshAuctionList(realm)    
        
    #Character was deleted, so lets remove all references...
    def perspective_deleteCharacter(self,cname):
        if not self.checkProxyConn():
            return
        
        return self.masterConn.perspective_deleteCharacter(cname)                    
          
    #Nothing.
    def logout(self):
        return
        
#Configure connection and User for AH <--> World Server.  Connection is AH to World Server since it should be fast and on the same machine/local network
def ConfigureRoles():
    ah = Role(name="AH")
    RoleAvatar(name="AHAvatar",role=ah)
    
def ConfigureUsers():
    reg = User(name="AH",password="AH")
    reg.addRole(Role.byName("AH"))

#Database setup for communications with World Server
sys.argv.append('database=data/ahserver')
ConfigureServer("ahcommunication.db")

#Drop tables on the comm DB
TABLES = [Role,RoleAvatar,User]
for t in TABLES:
    t.dropTable(ifExists=True)
    t.createTable()

ConfigureRoles()
ConfigureUsers()
    
#Start Services to ready a connection from the World Server
server = Server(AHSERVER_PORT,True)    # True to use md5 hashing for passwords
server.startServices()

print "->AH Server is up"
reactor.run()

if AHSERVER_AVATAR_GLOBAL:
    print "Dumping the Transactions to Database"
    AHSERVER_AVATAR_GLOBAL.conn.execute("END TRANSACTION;")
    AHSERVER_AVATAR_GLOBAL.conn.close()
    AHSERVER_AVATAR_GLOBAL.dbconn.close()
    print "Cleanly shutdown the Auction Server!"
    sys.exit()
    
print "Error, could not find the AHServer Avatar, shutdown was not clean!"

