import sys
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

def read_tree(filename):
	f = open(filename, 'r')
	contents = f.read()
	f.close()
	root = ET.fromstring(contents)
	return root

def write_tree(filename, root):
	pretty = minidom.parseString(ET.tostring(root).replace('\t','').replace('\n','')).toprettyxml()
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

def create_sorted_doc(inFileName, outFileName):
	root = read_tree(inFileName)
	sort_resursive(root.getchildren())
	write_tree(outFileName, root)
