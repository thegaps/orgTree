#!/usr/bin/python2.7

# Source tangled from org_tree.org

# Prints an org mode files outline (headlines only,
#     actual names given to the nodes are configurable)
# TODO:
# Seems sensitive to headline length.
# Incorrect results w/ out of order nesting, e.g:
# * h1
# *** h2
# ** h3

from PyOrgMode import PyOrgMode
from anytree import Node, RenderTree
import argparse as ap

# Handle arguments
parser = ap.ArgumentParser(description="Creates an image of the tree structure of an org file")
parser.add_argument("-v", "--verbose",
action="store_true")
nodeNameControl = parser.add_mutually_exclusive_group()
nodeNameControl.add_argument("-n", "--number-headings",
action="store_true",
 help="Don't include heading text in output, number them on discovery instead. Cannot use in conjunction with -l.")
nodeNameControl.add_argument("-l", "--len-heading",
type=int,
 metavar='X',
 default=-1,
 help="Limit the number of characters kept from org file headings to 'X'. 'X' = 0 will keep all characters. Cannot use in conjunction with -n.")
parser.add_argument("org",
 type=str,
 help="the input org file")
parser.add_argument("image",
 type=str,
 help="the output image")
args = parser.parse_args()
v = args.verbose

# if using the node heading as a node name;
#    how many chars to keep? (-1=all)
nodeHeadingTruncatedLength = args.len_heading

# Load the org file
tree = PyOrgMode.OrgDataStructure()
tree.load_from_file(args.org)

def nodeHead(node):
    '''
    Returns the heading to use for a node
    '''
    nodeHead.counter += 1
    heading = ''
    try:
        if nodeHeadingTruncatedLength == -1:
                heading = node.heading
        else:
                heading = node.heading[:nodeHeadingTruncatedLength]
    except:
        if v: print("heading is zero-length (I think)")
        heading = "<>" # use some symbols to stand for 'empty'
    if args.number_headings: heading = nodeHead.counter
    if v: print(nodeHead.counter, heading)
    return heading
nodeHead.counter = 0

def isNode(nodeCandidate):
    '''
    Super rough way of picking whether an instance is a node or something else
    Should use type() once classes in PyOrgMode library are updated
    '''
    return (18 <= (len(dir(nodeCandidate))) <= 19)

trunk = tree.root # org file root
currentNode = trunk
root = Node("root") # init our anytree root node
lastNode = root
def gobbleBranch(node,lastNode):
    '''
    Traverse!
    1) record node name
    2) if there are child nodes, repeat the proces with one of them
    3) if there are no children, pop back, and move along to the next node
    4) if there is no next node, quit
    
    Gonna need to learn about function scope w/ recursive calls
    '''
    if v: print("\ngobbling node")
    if v: print(nodeHead(node))
    #if v and node.content: print(node.content)
    #if v: print(len(dir(node)))
    if len(node.content) == 0:
        # Hit rock bottom, node does not contain text
        # Record this node, then return
        if v: print("_0_\nheading: {}\t level:{}".format(nodeHead(node),node.level))
        newNode = Node(nodeHead(node), parent=lastNode)
    else:
        # Node has something which could be children. Recursively call this function for all legitimate node-children
        lastNode = Node(nodeHead(node), parent=lastNode)
        for nextNode in node.content:
            if isNode(nextNode) and isinstance(nextNode, PyOrgMode.OrgElement):
                gobbleBranch(nextNode,lastNode)
    return

# Traverse the tree
gobbleBranch(trunk,lastNode)

# The location of the root node is a bit off
actualRoot = root.children[0]
actualRoot.name = "Org File Root"

# Render the tree in text
for pre, fill, node in RenderTree(actualRoot):
    # two ways to do the same thing
    #print("{}{}".format(pre.encode('utf-8'), node.name.encode('utf-8')))
    print("%s%s" % (pre, node.name))

# Render the tree as an image
from anytree.dotexport import RenderTreeGraph
RenderTreeGraph(actualRoot).to_picture(args.image)

# Source tangled from org_tree.org
