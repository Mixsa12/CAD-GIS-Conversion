# import libs
import arcpy as ar
import os
import numpy as np
import Tkinter, Tkconstants, tkFileDialog
from Tkinter import *
import pandas as pd

print "Starting... "

def getGDBPath():
    while True:
        GDB_path = tkFileDialog.askdirectory(initialdir = "/",title = "Select Geodatabase (.gdb)",)  
        if GDB_path.lower()[-3:] == "gdb":
            return GDB_path
            break
        else:
            print "Not a Geodatabase. Please try again, bud."


def getfloor():
    floordef ={ 'FirstFloor':'F1',  'SecondFloor' :'F2', 'GroundFloor': 'F0'}
    while True:
        flrlvl = str(raw_input("What floor? (Ground, First, or Second)\n")).capitalize() +"Floor"
        if flrlvl.strip() == 'FirstFloor'or flrlvl.strip() ==  'SecondFloor' or flrlvl.strip() == 'GroundFloor':
            return flrlvl.strip(), floordef[flrlvl.strip()] 
            break
        else:
            print "Tnry again, bud." 


def getbuild():
    bldgs =list(bld for bld in np.unique([str(fc[:fc.rfind("_")]) for fc in arcpy.ListFeatureClasses(feature_dataset=ds[0])]) )
    #W/O  mmerge records( i.e. Fx_...) list(bld for bld in np.unique([str(fc[:fc.rfind("_")]) for fc in arcpy.ListFeatureClasses(feature_dataset=ds[0])]) if bld != ds[1])
    bldgsdic= zip(range(1, len(bldgs)+1), bldgs)
    for choices in  bldgsdic:
        print "Type %s to selected: %s" % (choices[0],choices[1])
    while True:
        try: 
            num = int(raw_input("What building do you what to add? (type in number)\n"))
            if num in range(1, len(bldgs)+1):
                print "You have selected mumber %s for %s" % (num, bldgsdic[num-1][1])
                return bldgsdic[num-1][1]
                break
            else:
                print "Not a number in range. Please try agian."

        except:
            print "Please type number. Like 1 or 2 ..."

   

root = Tk()
#arcpy.env.workspace = "\\\\vsrvgisprod01\\gisintern\\SUMMER2018\\Sam_Mixer\\gisdata\\StageTest.gdb"
print "select the final desination gdd "
expgdb = getGDBPath()
print expgdb
print "select the staging/ new GBD"
stageGDB = getGDBPath()
print stageGDB
arcpy.env.workspace=stageGDB
root.destroy()

ds= getfloor()
#df = pd.DataFrame()
fctypes = np.unique([str(fc[fc.rfind("_")+1:]) for fc in arcpy.ListFeatureClasses(feature_dataset=ds[0])])
#print fctypes

new_build = getbuild()
print "------------------------------------------------------------------------"
#print "In %s there the:" %  ds[0]
for fctype in fctypes:
    FCinput = ds[0]+"/"+new_build+'_' +fctype
    Foutput = expgdb+"/"+ds[0]+"/"+ds[1]+'_' +fctype
    if ar.Exists(FCinput):
        print new_build+'_' +fctype
        if ar.Exists(Foutput):
            ar.Append_management(FCinput, Foutput, "NO_TEST")
            print " Appended to:",ds[1]+'_' +fctype
        else:
            try:
                ar.FeatureToPolygon_management(FCinput, Foutput)
            except:
                ar.FeatureToLine_management(FCinput, Foutput)
            print ' Created: ', ds[1]+'_' +fctype
        
         
print "------------------------------------------------------------------------"

