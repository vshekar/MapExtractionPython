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
    #List of road types excluded from parsing
    highways_excluded = ['steps','footway','pedestrian']
    num_nodes = 0
    num_roads = 0

    def run(self,filename):
        self.p = OSMParser(ways_callback=self.find_highway_nodes)
        self.p.parse(args.osm_filename)
        print("Highway nodes found")
        self.p =  OSMParser(coords_callback=self.count_nodes)
        self.p.parse(args.osm_filename)
        self.p = OSMParser(ways_callback=self.connect_nodes)
        self.p.parse(args.osm_filename)
        
        if args.draw:
            self.draw(args.draw)
        if args.output:
            self.tntp(args.output)
        if args.vissim:
            self.vissim(args.vissim)
        

    def find_highway_nodes(self, ways):
        """Find all nodes with the tag 'Highway'"""
        for osm_id, tags, refs in ways:
            if 'highway' in tags and tags['highway'] not in self.highways_excluded:
                for r in refs:
                    self.highway_nodes.add(r)

    def node_data_extract(self, nodes):
        """After finding all higway nodes, get their lat and lng values"""
        for osm_id, lat, lng in nodes:
            if osm_id in self.highway_nodes:
                self.osm_to_graph[osm_id] = self.num_nodes
                self.g.add_vertex()
                self.vprop_pos[self.g.vertex(self.nodes)] = [lat,lng]
                self.nodes+=1

    def add_edges(self, ways):
        """Add edges to the graph-tool Graph"""

        for osm_id, tags, refs in ways:
            if 'highway' in tags and tags['highway'] not in self.highways_excluded:
                self.num_roads += 1
                for i in range(len(refs)-1):
                    if refs[i] in self.osm_to_graph and refs[i+1] in self.osm_to_graph:
                        v1 = self.g.vertex(self.osm_to_graph[refs[i]])
                        v2 = self.g.vertex(self.osm_to_graph[refs[i+1]])
                        #Make sure that the road direction is correct
                        if i ==0:
                            e = self.g.add_edge(v2,v1)
                            self.vprop_size[v1] = self.node_size
                            if 'oneway' not in tags:
                                self.eprop_marker[e] = 2
                        else:
                            e = self.g.add_edge(v1,v2)
                        
                        if 'oneway' in tags and tags['oneway'] == 'yes':
                            self.eprop_thickness[e] = 0.25
                            if i==len(refs)-2:
                                self.eprop_marker[e] = 2
                        else:
                            self.eprop_thickness[e] = 0.75
                            self.eprop_marker[e] = 0
                        	
                        if self.vprop_size[v1] != self.node_size:
                            self.vprop_size[v1] = 0.0
                        if i==len(refs)-2:
                            self.vprop_size[v2] = self.node_size
                                

                        if self.vprop_size[v2] != self.node_size:
                            self.vprop_size[v2] = 0.0
                        self.vprop_fill_color[v1] = [0.640625, 0, 0, 0.9]
                        self.vprop_fill_color[v2] = [0.640625, 0, 0, 0.9]
                        self.vprop_shape[v1] = 0
                        self.vprop_shape[v2] = 0
                        
          
  

 
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
