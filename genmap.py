#!/usr/bin/python3

import sys
import json
from textwrap import fill
from optparse import OptionParser
class map_node:
    def __init__(self):
        self.name = ''
        self.content = ''
        self.solutions = list()
        self.evidence = list()
        self.deps = set()

class dot_map:
    def __init__(self):
        self.text = 'digraph map{\n'\
                    'graph [rankdir=RL, splines=polyline,'\
                           'arrowType=normal, style=normal]\n'\
                    'node [shape=record, margin=0];\n'
        self.nodes = list()

    def node_by_name(self, name):
        for n in self.nodes:
            if n.name == name:
                return n
        return None

    def add_node_text(self, node, linew=15):
        """Add a node's text to the graphviz output.

        Args:
            node (map_node): The node to format into graphviz text
            linew (num): Max characters per line, longer will be wrapped.

        """
        tprops = 'cellspacing="0" cellborder="1" border="0"'

        # Setup header text
        nText = '{0} [label=<\n'\
                '\t<table {1}>\n'.format(node.name, tprops)

        if 0 < len(node.solutions):
            # Assemble solutions
            srows = ""
            for s in node.solutions:
                ws = fill(s, width=linew).replace("\n", "<br/>")
                srows += '\t\t<tr><td bgcolor="aquamarine">{0}</td></tr>\n'.format(ws)

            # Add in solutions text
            nText += srows

        # Add in main content
        wcontent = fill(node.content, width=linew).replace("\n", "<br/>")
        nText += '\t\t<tr><td port="f0">{0}</td></tr>\n'.format(wcontent)

        if 0 < len(node.evidence):
            # Assemble evidence
            erows = ""
            for e in node.evidence:
                we = fill(e, width=linew).replace("\n", "<br/>")
                erows += '\t\t<tr><td bgcolor="lightpink">{0}</td></tr>\n'.format(we)

            # Add in evidence text
            nText += erows

        # Finish the node text
        nText += '\t</table>\n'\
                 '> shape=none ];\n'
        self.text += nText

    def add_node_linkage_text(self):
        """Add node linkage text to the graphviz output

        """
        # Generate node linkage and dummy node linkage
        # dummy nodes "joints" are used to unify lines going to the same node
        dep_text = ''
        for n in self.nodes:
            if 0 == len(n.deps):
                continue

            dep_text += (
                '{0}_joint[shape="none", label="", width=0, height=0];\n'
                '{0}_joint -> {0}:f0:e;\n').format(n.name)
            for d in n.deps:
                dep_text += '{0}:f0:w -> {1}_joint[arrowhead="none"];\n'.format(d, n.name)

        self.text += dep_text

    def add_rank_text(self):
        """Add node ranking text to the graphviz output

        """
        rank_dict = {}
        key_set = set()
        dep_set= set()
        for n in self.nodes:
            # get list of all nodes
            key_set |= {n.name}
            # combine all node dependencies into one set
            dep_set |= n.deps

        # get only nodes that are not dependencies of others
        rank_dict[0] = key_set - dep_set
        # Rank all other nodes
        irank = 0
        done = False
        while not done:
            done = True
            irank_set = rank_dict[irank]
            irankn = irank + 1
            for irn in irank_set:
                node = self.node_by_name(irn)
                if node is None:
                    continue
                if 0 == len(node.deps):
                    continue
                if not irankn in rank_dict:
                    rank_dict[irankn] = set()
                rank_dict[irankn] |= node.deps
                done = False

            irank = irankn

        # Ensure nodes are only specified in 1 rank
        for i in range(irank-1,-1,-1):
            for j in range(0,i):
                rank_dict[j] -= rank_dict[i]

        rank_text = ''
        for n in rank_dict:
            # Only rank sets with more than 1 node
            if 1 < len(rank_dict[n]):
                rank_text += '{' + 'rank=same {0}'.format(" ".join(rank_dict[n])) + '}\n'

        self.text += rank_text

    def load_map(self, m):
        """Load a cause map from a dictionary.

        Args:
            m (dict): The dictionary containing cause map information.

        """
        dep_tree = {}
        for n in m['nodes']:
            # Ensure minimal field requirements
            if not 'name' in n:
                print('Error: "name" missing from node.\n')
                sys.exit(-1)

            if not 'content' in n:
                print('Error: "content" missing from node: '
                      + n['name'] + '\n'
                )
                sys.exit(-1)

            node = map_node()
            node.name = n['name']
            node.content = n['content']

            if 'evidence' in n:
                node.evidence = n['evidence']

            if 'solutions' in n:
                node.solutions = n['solutions']

            # Load in dependencies we know about
            if 'effectedby' in n:
                node.deps |= set(n['effectedby'])

            self.nodes.append(node)

        # Load the rest of dependencies
        for n in m['nodes']:
            if 'effects' in n:
                for en in n['effects']:
                    node = self.node_by_name(en)
                    if node is None:
                        print('Error: In {0}, {1} listed under effects, but does not exist'.format(n['name'], en))
                        sys.exit(-1)

                    node.deps.add(n['name'])

        for node in self.nodes:
            self.add_node_text(node)

        self.add_node_linkage_text()
        self.add_rank_text()

        self.text += '}\n'

if __name__ == '__main__':
    # Setup commandline option parser
    parser = OptionParser()
    parser.add_option("-f", "--ifile", dest="ifilename", metavar="FILE",
                      help="Input json file containing map.")
    parser.add_option("-o", "--ofile", dest="ofilename", metavar="FILE",
                      help="Output dot file containing graphviz map."\
                           " If none specified, output is printed to stdout.")

    # Handle required arguments
    (opts, args) = parser.parse_args()
    if opts.ifilename is None:
        print('Error: Input file must be specified.\n')
        parser.print_help()
        sys.exit(-1)

    # Generate graphviz output
    in_file = open(opts.ifilename, 'r')
    json_map = json.load(in_file)
    map = dot_map()
    map.load_map(json_map)
    if opts.ofilename is None:
        # Print graphviz output to stdout
        print('{0}'.format(map.text))
    else:
        # Print graphviz output to file
        out_file = open(opts.ofilename, 'w')
        out_file.write(map.text)

