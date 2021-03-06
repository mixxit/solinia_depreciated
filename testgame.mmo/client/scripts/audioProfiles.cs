//-----------------------------------------------------------------------------
// Torque Game Engine
// Copyright (C) GarageGames.com, Inc.
//-----------------------------------------------------------------------------

// Channel assignments (channel 0 is unused in-game).

$GuiAudioType     = 1;
$SimAudioType     = 1;
$MessageAudioType = 1;
$MusicAudioType   = 2;
$MenuAudioType	  = 5;

new AudioDescription(AudioGui)
{
   volume   = 1.0;
   isLooping= false;
   is3D     = false;
   type     = $GuiAudioType;
};

new AudioDescription(AudioMessage)
{
   volume   = 1.0;
   isLooping= false;
   is3D     = false;
   type     = $MessageAudioType;
};

new AudioDescription(AudioMusic)
{
   volume   = 1.0;
   isLooping= false;
   isStreaming = true;
   is3D     = false;
   type     = $MusicAudioType;
};

//Added Looping Music Description
new AudioDescription(MusicLooping)
{
volume = 1.0;
isLooping= true;
is3D = false;
type = $MenuAudioType;
};


new AudioProfile(AudioButtonOver)
{
   filename = "~/data/sound/buttonOver.wav";
   description = "AudioGui";
   preload = true;
};

new AudioProfile(AudioButtonDown)
{
   filename = "~/data/sound/sfx/Menu_Accept.ogg";
   description = "AudioGui";
   preload = true;
};

new AudioProfile(AudioWindowOpen)
{
   filename = "~/data/sound/sfx/Menu_Magic01.ogg";
   description = "AudioGui";
   preload = true;
};

new AudioProfile(AudioWindowClose)
{
   filename = "~/data/sound/sfx/Menu_Cancel01.ogg";
   description = "AudioGui";
   preload = true;
};

new AudioProfile(Music_MainMenu)
{
filename = "~/data/sound/music/01 - Solinia Theme.ogg";
description = "MusicLooping";
preload = true;
};