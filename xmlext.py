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

	# Clean up extraneous whitespace; the ET parser ain't perfect
	rootIter = root.iter()

	for node in rootIter:
		if node.text and re.sub('\s', '', node.text)=='':
			node.text = None

		node.tail = None

	return root

def write_tree(filename, root):
	pretty = minidom.parseString(ET.tostring(root)).toprettyxml().encode('UTF-8')
	
	f = open(filename, 'w')
	f.write(pretty)
	f.close()

def sort_resursive(nodes):
	nodes.sort(key=node_key_selector)

	for node in nodes:
		sort_resursive(node.getchildren())

def node_key_selector(node):
	key = node.tag

	attrs = list(node.attrib.keys())

	attrs.sort()

	for attr in attrs:
		key += attr + node.attrib[attr]

	return key

def coalesce_children(parent):
	survivors = dict()

	for child in parent.getchildren():
		key = node_key_selector(parent)

		if key in survivors:
			survivors[key].extend(child.getchildren())
			parent.remove(child)
		else:
			survivors[key] = child

def unfuckulate(inFileName, outFileName):
	root = read_tree(inFileName)
	coalesce_children(root)
	sort_resursive(root.getchildren())
	write_tree(outFileName, root)

if __name__ == '__main__':
	unfuckulate(sys.argv[1], sys.argv[2])
	

