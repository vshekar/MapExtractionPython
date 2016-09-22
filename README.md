#OSM map extractor

##Synopsis
This is code is part of the research supported by the the United States Department of Homeland Security (DHS) through the National Center for Risk and Economic Analysis of Terrorism Events (CREATE) at the University of Southern California (USC) under award number 2010-ST-061-RE0001

This python script converts any OSM file into a network representation. Valid outputs can be pdf or png image, TNTP format or VISSIM (Experimental) format

##Dependencies

Imposm.parser: http://imposm.org/docs/imposm/latest/install.html

graph-tools: https://graph-tool.skewed.de/download

##Usage
usage: map_extract.py [-h] [-d DRAW] [-o OUTPUT] [-v VISSIM] osm_filename

-d Draws the network into a file called DRAW
-o Outputs the network into a TNTP file called OUTPUT
-v Outputs the network into a VISSIM file (version 12) [Currently not being worked on]

