# import libs
#
#

import arcpy as ar
import os
import numpy as np
import Tkinter, Tkconstants, tkFileDialog
from Tkinter import *
import pandas as pd
from subprocess import Popen

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
            print "Try again, bud." 

root = Tk()
#arcpy.env.workspace = "\\\\vsrvgisprod01\\gisintern\\SUMMER2018\\Sam_Mixer\\gisdata\\StageTest.gdb"
arcpy.env.workspace = getGDBPath()
root.destroy()

ds= getfloor()
#df = pd.DataFrame()
fctypes = np.unique([str(fc[fc.rfind("_")+1:]) for fc in arcpy.ListFeatureClasses(feature_dataset=ds[0])])
#yprint fctypes
buildtypes = list(bld for bld in np.unique([str(fc[:fc.rfind("_")]) for fc in arcpy.ListFeatureClasses(feature_dataset=ds[0])]) if bld != ds[1])
buildtypes.append("Final")
#np.insert(buildtypes, len(buildtypes)+1, "Final")
#print buildtypes
df = pd.DataFrame(index = buildtypes)
print "------------------------------------------------------------------------"
for fctype in fctypes:
    df[fctype]= 0
    output = ds[0]+"/"+ds[1]+'_' +fctype
    if ar.Exists(output):
        ar.Delete_management(output)      
    mergeable_listfc = [fc for fc in arcpy.ListFeatureClasses(feature_dataset=ds[0]) if fc[-len(fctype):] == fctype ]
    print "Found %s %s feature class(s) in %s" % (len(mergeable_listfc), fctype, ds[0])
    for mergx in  mergeable_listfc:
        result = arcpy.GetCount_management(mergx)
        print ('   {} has {} Features'.format(mergx, result[0]))
        df.loc[ mergx[:mergx.rfind("_")], fctype] = arcpy.GetCount_management(mergx)
    try:
        arcpy.Merge_management(mergeable_listfc, output)
        print " MERGED: %s. Total number of features: %s" %(fctype, arcpy.GetCount_management(output))
        df.loc["Final", fctype] = arcpy.GetCount_management(output)
        print "------------------------------------------------------------------------"
    except:
        print " NOT MERGED: %s " % fctype
        print "------------------------------------------------------------------------"
print df
print "done"
while True:
    Report = str(raw_input("Want to save a Report Table? (yes or no) "))
    if Report in["y", "Y" "yes", "Yes"]:
        root = Tk()
        rpath =tkFileDialog.asksaveasfile(mode='w',  filetypes = [('CSV files', '.csv')], defaultextension=".csv")
        #df.to_csv(tkFileDialog.asksaveasfile(mode='r+',  filetypes = [('CSV files', '.csv')], defaultextension=".csv"), sep=',' )
        df.to_csv(rpath, sep=',' )
        root.destroy()
        rpath =str(rpath)
        p = Popen(rpath[int(rpath.find("u'"))+2:int(rpath.rfind(".csv"))+4] , shell=True)
        break
    elif Report.lower() in ["no", "No", "N", "n"]:
        break
    else:
        print "Not an answer. Try again."

#print df
close = str(raw_input("Hit Enter to Close"))
# for CSV
#df.to_csv( "\\\\vsrvgisprod01\\gisintern\\SUMMER2018\\Sam_Mixer\\gisdata\\Finaltabletest.csv", sep=',')

