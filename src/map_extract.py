from imposm.parser import OSMParser
from graph_tool.all import *
from sets import Set
import csv
import math
from  datetime import datetime
import argparse

parser = argparse.ArgumentParser(description='OSM map parser to output network in different formats')
parser.add_argument('osm_filename', help='Name of the OSM file you want to parse')
parser.add_argument('-d','--draw', help='Outputs an image of the map network')
parser.add_argument('-o','--output', help='Output filename of network')
parser.add_argument('-v','--vissim', help='Output file in VISSIM format')
args = parser.parse_args()

map_parser = MapParser()
drawFile = None
outputFile = None
vissimFile = None

if args.draw:
	print("Output to filename : " + args.draw)
	drawFile = args.draw

if args.output:
	print("Output network to file : " + args.output)
	outputFile = args.output

if args.vissim:
	print("Output network to VISSIM format : " + args.vissim)
	vissimFile = args.vissim

map_parser.run(args)

class MapParser(object):
	nodes = 0
	hw = 0
	counter = 0
	g = Graph()
	osm_to_graph = {}
	highway_nodes = Set()
	vprop_pos = g.new_vertex_property("vector<double>")
	vprop_size = g.new_vertex_property("double")
	vprop_shape = g.new_vertex_property("double")
	vprop_text = g.new_vertex_property("string")
	vprop_font_size = g.new_vertex_property("int")
	vprop_text_rotation = g.new_vertex_property("double")

	vprop_fill_color = g.new_vertex_property("vector<double>")
	eprop_marker = g.new_edge_property("double")
	eprop_thickness = g.new_edge_property("double")
	node_size = 2.0
	
	#List of road types excluded from parsing
	highways_excluded = ['steps','footway','pedestrian']
	
	#Output filename for VISSIM
	vissim_ip = open('vissim_ip.inp','w')
	link_count = 1	
	
	def find_highway_nodes(self,ways):
		"""Finds all nodes in ways with tag 'Highway'"""
		for osm_id, tags, refs in ways:
			if 'highway' in tags and tags['highway'] not in self.highways_excluded:
				for r in refs:
					#Add nodes to a set of nodes 
					self.highway_nodes.add(r)

	
	def count_nodes(self, nodes):
		""" Callback to count the total number of nodes a way in the map"""
		for osm_id, lat, lng in nodes:
			if osm_id in self.highway_nodes:
				#Add a reference from OSM ID to a node in the graph
				#OSM ID input will give you a self.nodes position output
				self.osm_to_graph[osm_id] = self.nodes
				self.g.add_vertex()
				self.vprop_pos[self.g.vertex(self.nodes)] = [lng,lat]
				self.nodes+=1
				
	def haversine(self,lon1, lat1, lon2, lat2):
		"""
		Calculate the great circle distance between two points 
		on the earth (specified in decimal degrees)
		"""
		# convert decimal degrees to radians 
		print lon1, lat1, lon2, lat2
		lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
		
		# haversine formula 
		dlon = lon2 - lon1 
		dlat = lat2 - lat1 
		a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
		c = 2 * math.asin(math.sqrt(a)) 
		#r = 6371 # Radius of earth in kilometers. Use 3956 for miles
		r =	6378137
		return c * r

	def connect_nodes(self,ways):
		"""Add edges to the graphtool Graph """

		for osm_id, tags, refs in ways:
			if 'highway' in tags and tags['highway'] not in self.highways_excluded:
				self.hw += 1
				
				
				vissim_string = "LINK	" + str(self.link_count) + "  NAME \"\" LABEL 0.00 0.00\n BEHAVIORTYPE	1 DISPLAYTYPE	1\n"
				ip_string = ""
				total_way_dist = 0
				for i in range(len(refs)-1):
					if refs[i] in self.osm_to_graph and refs[i+1] in self.osm_to_graph:
						v1 = self.g.vertex(self.osm_to_graph[refs[i]])
						v2 = self.g.vertex(self.osm_to_graph[refs[i+1]])
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
						
						#Added data for VISSIM
						r = 6378137
						
						lat1, lon1, lat2, lon2 = map(math.radians, [self.vprop_pos[v1][0], self.vprop_pos[v1][1], self.vprop_pos[v2][0], self.vprop_pos[v2][1]])
						
						x1 = r*math.cos(lat1)*math.cos(lon1)
						y1 = r*math.cos(lat1)*math.sin(lon1)
						
						x2 = r*math.cos(lat2)*math.cos(lon2)
						y2 = r*math.cos(lat2)*math.sin(lon2)
						
						
						total_way_dist = math.sqrt(pow(x2-x1,2) + pow(y2-y1,2))
						#total_way_dist += self.haversine(self.vprop_pos[v1][0],self.vprop_pos[v1][1],self.vprop_pos[v2][0],self.vprop_pos[v2][1])
						
						if i ==0:
							ip_string += "\tFROM " + str(x1) + " " + str(y1) +"\n"
							print len(refs)
						elif i+1 == len(refs)-1:
							ip_string += "\n\tTO " + str(x2) + " " + str(y2) +"\n"
						else:
							ip_string += "\tOVER " + str(x2) + " " + str(y2) + "	0.000\t"
						
						if len(refs) ==2:
							ip_string += "\n\tTO " + str(x2) + " " + str(y2) +"\n"

				vissim_string += "LENGTH	"+str(total_way_dist) + "  LANES 1 LANE_WIDTH  3.50 GRADIENT 0.00000	COST 0.00000  SURCHARGE 0.00000 SEGMENT LENGTH 10.000\n"
				vissim_string += ip_string
				self.vissim_ip.write(vissim_string)
				self.link_count+=1

	def write_vissim(self,vissim_filename):
		print("Vissim output")
						


						
	def add_trip(self):
		track = open('track.csv','rb')
		reader = csv.reader(track,delimiter=',')
		counter = 1
		for i,row in enumerate(reader):
			v = self.g.add_vertex()
			self.vprop_pos[v] = [float(row[2]),float(row[3])]
			self.vprop_size[v] = 3
			self.vprop_shape[v] = 8
			self.vprop_fill_color[v] = [0, 0, 0.640625, 0.9]

			if i in [5,25,30,35,55,83,147,193,235,255,270,280,300,320,350]:
				self.vprop_size[v] = 1
				self.vprop_shape[v] = 9
				self.vprop_fill_color[v] = [0, 0.640625, 0, 0.9]
				self.vprop_text[v] = str(counter)
				self.vprop_text_rotation = 1.5708
				self.vprop_font_size = 6
				counter+=1				
			#if i>350:
			#	self.vprop_fill_color[v] = [0, 0.640625, 0, 0.9]


	
	def run2(self,filename):
		start = datetime.now()
		self.p = OSMParser(ways_callback=self.find_highway_nodes)
		self.p.parse(filename)
		print "Highway nodes found"
		self.p =  OSMParser(coords_callback=self.count_nodes)
		self.p.parse(filename)
		print "Created graph nodes"
		self.p = OSMParser(ways_callback=self.connect_nodes)
		self.p.parse(filename)
		#self.add_trip()
		print "Connected nodes. Drawing graph..."
		#graph_draw(self.g,vertex_size=self.vprop_size, pos=self.vprop_pos, vertex_fill_color = self.vprop_fill_color, vertex_shape= self.vprop_shape, vertex_text = self.vprop_text, vertex_text_rotation= self.vprop_text_rotation, vertex_font_size = self.vprop_font_size, edge_marker_size = self.eprop_marker, edge_pen_width=self.eprop_thickness, fit_view=True,output_size=(800,800),output="umassd_track_graph.pdf")
		graph_draw(self.g,vertex_size=self.vprop_size, pos=self.vprop_pos, edge_pen_width=self.eprop_thickness, fit_view=True,output_size=(800,800),output="nyc_test.pdf")
		#edge_marker_size = self.eprop_marker,
		print "Total nodes = " + str(self.nodes)
		print "Reduced nodes = " + str(2*self.hw)
		print "Time taken = " + str(datetime.now()-start)

	def run(self,args):
		start = datetime.now()
		self.p = OSMParser(ways_callback=self.find_highway_nodes)
		self.p.parse(args.osm_filename)
		print("Highway nodes found")
		self.p =  OSMParser(coords_callback=self.count_nodes)
		self.p.parse(args.osm_filename)
		self.p = OSMParser(ways_callback=self.connect_nodes)
		self.p.parse(args.osm_filename)
		if args.draw:
			graph_draw(self.g,vertex_size=self.vprop_size, pos=self.vprop_pos, edge_pen_width=self.eprop_thickness, fit_view=True,output_size=(800,800),output="args.draw")
		print("Connected nodes. Drawing graph...")
"""			
parser = MapParser()
#p = OSMParser(coords_callback=parser.coords_callback)
#parser.run('/home/vshekar/Downloads/map(2).osm')
#parser.run('/home/vshekar/Downloads/map_nyc.osm')
parser.run('./umassd.osm')
print parser.nodes
print "Parsing complete!"
"""
