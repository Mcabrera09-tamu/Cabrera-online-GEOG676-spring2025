

import arcpy

import time


class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [GraduatedColorRenderer]


class GraduatedColorRenderer:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "graduatedcolor"
        self.description = "create a graduated color map based on a specific attribute of a layer"
        self.canRunInBackground = False
        self.category = "MapTools"

    def getParameterInfo(self):
        """Define the tool parameters."""
        #This is the original Project Name
        param0 = arcpy.Parameter(
            displayName="Input ArcGIS Pro Project Name",
            name="aprxInputname",
            datatype="DEFile",
            parameterType="Required",
            direction="Input"
        )

        #Which layer to classify to get a color map
        param1 = arcpy.Parameter(
            displayName="Layer To Classify",
            name="LayertoClassify",
            datatype="GPLayer",
            parameterType="Required",
            direction="Input"
        )

        #The output Folder Location
        param2 = arcpy.Parameter(
            displayName="Output Location",
            name="OutputLocation",
            datatype="DEFolder",
            direction="Input"
        )

        #The Output Project Name
        param3 = arcpy.Parameter(
            displayName="Output Project Name",
            name="OutputProjectName",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        params = [param0, param1, param2, param3]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        #Define Progressor Variables
        readTime = 3 #The Time For Users To Read The Progress
        start = 0 #Beginning Position Of The Progressor
        max = 100 #End Position
        step = 33 #The Progress Interval To Move The Progressor Along

        #Setup Progressor
        arcpy.SetProgressor("step", "Validating Project File...", start, max, step)
        time.sleep(readTime) #pause the execution for 3 seconds
        #add messages to result Panel
        arcpy.AddMessage("Validating Project File...")

        #Project File
        project = arcpy.mp.ArcGISProject(parameters[0].valueAsText)

        #Grab the first Instance of a Map from the .aprx
        campus = project.listMaps('Map')[0]

        #Increment Progressor
        arcpy.SetProgressorPosition(start + step) #We are now at 33% completed
        arcpy.SetProgressorLabel("Finding your map layer...")
        time.sleep(readTime)
        arcpy.AddMessage("Finding your map layer...")

        #Loop through the layers of the map
        for layer in campus.listLayers():
            #Check that the layer is a Feature Layer
            if layer.isFeatureLayer:
                #copy the layers symbology
                symbology = layer.symbology
                #make sure the symbology has renderer attribute
                if hasattr(symbology, 'renderer'):
                    #Check layer name
                    if layer.name == parameters[1].valueAsText: #check if the input name matches the input layer

                        #increment Progressor
                        arcpy.SetProgressorPosition(start + step*2) #Now its 66% complete
                        arcpy.SetProgressorLabel("Calculating and classifying...")
                        time.sleep(readTime)
                        arcpy.AddMessage("Calculating and classifying...")

                        #update the copy's renderer to "Graduated colors renderer"
                        symbology.updateRenderer('GraduatedColorsRenderer')

                        #tell arcpy which field we want our chloropleth off at
                        symbology.renderer.classificationField = "Shape_Area"

                        #set how many classes we will have for the map
                        symbology.renderer.breakCount = 5

                        #set color ramp
                        symbology.renderer.colorRamp = project.listColorRamps('Oranges (5 Classes)')[0]

                        #set layers actual symbology equal to the copy
                        layer.symbology = symbology

                        arcpy.AddMessage("Finish Generating Layer...")
                    else:
                        print("NO feature layers found")


        #Increment Progressor
        arcpy.SetProgressorPosition(start + step*3) #now its 99% complete
        arcpy.SetProgressorLabel("Saving...")
        time.sleep(readTime)
        arcpy.AddMessage("Saving...")

        project.saveACopy(parameters[2].valueAsText + '\\' + parameters[3].valueAsText + ".aprx")
        #param2 is the folder location and param3 is the name of the new project

        return