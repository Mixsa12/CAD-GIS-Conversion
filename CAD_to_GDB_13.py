# Takes a selected clean, georefrenced CAD File, places it in selected geodatabase (by floor level)
# and saves each building feature types(ie doors, window, walls, etc), ie.. polygons and polylines, 
# as geodatabase feature classes. Also add class-specific fields to created GDB feature classes
#
# Sam Mix 2018
#
# Import needed libs
print "Getting started..."
import arcpy as ar
import numpy as np
from Tkinter import *
import Tkinter, Tkconstants, tkFileDialog
import os, getpass
import datetime, time
import matplotlib.pyplot as plt


# function to get floor level/ GDB dataset
def getfloor():
    floordef ={ 'FirstFloor':'F1',  'SecondFloor' :'F2', 'GroundFloor': 'F0'}
    while True:
        flrlvl = str(raw_input("What floor? (Ground, First, or Second)\n")).capitalize() +"Floor"
        if flrlvl.strip() == 'FirstFloor'or flrlvl.strip() ==  'SecondFloor' or flrlvl.strip() == 'GroundFloor':
            return flrlvl.strip(), floordef[flrlvl.strip()] 
            break
        else:
            print "try again, bud."

# function to move convert CAD file into GBD as one dataset
def CADtoGDB(CADpath, GDBpath ):
    arcpy.ClearWorkspaceCache_management()
    reference_scale = "1000"
    CAD_name = CADpath.split("/")[-1][:-4]
    print "Converting", CAD_name,"FROM", CADpath, "to be PLACED in ", out_gdb_path 
    try: 
        ar.CADToGeodatabase_conversion(CADpath, GDBpath, CAD_name, reference_scale)
    except:
        print "File may already be there.  Attempting to replace/update"
        arcpy.Delete_management(str(GDBpath)+ "/"+str(CAD_name),"DEFeatureDataset")
        ar.CADToGeodatabase_conversion(CADpath, GDBpath, CAD_name, reference_scale)
            
# function for getting path of converted CAD file's polygonn
def GDB_polyGfile_loc(datasate_name):
    for fc in arcpy.ListFeatureClasses(feature_dataset=datasate_name, feature_type= 'Polygon'):
        path = os.path.join(arcpy.env.workspace, datasate_name, fc)
        return(path)

# function for getting path of converted CAD file's polyLine
def GDB_polyLfile_loc(datasate_name):
   for fc in arcpy.ListFeatureClasses(feature_dataset=datasate_name, feature_type= 'Polyline'):
       path = os.path.join(arcpy.env.workspace, datasate_name, fc)
       return(path)

# function for removing FID_polylineXX/polygonXX field
def FID_poly_feild_delate(fc): 
    fieldlist =[("{0} ".format(field.name)) for field in ar.ListFields(fc)]
    for field in  fieldlist:
        if field[:8]== "FID_Poly":
            print "FIELD DELETED:", field
            ar.DeleteField_management(fc, field)
            
# function for matching building/feature type and adding the type specific fields (from dictionary)
def field_generator(inputclass): 
    #dictionary of feature type class types and their respected feilds 'FacilityID' [ "AssetType", "TEXT"],


    classfield ={
        "room" : [],#["RoomName", "TEXT"],["RoomNumber", "TEXT"],["Department", "TEXT"], [ "PaintCode", "TEXT"], ["FlooringMaterial", "TEXT"],["FloorInstallDate", "TEXT"],["DocumentPathway", "TEXT"]],
        "window" :[["RoomId", "TEXT"],[ "Quality", "TEXT"],["WindowType", "TEXT"], ["DoesOpen", "TEXT"]],
        "plumbing":[["RoomId", "TEXT"],[ "Quality", "TEXT"],["TypeOfFixture", "TEXT"]],
        "furniture":[["RoomId", "TEXT"],[ "Quality", "TEXT"],["FurnitureType", "TEXT"], ["Use", "TEXT"]],
        "wall": [["RoomId", "TEXT"],[ "Quality", "TEXT"],[ "Material", "TEXT"]],
        "railing":[["RoomId", "TEXT"],[ "Quality", "TEXT"],[ "Material", "TEXT"]],
        "partition":[["RoomId", "TEXT"],[ "Quality", "TEXT"],["Material", "TEXT"]],
        "door":[["RoomId", "TEXT"],[ "Quality", "TEXT"],["Swing", "TEXT"], [ "Size", "TEXT"], [ "DoorNumber", "TEXT"], [ "LockFunctio", "TEXT"], [ "KeyType", "TEXT"],["Material", "TEXT"], [ "Alarmed", "TEXT"],[ "Finish", "TEXT"],[ "ExteriorDoor", "TEXT"]],
        "incline":[],
        "doorswing": [["RoomId", "TEXT"],[ "Quality", "TEXT"]],
        "stair":[],
        "hvacpolygon":[["RoomId", "TEXT"],[ "Quality", "TEXT"],[ "AssetType", "TEXT"]],
        "fireprotection": [["RoomId", "TEXT"],[ "EquipmentType", "TEXT"],[ "FireExtinguisherType", "TEXT"]],
        "hvac":[["RoomId", "TEXT"], [ "Quality", "TEXT"], ["EquipmentType", "TEXT"], ["Manufacturer", "TEXT"], [ "ModelNumber", "TEXT"], [ "BeltSize", "TEXT"], ["FilterSize", "TEXT"], [ "IsGas", "TEXT"], ["IsElectric", "TEXT"], [ "SerialNumber", "TEXT"], [ "EquipmentTag", "TEXT"], [ "Equipment_Type", "TEXT"]],
        "fence":[["RoomId", "TEXT"],[ "Quality", "TEXT"],],
        "unknown":[["RoomId", "TEXT"],[ "Quality", "TEXT"],],
        "department":[["FacilityID", "TEXT"], ["Department", "TEXT"]]
   }
    for key in classfield.keys():
        if key == inputclass:
            for field in  classfield[inputclass]:
                try:
                    ar.AddField_management(output, field[0], field[1])
                    print "FIELD ADDED: %s as %s datatype" % (field[0], field[1])    
                except:
                    print "FEILD SKIPPED: ", field[0]
    # cal/ populate filed fo Create date and createby
    exp = '''def Add_date():
        import time
        return time.strftime('%d/%m/%Y')'''
    ar.CalculateField_management(output, "CreateDate", 'Add_date()', "PYTHON", exp)
    exp = str("\""+ str(getpass.getuser())+"\"")
    ar.CalculateField_management(output, "CreateBy", exp, "PYTHON")

# function to identify pathway to a GDB (and only GDB)
def getGDBPath():
    while True:
        GDB_path = tkFileDialog.askdirectory(initialdir = "/",title = "Select Geodatabase (.gdb)",)  
        if GDB_path.lower()[-3:] == "gdb":
            return GDB_path
            break
        else:
            print "Not a Geodatabase. Please try again, bud."

# function to match FCtype to its respected abbreviation as part of asset ID
def FCTYPE_TO_ID_engine(fctype):
    fctypeIDlist =[["DP",	"DEPARTMENT"],["DR",	"DOOR"],["DS",	"DOORSWING"],["EL",  "ELECTRICAL"],["FC","FENCE"],["FP",	"FIRE PROTECTION"],["FR", "FURNITURE"],["HVAC", "HVAC"],["HVACP","HVAC POLYGON"],["IN","INCLINE"],["PR","PARTITION"],["PF",	"PLUMBING"],["RL",  "RAILING"],["RM", "ROOM"],["ST",	"STAIR"],["WL",	"WALL"],["WD",	"WINDOW"]]
    for fctypeid in fctypeIDlist:
        if fctypeid[1] ==  str(lyrtype)[3:-3].upper():
            return fctypeid[0]

# function to build final Report
def reportbuilder(strl,finl,labl):
    n_groups = len(labl)
    index = np.arange(n_groups)
    fig, ax = plt.subplots()
    labl = [str(x)[3:-3] for x in labl]
    bar_width = 0.35
    opacity = 0.4
    error_config = {'ecolor': '0.3'}
    rects1 = ax.bar(index, strl, bar_width, alpha=opacity, color='b', label='Start')

    rects2 = ax.bar(index+ bar_width  , finl, bar_width, alpha=opacity, color='G', label='Final')

    ax.set_ylabel('Count of Features')
    ax.set_xlabel('Building Feature Type')
    ax.set_title('CAD-GDB Report for: ' +out_dataset_name)
    ax.set_xticks(index)
    ax.set_xticklabels(labl,ha = 'center', rotation= 40)
    ax.legend()
    plt.show(block=True)

#### BEGINING 


print "------------------------------------------------------------------------"
# clearing workspace from previous runs
arcpy.ClearWorkspaceCache_management()

# get locations of CAD file and GDB
root = Tk()
CADpath =str(tkFileDialog.askopenfilename(initialdir = "//vsrvgisprod01/gisintern/",title = "Select Drawing file (.DWG)",filetypes = (("DWG files","*.dwg"),("all files","*.*"))))
#name CAD file 
out_dataset_name = CADpath.split("/")[-1][:-4] 
# get locaiton of GDB
out_gdb_path = getGDBPath()  
root.destroy()
#bring cad to Geodatbase
CADtoGDB(CADpath, out_gdb_path)
#get floor type 
flrlvl =getfloor()
#Create name var       
flpath = out_gdb_path+'/'+flrlvl[0]
# creater list of feature cout for final report  
strbdf= []
finbdf= []
labl = []
# set workplace 
ar.env.workspace =out_gdb_path
ar.env.overwriteOutput== True
# used fuction at top to selct path of input polygon feature class 
print "------------------------------------------------------------------------"
print GDB_polyGfile_loc(out_dataset_name)
polygon = GDB_polyGfile_loc(out_dataset_name)

#line feature colected 
line = GDB_polyLfile_loc(out_dataset_name)
# Build a list of types of building features /GDB feature classes for polygon and polyline 
poly_lyrtypes = np.unique(ar.da.TableToNumPyArray(polygon,"layer"))
line_lyrtypes = np.unique(ar.da.TableToNumPyArray(line,"layer"))
#remove building features in polygon list fromthe polyline list 
line_lyrtypes = [x for x in line_lyrtypes if x not in  poly_lyrtypes]

# set has GBD FCs as features layers 
ar.MakeFeatureLayer_management(polygon, "polygon")
ar.MakeFeatureLayer_management(line, "line")
#list of commnon fields. (aka fields that all building types have )
comfields= [["AssetID", "TEXT"],["RoomID", "TEXT"],["CreateDate", "DATE"], ["CreateBy", "TEXT"],["UpdateDate", "DATE"], ["UpdateBy", "TEXT"], ["Notes", "TEXT"]]
# list of fields not used
delfields =["Entity", "Handle", "LyrFrzn", "LyrLock", "LyrOn", "LyrVPFrzn", "LyrHandle",
            "Color", "EntColor", "LyrColor", "BlkColor", "Linetype","EntLinetype", "LyrLnType", "BlkLinetype", "Elevation",
            "Thickness", "LineWt", "EntLineWt", "LyrLineWt", "BlkLineWt",
            "RefName", "LTScale", "ExtX", "ExtY", "ExtZ", "DocName",
            "DocPath", "DocType", "DocVer"]
for field in delfields:
    try:
        ar.DeleteField_management("polygon", field)
        print "FIELD DELETED:", field
    except:
        print "FEILD SKIPPED: ", field
for field in comfields:
    ar.AddField_management("polygon", field[0], field[1])
    print "FIELD ADDED: %s as %s datatype" % (field[0], field[1]) 


print "------------------------------------------------------------------------"
print line

for field in delfields:
    try:
        ar.DeleteField_management("line", field)
        print "FIELD DELETED:", field
    except:
        print "FEILD SKIPPED: ", field

for field in comfields:
    ar.AddField_management("line", field[0], field[1])
    print "FIELD ADDED: %s as %s datatype" % (field[0], field[1])
    


print "------------------------------------------------------------------------"
# for loop to created a GDB FC for each polygon building feature(i.e. doors, walls, etc.)
for lyrtype in poly_lyrtypes:
        # Append to lable list
        labl.append(lyrtype)
        lyrtype= str(lyrtype).replace(" ","_")
        #output 
        output = flpath +"/"+out_dataset_name+"_"+str(lyrtype)[3:-3]
        #removing old Feature Class if exists
        if ar.Exists(output):
            print "Replaced old Feature Class located at:", output
            ar.Delete_management(output)    
       
        SQL_query = "Layer= "+ str(lyrtype)[2:-2]
        # Select building feature type  
        selected = ar.SelectLayerByAttribute_management("polygon", "NEW_SELECTION", SQL_query)
        print str(lyrtype)[3:-3],  " \t \t Starting Number: \t" + str(ar.GetCount_management(selected))
        # append to starlist
        strbdf.append(int(ar.GetCount_management(selected).getOutput(0)))
        # Feature To Polygon or Line 
        ar.FeatureToPolygon_management(selected, output)
        # Add Location Field to created GDB feature class
        ar.AddField_management(output, "Location", "TEXT")
        # Calculate Location Field created GDB feature class (based off of )
        calc = str("\""+ out_dataset_name +"\"")
        ar.CalculateField_management(output, "Location", calc, "PYTHON")
        print str(lyrtype)[3:-3], " \t \t Final Number:    \t" + str(ar.GetCount_management(output))
        #append to final list 
        finbdf.append(int(ar.GetCount_management(output).getOutput(0)))
        #remove FID_Polyline/gon field and layer field
        FID_poly_feild_delate(output)
        ar.DeleteField_management(output, "layer")
        #Add class-specific Fields to created GDB feature class
        try:
            field_generator(str(lyrtype)[3:-3])
        except:
            print "building type not defined"
      
        #populate  a AssetID 
        FCID= FCTYPE_TO_ID_engine(lyrtype)                                                                   #update 
        exp =  str("\""+ str(flrlvl[1]) +"\""+"+"+ "\""+ str(FCID) +"\""" + str(!OBJECTID!)")
        print exp
        ar.CalculateField_management(output, "AssetID", exp, "PYTHON")

        print "Completed Feature Class located at:",  output
        print "------------------------------------------------------------------------"     
## to created a GDB FC for each polyline building feature(i.e. doorswing, roomlines, etc.)
print line
print "------------------------------------------------------------------------"
for lyrtype in line_lyrtypes:# Append to lable list
        labl.append(lyrtype)
        lyrtype= str(lyrtype).replace(" ","_")
        #output 
        output = flpath +"/"+out_dataset_name+"_"+str(lyrtype)[3:-3]
        
        #removing old Feature Class if exists
        if ar.Exists(output):
            print "Replaced old Feature Class located at:", output
            ar.Delete_management(output)    
        SQL_query = "Layer= "+ str(lyrtype)[2:-2]
        # Select building feature type  
        selected = ar.SelectLayerByAttribute_management("line", "NEW_SELECTION", SQL_query)
        print str(lyrtype)[3:-3],  " \t \t Starting Number: \t" + str(ar.GetCount_management(selected))
        # append to starlist
        strbdf.append(int(ar.GetCount_management(selected).getOutput(0)))
        # Feature To Polygon or Line
        ar.FeatureToLine_management(selected, output)
        # Add Location Field to created GDB feature class
        ar.AddField_management(output, "Location", "TEXT")
        # Calculate Location Field created GDB feature class (based off of )
        calc = str("\""+ out_dataset_name +"\"")
        ar.CalculateField_management(output, "Location", calc, "PYTHON")
        print str(lyrtype)[3:-3], " \t \t Final Number:    \t" + str(ar.GetCount_management(output))
        #append to final list 
        finbdf.append(int(ar.GetCount_management(output).getOutput(0)))
        #remove FID_Polyline/gon field and layer field
        FID_poly_feild_delate(output)
        ar.DeleteField_management(output, "layer")
        #  Add class-specific Fields to created GDB feature class
        try:
            field_generator(str(lyrtype)[3:-3])
        except:
           print "building type not defined"
        #populate  a AssetID 
        FCID= FCTYPE_TO_ID_engine(lyrtype)                                                                   #update 
        exp =  str("\""+ str(flrlvl[1]) +"\""+"+"+ "\""+ str(FCID) +"\""" + str(!OBJECTID!)")
        print exp
        ar.CalculateField_management(output, "AssetID", exp, "PYTHON")


        print "Completed Feature Class located at:",  output
        print "------------------------------------------------------------------------"
# by this point all should be done 
print "ALL DONE"

#print strbdf
#print finbdf
#print labl

while True:
    Report = str(raw_input("Want a Report Graphic? (yes or no) "))
    if Report in["y", "Y", "yes", "Yes"]:
        reportbuilder(strbdf,finbdf,labl)
        break
    elif Report.lower() in ["no", "N", "No", "n"]:
        break
    else:
        print "Not an answer. Try again."
print "------------------------------------------------------------------------"
close = str(raw_input("Hit Enter to Close"))
