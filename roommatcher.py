import arcpy
import os
import numpy as np
import Tkinter, Tkconstants, tkFileDialog
from Tkinter import *


# inputFClasslyr= arcpy.GetParameterAsText(0)
# inputroomlyr =arcpy.GetParameterAsText(1)
#arcpy.MakeFeatureLayer_management(arcpy.GetParameterAsText(0), "inputFClasslyr")
#arcpy.MakeFeatureLayer_management(arcpy.GetParameterAsText(1), "inputroomlyr")
#arcpy.MakeFeatureLayer_management(arcpy.GetParameterAsText(0), "inputFClasslyr")
#arcpy.MakeFeatureLayer_management(arcpy.GetParameterAsText(1), "inputroomlyr")
#inputroomlyr = arcpy.GetParameterAsText(1)
# print inputFClasslyr,inputroomlyr #10
def roomchecker(inputFClasslyr, inputroomlyr):
    arcpy.MakeFeatureLayer_management(inputFClasslyr,"inputFClasslyr")
    arcpy.MakeFeatureLayer_management(inputroomlyr, "inputroomlyr")
    fld = ["AssetID", "SHAPE@"]
    with arcpy.da.SearchCursor("inputroomlyr", fld) as cursor:
        for room in cursor:
            room_geom = room[1]
            room_id = room[0]
            arcpy.SelectLayerByLocation_management("inputFClasslyr", "INTERSECT", room_geom, selection_type="NEW_SELECTION")
            arcpy.CalculateField_management("inputFClasslyr", "RoomID", "\""+"{}".format(room_id)+"\"","PYTHON")
    arcpy.Delete_management("inputFClasslyr")
    arcpy.Delete_management("inputroomlyr")
            #cursor.reset()

def getfloor():
    floordef ={ 'FirstFloor':'F1',  'SecondFloor' :'F2', 'GroundFloor': 'F0'}
    while True:
        flrlvl = str(raw_input("What floor? (Ground, First, or Second)\n")).capitalize() +"Floor"
        if flrlvl.strip() == 'FirstFloor'or flrlvl.strip() ==  'SecondFloor' or flrlvl.strip() == 'GroundFloor':
            return flrlvl.strip(), floordef[flrlvl.strip()]
            break
        else:
            print "Try again, bud."

def getGDBPath():
    while True:
        GDB_path = tkFileDialog.askdirectory(initialdir = "/",title = "Select Geodatabase (.gdb)",)
        if GDB_path.lower()[-3:] == "gdb":
            return GDB_path
            break
        else:
            print "Not a Geodatabase. Please try again, bud."

def getbuild():
    bldgs =list(fc for fc in arcpy.ListFeatureClasses(feature_dataset=ds[0]) )
    #W/O  mmerge records( i.e. Fx_...) list(bld for bld in np.unique([str(fc[:fc.rfind("_")]) for fc in arcpy.ListFeatureClasses(feature_dataset=ds[0])]) if bld != ds[1])
    bldgsdic= zip(range(1, len(bldgs)+1), bldgs)
    for choices in  bldgsdic:
        print "Type %s to selected: %s" % (choices[0],choices[1])
    while True:
        try:
            num = int(raw_input("select room feature Class (type in number)\n"))
            if num in range(1, len(bldgs)+1):
                print "You have selected mumber %s for %s" % (num, bldgsdic[num-1][1])
                return bldgsdic[num-1][1]
                break
            else:
                print "Not a number in range. Please try agian."
        except:
            print "Please type number. Like 1 or 2 ..."

arcpy.env.workspace= getGDBPath()
ds= getfloor()
RoomFClass = getbuild()
fctypes = np.unique([str(fc[fc.rfind("_")+1:]) for fc in arcpy.ListFeatureClasses(feature_dataset=ds[0]) if str(fc[fc.rfind("_")+1:]) not in ["room","department"] and fc[-4:] != "Room"])
#str(fc[fc.rfind("_")+1:])str(fc[fc.rfind("_")+1:])!= "room" or
for fc in fctypes:
    print "{}_{}".format(ds[1],fc)
    try:
        roomchecker("{}_{}".format(ds[1],fc), RoomFClass)
        print "Room Match Completed"
    except:
        print "Room Match Failed"
# del cursor
# del room
