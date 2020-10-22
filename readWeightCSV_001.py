# -*- coding: UTF-8 -*-

import rhinoscriptsyntax as rs
import System.Drawing.Color

# ---- function to fix strings ----------------------------------------------------------
def fixString(s):
    
    items = s.strip("()\n").split("\"")
    
    if(len(items)>1):
        replacing = False
        
        outStr=""
        for ch in s:
            if ch=='"':
                if replacing:
                    replacing = False
                else:
                    replacing = True
                    
            if ch==',':
                if replacing:
                    ch='_'
            
            outStr += ch
        s=outStr        
    
    return s


# ---- function to convert strings to numbers ------------------------------------------------------
def convert(s):
    conv=0
    doRetry=False
    
    try:
        conv = float(s)
    except:
        doRetry=True

    if doRetry:        
        try:
            s=s.replace("_",'')
            s=s.replace("\"",'')
            conv = float(s)
        except:
            conv=0
            raise Exception("Sorry, could not convert the text to a number") 
        
    return conv


# ---- function to read the weight file ------------------------------------------------------
def ReadWeightFile():
    filename = 'C:/Users/Public/code_example/weights.csv'       # the name of the weights CSV file
    file = open(filename, "r")                                  # open the file for reading
    
    weightLayerParent="WeightsImport"                           #   the Rhino layer to which we will add our geometry
    if not rs.IsLayer(weightLayerParent):                       #   if the layer doesn't already exist......
        rs.AddLayer(weightLayerParent, System.Drawing.Color.Blue,True,False);   # create the new layer

    systemColours =  {  'Structure'     : rs.CreateColor(128,128,255),          # colour for items tagged 'Structure' in the CSV file
                        'Engineering'   : rs.CreateColor(255,32,32),            # colour for items tagged 'Engineering' in the CSV file
                        'Outfitting'    : rs.CreateColor(255,255,128)           # colour for items tagged 'Outfitting' in the CSV file
                        }    
   
    #... read the file .................
    row=0                                                   # keep track of the row of the CSV file we're reading

    for line in file:                                       # for each line in the file....
        row+=1                                              # increment the row count
        
        if( row>1 ):                                        # ignore the first row (the headers)    
            
            line = fixString(line)                          # clean up the text fom the spreadsheet - needed when there are commas insode quote marks
            items = line.strip("()\n").split(",")           # break the line into comma-separated values   
            
            if len(items)>11:                               # make sure the lines contain redable data
            
                readOkay = False
                
                try:                                        # use a try...catch block in case parsing the data fails
                    group=items[0]                          # read the data....
                    subGroup=items[1]                       #    
                    item=items[2]                           #
                    name = group + "|" + subGroup + "|" + item 
                    weig=convert(items[7])                  #
                    posL=convert(items[8])*1000             # convert m to mm
                    posT=convert(items[9])*1000             # convert m to mm
                    posV=convert(items[10])*1000            # convert m to mm
                    readOkay = True                         
                
                    # create the box geometry ............
                    boxCentre = [posL,posT,posV]            # centre of the box  
                    corners = []                            # make a list of corners of the box  
                    
                    for i in range(0,8): 
                        corners.append( [posL,posT,posV] )
                    
                    edSize= 250 + weig*1                    # scale the weight into a size for the box
                    edSize= 0.5 * edSize                    # size = total length of an edge, so divide by 2
                    
                    corners[0][0]-=edSize
                    corners[3][0]-=edSize
                    corners[4][0]-=edSize
                    corners[7][0]-=edSize
                    corners[1][0]+=edSize
                    corners[2][0]+=edSize
                    corners[5][0]+=edSize
                    corners[6][0]+=edSize
                    
                    corners[0][1]-=edSize
                    corners[1][1]-=edSize
                    corners[4][1]-=edSize
                    corners[5][1]-=edSize
                    corners[2][1]+=edSize
                    corners[3][1]+=edSize
                    corners[6][1]+=edSize
                    corners[7][1]+=edSize
        
                    corners[4][2]+=edSize
                    corners[5][2]+=edSize
                    corners[6][2]+=edSize
                    corners[7][2]+=edSize
        
        
                    box = rs.AddBox(corners)                #   add the box to the Rhino database
                    rs.ObjectName( box, name )
                
                    if group in systemColours:                          # if the 'system' matches a name in our list
                        rs.ObjectColor( box, systemColours[group] )     #   set the colour
                    else:                                               # otherwise...
                        rs.ObjectColor( box, (255,0,0 ))                # use a default colour    

                    # set the 'user text' fields for this object                
                    rs.SetUserText( box, "group", group)
                    rs.SetUserText( box, "subGroup", subGroup)
                    rs.SetUserText( box, "item", item)
                    rs.SetUserText( box, "Weight", weig)
                    rs.SetUserText( box, "_importRowNum", row)

                    # put the object on a layer whose name matches the 'Group' column from the CSV file
                    layerName=group
                    if not rs.IsLayer(layerName):
                        rs.AddLayer(layerName, System.Drawing.Color.Blue,True,False,weightLayerParent);
                    rs.ObjectLayer(box, layerName)
                    
                    readOkay = True
                        
                except:
                    print "CONVERSION ERROR: line" + str(row) + ":" + line      # in case something went wrong, show a warning


# ---- main function ------------------------------------------------------
#      execution of the code starts here
#
if( __name__ == "__main__" ):
    rs.EnableRedraw(False)
    ReadWeightFile()
    rs.EnableRedraw(True)
