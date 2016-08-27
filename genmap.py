#!/usr/bin/python3

import sys
import json
from textwrap import fill
from optparse import OptionParser

class dot_map:
    def __init__(self):
        self.text = 'digraph map{\n'\
                    'graph [rankdir=RL, splines=polyline,'\
                           'arrowType=normal, style=normal]\n'\
                    'node [shape=record, margin=0];\n'

    def add_node_text(self, name, content,
                      solutions=None, evidence=None, linew=15):
        """Add a node's text to the graphviz output.

        Args:
            name (str): The name of the graphviz map node.
            content (str): The main content text of the node.
            solutions (list of str): List of solution strings.
            evidence (list of str): List of evidence strings.
            linew (num): Max characters per line, longer will be wrapped.

        """
        tprops = 'cellspacing="0" cellborder="1" border="0"'

        # Setup header text
        nText = '{0} [label=<\n'\
                '\t<table {1}>\n'.format(name, tprops)

        if solutions is not None:
            # Assemble solutions
            srows = ""
            for s in solutions:
                ws = fill(s, width=linew).replace("\n", "<br/>")
                srows += '\t\t<tr><td bgcolor="aquamarine">{0}</td></tr>\n'.format(ws)

            # Add in solutions text
            nText += srows

        # Add in main content
        wcontent = fill(content, width=linew).replace("\n", "<br/>")
        nText += '\t\t<tr><td port="f0">{0}</td></tr>\n'.format(wcontent)

        if evidence is not None:
            # Assemble evidence
            erows = ""
            for e in evidence:
                we = fill(e, width=linew).replace("\n", "<br/>")
                erows += '\t\t<tr><td bgcolor="lightpink">{0}</td></tr>\n'.format(we)

            # Add in evidence text
            nText += erows

        # Finish the node text
        nText += '\t</table>\n'\
                 '> shape=none ];\n'
        self.text += nText

    def load_map(self, m):
        """Load a cause map from a dictionary.

        Args:
            m (dict): The dictionary containing cause map information.

        """
        dep_tree = {}
        for n in m['nodes']:
            # Add text for each node
            e = None
            s = None

            # Ensure minimal field requirements
            if not 'name' in n:
                print('Error: "name" missing from node.\n')
                sys.exit(-1)

            if not 'content' in n:
                print('Error: "content" missing from node: '
                      + n['name'] + '\n'
                )
                sys.exit(-1)

            if 'evidence' in n:
                e = n['evidence']

            if 'solutions' in n:
                s = n['solutions']

            self.add_node_text(n['name'], n['content'], s, e)

            # Create a dependency tree
            if 'effectedby' in n:
                if not n['name'] in dep_tree:
                    dep_tree[n['name']] = n['effectedby']
                else:
                    no_dups = set(dep_tree[n['name']] + n['effectedby'])
                    dep_tree[n['name']] = list(no_dups)

            if 'effects' in n:
                for en in n['effects']:
                    if not en in dep_tree:
                        dep_tree[en] = []

                    if not n['name'] in dep_tree[en]:
                        dep_tree[en].append(n['name'])

        # Generate node linkage and dummy node linkage
        # dummy nodes "joints" are used to unify lines going to the same node
        dep_text = ''
        for n in dep_tree:
            dep_text += (
                '{0}_joint[shape="none", label="", width=0, height=0];\n'
                '{0}_joint -> {0}:f0:e;\n').format(n)
            for d in dep_tree[n]:
                dep_text += '{0}:f0:w -> {1}_joint[arrowhead="none"];\n'.format(d, n)

        self.text += dep_text + '}\n'

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

