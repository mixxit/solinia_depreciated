;NSIS Modern User Interface version 1.70

;--------------------------------
;Include Modern UI

!include "MUI.nsh"

;--------------------------------
;General

;Name and file
Name "MMO Game"
OutFile "MMOGame.exe"

;Default installation folder
InstallDir "$PROGRAMFILES\MMO Game"
InstallDirRegKey HKLM "SOFTWARE\MMO Game" ""
DirText "This will install the Solinia Online on your computer. Choose a directory"

RequestExecutionLevel admin

SetCompressor bzip2

;--------------------------------
;Interface Settings

!define MUI_ABORTWARNING
!define MUI_ICON "main.ico"
!define MUI_UNICON "main.ico"
!define MUI_COMPONENTSPAGE_SMALLDESC
!define MUI_HEADERIMAGE
!define MUI_WELCOMEFINISHPAGE_BITMAP "mmogame_panel.bmp"
!define MUI_HEADERIMAGE_BITMAP "mmogame_header.bmp"


;--------------------------------
;Pages

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "license.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH


;--------------------------------
;Languages

!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Main Demo section

Section "!MMO Game (required)" SecStarter
  SectionIn RO
  SetOutPath "$INSTDIR"
  File "getdxver.exe"
  File /a /r ..\..\distrib\*.*

  ; Start Menu
  SetOutPath "$SMPROGRAMS\Solinia Online"

  SetOutPath "$INSTDIR\bin"
  CreateShortCut "$SMPROGRAMS\Solinia Online\Solinia Online.lnk" \
  	"$INSTDIR\bin\Client.exe"
  SetOutPath "$INSTDIR"
  CreateShortCut "$SMPROGRAMS\Solinia Online\Uninstall Solinia Online.lnk" \
  	"$INSTDIR\uninst-mmogame.exe"

  ; Registry uninstall

  ; Vista fix
  WriteRegStr HKLM "Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers" \
		 "$INSTDIR\bin\Client.exe" "RUNASADMIN"

  WriteRegStr HKLM "SOFTWARE\MMOGame" "" $INSTDIR
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MMOGame" \
                 "DisplayName" "MMO Game (remove only)"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MMOGame" \
                 "UninstallString" '"$INSTDIR\uninst-mmogame.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MMOGame" \
                 "DisplayIcon" "$INSTDIR\uninst-mmogame.exe"

  ; Check for DX version
  ExecWait "$INSTDIR\getdxver.exe" $R1
  IntCmp 2048 $R1 NoDXInstall NoDXInstall
  MessageBox MB_YESNO|MB_ICONQUESTION \
           "Solinia Online requires a newer version of DirectX than you have installed on your computer.  Would you like to go to the Microsoft DirectX Downloads page now?" IDNO NoDXInstall
    ExecShell "open" "http://www.microsoft.com/windows/directx/downloads/default.asp"
  NoDXInstall:

  ;Create uninstaller
  WriteUninstaller $INSTDIR\uninst-mmogame.exe
SectionEnd

;--------------------------------
; Configure Firewall

Section "Configure Windows Firewall (recommended)" SecFirewall
ExecWait '"netsh" firewall add allowedprogram program = "$INSTDIR\bin\Client.exe" name = SoliniaOnline mode = ENABLE scope = ALL profile = ALL' 
SectionEnd


;--------------------------------
; Desktop Shortcut

Section "Desktop Shortcut" SecDesktop
  ; Desktop
  SetOutPath "$INSTDIR\bin"
  CreateShortCut "$DESKTOP\Solinia Online.lnk" "$INSTDIR\bin\Client.exe"
  SetOutPath "$INSTDIR"

SectionEnd

;--------------------------------
; Readme at the end

;Section "View ReadMe" SecReadMe
;  ExecShell open '$INSTDIR\ReadMe.html'
;SectionEnd

;--------------------------------
; Uninstaller

Section Uninstall
  MessageBox MB_YESNO|MB_ICONQUESTION \
           "Everything in the Solinia Online directory will be deleted. Are you sure you wish to uninstall MMO Game?" \
           IDNO Removed

  ; Shortcuts
  Delete "$DESKTOP\MMO Game.lnk"

  Delete "$SMPROGRAMS\MMO Game\Solinia Online.lnk"
  Delete "$SMPROGRAMS\MMO Game\Uninstall Solinia Online.lnk"
  RMDir "$SMPROGRAMS\Solinia Online"

  ; Registry
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MMOGame"
  DeleteRegKey HKLM "SOFTWARE\MMOGame"

  ; Demo Source and Binaries
  RMDir /r $INSTDIR
  IfFileExists $INSTDIR 0 Removed
    MessageBox MB_OK|MB_ICONEXCLAMATION \
               "Note: $INSTDIR could not be removed."
  Removed:
SectionEnd

;--------------------------------
;Descriptions

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
!insertmacro MUI_DESCRIPTION_TEXT ${SecStarter} "Install Solinia Online. This component is required."
!insertmacro MUI_DESCRIPTION_TEXT ${SecFirewall} "Enable Solinia Online for Windows Firewall.  This component is required for single and multiplayer."
!insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} "Create a shortcut on your desktop for launching the game"
;!insertmacro MUI_DESCRIPTION_TEXT ${SecReadMe} "View the  ReadMe at the end of the installation process"
!insertmacro MUI_FUNCTION_DESCRIPTION_END


