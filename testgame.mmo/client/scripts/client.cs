//-----------------------------------------------------------------------------
// Torque Game Engine 
// Copyright (C) GarageGames.com, Inc.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// Server Admin Commands
//-----------------------------------------------------------------------------

function SAD(%password)
{
   if (%password !$= "")
      commandToServer('SAD', %password);
}

function SADSetPassword(%password)
{
   commandToServer('SADSetPassword', %password);
}


//----------------------------------------------------------------------------
// Misc server commands
//----------------------------------------------------------------------------

function clientCmdSyncClock(%time)
{
   // Time update from the server, this is only sent at the start of a mission
   // or when a client joins a game in progress.
}

function clientCmdNewDamagePopup(%ghostId,%damageStr,%r,%g,%b)
{
//    echo( "creating popup " @ %damageStr @ " for object " @ %shape );

		if ($pref::Video::ShowFloatingText)
    	%shape = ServerConnection.resolveGhostID( %ghostId );
    	DamageHud.addPopup(2000, %r @ " " @ %g @ " " @ %b, %shape, %damageStr );
}


