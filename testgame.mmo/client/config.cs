// Torque Input Map File
if (isObject(moveMap)) moveMap.delete();
new ActionMap(moveMap);
moveMap.bindCmd(keyboard, "escape", "", "ToggleGameOptionsWnd();");
moveMap.bind(keyboard, "ctrl f5", toggleParticleEditor);
moveMap.bind(keyboard, "q", turnLeft);
moveMap.bind(keyboard, "e", turnRight);
moveMap.bind(keyboard, "w", moveforward);
moveMap.bind(keyboard, "s", movebackward);
moveMap.bind(keyboard, "a", moveleft);
moveMap.bind(keyboard, "d", moveright);
moveMap.bind(keyboard, "space", jump);
moveMap.bind(keyboard, "comma", toggleFirstPerson);
moveMap.bind(keyboard, "alt c", toggleCamera);
moveMap.bind(keyboard, "f", InputToggleBuffWnd);
moveMap.bind(keyboard, "j", InputToggleJournalWnd);
moveMap.bind(keyboard, "h", InputToggleHelpWnd);
moveMap.bind(keyboard, "i", InputTogglePartyWndInventory);
moveMap.bind(keyboard, "k", InputTogglePartyWndSkills);
moveMap.bind(keyboard, "c", InputTogglePartyWndStats);
moveMap.bind(keyboard, "b", InputTogglePartyWndSpells);
moveMap.bind(keyboard, "t", InputToggleTrackingWnd);
moveMap.bind(keyboard, "p", InputToggleCharMiniWnd);
moveMap.bind(keyboard, "y", InputToggleAllianceWnd);
moveMap.bind(keyboard, "l", InputToggleLeaderWnd);
moveMap.bind(keyboard, "m", InputToggleMapWnd);
moveMap.bind(keyboard, "n", InputToggleMacroWnd);
moveMap.bind(keyboard, "r", InputTomeToggleReply);
moveMap.bindCmd(keyboard, "f7", "Py::OnHotKey(F7);", "");
moveMap.bindCmd(keyboard, "f8", "Py::OnHotKey(F8);", "");
moveMap.bindCmd(keyboard, "f9", "Py::OnHotKey(F9);", "");
moveMap.bindCmd(keyboard, "f10", "Py::OnHotKey(F10);", "");
moveMap.bindCmd(keyboard, "f11", "Py::OnHotKey(F11);", "");
moveMap.bindCmd(keyboard, "f12", "Py::OnHotKey(F12);", "");
moveMap.bindCmd(keyboard, "1", "Py::OnHotKey(1);", "");
moveMap.bindCmd(keyboard, "2", "Py::OnHotKey(2);", "");
moveMap.bindCmd(keyboard, "3", "Py::OnHotKey(3);", "");
moveMap.bindCmd(keyboard, "4", "Py::OnHotKey(4);", "");
moveMap.bindCmd(keyboard, "5", "Py::OnHotKey(5);", "");
moveMap.bindCmd(keyboard, "6", "Py::OnHotKey(6);", "");
moveMap.bindCmd(keyboard, "7", "Py::OnHotKey(7);", "");
moveMap.bindCmd(keyboard, "8", "Py::OnHotKey(8);", "");
moveMap.bindCmd(keyboard, "9", "Py::OnHotKey(9);", "");
moveMap.bindCmd(keyboard, "0", "Py::OnHotKey(0);", "");
moveMap.bindCmd(keyboard, "f1", "MACROWND_CHAR0.performClick();", "");
moveMap.bindCmd(keyboard, "f2", "MACROWND_CHAR1.performClick();", "");
moveMap.bindCmd(keyboard, "f3", "MACROWND_CHAR2.performClick();", "");
moveMap.bindCmd(keyboard, "f4", "MACROWND_CHAR3.performClick();", "");
moveMap.bindCmd(keyboard, "f5", "MACROWND_CHAR4.performClick();", "");
moveMap.bindCmd(keyboard, "f6", "MACROWND_CHAR5.performClick();", "");
moveMap.bindCmd(keyboard, "shift f1", "Py::CharSetTarget(0);", "");
moveMap.bindCmd(keyboard, "shift f2", "Py::CharSetTarget(1);", "");
moveMap.bindCmd(keyboard, "shift f3", "Py::CharSetTarget(2);", "");
moveMap.bindCmd(keyboard, "shift f4", "Py::CharSetTarget(3);", "");
moveMap.bindCmd(keyboard, "shift f5", "Py::CharSetTarget(4);", "");
moveMap.bindCmd(keyboard, "shift f6", "Py::CharSetTarget(5);", "");
moveMap.bind(keyboard, "backspace", InputClearTarget);
moveMap.bind(keyboard, "g", InputEvaluate);
moveMap.bind(keyboard, "v", InputToggleAutowalk);
moveMap.bind(keyboard, "shift tab", InputCycleTargetBackwards);
moveMap.bind(keyboard, "tab", InputTargetNearest);
moveMap.bind(keyboard, "ctrl c", dropPlayerAtCamera);
moveMap.bind(keyboard, "ctrl o", bringUpOptions);
moveMap.bindCmd(keyboard, "slash", "TomeToggleSlash();", "");
moveMap.bindCmd(keyboard, "return", "TomeToggleEnter();", "");
moveMap.bindCmd(keyboard, "ctrl n", "NetGraph::toggleNetGraph();", "");
moveMap.bind(keyboard, "x", ToggleMouseLook);
moveMap.bind(keyboard, "z", toggleZoom);
moveMap.bind(mouse0, "xaxis", yaw);
moveMap.bind(mouse0, "yaxis", pitch);
moveMap.bind(mouse0, "button2", toggleFreeLook);
