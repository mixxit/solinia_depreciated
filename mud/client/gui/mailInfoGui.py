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

MAILINFOGUI = None

class MailInfoGui:
    #Initial function called with the MailInfoGui is created
    def __init__(self):
        #Declare all of GUI objects, easier than all of these TGE calls later
        self.window = TGEObject("MailInfoGui_Window")
        
        self.mailFrom = TGEObject("MailInfoGui_From")
        self.mailSubject = TGEObject("MailInfoGui_Subject")
        self.mailMessage = TGEObject("MailInfoGui_Message_Text")
        
        self.moneyGroup = TGEObject("MailInfoGui_Money_Container")
        self.money_P = TGEObject("MailInfoGui_Money_P")
        self.money_G = TGEObject("MailInfoGui_Money_G")
        self.money_S = TGEObject("MailInfoGui_Money_S")
        self.money_C = TGEObject("MailInfoGui_Money_C")

        self.itemGroup = TGEObject("MailInfoGui_Item_Container")
        self.itemButton = TGEObject("MailInfoGui_Item_B")
        
        self.getDescription = 0
        self.mailID = 0
        self.mailItemGhost = None

        self.clearresults()
        
    #Cleans up some cached data when a player logs off
    def cleanup(self):
        self.getDescription = 0
        self.mailID = 0
        self.mailItemGhost = None

        self.clearresults()

    #Clears out the contents of the Window
    def clearresults(self):         
        self.mailFrom.setValue("")
        self.mailSubject.setValue("")
        self.mailMessage.setValue("")
        
        self.itemButton.setBitmap("")
        self.itemButton.number = -1
        
        self.money_P.setValue("")
        self.money_G.setValue("")
        self.money_S.setValue("")
        self.money_C.setValue("")
        
        self.getDescription = 0
        self.mailID = 0
        self.mailItemGhost = None
        
        self.itemGroup.visible = False
        self.moneyGroup.visible = False       
        
    #Displays the information based on the button clicked in the mailGUI
    def displayInfo(self, mailID):  
        from mailGui import MAILGUI
        from mud.client.playermind import PLAYERMIND
        
        self.clearresults()
        if (MAILGUI.mailCache.has_key(mailID)):
            mail = MAILGUI.mailCache[mailID]
            self.mailID = mailID
            self.mailFrom.setValue(mail.MAILFROM)
            self.mailSubject.setValue(mail.SUBJECT)
            
            if mail.TIN:
                self.moneyGroup.visible = True
                cT,cC,cS,cG,cP=CollapseMoney(mail.TIN)
                self.money_P.setValue(cP)
                self.money_G.setValue(cG)
                self.money_S.setValue(cS)
                self.money_C.setValue(cC)
                
            if mail.MESSAGE == "":
                self.getDescription = mailID
                #GetMailDescription also will get the item info
                PLAYERMIND.perspective.callRemote("PlayerAvatar","getMailDescription",mailID)
            else:
                self.mailMessage.setValue(mail.MESSAGE)
                
            if mail.ITEM:
                self.itemGroup.visible = True
                self.mailItemGhost = mail.ITEM
                self.itemButton.setBitmap("~/data/ui/items/%s/0_0_0"%mail.ITEM.BITMAP)
                if mail.ITEM.STACKMAX > 1:
                    self.itemButton.number =  mail.ITEM.STACKCOUNT
        else:
            TGECall("MessageBoxOK","Error: Mail not Found","The mail you clicked on could not be found.  Please report this error.")
            
    def tick(self):
        from mailGui import MAILGUI
        if self.getDescription:
            if (MAILGUI.mailCache.has_key(self.getDescription)):
                mail = MAILGUI.mailCache[self.getDescription]
                if mail.MESSAGE != "":
                    if mail.ITEMPROTOID:
                        if not mail.ITEM:
                            return
                        else:
                            self.itemGroup.visible = True
                            self.mailItemGhost = mail.ITEM
                            self.itemButton.setBitmap("~/data/ui/items/%s/0_0_0"%mail.ITEM.BITMAP)
                            if mail.ITEM.STACKMAX > 1:
                               self.itemButton.number =  mail.ITEM.STACKCOUNT
                    self.mailMessage.setValue(mail.MESSAGE)
                    self.getDescription = 0
        
    def doDelete(self):
        from mailGui import MAILGUI
        
        if self.mailID:
            MAILGUI.deleteMail(self.mailID,False)
            TGEEval("canvas.popDialog(MailInfoGui);")
        
#Needed to connect Python to the GUI.  All the Export functions map the GUI calls to python functions
def PyExec():
    global MAILINFOGUI
    MAILINFOGUI = MailInfoGui()
    
    TGEExport(MAILINFOGUI.doDelete,"Py","DoDelete","desc",1,1)