
//~~~~~~~~~~~~~~~~~~~~//~~~~~~~~~~~~~~~~~~~~//~~~~~~~~~~~~~~~~~~~~//~~~~~~~~~~~~~~~~~~~~~//
// Arcane-FX
//
// SELECTRONS (Core Tech)
//
// Copyright (C) Faust Logic, Inc.
//~~~~~~~~~~~~~~~~~~~~//~~~~~~~~~~~~~~~~~~~~//~~~~~~~~~~~~~~~~~~~~//~~~~~~~~~~~~~~~~~~~~~//

// style numbers
$MMOKit_Style = 6;


%mySelectronDataPath = "~/data/spells/SELE";

//~~~~~~~~~~~~~~~~~~~~//~~~~~~~~~~~~~~~~~~~~//~~~~~~~~~~~~~~~~~~~~//

$AdvancedLighting = ($pref::AFX::advancedFXLighting && !afxLegacyLighting());

//~~~~~~~~~~~~~~~~~~~~//~~~~~~~~~~~~~~~~~~~~//~~~~~~~~~~~~~~~~~~~~//~~~~~~~~~~~~~~~~~~~~~//
//~~~~~~~~~~~~~~~~~~~~//~~~~~~~~~~~~~~~~~~~~//~~~~~~~~~~~~~~~~~~~~//~~~~~~~~~~~~~~~~~~~~~//

// MMOKit Selectron Style
//

datablock afxZodiacData(MMOKit_glo_Zode_CE)
{  
  texture = %mySelectronDataPath @ "/mmokit_style/glow_ring.png";
  radius = 1.5;
  startAngle = 0;
  rotationRate = 80.0;
  color = "1.0 1.0 1.0 1.0";
  blend = additive;
  interiorHorizontalOnly = true;
};
datablock afxEffectWrapperData(MMOKit_glo_Zode_EW)
{
  effect = MMOKit_glo_Zode_CE;
  posConstraint = selected;
  lifetime = 0.3;
  fadeInTime = 0.3;
  fadeOutTime = 0.20;
  delay = 0;
};


datablock afxZodiacData(MMOKit_Zode_CE)
{  
  texture = %mySelectronDataPath @ "/mmokit_style/ring.png";
  radius = 1.5;
  startAngle = 0.0;
  rotationRate = 80.0;
  color = "1.0 1.0 1.0 1.0";
  blend = additive;
  interiorHorizontalOnly = true;
};
//
datablock afxEffectWrapperData(MMOKit_Zode_EW)
{
  effect = MMOKit_Zode_CE;
  posConstraint = selected;
  fadeInTime = 0.30;
  fadeOutTime = 0.30;
  delay = 0.3;
};

//~~~~~~~~~~~~~~~~~~~~//~~~~~~~~~~~~~~~~~~~~//
// MMOKit Selectron
//~~~~~~~~~~~~~~~~~~~~//~~~~~~~~~~~~~~~~~~~~//

datablock afxSelectronData(MMOKit_SELE)
{
  selectionTypeStyle = $MMOKit_Style;
  selectionTypeMask = $TypeMasks::PlayerObjectType | $TypeMasks::CorpseObjectType;
  mainDur = $AFX::INFINITE_TIME;
  addMainEffect = MMOKit_glo_Zode_EW;
  addMainEffect = MMOKit_Zode_EW;
};



// Add styles to the demo's selectron manager. (This is only
// needed to allow selectron cycling using the 't' key.)
// 
addDemoSelectronStyle("MMOKit",      $MMOKit_Style);


//~~~~~~~~~~~~~~~~~~~~//~~~~~~~~~~~~~~~~~~~~//~~~~~~~~~~~~~~~~~~~~//~~~~~~~~~~~~~~~~~~~~~//
