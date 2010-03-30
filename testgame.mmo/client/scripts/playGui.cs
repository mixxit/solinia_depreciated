//-----------------------------------------------------------------------------
// Torque Game Engine 
// Copyright (C) GarageGames.com, Inc.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// PlayGui is the main TSControl through which the game is viewed.
// The PlayGui also contains the hud controls.
//-----------------------------------------------------------------------------

function PlayGui::onWake(%this)
{
   // Turn off any shell sounds...
   // alxStop( ... );

   $enableDirectInput = "1";
   activateDirectInput();

   // Message hud dialog
   Canvas.pushDialog( MainChatHud );
   chatHud.attach(HudMessageVector);

   // just update the action map here
   moveMap.push();
   
   // hack city - these controls are floating around and need to be clamped
   schedule(0, 0, "refreshCenterTextCtrl");
   schedule(0, 0, "refreshBottomTextCtrl");
   
   ServerConnection.setFirstPerson(true);
}

function PlayGui::onSleep(%this)
{
   Canvas.popDialog( MainChatHud  );
   
   // pop the keymaps
   moveMap.pop();
}


//-----------------------------------------------------------------------------

function refreshBottomTextCtrl()
{
   BottomPrintText.position = "0 0";
}

function refreshCenterTextCtrl()
{
   CenterPrintText.position = "0 0";
}

//-----------------------------------------------------------------------------
function processSelectron(%id,%selectronID)
{
  %obj = ServerConnection.resolveGhostID(%id);
  if (%obj.selectron == 0)
  {
    %selectron = startSelectron(%obj, %selectronID);
    if (%selectron != 0)
      %selectron.addConstraint(%obj, "selected");
    %obj.selectron = %selectron;
  }  
}

function processSelectronStop(%id)
{
  %obj = ServerConnection.resolveGhostID(%id);
  if (%obj.selectron != 0)
  {
    %obj.selectron.stopSelectron();
    %obj.selectron = 0;
  }
}

