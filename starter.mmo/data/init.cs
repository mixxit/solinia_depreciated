//-----------------------------------------------------------------------------
// Torque Game Engine 
// Copyright (C) GarageGames.com, Inc.
//-----------------------------------------------------------------------------

// A temporary hack until we can find a better way to initialize
// material properties.
exec( "./terrains/grassland/propertyMap.cs" );
exec( "./terrains/scorched/propertyMap.cs" ); 

if( isTMKenabled() )
{
//------------------------------------------------------------------
// TGE Modernization Kit
//------------------------------------------------------------------

// Normal maps
exec("./interiors/autogenMatList.cs");


//------------------------------------------------------------------
// TGE Modernization Kit
//------------------------------------------------------------------
}
