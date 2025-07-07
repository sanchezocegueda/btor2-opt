##########################################################################
# BTOR2 parser, code optimizer, and circuit miter
# Copyright (C) 2024  Amelia Dobis
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
##########################################################################

# Marks all the dependents and anti-dependents of the specified instruction (lid)

from ..genericpass import Pass
from ...program import *
from collections import deque
import networkx as nx
import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)

class MarkInsts(Pass):
    def __init__(self):
        super().__init__("mark-insts")
        self.source_insts = None

    def get_m(self) -> list[int]:
        if self.source_insts is None:
            module_path = self.args.get('module_path', None)
            if module_path is None:
                raise ValueError(f"Module path not provided. Pass {self.id} module_path argument as --module_path=<name of file>.")
            with open(module_path, 'r') as f:
                m = [int(i) for i in f.readlines()]
            self.source_insts = m
            return m
        else:
            return self.source_insts

    def run(self, p: list[Instruction]) -> list[Instruction]:

        pretty_print(p)

        ## Create an undirected graph 
        G =  nx.Graph()
        adj = [[] for i in range(len(p)+1)] # Extra entry so that we can keep the 1-indexing

        for inst in p:
            i = inst.lid
            G.add_node(i)
            # print(f"i: {i}")
            if isinstance(inst, Ite): 
                ops = inst.operands[2:] # Avoid propagating to condition
            else:
                ops = inst.operands[1:] # 0th instruction is always the Sort (which we don't want to propagate to, either)
            
            for op in ops:
                if isinstance(op, Instruction):
                    if isinstance(op, Sort):
                        continue
                    j = op.lid
                else:
                    continue
                G.add_edge(i, j)
                adj[i].append(j)
                adj[j].append(i)

        if True:

            states = [inst.lid for inst in p if isinstance(inst, State)]
            ites = [inst.lid for inst in p if isinstance(inst, Ite)]
            sorts = [inst.lid for inst in p if isinstance(inst, Sort)]


            # Improved coloring by node type
            node_colors = {}
            lid_to_inst = {inst.lid: inst for inst in p}
            for node in G.nodes():
                inst = lid_to_inst.get(node, None)
                if inst is None:
                    node_colors[node] = 'lightblue'
                elif isinstance(inst, Ite):
                    node_colors[node] = 'yellow'
                elif isinstance(inst, Sort):
                    node_colors[node] = 'lightblue'
                elif isinstance(inst, State):
                    node_colors[node] = 'orange'
                elif isinstance(inst, Input):
                    node_colors[node] = 'green'
                elif isinstance(inst, Output):
                    node_colors[node] = 'pink'
                elif isinstance(inst, (Const, Constd, Consth, Zero, One, Ones)):
                    node_colors[node] = 'yellow'
                else:
                    node_colors[node] = 'lightgray'

            pos = nx.circular_layout(G)

            nx.draw(G, pos, with_labels=True, 
                    node_color=[node_colors[node] for node in G.nodes()], 
                    edge_color='gray', node_size=2000)

            # Add a legend for node types
            import matplotlib.patches as mpatches
            legend_patches = [
                mpatches.Patch(color='red', label='Ite'),
                mpatches.Patch(color='green', label='Sort'),
                mpatches.Patch(color='orange', label='State'),
                mpatches.Patch(color='blue', label='Input'),
                mpatches.Patch(color='purple', label='Output'),
                mpatches.Patch(color='yellow', label='Const/Zero/One/Ones'),
                mpatches.Patch(color='lightgray', label='Other'),
            ]
            plt.legend(handles=legend_patches, bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            plt.show()
        
        # Initialize the queue with the source instructions
        q = deque()
        # q.extend(self.get_m())

        # Marked set of instruction
        marked = set()

        # Breadth-first search
        while q:
            lid = q.pop()
            if lid in marked:
                continue
            # Mark the message
            marked.add(lid)
            # Recursively mark all dependents
            for other_lid in adj[lid]:
                q.append(other_lid)

        # logger.debug(f"Pass {self.id}: Found marked set ", marked)
        return marked
