


//Main mob functions


//-----------------------------------------------------------------------------
// Torque Game Engine
// Copyright (C) GarageGames.com, Inc.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// rpgAIPlayer callbacks
// The rpgAIPlayer class implements the following callbacks:
//
//    rpgPlayerData::onStuck(%this,%obj)
//    rpgPlayerData::onUnStuck(%this,%obj)
//    rpgPlayerData::onStop(%this,%obj)
//    rpgPlayerData::onMove(%this,%obj)
//    rpgPlayerData::onReachDestination(%this,%obj)
//    rpgPlayerData::onTargetEnterLOS(%this,%obj)
//    rpgPlayerData::onTargetExitLOS(%this,%obj)
//    rpgPlayerData::onAdd(%this,%obj)
//
// Since the rpgAIPlayer doesn't implement it's own datablock, these callbacks
// all take place in the rpgPlayerData namespace.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// Demo Pathed rpgAIPlayer.
//-----------------------------------------------------------------------------



function DemoPlayer::onReachDestination(%this,%obj)
{
   // Moves to the next node on the path.
   // Override for all player. Normally we'd override this for only
   // a specific player datablock or class of players.
   if (%obj.path !$= "") {
      if (%obj.currentNode == %obj.targetNode)
         %this.onEndOfPath(%obj,%obj.path);
      else
         %obj.moveToNextNode();
   }
}

function DemoPlayer::onEndOfPath(%this,%obj,%path)
{
   %obj.nextTask();
}

function DemoPlayer::onEndSequence(%this,%obj,%slot)
{
   echo("Sequence Done!");
   %obj.stopThread(%slot);
   %obj.nextTask();
}


//-----------------------------------------------------------------------------
// rpgAIPlayer static functions
//-----------------------------------------------------------------------------

function rpgAIPlayer::spawn(%name,%spawnPoint,%dbname)
{
   // Create the demo player object
   %player = new rpgAIPlayer() {
      dataBlock = %dbname;
      path = "";
   };
   MissionCleanup.add(%player);
   PlayerGroup.add(%player);
   %player.setShapeName(%name);
   %player.setTransform(%spawnPoint);
   //%player.playThread(0,"pause1");

   return %player;
   
}

function rpgAIPlayer::spawnOnPath(%name,%path)
{
   // Spawn a player and place him on the first node of the path
   if (!isObject(%path))
   {
      echo ("WARNING: PATH NODE FOUND!!!");
      return;
   }
   %node = %path.getObject(0);
   %player = rpgAIPlayer::spawn(%name,%node.getTransform());
   return %player;
}


//-----------------------------------------------------------------------------
// rpgAIPlayer methods
//-----------------------------------------------------------------------------

function rpgAIPlayer::followPath(%this,%path,%node)
{
   // Start the player following a path
   %this.stopThread(0);
   if (!isObject(%path)) {
      %this.path = "";
      return;
   }
   if (%node > %path.getCount() - 1)
      %this.targetNode = %path.getCount() - 1;
   else
      %this.targetNode = %node;
   if (%this.path $= %path)
      %this.moveToNode(%this.currentNode);
   else {
      %this.path = %path;
      %this.moveToNode(0);
   }
}

function rpgAIPlayer::moveToNextNode(%this)
{
   if (%this.targetNode < 0 || %this.currentNode < %this.targetNode) {
      if (%this.currentNode < %this.path.getCount() - 1)
         %this.moveToNode(%this.currentNode + 1);
      else
         %this.moveToNode(0);
   }
   else
      if (%this.currentNode == 0)
         %this.moveToNode(%this.path.getCount() - 1);
      else
         %this.moveToNode(%this.currentNode - 1);
}

function rpgAIPlayer::moveToNode(%this,%index)
{
   // Move to the given path node index
   %this.currentNode = %index;
   %node = %this.path.getObject(%index);
   %this.setMoveDestination(%node.getTransform(), %index == %this.targetNode);
}


//-----------------------------------------------------------------------------
//
//-----------------------------------------------------------------------------

function rpgAIPlayer::pushTask(%this,%method)
{
   if (%this.taskIndex $= "") {
      %this.taskIndex = 0;
      %this.taskCurrent = -1;
   }
   %this.task[%this.taskIndex] = %method;
   %this.taskIndex++;
   if (%this.taskCurrent == -1)
      %this.executeTask(%this.taskIndex - 1);
}

function rpgAIPlayer::clearTasks(%this)
{
   %this.taskIndex = 0;
   %this.taskCurrent = -1;
}

function rpgAIPlayer::nextTask(%this)
{
   if (%this.taskCurrent != -1)
      if (%this.taskCurrent < %this.taskIndex - 1)
         %this.executeTask(%this.taskCurrent++);
      else
         %this.taskCurrent = -1;
}

function rpgAIPlayer::executeTask(%this,%index)
{
   %this.taskCurrent = %index;
   eval(%this.getId() @ "." @ %this.task[%index] @ ";");
}


//-----------------------------------------------------------------------------

function rpgAIPlayer::singleShot(%this)
{
   // This shooting delay is here for the demo, don't want to fire
   // at the weapon's full rate.
   %this.setImageTrigger(0,true);
   %this.setImageTrigger(0,false);
   %this.trigger = %this.schedule(2000,singleShot);
}

//-----------------------------------------------------------------------------

function rpgAIPlayer::wait(%this,%time)
{
   %this.schedule(%time * 1000,"nextTask");
}

function rpgAIPlayer::done(%this,%time)
{
   %this.schedule(0,"delete");
}

function rpgAIPlayer::fire(%this,%bool)
{
   if (%bool) {
      cancel(%this.trigger);
      %this.singleShot();
   }
   else
      cancel(%this.trigger);
   %this.nextTask();
}

function rpgAIPlayer::aimAt(%this,%object)
{
   echo("Aim: " @ %object);
   %this.setAimObject(%object);
   %this.nextTask();
}

function rpgAIPlayer::animate(%this,%seq)
{
   //%this.stopThread(0);
   //%this.playThread(0,%seq);
   %this.setActionThread(%seq);
}

function rpgAIPlayer::test()
{
   %player = rpgAIPlayer::spawnOnPath("xasd","MissionGroup/Paths/Path2");
   %player.mountImage(CrossbowImage,0);
   %player.setInventory(CrossbowAmmo,1000);

   %player.pushTask("followPath(\"MissionGroup/Paths/Path2\")");
   %player.pushTask("aimAt(\"MissionGroup/Room6/target\")");
   %player.pushTask("wait(1)");
   %player.pushTask("fire(true)");
   %player.pushTask("wait(10)");
   %player.pushTask("fire(false)");
   %player.pushTask("playThread(0,\"celwave\")");
   %player.pushTask("done()");
}



function newNPCOrc(%transform,%speed,%name,%dbname)
{
   %orc = rpgAIPlayer::spawn(%name,%transform,%dbname);
   %orc.setMoveSpeed(%speed);
   return %orc;
}



