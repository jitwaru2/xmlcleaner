import sys
import re
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

def register_namespaces():
	ET.register_namespace("", "http://schemas.microsoft.com/developer/msbuild/2003")

register_namespaces()

def read_tree(filename):
	f = open(filename, 'r')
	contents = f.read()
	f.close()
	root = ET.fromstring(contents)

	# Clean up extraneous whitespace
	# Take the following XML:
	# <node>\n\t
	# 	<innerNode>\n\t
	# 	</innerNode>\n
	# </node>
	# ET treats the whitespace follwing each starting tag declaration as node
	# text, maybe in an attempt to prevent data loss - but this screws with 
	# pretty printing. I think it's safe to treat any pure whitespace string
	# as insignificant.
	rootIter = root.iter()

	for node in rootIter:
		if node.text and re.sub('\s', '', node.text)=='':
			node.text = None

		node.tail = None

	return root

def write_tree(filename, root):
	# Unfortunately have to rely on minidom to do the pretty printing
	# because ET sucks at it
	pretty = minidom.parseString(ET.tostring(root)).toprettyxml().encode('UTF-8')
	
	f = open(filename, 'w')
	f.write(pretty)
	f.close()

##
# Combines the children of nodes that have the same natural key.
# The combination is stable; that is, the children are travered
# in document order (depth first) and node children are appended
# to the first encountered node with the same natural key

def coalesce_tree(root):
	_coalesce_children(root)


def _coalesce_children(parent):
	survivors = dict()

	for child in parent.getchildren():
		key = _natural_key(parent)

		if key in survivors:
			survivors[key].extend(child.getchildren())
			parent.remove(child)
		else:
			survivors[key] = child

##
# Sorts nodes recursively, ordered by natural key

def sort_tree(root):
	_sort_nodes_resursive(root.getchildren())


def _sort_nodes_resursive(nodes):
	nodes.sort(key=_natural_key)

	for node in nodes:
		_sort_nodes_resursive(node.getchildren())

##
# Generates a natural key for a node by concatenating the tag, attribute 
# names, and attribute value (after lexicographically sorting the attributes 
# by key)
# i.e. <Josh Attr2="Value2" Attr1="Value1"></Josh>
# Generated key: JoshAttr1Value1Attr2Value2
#
# Useful for sorting nodes and identifying which nodes can safely be 
# coalesced

def _natural_key(node):
	key = node.tag

	attrs = list(node.attrib.keys())

	attrs.sort()

	for attr in attrs:
		key += attr + node.attrib[attr]

	return key

##
# Fuck your arbitrary bullshit .csproj files

def unfuckulate(inFileName, outFileName):
	root = read_tree(inFileName)
	coalesce_tree(root)
	sort_tree(root)
	write_tree(outFileName, root)

if __name__ == '__main__':
	unfuckulate(sys.argv[1], sys.argv[2])
	

