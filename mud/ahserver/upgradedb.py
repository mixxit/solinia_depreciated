#Upgrades the Auction related DBs with item prototype changes.  Ran from upgrade.bat
import os
import sys

sys.path.append(os.getcwd())

from mud.gamesettings import *
from datetime import datetime
import re
import shutil
from sqlite3 import dbapi2 as sqlite
import traceback

BASELINE_DB = "./data/ahserver/itemProtoDB.db"
MULTIPLAYER_DB = "%s/data/worlds/multiplayer.baseline/world.db"%GAMEROOT
AH_DB = "./data/ahserver/ahmaster.db"
MAIL_DB = "./data/ahserver/mailmaster.db"

TRANS_AH_ITEMLIST = {}
TRANS_AH_ITEMTRANS = {}
TRANS_MAIL_STORE = {}

def create_protoDB(bcursor,mcursor,clean):
    #Clean the DB if it already exists
    if clean:
        try:
            bcursor.execute("drop table item_proto")
            bcursor.execute("vacuum item_proto")
        except:
            pass
            
    #Create the item_proto table
    bcursor.execute("create table item_proto(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT);")
                    
    mcursor.execute("SELECT id, name from item_proto;")
    bcursor.execute("BEGIN TRANSACTION;")
    for row in mcursor.fetchall():
        name = row[1].replace("'","''")
        bcursor.execute("insert into item_proto values(%d,'%s');"%(row[0],name)) 
    bcursor.execute("END TRANSACTION;")

#Item Prototype Database does not exist so lets create it as the baseline and then quit
if not os.path.exists(BASELINE_DB):
    print "No Prototype Database found for the Auctin and Mail Store!  Creating a new one!"
    MULTICONN = sqlite.connect(MULTIPLAYER_DB,isolation_level = None)
    BASECONN = sqlite.connect(BASELINE_DB,isolation_level = None)

    mcursor = MULTICONN.cursor()
    bcursor = BASECONN.cursor()
    
    create_protoDB(bcursor,mcursor,False)
    
    mcursor.close()
    bcursor.close()
    MULTICONN.close()
    BASECONN.close()
    print "New Baseline Item Prototype Database has been created!"
    sys.exit(0)  
    
print "Comparing the Baseline Prototype Database for the Auction and Mail Store!"
#Prototype DB exists, so lets look for some changes
MULTICONN = sqlite.connect(MULTIPLAYER_DB,isolation_level = None)
BASECONN = sqlite.connect(BASELINE_DB,isolation_level = None)
AHCONN = sqlite.connect(AH_DB,isolation_level = None)
MAILCONN = sqlite.connect(MAIL_DB,isolation_level = None)

mcursor = MULTICONN.cursor()
bcursor = BASECONN.cursor()
acursor = AHCONN.cursor()
mailcursor = MAILCONN.cursor()

#Query the new Multi-player DB to see if there are any changes.  If something is deleted it will be handled too
bcursor.execute("SELECT name,id from item_proto;")
for name,oid in bcursor.fetchall():
    try:
        #Look for the item...this will fail if nothing is returned
        mcursor.execute('SELECT id from item_proto WHERE name = "%s" LIMIT 1;'%name)
        nid = mcursor.fetchone()[0]
        #Only need to perform changes if something changed...
        if nid != oid:
            try:
                acursor.execute('SELECT id from ItemList WHERE item_id = %d;'%oid)
                for itemListID in acursor.fetchall():
                    TRANS_AH_ITEMLIST[itemListID] = nid
            except:
                pass
                
            try:
                acursor.execute('SELECT id from ItemTransactionDB WHERE item_proto_id = %d;'%oid)
                for ItemTransID in acursor.fetchall():
                    TRANS_AH_ITEMTRANS[ItemTransID] = nid
            except:
                pass
                
            try:
                mailcursor.execute('SELECT id from mailStore WHERE item_proto = %d;'%oid)
                for mailID in mailcursor.fetchall():
                    TRANS_MAIL_STORE[mailID] = nid
            except:
                pass
                
    #Item not found in the new DB, time to clean it from the databases
    except:
        print "ItemProto %s no longer exists.  Purging from the DBs"%name
        
        acursor.execute("BEGIN TRANSACTION;")
        mailcursor.execute("BEGIN TRANSACTION;")
        
        #Active Auctions...Clean it up and spit out a warning
        try:
            acursor.execute('SELECT id from ItemList WHERE item_id = %d;'%oid)
            for AHID in acursor.fetchall():
                print "***Warning: %s was found in an Active Auction...It has been purged"%name
                acursor.execute('DELETE from ItemList WHERE id = %d;'%AHID)
                acursor.execute('DELETE from ItemInstance WHERE item_list_id = %d;'%AHID)
                acursor.execute('DELETE from ItemVariant WHERE item_list_id = %d;'%AHID)               
        except:
            pass       
               
        #Transaction History, clean, but don't really care since it could be REALLY old
        acursor.execute('DELETE from ItemTransactionDB WHERE item_proto_id = %d;'%oid)
        
        #Active Mail...Clean up and spit out a warning
        try:
            mailcursor.execute('SELECT id from mailStore WHERE item_proto = %d;'%oid)
            for AHID in mailcursor.fetchall():
                print "***Warning: %s was found in an Active Mail...It has been purged"%name
                mailcursor.execute('DELETE from mailStore WHERE id = %d;'%AHID)
                mailcursor.execute('DELETE from ItemInstance WHERE item_list_id = %d;'%AHID)
                mailcursor.execute('DELETE from ItemVariant WHERE item_list_id = %d;'%AHID)               
        except:
            pass    
            
        acursor.execute("END TRANSACTION;")
        mailcursor.execute("END TRANSACTION;")
        
#If any changes were made they should be in the TRANS key stores, lets parse those changes now...
acursor.execute("BEGIN TRANSACTION;")
mailcursor.execute("BEGIN TRANSACTION;")

for id,value in TRANS_AH_ITEMLIST.iteritems():
    acursor.execute("UPDATE ItemList set item_id = %d WHERE id = %d;"%(value,id[0]))
    
for id,value in TRANS_AH_ITEMTRANS.iteritems():
    acursor.execute("UPDATE ItemTransactionDB set item_proto_id = %d WHERE id = %d;"%(value,id[0]))
    
for id,value in TRANS_MAIL_STORE.iteritems():
    mailcursor.execute("UPDATE mailStore set item_proto = %d WHERE id = %d;"%(value,id[0]))
    
acursor.execute("END TRANSACTION;")
mailcursor.execute("END TRANSACTION;")

create_protoDB(bcursor,mcursor,True)
                
mcursor.close()
bcursor.close()
acursor.close()
mailcursor.close()

MULTICONN.close()
BASECONN.close()
AHCONN.close()
MAILCONN.close()

print "Auction and Mail Store has been updated with the latest changes!"
sys.exit(0)  