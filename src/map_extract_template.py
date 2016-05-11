#!/usr/bin/env python
#
from imposm.parser import OSMParser
from graph_tool.all import 
from sets import sets
from datetime import datetime
import sys, argparse, logging, math


# Gather our code in a main() function
def main(args, loglevel):
  logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)
  #Initialize MapParser object
  map_parser = MapParser()
  map_parser.run(args)
  
class MapParser(object):
  def run(self,filename):
    if args.draw:
      self.draw(args.draw)
    if args.output:
      self.tntp(args.output)
    if args.vissim:
      self.vissim(args.vissim)
      
  

 
if __name__ == '__main__':
 
  parser = argparse.ArgumentParser(description='OSM map parser to output network in different formats')
  parser.add_argument('osm_filename', help='Name of the OSM file you want to parse')
  parser.add_argument('-d','--draw', help='Outputs an image of the map network')
  parser.add_argument('-o','--output', help='Output filename of network')
  parser.add_argument('-v','--vissim', help='Output file in VISSIM format')
  args = parser.parse_args()
  
  # Setup logging
  if args.verbose:
    loglevel = logging.DEBUG
  else:
    loglevel = logging.INFO
  
  main(args, loglevel)
