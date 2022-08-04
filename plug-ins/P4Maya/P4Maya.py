import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginCmdName = "MayaP4Integration"

import pyp4qt

class scriptedCommand(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)

    def doIt(self,argList):
        print("P4Maya.py")

def cmdCreator():
    return OpenMayaMPx.asMPxPtr(scriptedCommand())

def initializePlugin(mobject):
    plugin = OpenMayaMPx.MFnPlugin(mobject, "Justin Tirado", "1.0.0", "Any")
    try:
        # print("Adding Perforce Menu")
        # pyp4qt.init()
        plugin.registerCommand(kPluginCmdName, cmdCreator)
        plugin.registerUI(pyp4qt.init, pyp4qt.close)
    except:
        sys.stderr.write("Failed to register command: %s\n" % kPluginCmdName)
        raise
    return


# Uninitialize the script plug-in
def uninitializePlugin(mobject):
    plugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        # print("Removing Perforce Menu")
        # pyp4qt.close()
        plugin.deregisterCommand(kPluginCmdName)
    except Exception as e:
        print(e)
        sys.stderr.write("Failed to unregister command: %s\n" % kPluginCmdName)
    return
