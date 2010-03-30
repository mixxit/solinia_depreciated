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
from mud.common.persistent import Persistent,PersistentGhost
from sqlobject import *
from mud.gamesettings import *
from random import randint
from mud.world.item import ItemInstanceReceive, MailItem
from mud.world.itemvariants import ItemVariantsAHSave,ItemVariantsAHLoad
from copy import copy
import shutil

from md5 import md5
from time import strftime,time

from sqlite3 import dbapi2 as sqlite
#http://pypi.python.org/pypi/pylzma/0.3.0 - This is needed if it is not installed already!
import pylzma
import traceback

print "\nMail Server"
print "->Initializing"

MAILCONNECT = None

"""
DB Use Information
----------------------------------------
 MailStore - Core table with all of the mail data.

 Message - List of messages attached to the mails.  You can specify some default messages if you wish and leave them in the DB.
  
 ItemInstance - Contains Instance information that pertains to the auction item such as stack, quality, repair, etc.  Used to create an instance of the item for both
                buying and selling
                
 ItemCharacterMapping - Unique IDs to map a Character to an ID
 
 ItemVarient - Contains an identical table to the item_variant table for items on the world side
----------------------------------------
"""
            
#FLUSH the DB, only do this if you want to delete everything!
if "dbreset" in sys.argv:
    dbconn = sqlite.connect("./data/ahserver/mailmaster.db",isolation_level = None)
    dcursor = dbconn.cursor()
    try:
        dcursor.execute("drop table MailStore")
        dcursor.execute("drop table ItemInstance")
        dcursor.execute("drop table ItemVariant")
        dcursor.execute("vacuum MailStore")
        dcursor.execute("vacuum ItemVariant")
        dcursor.execute("vacuum ItemInstance")
    except:
        pass
    dcursor.execute("BEGIN TRANSACTION;")
    dcursor.execute("create table MailStore(id INTEGER PRIMARY KEY AUTOINCREMENT, message_to TEXT COLLATE NOCASE, message_from TEXT COLLATE NOCASE, subject TEXT, item_proto INTEGER, message TEXT, tin INTEGER,time_end TIMESTAMP);")
    dcursor.execute("create table ItemInstance(id INTEGER PRIMARY KEY AUTOINCREMENT, item_list_id INTEGER, stackCount INTEGER, useCharges INTEGER, quality INTEGER, food INTEGER, drink INTEGER, repairMax INTEGER, \
                                               repair INTEGER, lifeTime INTEGER, descOverride TEXT, levelOverride INTEGER, spellenhanceLevel INTEGER, bitmap TEXT, \
                                               hasVariants BOOLEAN, crafted BOOLEAN, name TEXT);")
    dcursor.execute("create table ItemVariant(id INTEGER PRIMARY KEY AUTOINCREMENT, code INTEGER, svalue TEXT, value INTEGER, item_list_id INTEGER, \
                                              value2 INTEGER, value3 INTEGER, value4 INTEGER, value5 INTEGER);") 
                                              
    dcursor.execute("create index index_message_to ON MailStore(message_to ASC);")
    dcursor.execute("create index index_item_list_variant ON ItemVariant(item_list_id ASC);")
    dcursor.execute("create index index_item_list_instance ON ItemInstance(item_list_id ASC);")
    dcursor.execute("create index index_message_timestamp ON MailStore(time_end ASC);")
    dcursor.execute("END TRANSACTION;")
    dcursor.close()
    dbconn.close()           
    print "***Database is reset and cleaned****"
    sys.exit(0)       

#Mail Server Master Class.  The World Clusters and the Auction Server proxy into this class
class MailMaster():
    #Init the Mail Server Master
    def __init__(self):
        global MAILCONNECT
        #Backup Counter
        self.backupCounter = 1
        #Connect the master DB up to the class so we can call it from a single source.  isolation_level is needed to write
        dbconn = sqlite.connect("./data/ahserver/mailmaster.db",isolation_level = None)
        self.dbconn = dbconn
        self.conn = dbconn.cursor()
        #Clean up empty space
        self.conn.execute("vacuum MailStore")
        self.conn.execute("vacuum ItemVariant")
        self.conn.execute("vacuum ItemInstance")
        #Begin Transaction process.  BE CAREFUL it writes every 10 seconds and transactions can be lost if server is shut down improperly
        self.conn.execute("BEGIN TRANSACTION;")
        #Expires mail
        self.checkTimeStamps()
        #DB update...mainly to commit
        self.DBUpdate()
        self.tickSync = None
        self.timeStampSync = None
        MAILCONNECT = self
        
    #Checks for expired auctions and ones that need to be reflagged for duration.  Fairly high cost here if there are a lot of items.
    #Also has the DB Update Check
    def checkTimeStamps(self):          
        count = 0   
            
        #Update Tables
        try:
            #Update Tables
            self.conn.execute("DELETE from ItemInstance WHERE item_list_id IN (select id from MailStore WHERE time_end < datetime('now','localtime'))" )
            self.conn.execute("DELETE from ItemVariant WHERE item_list_id IN (select id from MailStore WHERE time_end < datetime('now','localtime'))" )
            self.conn.execute("DELETE from MailStore WHERE time_end < datetime('now','localtime')")
        except:
            traceback.print_exc()
        
        #Backup DBs
        self.backupCounter -= 1
        if not self.backupCounter:    
            print "Backing up AH and Mail databases"
            self.backupCounter = 80 #once every 80 minutes
            try:
                self.BackupDB("./data/ahserver/mailmaster.db")
                self.BackupDB("./data/ahserver/ahmaster.db")
                self.BackupDB("./data/ahserver/itemProtoDB.db")
            except:
                traceback.print_exc()
            
        #Calls itself again in 60 seconds.  Change accordingly if needed.
        self.timeStampSync = reactor.callLater(60,self.checkTimeStamps)
        
    def BackupDB(self,filename):
        import datetime

        n = datetime.datetime.now()
        s = n.strftime("%B_%d_%Y")
        d,f = os.path.split(filename)
    
        f,ext = os.path.splitext(f)
    
        backfolder = d+"/"+s
        if not os.path.exists(backfolder):
            os.makedirs(backfolder)
        
        x = 1
        while True:
            backupfile = backfolder+"/"+"%s_backup_%i%s"%(f,x,ext)
            if os.path.exists(backupfile):
                x+=1
                continue
        
        
            shutil.copyfile(filename,backupfile)
            break
        
    #Updates the DB with all changes by committing the transactions.
    def DBUpdate(self):
        try:
            #Ends the transaction and forces the changes to the master database
            self.conn.execute("END TRANSACTION;")
        except:
            print "Error: Failed to Commit Transaction.  Make sure you don't have the DB open and locked"             
        
        try:
            #Start the transaction process back up
            self.conn.execute("BEGIN TRANSACTION;")
        except:
            print "Error: Failed to Begin Transaction.  Make sure you don't have the DB open and locked"            
                
        #Calls itself again in 10 seconds.  Change accordingly if needed.
        self.tickSync = reactor.callLater(10,self.DBUpdate)                  

    def perspective_refreshInboxList(self, charName, lastID):
        #Find all the mail since the last update (or first update)..a handful of joins here
        cnt = 0
        mailList = {}
        query = "SELECT id, message_from,subject,message_to,tin,message,time_end,item_proto from MailStore \
                 WHERE id > %d and message_to = '%s';"%(lastID,charName)
        for id, mail_from, subject, mail_to, tin, message, time_end, itemProto in self.conn.execute(query):
            cnt += 1
            mailList[id] = MailItem(mail_from, subject, mail_to, tin, message, time_end,id)
            mailList[id].itemProto = itemProto
            
        if cnt < 1:
            return None
        else:
            for id, mail in mailList.iteritems():
                if mail.itemProto:
                    item = ItemInstanceReceive(None, True)
                    #Populate the item with instance values
                    item.setItemAH(self.conn,id)
                    #Set Auction values to be used by the world server and client
                    item.auctionID = id
                    item.auctionItemID = mail.itemProto
                    mailList[id].item = item
            return mailList            
            
    def perspective_sendMail(self, mail,protoID):
        #Use the ID from the server if it is valid
        try:
            durtime = 86400*14 #14 days
                
            tstring = "datetime(%f, 'unixepoch', 'localtime')"%(time()+durtime)
            #Insert the message info into the MailStore.  Make sure to clean characters first though
            mailTo = mail.mail_to.replace("'", "''")
            mailFrom = mail.mail_from.replace("'", "''")
            mailSubject = mail.subject.replace("'", "''")
            mailMessage = mail.message.replace("'", "''")
            
            self.conn.execute("INSERT INTO MailStore VALUES(NULL, '%s','%s','%s',%d,'%s',%d,%s);"%(mailTo,mailFrom,mailSubject,protoID,mailMessage,mail.tin,tstring))     
             
            maxItemList = self.conn.execute("select MAX(id) from MailStore;").fetchone()[0]
            if mail.item:
                item = mail.item
                self.conn.execute("insert into ItemInstance values(NULL, %d, %d, %d, %d, %d, %d, %d, %d, %d, '%s', %d, %d, '%s', %d, %d, '%s');"%(maxItemList,item.stackCount,item.useCharges,item.quality,item.food,item.drink,item.repairMax,item.repair,item.lifeTime,item.descOverride,item.levelOverride,item.spellEnhanceLevel,item.bitmap,item.hasVariants,item.crafted,item.name))
                ItemVariantsAHSave(item, self.conn, maxItemList)
            return maxItemList
        except:
            return False             
        
    def perspective_deleteMail(self, mailID):
        self.conn.execute("DELETE FROM MailStore WHERE id=%s;"%mailID)
        self.conn.execute("DELETE from ItemInstance WHERE item_list_id = %s;"%mailID)
        self.conn.execute("DELETE from ItemVariant WHERE item_list_id = %s;"%mailID)
        
    #Character was deleted, so lets remove all references...
    def perspective_deleteCharacter(self,cname):
        try: 
            self.conn.execute("SELECT id from MailStore WHERE message_to = '%s';"%cname)
            for AHID in self.conn.fetchall():
                self.conn.execute('DELETE from MailStore WHERE id = %d;'%AHID)
                self.conn.execute('DELETE from ItemInstance WHERE item_list_id = %d;'%AHID)
                self.conn.execute('DELETE from ItemVariant WHERE item_list_id = %d;'%AHID)  
        except:
            pass
  
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
            
        print "Logout from the Mail Server is Complete"

#Mail Server Class.  This is a proxy to push commands back up to the master so we can have multiple connections from World Clusters
class MailAvatar(Avatar):
    #Init the Mail Server Avatar.  
    def __init__(self, username, role, mind):
        global MAILCONNECT
        #Avatar information used by system to system communication (Mail Server <--> World)
        Avatar.__init__(self,username,role,mind)
        self.username = username
        self.role = role
        self.mind = mind
        self.masterConn = None
        if not MAILCONNECT:
            #Start the master connection to the DB
            MailMaster()
        
    def checkProxyConn(self):
        global MAILCONNECT
        if not self.masterConn:
            if not MAILCONNECT:
                print "FATAL ERROR CONNECTING WORLD PROXY TO AUCTION SERVER!!!"
                return False
            else:
                self.masterConn = MAILCONNECT 
                
        return True  
                     

    def perspective_refreshInboxList(self, charName, lastID):
        if not self.checkProxyConn():
            return
        
        return self.masterConn.perspective_refreshInboxList(charName, lastID)            
            
    def perspective_sendMail(self, mail,protoID):
        if not self.checkProxyConn():
            return
        
        return self.masterConn.perspective_sendMail(mail,protoID)              
        
    def perspective_deleteMail(self, mailID):
        if not self.checkProxyConn():
            return
        
        return self.masterConn.perspective_deleteMail(mailID) 
        
    #Character was deleted, so lets remove all references...
    def perspective_deleteCharacter(self,cname):
        if not self.checkProxyConn():
            return
        
        return self.masterConn.perspective_deleteCharacter(cname) 
  
    #Nothing
    def logout(self):
        return
        
#Used by the AH Server to communicate with the Mail Server.  Passes information back to primary handler
class MailProxyAvatar(Avatar):
    #Init the Mail Server Communication Proxy 
    def __init__(self, username, role, mind):
        #Avatar information used by system to system communication (Mail Server <--> World)
        Avatar.__init__(self,username,role,mind)
        self.username = username
        self.role = role
        self.mind = mind
        self.mailConn = None
        
    def checkProxyConn(self):
        global MAILCONNECT
        if not self.mailConn:
            if not MAILCONNECT:
                print "FATAL ERROR CONNECTING PROXY TO MAIL SERVER, MAIL FROM AH DROPPED!!!"
                return False
            else:
                self.mailConn = MAILCONNECT 
                
        return True
        
    def perspective_sendWinnings(self,item,money,buyer,seller):
        if not self.checkProxyConn():
            return
       
        #buyer         
        mail = MailItem("Auction House", "You have won %s!"%item.name, buyer, 0, "You have won %s!  Please take your winnings!"%item.name, time()+7200,0)
        mail.item = item
        MAILCONNECT.perspective_sendMail(mail, item.auctionItemID)
        
        #seller
        mail = MailItem("Auction House", "You successfully sold %s"%item.name, seller, money, "You successfully sold %s!  Please take your earnings!"%item.name, time()+7200,0)
        MAILCONNECT.perspective_sendMail(mail,0)    
        
    def perspective_refundBid(self,money,target,item_name):
        if not self.checkProxyConn():
            return
        
        mail = MailItem("Auction House", "You have been outbid on %s!"%item_name, target, money, "You have been outbid on %s!  Your bid has been refunded."%item_name, time()+7200,0)
        MAILCONNECT.perspective_sendMail(mail, 0)
       
    def perspective_refundBidDelete(self,money,target,item_name):
        if not self.checkProxyConn():
            return
        
        mail = MailItem("Auction House", "Your bid refund on %s!"%item_name, target, money, "The seller of %s has deleted.  Refunding your bid."%item_name, time()+7200,0)
        MAILCONNECT.perspective_sendMail(mail, 0)
        
    def perspective_refundBidBuyout(self,money,target,item_name): 
        if not self.checkProxyConn():
            return
        
        mail = MailItem("Auction House", "Your bid refund on %s!"%item_name, target, money, "%s has been purchased outright.  Your bid has been refunded."%item_name, time()+7200,0)
        MAILCONNECT.perspective_sendMail(mail, 0)
        

    def perspective_auctionTimeLimit(self,item,target):
        if not self.checkProxyConn():
            return
       
        #buyer         
        mail = MailItem("Auction House", "%s failed to sell!"%item.name, target, 0, "%s failed to sell so it is being returned."%item.name, time()+7200,0)
        mail.item = item
        MAILCONNECT.perspective_sendMail(mail, item.auctionItemID) 
        
    def perspective_sendRevoke(self,item,target):   
        if not self.checkProxyConn():
            return
       
        #buyer         
        mail = MailItem("Auction House", "%s has been returned!"%item.name, target, 0, "%s has been returned from the Auction House."%item.name, time()+7200,0)
        mail.item = item
        MAILCONNECT.perspective_sendMail(mail, item.auctionItemID) 
        
#Configure connection and User for MailServer <--> World Server.  Connection is MailServer to World Server since it should be fast and on the same machine/local network
#MSP is used as a proxy between the AH Server and the Mail Server so it can send information to the already running process connected to the World Server
def ConfigureRoles():
    ms = Role(name="MS")
    RoleAvatar(name="MailAvatar",role=ms)
    
    msp = Role(name="MSP")
    RoleAvatar(name="MailProxyAvatar",role=msp)
    
def ConfigureUsers():
    reg = User(name="MS",password="MS")
    reg.addRole(Role.byName("MS"))
    
    reg2 = User(name="MSP",password="MSP")
    reg2.addRole(Role.byName("MSP"))

#Database setup for communications with World Server
sys.argv.append('database=data/ahserver')
ConfigureServer("mailcommunication.db")

#Drop tables on the comm DB
TABLES = [Role,RoleAvatar,User]
for t in TABLES:
    t.dropTable(ifExists=True)
    t.createTable()

ConfigureRoles()
ConfigureUsers()
    
#Start Services to ready a connection from the World Server
server = Server(MAILSERVER_PORT,True)    # True to use md5 hashing for passwords
server.startServices()

print "->Mail Server is up"
reactor.run()

if MAILCONNECT:
    print "Dumping the Transactions to Database"
    MAILCONNECT.conn.execute("END TRANSACTION;")
    MAILCONNECT.conn.close()
    MAILCONNECT.dbconn.close()
    print "Cleanly shutdown the Mail Server!"
    sys.exit()
    
print "Error, could not find the MailServer Avatar, shutdown was not clean!"



