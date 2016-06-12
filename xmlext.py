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
# Combines the immediate child nodes of a parent, where the child nodes
# have the same natural key.
# The combination is stable; that is, nodes are travered
# in document order (depth first) and node children are appended
# to the first encountered node with the same natural key. This only
# combines child nodes with the same immediate parent; if two nodes
# have the same natural key, but have different immediate parents,
# they will not be combined.

def coalesce_tree(root):
	_coalesce_recursive(root)


def _coalesce_recursive(parent):
	survivors = dict()

	for child in parent.getchildren():
		_coalesce_recursive(child)

		key = _natural_key(child)

		if key in survivors:
			survivors[key].extend(child.getchildren())
			parent.remove(child)
		else:
			survivors[key] = child

##
# Sorts nodes recursively, ordered by natural key
#
# @param ignoreTags Don't sort a subtree if the root has any of these tags
# This is useful if you have nodes with meaningful order
# i.e. A 'Target' node that specifies an ordered build task

def sort_tree(root, ignoreTags=[]):
	_sort_nodes_resursive(root.getchildren(), ignoreTags)


def _sort_nodes_resursive(nodes, ignoreTags):
	nodes.sort(key=_natural_key)

	for node in nodes:
		if  node.tag not in ignoreTags:
			_sort_nodes_resursive(node.getchildren(), ignoreTags)

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
# Unfuckulate the xml

def unfuckulate(inFileName, outFileName, dontSortTags=[]):
	root = read_tree(inFileName)
	coalesce_tree(root)
	sort_tree(root, dontSortTags)
	write_tree(outFileName, root)

def unfuckulate_csproj(inFileName, outFileName):
	unfuckulate(inFileName, outFileName, ['Target', 'PostBuildEvent'])

if __name__ == '__main__':
	unfuckulate(sys.argv[1], sys.argv[2])
	

