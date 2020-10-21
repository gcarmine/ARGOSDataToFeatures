##---------------------------------------------------------------------
## ImportARGOS.py
##
## Description: Read in ARGOS formatted tracking data and create a line
##    feature class from the [filtered] tracking points
##
## Usage: ImportArgos <ARGOS folder> <Output feature class> 
##
## Created: Fall 2020
## Author: John.Fay@duke.edu (for ENV859)
##---------------------------------------------------------------------

# Import modules
import sys, os, arcpy

#Allow arcpy to overwrite outputs
arcpy.env.overwriteOutput = True

# Set input variables (user input)
inputFolder = arcpy.GetParameterAsText(0)
outputFC = arcpy.GetParameterAsText(1)
outputSR = arcpy.GetParameterAsText(2)

#Create an empty feature class to which we'll add features
outPath, outName = os.path.split(outputFC)
arcpy.CreateFeatureclass_management(outPath,outName, "POINT","","","",outputSR)

# Add TagID, LC, IQ, and Date fields to the output feature class
arcpy.AddField_management(outputFC,"TagID","LONG")
arcpy.AddField_management(outputFC,"LC","TEXT")
arcpy.AddField_management(outputFC,"Date","TEXT")

# Create the insert cursor
cur = arcpy.da.InsertCursor(outputFC,['Shape@','TagID','LC','Date'])

#Iterate through each ARGOS file
inputFiles = os.listdir(inputFolder)
for inputFile in inputFiles:
    #Don't process README.txt file
    if inputFile == "README.txt":
        continue
    
    #Add full path to inputFile name
    inputFile_full = os.path.join(inputFolder,inputFile)
    arcpy.AddMessage(f"Processing {inputFile}")
    
    # Open the ARGOS data file for reading
    inputFileObj = open(inputFile_full,'r')
    
    # Get the first line of data, so we can use the while loop
    lineString = inputFileObj.readline()
    
    #Start the while loop
    while lineString: 
        
        # Set code to run only if the line contains the string "Date: "
        if ("Date :" in lineString):
            
            # Parse the line into a list
            lineData = lineString.split()
            
            # Extract attributes from the datum header line
            tagID = lineData[0]
            obsDate = lineData[3]
            obsTime = lineData[4]
            obsLC = lineData[7]
            
            # Extract location info from the next line
            line2String = inputFileObj.readline()
            
            # Parse the line into a list
            line2Data = line2String.split()
            
            # Extract the date we need to variables
            obsLat = line2Data[2]
            obsLon= line2Data[5]
            
            try:
            
              # Convert raw coordinate strings to numbers
                if obsLat[-1] == 'N':
                    obsLat = float(obsLat[:-1])
                else:
                    obsLat = float(obsLat[:-1]) * -1
                if obsLon[-1] == 'E':
                    obsLon = float(obsLon[:-1])
                else:
                    obsLon = float(obsLon[:-1]) * -1   
                
               # Construct a point object from the feature class
                obsPoint = arcpy.Point()
                obsPoint.X = obsLon
                obsPoint.Y = obsLat
                
            #handle any error
            except Exception as e:
                pass
                #print(f"Error adding record {tagID} to the output")     
            
             # Convert the point to a point geometry object with spatial reference
            inputSR = arcpy.SpatialReference(4326)
            obsPointGeom = arcpy.PointGeometry(obsPoint,inputSR)
            
             # Add a feature using our insert cursur
            feature = cur.insertRow((obsPointGeom,tagID,obsLC,obsDate.replace(".","/") + " " + obsTime))
            
        
        # Move to the next line so the while loop progresses
        lineString = inputFileObj.readline()
        
    #Close the file object
    inputFileObj.close()

#Delete the cursor object
del cur