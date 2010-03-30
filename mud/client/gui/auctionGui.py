from tgenative import *
from mud.tgepython.console import TGEExport
from mud.world.defines import *

from twisted.spread import pb
from twisted.internet import reactor
from twisted.cred.credentials import UsernamePassword
from mud.gamesettings import GAMEROOT
from sqlite3 import dbapi2 as sqlite
from mud.client.playermind import GetMoMClientDBConnection
from mud.world.defines import *
from mud.world.core import CollapseMoney,GetItemRarity,ExpandMoney
from mud.world.item import ItemProto
from mud.world.shared.playdata import ItemInfo
import string
from time import time

#http://pypi.python.org/pypi/pylzma/0.3.0 - This is needed if it is not installed already!
import pylzma

AUCTIONGUI = None

class AuctionGui:
    #Initial function called with the AuctionGUI is created
    def __init__(self):
        #Declare all of GUI objects, easier than all of these TGE calls later
        self.window = TGEObject("AuctionGui_Window")
        self.auctionDB = None
        self.itemCache = {}
        self.itemButtonId = {}
        self.scrollWnd = TGEObject("AuctionGui_Scroll")
        #10 items in a window, change these if you decide to do more than 10
        self.itemButton = dict((x,TGEObject("AuctionGui_item_B%i"%x)) for x in xrange(1,11)) #1-10
        self.itemNameColor = {}
        self.itemName = dict((x,TGEObject("AuctionGui_item_Name%i"%x)) for x in xrange(1,11)) #1-10
        self.itemLevel = dict((x,TGEObject("AuctionGui_item_Level%i"%x)) for x in xrange(1,11)) #1-10
        self.itemTimeLeft = dict((x,TGEObject("AuctionGui_item_Time%i"%x)) for x in xrange(1,11)) #1-10
        self.itemBidP = dict((x,TGEObject("AuctionGui_item_BIDP%i"%x)) for x in xrange(1,11)) #1-10
        self.itemBidG = dict((x,TGEObject("AuctionGui_item_BIDG%i"%x)) for x in xrange(1,11)) #1-10
        self.itemBidS = dict((x,TGEObject("AuctionGui_item_BIDS%i"%x)) for x in xrange(1,11)) #1-10
        self.itemBidC = dict((x,TGEObject("AuctionGui_item_BIDC%i"%x)) for x in xrange(1,11)) #1-10
        self.itemBuyP = dict((x,TGEObject("AuctionGui_item_BUYP%i"%x)) for x in xrange(1,11)) #1-10
        self.itemBuyG = dict((x,TGEObject("AuctionGui_item_BUYG%i"%x)) for x in xrange(1,11)) #1-10
        self.itemBuyS = dict((x,TGEObject("AuctionGui_item_BUYS%i"%x)) for x in xrange(1,11)) #1-10
        self.itemBuyC = dict((x,TGEObject("AuctionGui_item_BUYC%i"%x)) for x in xrange(1,11)) #1-10
        self.itemShowBuy = dict((x,TGEObject("AuctionGui_item_SBUY%i"%x)) for x in xrange(1,11)) #1-10
        self.itemBidInfo = dict((x,TGEObject("AuctionGui_item_BIDBUY%i"%x)) for x in xrange(1,11)) #1-10
        self.itemGuiBG = dict((x,TGEObject("AuctionGui_BG%i"%x)) for x in xrange(1,11)) #1-10
        self.searchName = TGEObject("AuctionGui_Name_Search")
        self.levelLow = TGEObject("AuctionGui_Level_Low")
        self.levelHigh = TGEObject("AuctionGui_Level_High")
        self.itemNext = TGEObject("AuctionGui_Next")
        self.itemPrev = TGEObject("AuctionGui_Prev")
        self.playerCoinsP = TGEObject("AuctionGUI_PlayerCoins_P")
        self.playerCoinsG = TGEObject("AuctionGUI_PlayerCoins_G")
        self.playerCoinsS = TGEObject("AuctionGUI_PlayerCoins_S")
        self.playerCoinsC = TGEObject("AuctionGUI_PlayerCoins_C")
        self.sellPane = TGEObject("AuctionGui_SellPane")
        self.buyPane = TGEObject("AuctionGui_BuyPane")
        self.buySwitch = TGEObject("AuctionGui_Buy_Switch")
        self.sellSwitch = TGEObject("AuctionGui_Sell_Switch")
        self.StartingBid_P = TGEObject("AuctionGui_StartingBid_P")
        self.StartingBid_G = TGEObject("AuctionGui_StartingBid_G")
        self.StartingBid_S = TGEObject("AuctionGui_StartingBid_S")
        self.StartingBid_C = TGEObject("AuctionGui_StartingBid_C")
        self.Buyout_P = TGEObject("AuctionGui_Buyout_P")
        self.Buyout_G = TGEObject("AuctionGui_Buyout_G")
        self.Buyout_S = TGEObject("AuctionGui_Buyout_S")
        self.Buyout_C = TGEObject("AuctionGui_Buyout_C")
        self.Fare_P = TGEObject("AuctionGui_Fare_P")
        self.Fare_G = TGEObject("AuctionGui_Fare_G")
        self.Fare_S = TGEObject("AuctionGui_Fare_S")
        self.Fare_C = TGEObject("AuctionGui_Fare_C")
        self.Fare = 0
        self.Duration_4 = TGEObject("AuctionGui_Duration_4")
        self.Duration_8 = TGEObject("AuctionGui_Duration_8")
        self.Duration_24 = TGEObject("AuctionGui_Duration_24")
        self.auctionItemButton = TGEObject("AuctionGui_AuctionItem_Button")
        self.auctionItemName = TGEObject("AuctionGui_AuctionItem_Name")
        self.auctionItemGhost = None
        self.searchPage = 1
        self.sellPane.visible = False
        self.buyPane.visible = True
        self.buySwitch.SetValue(1)
        self.buySwitch.toggleLocked = True
        self.sellSwitch.SetValue(0)
        self.sellSwitch.toggleLocked = False
        self.lastUpdate = time() - 10000
        self.auctionCharID = 0
        self.tickcnt = 1
        self.clearresults()
        
    #Cleans up some cached data when a player logs off
    def cleanup(self):
        self.itemCache.clear()
        self.itemButtonId.clear()
        self.auctionItemGhost = None
        self.searchPage = 1
        self.sellPane.visible = False
        self.buyPane.visible = True
        self.buySwitch.SetValue(1)
        self.buySwitch.toggleLocked = True
        self.sellSwitch.SetValue(0)
        self.sellSwitch.toggleLocked = False
        self.lastUpdate = time() - 10000
        self.auctionCharID = 0
        self.auctionDB = None
        self.tickcnt = 1
        self.searchName.setValue("")
        self.levelLow.setValue("")
        self.levelHigh.setValue("")
        self.clearresults()
        
    #Clears out the contents of the panes so things are clean
    def clearresults(self):
        self.clearresultslite()
        
        for x in xrange(1,11):
            self.itemButton[x].pulseGreen = False
            self.itemButtonId[x] = -1

        self.StartingBid_P.setValue("0")
        self.StartingBid_G.setValue("0")
        self.StartingBid_S.setValue("0")
        self.StartingBid_C.setValue("0")
        self.Buyout_P.setValue("0")
        self.Buyout_G.setValue("0")
        self.Buyout_S.setValue("0")
        self.Buyout_C.setValue("0")
        self.Fare_P.setValue("")
        self.Fare_G.setValue("")
        self.Fare_S.setValue("")
        self.Fare_C.setValue("")
        self.Fare = 0
        self.Duration_4.setValue(0)
        self.Duration_8.setValue(0)
        self.Duration_24.setValue(0)
        self.auctionItemButton.setBitmap("")
        self.auctionItemButton.number = -1
        self.auctionItemName.setValue("")
        self.auctionItemGhost = None
        
    #Clears out the contents of the panes so things are clean - Lite version
    def clearresultslite(self):
        for x in xrange(1,11):
            self.itemName[x].setText("")
            self.itemNameColor[x] = ""
            self.itemLevel[x].setText("")
            self.itemTimeLeft[x].setText("") 
            self.itemBidP[x].setText("")
            self.itemBidG[x].setText("")
            self.itemBidS[x].setText("")
            self.itemBidC[x].setText("")
            self.itemBuyP[x].setText("")
            self.itemBuyG[x].setText("")
            self.itemBuyS[x].setText("")
            self.itemBuyC[x].setText("")
            self.itemBidInfo[x].setText("")
            self.itemBidInfo[x].visible = False
            self.itemShowBuy[x].visible = False
            self.itemGuiBG[x].setBitmap("~/data/ui/elements/auctionitem")
            self.itemGuiBG[x].visible = False
            self.itemButton[x].visible = False
            self.itemButton[x].number = -1
        self.itemNext.visible = False
        self.itemPrev.visible = False
     
    def setRealm(self,realm):
        self.auctionDB = RPG_AUCTION_DBNAME[realm]
        
    def getDBConnection(self):
        return sqlite.connect("./%s/data/%s"%(GAMEROOT,self.auctionDB),isolation_level = None)
        
    #Called to set an item to button so it can be sold   
    def doItemSlot(self):
        from partyWnd import PARTYWND
        cinfo = PARTYWND.charInfos[PARTYWND.curIndex]
        if (PARTYWND.invPane.lastSlot <= 0):
            TGECall("MessageBoxOK","Invalid Item","You can only use items in your inventory.  The item MUST be unequiped.")
            return
            
        for slot,ghost in cinfo.ITEMS.iteritems():
            if slot != RPG_SLOT_CURSOR:
                continue
            
            if ghost.CONTAINERSIZE and len(ghost.CONTENT):
                TGECall("MessageBoxOK","Invalid Item","You cannot auction a container with anything in it.  Please empty it first!.")
                return 
                
            if ghost.FLAGS&(RPG_ITEM_SOULBOUND|RPG_ITEM_ETHEREAL|RPG_ITEM_WORLDUNIQUE) or not ghost.WORTHTIN:
                TGECall("MessageBoxOK","Invalid Item","Item cannot have any of these flags: Soulbound, Ethereal, or World Unique.  It must also have a value.")
                return                 
        
            self.auctionItemButton.setBitmap("~/data/ui/items/"+ghost.BITMAP+"/0_0_0")
            self.auctionItemName.setText("%s%s"%(GetItemRarity(ghost.FLAGS),ghost.NAME))
            if ghost.STACKMAX > 1:
                self.auctionItemButton.number = ghost.STACKCOUNT
            self.auctionItemGhost = ghost
            PARTYWND.mind.onInvSlot(cinfo,PARTYWND.invPane.lastSlot)
            PARTYWND.invPane.lastSlot = 0
            return
      
    #Called in partyWnd to clear out the auction item button and info
    def clearItemButton(self):
        self.auctionItemButton.setBitmap("")
        self.auctionItemButton.number = -1
        self.auctionItemName.setValue("")
        self.auctionItemGhost = None
        
    #Called from the GUI, Creates an Auction from all of the information present on the GUI 
    def doCreateAuction(self):
        from partyWnd import PARTYWND
        from mud.client.playermind import PLAYERMIND
        
        slotfound = 0
        cinfo = PARTYWND.charInfos[PARTYWND.curIndex]
        #Get Bid/Buyout Values and then check them
        bidP = self.StartingBid_P.getValue()
        bidG = self.StartingBid_G.getValue()
        bidS = self.StartingBid_S.getValue()
        bidC = self.StartingBid_C.getValue()
        buyP = self.Buyout_P.getValue()
        buyG = self.Buyout_G.getValue()
        buyS = self.Buyout_S.getValue()
        buyC = self.Buyout_C.getValue()

        if not bidP.isdigit() or not bidG.isdigit() or not bidS.isdigit() or not bidC.isdigit():
            TGECall("MessageBoxOK","Invalid Bid Value","Please Make sure your bid values are numeric.")
            return
            
        if not buyP.isdigit() or not buyG.isdigit() or not buyS.isdigit() or not buyC.isdigit():
            TGECall("MessageBoxOK","Invalid Buyout Value","Please Make sure your buyout values are numeric.")
            return
        
        bidTin = ExpandMoney(0,bidC,bidS,bidG,bidP)
        buyTin = ExpandMoney(0,buyC,buyS,buyG,buyP)
        
        if bidTin <= 0:
            TGECall("MessageBoxOK","Invalid Bid Value","You cannot have a bid value of 0 or less.")
            return
            
        if buyTin < 0:
            TGECall("MessageBoxOK","Invalid Buyout Value","You cannot have a buyout value less than 0.")
            return
            
        if bidTin > buyTin and buyTin != 0:
            TGECall("MessageBoxOK","Invalid Bid Value","You cannot have a bid value higher than the buyout value.")
            return
            
        #Check Duration values
        if (not int(self.Duration_4.getValue()) and not int(self.Duration_8.getValue()) and not int(self.Duration_24.getValue())):
            TGECall("MessageBoxOK","Invalid Duration","You need to select a duration.")
            return
            
        if int(self.Duration_4.getValue()):
            duration = 1
        elif int(self.Duration_8.getValue()):
            duration = 2
        else:
            duration = 3
             
        #Check Fare Costs
        if self.Fare <= 0:
            TGECall("MessageBoxOK","Invalid Fare","The Fare for the auction is invalid.")
            return
            
        if (PARTYWND.mind.rootInfo.TIN < self.Fare):
            TGECall("MessageBoxOK","Cannot cover the Fare","You cannot afford to pay the fare to sell this item.")
            return
            
        #Check to see if a ghost exists for the item in the auction slot
        if self.auctionItemGhost == None:
            TGECall("MessageBoxOK","No item is up for auction","Please drag an item to be placed up for auction.")
            return          
        
        #Validate it to make sure it is actually in an inventory slot
        for slot,ghost in cinfo.ITEMS.iteritems():
            if ghost == self.auctionItemGhost:
                if RPG_SLOT_CARRY_END > slot >= RPG_SLOT_CARRY_BEGIN:
                    slotfound = 1
                    break
                
        if not slotfound:
            TGECall("MessageBoxOK","Invalid item in the slot","The item selected to be sold is not in your inventory.")
            return
            
        #Send to the server for processing!
        PLAYERMIND.perspective.callRemote("PlayerAvatar","AHSell",cinfo.CHARID,ghost.PROTOID,slot,bidTin,buyTin,duration,self.Fare)
        
    #Called when the Buy Pane is switched to
    def doBuySwitch(self):
        self.sellPane.visible = False
        self.buyPane.visible = True
        self.buySwitch.SetValue(1)
        self.buySwitch.toggleLocked = True
        self.sellSwitch.SetValue(0)
        self.sellSwitch.toggleLocked = False
        self.clearresults()
        self.scrollWnd.scrollToTop()
     
    #Called when the Sell Pane is switched to   
    def doSellSwitch(self):
        self.sellPane.visible = True
        self.buyPane.visible = False
        self.buySwitch.SetValue(0)
        self.buySwitch.toggleLocked = False
        self.sellSwitch.SetValue(1)
        self.sellSwitch.toggleLocked = True
        self.clearresults()
        self.getCharacterSellList(0)
        self.scrollWnd.scrollToTop()      
                
    #gets the ID from the AH server for the player so he/she can match up the auction list
    def getCharacterAHID(self):
        from mud.client.playermind import PLAYERMIND
        from partyWnd import PARTYWND
        
        if self.auctionCharID > 0:
            return
        
        cinfo = PARTYWND.charInfos[PARTYWND.curIndex]
        
        if (self.auctionCharID == 0 and cinfo.AUCTIONID == 0):            
            PLAYERMIND.perspective.callRemote("PlayerAvatar","getCharacterAHID")
            self.auctionCharID = -1
            
        if (cinfo.AUCTIONID > 0):
            self.auctionCharID = cinfo.AUCTIONID

    #gets the list of items for sell by the character
    def getCharacterSellList(self, page):
        from mud.client.playermind import PLAYERMIND
        from partyWnd import PARTYWND
        from time import time
        
        cinfo = PARTYWND.charInfos[PARTYWND.curIndex]
        
        if (self.auctionCharID <= 0):
            return            
                
        #Sets the page we are on.  100 is no change, 0 is the first page, otherwise increase/decrease
        if (page == 0):
            self.searchPage = 1
        elif (page == 100):
            self.searchPage = self.searchPage
        else:
            self.searchPage += page
        
        if (self.lastUpdate + RPG_AUCTION_SEARCH_REFRESH < time()):
            PLAYERMIND.perspective.callRemote("PlayerAvatar","refreshAuctionList", 2)
            return
            
        ida = {}
        #Clear item list (lite)
        self.clearresultslite()

        if (self.searchPage < 1):
            self.searchPage = 1
        #Show Prev button if we are past page 1
        if (self.searchPage > 1):
            self.itemPrev.visible = True
        count=tcount=1          
        
        #Connect to local game DB to get item proto information
        con = GetMoMClientDBConnection()
        #Connect to AH DB to get AH info
        conn = self.getDBConnection()
        cursor = conn.cursor()
        scount = (self.searchPage-1)*10+1
        ecount = (self.searchPage)*10
        #Query local game DB and then AH DB on the client to get search results
        for id,buyout,cost,item_id,time,bidder_id in cursor.execute("SELECT id, buyout_cost, cost, item_id, time_left,bidder_id FROM ItemList WHERE char_id = %s ORDER BY time_left;"%self.auctionCharID):
            for iid,name,flags,level,bitmap in con.execute("SELECT id,name,flags,level,bitmap from item_proto WHERE id = %s;"%item_id):         
                #Show only 10 items...we are good now
                if (tcount < scount):
                    tcount += 1
                    continue
                #Show only 10 items...we are good now.  
                if (tcount > ecount):
                    #More items left...show next button
                    self.itemNext.visible = True
                    cursor.close()
                    conn.close()
                    #We have items in the ghost cache, so lets get that info
                    if len(ida):
                        PLAYERMIND.perspective.callRemote("PlayerAvatar","getItemInfo",ida)
                    return
                 
                #setup values to show on the GUI such as name, time left, level, etc   
                self.itemNameColor[count] = GetItemRarity(flags)
                    
                if (time == 4):
                    tleft = "<color:FFFFFF>Very Long"
                elif (time == 3):
                    tleft = "<color:469B00>Long"
                elif (time == 2):
                    tleft = "<color:FFD800>Medium"
                else:
                    tleft = "<color:FF0000>Short"
                    
                self.itemTimeLeft[count].setText(tleft)               
                self.itemName[count].setText("%s%s"%(self.itemNameColor[count],name))
                self.itemLevel[count].setText("<color:FFFFFF>%s"%level)
                self.itemButton[count].SetBitmap("~/data/ui/items/%s/0_0_0"%bitmap)
                self.itemButton[count].visible = True
                self.itemGuiBG[count].visible = True
                cT,cC,cS,cG,cP=CollapseMoney(cost)
                self.itemBidC[count].setText(cC)
                self.itemBidS[count].setText(cS)
                self.itemBidG[count].setText(cG)
                self.itemBidP[count].setText(self.listplat(cP))
                if (buyout > 0):
                    bT,bC,bS,bG,bP=CollapseMoney(buyout)
                    self.itemBuyC[count].setText(bC)
                    self.itemBuyS[count].setText(bS)
                    self.itemBuyG[count].setText(bG)
                    self.itemBuyP[count].setText(self.listplat(bP))                    
                    self.itemShowBuy[count].visible = True
                 
                if (bidder_id <= 0):
                    self.itemBidInfo[count].visible = True
                    self.itemBidInfo[count].setText("No Bid")
                else:
                    self.itemBidInfo[count].visible = True
                    self.itemBidInfo[count].setText("Curent Bid")
                    self.itemGuiBG[count].setBitmap("~/data/ui/elements/auctionitem_winbid")
                    
                #Set auction ID on button for reference later
                self.itemButtonId[count] = id
                #Item is not in the ghost Cache...add it
                if not self.itemCache.has_key(id):
                    ida[id] = iid
                else:
                    if self.itemCache[id].STACKMAX > 1:
                        self.itemButton[count].number =  self.itemCache[id].STACKCOUNT
                    if self.itemCache[id].NAME != self.itemName[count].getText():
                        self.itemName[count].setText("%s%s"%(self.itemNameColor[count],self.itemCache[id].NAME))                        
                count += 1
                tcount += 1
                
        #We have items in the ghost cache, so lets get that info
        if len(ida):
            PLAYERMIND.perspective.callRemote("PlayerAvatar","getItemInfo",ida)
        cursor.close()
        conn.close()
        
    def doRemoveFromAuction(self):
        from mud.client.playermind import PLAYERMIND
        revokeID = -1
        #Search item Buttons to see if one is selected
        for x in xrange(1,11):
            if (self.itemButton[x].pulseGreen == True):
                revokeID = self.itemButtonId[x]
                break
          
        if (revokeID < 0):
            TGECall("MessageBoxOK","No item Selected","You need to click on an item to remove it from the Auction.")
            return
            
        #Connect local DB to see if there is a bidder
        conn = self.getDBConnection()
        cursor = conn.cursor()
        bidder_id = cursor.execute("SELECT bidder_id FROM ItemList WHERE id = %s;"%revokeID).fetchone()[0]
        
        if bidder_id:
            TGECall("MessageBoxOK","There is a bid on this item","Once a bid has been placed you cannot revoke the item.")
            cursor.close()
            conn.close()
            return             
        
        PLAYERMIND.perspective.callRemote("PlayerAvatar","AHRevokeSell",revokeID)
        #close DB connections
        cursor.close()
        conn.close()
        
    #Updates the local Auction DB when a bid is made by the player
    def updatelocalDBBid(self, auctionID,cost):
        from time import time
        conn = self.getDBConnection()
        cursor = conn.cursor()
        cursor.execute("update ItemList SET bidder_id = %s, cost = %s WHERE id = %s;"%(self.auctionCharID, cost,auctionID))
        cursor.close()
        conn.close()
        if (self.lastUpdate + RPG_AUCTION_SEARCH_REFRESH - time() <= 15.0):
            self.lastUpdate+=15.0 #So a refresh doesn't kill the results
        #Search results refresh
        self.Search(100)
        
    #Updates the local Auction DB when a purchase happens so a full refresh is not needed when an item is purchased
    #Also called when an item is revoked on the Sell pane.
    def updatelocalDBPurchase(self, auctionID):
        from time import time
        conn = self.getDBConnection()
        cursor = conn.cursor()
        cursor.execute("DELETE from ItemList WHERE id = %s;"%auctionID)
        cursor.close()
        conn.close()
        if (self.lastUpdate + RPG_AUCTION_SEARCH_REFRESH - time() <= 15.0):
            self.lastUpdate+=15.0 #So a refresh doesn't kill the results
        #Search results refresh
        if self.sellSwitch.toggleLocked:
            self.getCharacterSellList(100)
        else:
            self.Search(100)
        
    #Updates the local Auction DB when a purchase happens so a full refresh is not needed when an item is sold  
    def updatelocalDBSell(self, buyTin, bidTin, auctionID, duration, charID,protoID):
        from time import time
        conn = self.getDBConnection()
        cursor = conn.cursor()
        cursor.execute("insert into ItemList values(%d,%d,%d,%d,%d,%d,0);"%(auctionID,buyTin,bidTin,protoID,duration,charID))
        cursor.close()
        conn.close()
        if (self.lastUpdate + RPG_AUCTION_SEARCH_REFRESH - time() <= 15.0):
            self.lastUpdate+=15.0 #So a refresh doesn't kill the results
        #Sell list refresh
        self.getCharacterSellList(100)
        
    #Processes an item for bid by selecting the item pulsing green and sending it to the AH server for processing
    def doBid(self):
        from partyWnd import PARTYWND
        from mud.client.playermind import PLAYERMIND
        buyid = -1
        #Search item Buttons to see if one is selected
        for x in xrange(1,11):
            if (self.itemButton[x].pulseGreen == True):
                buyid = self.itemButtonId[x]
                break
          
        if (buyid < 0):
            TGECall("MessageBoxOK","No item Selected","You need to click on an item to select it for bidding.")
            return
            
        #Connect local DB to search for valid item and get its buyout cost.  Then validate the player is rich enough
        #NOTE - Local client could be a bit behind, so this is a best guess on local information
        conn = self.getDBConnection()
        cursor = conn.cursor()
        cost,char_id,bidder_id = cursor.execute("SELECT cost, char_id, bidder_id FROM ItemList WHERE id = %s;"%buyid).fetchone()
        
        if not cost:
            TGECall("MessageBoxOK","No item was found","The item selected could not be found, please do a new search.")
            cursor.close()
            conn.close()
            return 
            
        if self.auctionCharID == char_id:
            TGECall("MessageBoxOK","You cannot bid on your own item.","You cannot bid on your own item.")
            cursor.close()
            conn.close()
            return 
            
        if self.auctionCharID == bidder_id:
            TGECall("MessageBoxOK","You already have the winning bid.","You already have the winning bid.")
            cursor.close()
            conn.close()
            return 

        if (PARTYWND.mind.rootInfo.TIN < int(cost*RPG_AUCTION_BIDCOST)):
            TGECall("MessageBoxOK","You cannot afford to bid on this item","You do not have the money to cover the 25% increase in bid on the item")
            cursor.close()
            conn.close()
            return 
        
        #player has the funds, send to server      
        PLAYERMIND.perspective.callRemote("PlayerAvatar","AHBid",buyid)
        #close DB connections
        cursor.close()
        conn.close()
        
    #Processes an item for buyout by selecting the item pulsing green and sending it to the AH server for processing
    def doBuyout(self):
        from partyWnd import PARTYWND
        from mud.client.playermind import PLAYERMIND
        buyid = -1
        #Search item Buttons to see if one is selected
        for x in xrange(1,11):
            if (self.itemButton[x].pulseGreen == True):
                buyid = self.itemButtonId[x]
                break
          
        if (buyid < 0):
            TGECall("MessageBoxOK","No item Selected","You need to click on an item to select it for purchase.")
            return
            
        #Connect local DB to search for valid item and get its buyout cost.  Then validate the player is rich enough
        conn = self.getDBConnection()
        cursor = conn.cursor()
        cost, char_id = cursor.execute("SELECT buyout_cost,char_id FROM ItemList WHERE id = %s;"%buyid).fetchone()
        if not cost:
            TGECall("MessageBoxOK","No item was found","The item selected could not be found, please do a new search.")
            cursor.close()
            conn.close()
            return 
            
        if (cost <= 0):
            TGECall("MessageBoxOK","You cannot buyout this item","The item selected cannot be purchased via buyout!")
            cursor.close()
            conn.close()
            return 
            
        if self.auctionCharID == char_id:
            TGECall("MessageBoxOK","You cannot purhase your own item.","You cannot purhase your own item.")
            cursor.close()
            conn.close()
            return 

        if (PARTYWND.mind.rootInfo.TIN < cost):
            TGECall("MessageBoxOK","You cannot afford this item","The item selected costs more than you can afford!")
            cursor.close()
            conn.close()
            return 
        
        #player has the funds, send to server      
        PLAYERMIND.perspective.callRemote("PlayerAvatar","AHBuyout",buyid)
        #close DB connections
        cursor.close()
        conn.close()

    #Called from Gui.  Makes the button pulse green
    def doBuyClick(self, args):
        button = int(args[1])
        for x in xrange(1,11):
            self.itemButton[x].pulseGreen = False

        self.itemButton[button].pulseGreen = True
        
    #Updates the last time since a DB update to preserve bandwidth
    def updateDBTime(self, time, type):
        from time import time
        self.lastUpdate = time()
        if (type == 1): #refresh search results
            self.Search(100)
        else: #refresh selling list results
            self.getCharacterSellList(100)
        
    #Update DB function that is called from the server.  Sends compressed DB over and this function decompresses it
    def updateDB(self, updatedDB, type):
        from time import time
        buffer = pylzma.decompress(updatedDB)
        f = file("./%s/data/%s"%(GAMEROOT,self.auctionDB),"wb")
        f.write(buffer)
        f.close()
        self.lastUpdate = time()
        if (type == 1): #refresh search results
            self.Search(100)
        else: #refresh selling list results
            self.getCharacterSellList(100)
        
     
    #Search function called by GUI
    def doSearch(self, pageSearch):
        page = int(pageSearch[1])
        self.scrollWnd.scrollToTop()
        for x in xrange(1,11):
            self.itemButton[x].pulseGreen = False
            self.itemButtonId[x] = -1
        if (self.sellPane.visible == True):
            self.getCharacterSellList(page)
        else:
            self.Search(page)
        
    #Updates the Fare.  Called from Tick
    def setFare(self):
        from partyWnd import PARTYWND
        from mud.client.playermind import PLAYERMIND
        
        cinfo = PARTYWND.charInfos[PARTYWND.curIndex]
        bidP = self.StartingBid_P.getValue()
        bidG = self.StartingBid_G.getValue()
        bidS = self.StartingBid_S.getValue()
        bidC = self.StartingBid_C.getValue()
        buyP = self.Buyout_P.getValue()
        buyG = self.Buyout_G.getValue()
        buyS = self.Buyout_S.getValue()
        buyC = self.Buyout_C.getValue()

        if not bidP.isdigit() or not bidG.isdigit() or not bidS.isdigit() or not bidC.isdigit():
            return
            
        if not buyP.isdigit() or not buyG.isdigit() or not buyS.isdigit() or not buyC.isdigit():
            return
        
        bidTin = ExpandMoney(0,bidC,bidS,bidG,bidP)
        buyTin = ExpandMoney(0,buyC,buyS,buyG,buyP)
        
        if bidTin <= 0:
            return
            
        if buyTin < 0:
            return
            
        if bidTin > buyTin and buyTin != 0:
            return
            
        if (not int(self.Duration_4.getValue()) and not int(self.Duration_8.getValue()) and not int(self.Duration_24.getValue())):
            return
            
        if int(self.Duration_4.getValue()):
            duration = 1
        elif int(self.Duration_8.getValue()):
            duration = 2
        else:
            duration = 3
            
        if buyTin:
            startCost = buyTin
        else:
            startCost = bidTin
            
        startCost = startCost * 2 / 100 # 2% - 4 Hours
        
        if (duration == 2):
            startCost = startCost * 3 / 2 # 3% - 8 Hours
            
        if (duration == 3):
            startCost = startCost * 5 / 2 # 5% - 24 Hours
            
        self.Fare = startCost
        tin,copper,silver,gold,platinum = CollapseMoney(startCost)

        self.Fare_C.setText(str(copper))
        self.Fare_S.setText(str(silver))
        self.Fare_G.setText(str(gold))
        self.Fare_P.setText(self.listplat(platinum))
        
    #Updates the Player's coin values on the GUI screen.  Called from tick
    def showPlayerCoins(self):
        from partyWnd import PARTYWND
        rootInfo = PARTYWND.mind.rootInfo
        tin,copper,silver,gold,platinum = CollapseMoney(rootInfo.TIN)

        self.playerCoinsC.setText(str(copper))
        self.playerCoinsS.setText(str(silver))
        self.playerCoinsG.setText(str(gold))
        self.playerCoinsP.setText(self.listplat(platinum))
        
    #Updates the sell Panel on tick
    def sellPanelUpdate(self):
        if (self.sellPane.visible == True):
            if (self.tickcnt % 6 == 5):
                self.tickcnt = 1
                self.getCharacterSellList(100)
            else:
                self.tickcnt = self.tickcnt + 1

    #Refreshes for the GUI.  Called quite often from PartyWnd   
    def tick(self):
        #Only update when things are in use.  No need to send updates to everyone.
        if (TGEObject("AuctionGui").visible):
            self.showPlayerCoins()
            self.setFare()
            self.getCharacterAHID()
            self.sellPanelUpdate()
       
    #lists plat in text form
    def listplat(self, platinum):
        # Need to format plat a bit since there's currently no specific upper bound.
        # Let's just hope nobody reaches 1G plat.
        if platinum > 1000:
            if platinum > 1000000:
                if platinum > 100000000:
                    plat = "%s M"%str((platinum / 100000) / 10.0)
                else:
                    plat = "%s M"%str((platinum / 10000) / 100.0)
            else:
                if platinum > 100000:
                    plat = "%s K"%str((platinum / 100) / 10.0)
                else:
                    plat = "%s K"%str((platinum / 10) / 100.0)
        else:
            plat = str(platinum)
            
        return plat

    #Actual Search function.
    def Search(self, page):
        from mud.client.playermind import PLAYERMIND
        from time import time
        
        #Sets the page we are on.  100 is no change, 0 is the first page, otherwise increase/decrease
        if (page == 0):
            self.searchPage = 1
        elif (page == 100):
            self.searchPage = self.searchPage
        else:
            self.searchPage += page
            
        #Update is due...Do this first and it will call search again with a refreshed DB
        #RPG_AUCTION_SEARCH_REFRESH is stored in defines.py and is a default of 1 minute.
        if (self.lastUpdate + RPG_AUCTION_SEARCH_REFRESH < time()):
            PLAYERMIND.perspective.callRemote("PlayerAvatar","refreshAuctionList", 1)
            return
            
        ida = {}
        #Clear screen
        self.clearresults()

        if (self.searchPage < 1):
            self.searchPage = 1
        #Show Prev button if we are past page 1
        if (self.searchPage > 1):
            self.itemPrev.visible = True
        count=tcount=1
        SearchText = self.searchName.getValue()
        #Validate level values and fix them if there is an issue.
        if (not self.levelLow.getValue().isdigit() or not self.levelHigh.getValue().isdigit()):
            lvllow = 0
            lvlhi = 1000
            self.levelLow.setValue("")
            self.levelHigh.setValue("")
        else:
            lvllow = string.atoi(self.levelLow.getValue())
            lvlhi = string.atoi(self.levelHigh.getValue())
            
        if SearchText == "":
            TGECall("MessageBoxOK","Please type an item name to search for","You need to type an item name to search for.")
            return
        
        #Connect to local game DB to get item proto information
        con = GetMoMClientDBConnection()
        #Connect to AH DB to get AH info
        conn = self.getDBConnection()
        cursor = conn.cursor()
        scount = (self.searchPage-1)*10+1
        ecount = (self.searchPage)*10
        #Query local game DB and then AH DB on the client to get search results
        for iid,name,flags,level,bitmap in con.execute("SELECT id,name,flags,level,bitmap from item_proto WHERE name LIKE '%s%%' AND level >= %i AND level <= %i;"%(SearchText,lvllow,lvlhi)):         
            for id,buyout,cost,item_id,time,bidder_id,char_id in cursor.execute("SELECT id, buyout_cost, cost, item_id, time_left,bidder_id,char_id FROM ItemList WHERE item_id = %s;"%iid):
                #Show only 10 items...we are good now
                if (tcount < scount):
                    tcount += 1
                    continue
                #Show only 10 items...we are good now.  
                if (tcount > ecount):
                    #More items left...show next button
                    self.itemNext.visible = True
                    cursor.close()
                    conn.close()
                    #We have items in the ghost cache, so lets get that info
                    if len(ida):
                        PLAYERMIND.perspective.callRemote("PlayerAvatar","getItemInfo",ida)
                    return
                 
                #setup values to show on the GUI such as name, time left, level, etc   
                self.itemNameColor[count] = GetItemRarity(flags)
                    
                if (time == 4):
                    tleft = "<color:FFFFFF>Very Long"
                elif (time == 3):
                    tleft = "<color:469B00>Long"
                elif (time == 2):
                    tleft = "<color:FFD800>Medium"
                else:
                    tleft = "<color:FF0000>Short"
                    
                self.itemTimeLeft[count].setText(tleft)               
                self.itemName[count].setText("%s%s"%(self.itemNameColor[count],name))
                self.itemLevel[count].setText("<color:FFFFFF>%s"%level)
                self.itemButton[count].SetBitmap("~/data/ui/items/%s/0_0_0"%bitmap)
                self.itemButton[count].visible = True
                self.itemGuiBG[count].visible = True
                cT,cC,cS,cG,cP=CollapseMoney(cost)
                self.itemBidC[count].setText(cC)
                self.itemBidS[count].setText(cS)
                self.itemBidG[count].setText(cG)
                self.itemBidP[count].setText(self.listplat(cP))
                if (buyout > 0):
                    bT,bC,bS,bG,bP=CollapseMoney(buyout)
                    self.itemBuyC[count].setText(bC)
                    self.itemBuyS[count].setText(bS)
                    self.itemBuyG[count].setText(bG)
                    self.itemBuyP[count].setText(self.listplat(bP))
                    self.itemShowBuy[count].visible = True
                    
                if (bidder_id <= 0):
                    self.itemBidInfo[count].visible = True
                    self.itemBidInfo[count].setText("No Bid")
                elif bidder_id == self.auctionCharID:
                    self.itemBidInfo[count].visible = True
                    self.itemBidInfo[count].setText("Curent Bid")
                    self.itemGuiBG[count].setBitmap("~/data/ui/elements/auctionitem_winbid")
                else:
                    self.itemBidInfo[count].visible = True
                    self.itemBidInfo[count].setText("Curent Bid")
                    
                if char_id == self.auctionCharID:
                    self.itemGuiBG[count].setBitmap("~/data/ui/elements/auctionitem_mine")
                    
                #Set auction ID on button for reference later
                self.itemButtonId[count] = id
                #Item is not in the ghost Cache...add it
                if not self.itemCache.has_key(id):
                    ida[id] = iid
                else:
                    if self.itemCache[id].STACKMAX > 1:
                        self.itemButton[count].number =  self.itemCache[id].STACKCOUNT
                    if self.itemCache[id].NAME != self.itemName[count].getText():
                        self.itemName[count].setText("%s%s"%(self.itemNameColor[count],self.itemCache[id].NAME))
                count += 1
                tcount += 1
                
        #We have items in the ghost cache, so lets get that info
        if len(ida):
            PLAYERMIND.perspective.callRemote("PlayerAvatar","getItemInfo",ida)
        cursor.close()
        conn.close()
        
    #Ghost information from the server.  Set it in the cache so we know not to request it again
    def setItemInfo(self, item):
        if not self.itemCache.has_key(item.AUCTIONID):
            self.itemCache[item.AUCTIONID] = item
            for x in xrange(1,11):
                if self.itemButtonId[x] == item.AUCTIONID:
                    #Set the stack value if there is one
                    if item.STACKMAX > 1:
                        self.itemButton[x].number = item.STACKCOUNT
                    #Set the name if it different
                    if item.NAME != self.itemName[x].getText():
                        self.itemName[x].setText("%s%s"%(self.itemNameColor[x],item.NAME))
                    
        return
        
#Needed to connect Python to the GUI.  All the Export functions map the GUI calls to python functions
def PyExec():
    global AUCTIONGUI
    AUCTIONGUI = AuctionGui()
    
    TGEExport(AUCTIONGUI.doSearch,"Py","DoSearch","desc",2,2)
    TGEExport(AUCTIONGUI.doBuyClick,"Py","doBuyClick","desc",2,2)
    TGEExport(AUCTIONGUI.doBuyout,"Py","DoBuyout","desc",1,1)
    TGEExport(AUCTIONGUI.doBuySwitch,"Py","DoBuySwitch","desc",1,1)
    TGEExport(AUCTIONGUI.doSellSwitch,"Py","DoSellSwitch","desc",1,1)
    TGEExport(AUCTIONGUI.doItemSlot,"Py","DoItemSlot","desc",1,1)
    TGEExport(AUCTIONGUI.doCreateAuction,"Py","DoCreateAuction","desc",1,1)
    TGEExport(AUCTIONGUI.doBid, "Py","DoBid","desc",1,1)
    TGEExport(AUCTIONGUI.doRemoveFromAuction,"Py","DoRemoveFromAuction","desc",1,1)