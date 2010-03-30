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
from mud.world.item import ItemProto,MailItem
from mud.world.shared.playdata import ItemInfo
import string
from time import time

#http://pypi.python.org/pypi/pylzma/0.3.0 - This is needed if it is not installed already!
import pylzma

MAILGUI = None

class MailGui:
    #Initial function called with the MailGui is created
    def __init__(self):
        #Declare all of GUI objects, easier than all of these TGE calls later
        self.window = TGEObject("MailGui_Window")
        self.mailButtonId = {}
        self.mailCache = {}
        self.mailNum = 0
        self.mailItemGhost = None
        #7 items in a window, change these if you decide to do more than 7
        self.inboxButton = dict((x,TGEObject("MailGui_Inbox_I%i_B"%x)) for x in xrange(1,8)) #1-7
        self.inboxFrom = dict((x,TGEObject("MailGui_Inbox_I%i_From"%x)) for x in xrange(1,8)) #1-7
        self.inboxSubject = dict((x,TGEObject("MailGui_Inbox_I%i_Subject"%x)) for x in xrange(1,8)) #1-7
        self.inboxTimeLeft = dict((x,TGEObject("MailGui_Inbox_I%i_TimeLeft"%x)) for x in xrange(1,8)) #1-7
        
        self.sendTo = TGEObject("MailGui_Send_To")
        self.sendSubject = TGEObject("MailGui_Send_Subject")
        self.sendMessage = TGEObject("MailGui_Send_Message")
        self.sendItem = TGEObject("MailGui_Send_Item_B")
        self.sendMoney_P = TGEObject("MailGui_Send_Money_P")
        self.sendMoney_G = TGEObject("MailGui_Send_Money_G")
        self.sendMoney_S = TGEObject("MailGui_Send_Money_S")
        self.sendMoney_C = TGEObject("MailGui_Send_Money_C")
        self.sendButton = TGEObject("MailGui_Send_B")
        
        self.inboxNext = TGEObject("MailGui_Inbox_Next")
        self.inboxPrev = TGEObject("MailGui_Inbox_Prev")
        self.inboxPane = TGEObject("MailGui_Inbox_pane")
        self.sendPane = TGEObject("MailGui_Send_Pane")
        self.inboxSwitch = TGEObject("MailGui_Inbox_Button")
        self.sendSwitch = TGEObject("MailGui_Send_Button")

        self.inboxPage = 1
        self.sendPane.visible = False
        self.inboxPane.visible = True
        self.inboxSwitch.SetValue(1)
        self.inboxSwitch.toggleLocked = True
        self.sendSwitch.SetValue(0)
        self.sendSwitch.toggleLocked = False
        self.lastUpdate = time() - 10000
        self.tickcnt = 1
        self.clearresults()

    #Cleans up some cached data when a player logs off
    def cleanup(self):
        self.mailButtonId.clear()
        self.mailCache.clear()
        self.mailNum = 0
        self.mailItemGhost = None
        self.inboxPage = 1
        self.sendPane.visible = False
        self.inboxPane.visible = True
        self.inboxSwitch.SetValue(1)
        self.inboxSwitch.toggleLocked = True
        self.sendSwitch.SetValue(0)
        self.sendSwitch.toggleLocked = False
        self.lastUpdate = time() - 10000
        self.tickcnt = 1
        self.clearresults()
        
    #Clears out the inbox information
    def clearlite(self):
        for x in xrange(1,8):
            self.inboxFrom[x].setText("")
            self.inboxSubject[x].setText("")
            self.inboxTimeLeft[x].setText("") 
            self.inboxButton[x].visible = False
            self.inboxButton[x].pulseGreen = False
            self.inboxButton[x].number = -1
            
        self.inboxNext.visible = False
        self.inboxPrev.visible = False
            
    #Clears out the contents of the panes so things are clean
    def clearresults(self):
        self.clearlite()
            
        self.sendTo.setText("")
        self.sendSubject.setText("")
        self.sendMessage.setText("")
        self.sendItem.setBitmap("")
        self.sendItem.number = -1
        self.sendMoney_P.setText("0")
        self.sendMoney_G.setText("0")
        self.sendMoney_S.setText("0")
        self.sendMoney_C.setText("0")
        self.mailButtonId.clear()
        self.mailItemGhost = None
      
    #Called when the Send Pane is switched to
    def doSendSwitch(self):
        self.inboxPane.visible = False
        self.sendPane.visible = True
        self.sendSwitch.SetValue(1)
        self.sendSwitch.toggleLocked = True
        self.inboxSwitch.SetValue(0)
        self.inboxSwitch.toggleLocked = False
        self.clearresults()
     
    #Called when the Inbox Pane is switched to   
    def doInboxSwitch(self):
        self.inboxPane.visible = True
        self.sendPane.visible = False
        self.sendSwitch.SetValue(0)
        self.sendSwitch.toggleLocked = False
        self.inboxSwitch.SetValue(1)
        self.inboxSwitch.toggleLocked = True
        self.clearresults()
        self.DisplayMail(0)
        
    def doSendMail(self):
        from partyWnd import PARTYWND
        from mud.client.playermind import PLAYERMIND
        
        cinfo = PARTYWND.charInfos[PARTYWND.curIndex]
        sendTo = self.sendTo.getValue()
        sendSubject = self.sendSubject.getValue()
        sendMessage = self.sendMessage.getValue()
        sslot = protoid = 0
        
        if (sendTo == ""):
            TGECall("MessageBoxOK","Please type in the name of the recepient","You need to specify who to send the mail to.")
            return
            
        if (sendSubject == ""):
            TGECall("MessageBoxOK","Please type in the Subject","You need to specify a subject.")
            return
            
        if (sendMessage == ""):
            TGECall("MessageBoxOK","Please type in the Message","You need to provide some kind of message.")
            return        
            
        coinsP = self.sendMoney_P.getValue()
        coinsG = self.sendMoney_G.getValue()
        coinsS = self.sendMoney_S.getValue()
        coinsC = self.sendMoney_C.getValue()
        
        if not coinsP.isdigit() or not coinsG.isdigit() or not coinsS.isdigit() or not coinsC.isdigit():
            coinsP=coinsG=coinsS=coinsC=0
        
        mailTin = ExpandMoney(0,coinsC,coinsS,coinsG,coinsP)
        
        if mailTin < 0:
            TGECall("MessageBoxOK","Invalid Coin Value","You cannot have a coin value of less than 0.")
            return
            
        if (PARTYWND.mind.rootInfo.TIN < mailTin):
            TGECall("MessageBoxOK","You don't have enough money","The value you want to send is more than you have.  Try again.")
            return
            
        #Validate it to make sure it is actually in an inventory slot if an item is in the mail
        if self.mailItemGhost:
            slotfound = 0
            for slot,ghost in cinfo.ITEMS.iteritems():
                if ghost == self.mailItemGhost:
                    if RPG_SLOT_CARRY_END > slot >= RPG_SLOT_CARRY_BEGIN:
                        slotfound = 1
                        break
                
            if not slotfound:
                TGECall("MessageBoxOK","Invalid item in the slot","The item selected to be mailed is not in your inventory.")
                return
                
            sslot = slot
            protoid = ghost.PROTOID
            
        newMail = MailItem(cinfo.NAME, sendSubject, sendTo, mailTin, sendMessage, time())
            
        PLAYERMIND.perspective.callRemote("PlayerAvatar","sendMail",newMail,protoid,sslot)
        
    def refreshInboxList(self, mailList):
        for id, mail in mailList.iteritems():
            if self.mailCache.has_key(id):
                print "Error: Mail send that was already in the cache"
                continue
                
            self.mailCache[id] = mail
        self.DisplayMail(100)
        
    def doChangePage(self, pageSearch):
        page = int(pageSearch[1])
        self.DisplayMail(page)
        
    def doViewMail(self, pageSearch):
        from mailInfoGui import MAILINFOGUI
        buttonNum = int(pageSearch[1])
        if self.mailButtonId.has_key(buttonNum):
            self.mailNum = buttonNum
            TGEEval("canvas.pushDialog(MailInfoGui);")
            MAILINFOGUI.displayInfo(self.mailButtonId[buttonNum])
            
    def deleteMail(self,mailID,fromServer):
        from mud.client.playermind import PLAYERMIND
        
        if not self.mailCache.has_key(mailID):
            TGECall("MessageBoxOK","Error Deleting Mail","The mail selected could not be found on the client.  Aborted.")
            return
          
        if not fromServer:  
            PLAYERMIND.perspective.callRemote("PlayerAvatar","deleteMail",mailID)
        del self.mailCache[mailID]
        self.DisplayMail(100)
        
    #Called to set an item to button so it can be mailed 
    def doMailSlot(self):
        from partyWnd import PARTYWND
        cinfo = PARTYWND.charInfos[PARTYWND.curIndex]
        if (PARTYWND.invPane.lastSlot <= 0):
            TGECall("MessageBoxOK","Invalid Item","You can only use items in your inventory.  The item MUST be unequiped.")
            return
            
        for slot,ghost in cinfo.ITEMS.iteritems():
            if slot != RPG_SLOT_CURSOR:
                continue
                
            if ghost.FLAGS&(RPG_ITEM_SOULBOUND|RPG_ITEM_ETHEREAL|RPG_ITEM_WORLDUNIQUE) or not ghost.WORTHTIN:
                TGECall("MessageBoxOK","Invalid Item","Item cannot have any of these flags: Soulbound, Ethereal, or World Unique.  It must also have a value.")
                return
                
            self.sendItem.setBitmap("~/data/ui/items/"+ghost.BITMAP+"/0_0_0")
            if ghost.STACKMAX > 1:
                self.sendItem.number = ghost.STACKCOUNT
            self.mailItemGhost = ghost
            PARTYWND.mind.onInvSlot(cinfo,PARTYWND.invPane.lastSlot)
            PARTYWND.invPane.lastSlot = 0
            return
            
    #Called in partyWnd to clear out the auction item button and info
    def clearItemButton(self):
        self.sendItem.setBitmap("")
        self.sendItem.number = -1
        self.mailItemGhost = None
        
    def getTimeLeft(self,timeLeft):
        from time import time,mktime,strptime
        from datetime import datetime
        from math import floor
        
        #Convert to Datetime
        time_format = "%Y-%m-%d %H:%M:%S"
        mytime = strptime(timeLeft,time_format)
        dtime = datetime(*mytime[:6])
        #Convert to time (seconds)    
        timeLeftDT = mktime(dtime.timetuple())+1e-6*dtime.microsecond
        #get the Difference and then parse it
        seconds = timeLeftDT - time()
        days = floor(seconds / 86400)
        hours = floor(seconds / 3600) % 24
        minutes = floor(seconds / 60) % 60
        
        if seconds < 0:
            return "0 Seconds"
        elif days:
            if days <= 3:
                return "<color:00FF21>%d Days"%days
            else:
                return "<color:0026FF>%d Days"%days
        elif hours:
            return "<color:FF6A00>%d Hours"%hours
        elif minutes:
            return "<color:FF0000>%d Minutes"%minutes
        else:
            return "<color:FF0000>%d Seconds"%seconds
       
    def DisplayMail(self, page):
        from time import time
        
        #Sets the page we are on.  100 is no change, 0 is the first page, otherwise increase/decrease
        if (page == 0):
            self.inboxPage = 1
        elif (page == 100):
            self.inboxPage = self.inboxPage
        else:
            self.inboxPage += page
                        
        ida = {}
        
        #Clear screen
        self.clearlite()      

        if (self.inboxPage < 1):
            self.inboxPage = 1
        #Show Prev button if we are past page 1
        if (self.inboxPage > 1):
            self.inboxPrev.visible = True
        count=tcount=1
        scount = (self.inboxPage-1)*7+1
        ecount = (self.inboxPage)*7
        for id,mail in self.mailCache.iteritems():           
            #Show only 7 items...we are good now
            if (tcount < scount):
                tcount += 1
                continue
            #Show only 7 items...we are good now.  
            if (tcount > ecount):
                #More mail left...show next button
                self.inboxNext.visible = True
                #We have items in the ghost cache, so lets get that info
                #if len(ida):
                #    PLAYERMIND.perspective.callRemote("PlayerAvatar","getItemInfo",ida)
                return                 
                    
            self.inboxFrom[count].setText("<color:007A02>%s"%mail.MAILFROM)               
            self.inboxSubject[count].setText("<color:2E5691>%s"%mail.SUBJECT)
            self.inboxTimeLeft[count].setText("%s"%self.getTimeLeft(mail.TIMEEND))
            if mail.ITEMPROTOID:
                #Connect to local game DB to get item proto information
                con = GetMoMClientDBConnection()    
                try:          
                    bitmap = con.execute("SELECT bitmap FROM item_proto WHERE id = %s;"%mail.ITEMPROTOID).fetchone()[0]
                    self.inboxButton[count].SetBitmap("~/data/ui/items/%s/0_0_0"%bitmap)
                except:
                    self.inboxButton[count].SetBitmap("~/data/ui/elements/mail")           
            elif mail.TIN:
                self.inboxButton[count].SetBitmap("~/data/ui/elements/coinpile")  
            else:
                self.inboxButton[count].SetBitmap("~/data/ui/elements/mail")    
            self.inboxButton[count].visible = True 
            #Set auction ID on button for reference later
            self.mailButtonId[count] = id
            #Item is not in the ghost Cache...add it
            #if not self.itemCache.has_key(id):
            #    ida[id] = iid
            #else:
            #    if self.itemCache[id].STACKMAX > 1:
            #        self.itemButton[count].number =  self.itemCache[id].STACKCOUNT
            count += 1
            tcount += 1
                
        #We have items in the ghost cache, so lets get that info
        #if len(ida):
        #    PLAYERMIND.perspective.callRemote("PlayerAvatar","getItemInfo",ida)
            
        
    def updateInbox(self):
        from mud.client.playermind import PLAYERMIND
        if (self.lastUpdate + RPG_MAIL_REFRESH < time()):
            PLAYERMIND.perspective.callRemote("PlayerAvatar","refreshInboxList", self.inboxPage)
            self.lastUpdate = time()
            return            

    #Refreshes for the GUI.  Called quite often from PartyWnd   
    def tick(self):
        from partyWnd import PARTYWND        
        from mailInfoGui import MAILINFOGUI
        cinfo = PARTYWND.charInfos[PARTYWND.curIndex]
        
        #Updates can come in at any time.  Overhead is fairly low after the initial login anyway
        self.updateInbox()            
        MAILINFOGUI.tick()
        
#Needed to connect Python to the GUI.  All the Export functions map the GUI calls to python functions
def PyExec():
    global MAILGUI
    MAILGUI = MailGui()
    
    TGEExport(MAILGUI.doInboxSwitch,"Py","DoInboxSwitch","desc",1,1)
    TGEExport(MAILGUI.doSendSwitch,"Py","DoSendSwitch","desc",1,1)
    TGEExport(MAILGUI.doChangePage,"Py","DoChangePage","desc",2,2)
    TGEExport(MAILGUI.doSendMail,"Py","DoSendMail","desc",1,1)
    TGEExport(MAILGUI.doViewMail,"Py","DoViewMail","desc",2,2)
    TGEExport(MAILGUI.doMailSlot,"Py","DoMailSlot","desc",1,1)