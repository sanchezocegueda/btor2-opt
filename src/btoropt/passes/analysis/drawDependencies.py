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

# Automatically infers the pipeline stages by analyzing data-flow dependencies between state registers

from ..genericpass import Pass
from ...program import Instruction, Sort, Next, Ite, State
from collections import deque, defaultdict
from functools import reduce
import networkx as nx
import matplotlib.pyplot as plt


class DrawDependencies(Pass):
    def __init__(self):
        super().__init__("draw-dependencies")

    def run(self, p: list[Instruction]) -> list[Instruction]:
        
        edges = []

        for inst in p:
            for o in inst.operands:
                if isinstance(o, Instruction):
                    edges.append((inst.lid, o.lid))
        
        G = nx.DiGraph()
        G.add_edges_from(edges)



        nexts = []
        next_insts = [inst for inst in p if isinstance(inst, Next)]

        for inst in p:
            if isinstance(inst, Next):
                nexts.append(inst.lid)

        states = [inst.lid for inst in p if isinstance(inst, State)]
        sorts = [inst.lid for inst in p if isinstance(inst, Sort)]
        
        next_insts.pop()
        last_next = next_insts.pop()

        # des = nx.descendants(G, last_next.lid) | set([last_next.lid])
        des = nx.descendants(G, 26) | set([26])

        H = nx.subgraph(G, des)

        node_colors = ['red' if node in states else ('green' if node in sorts else ('yellow' if node == last_next.lid else 'lightblue')) for node in G.nodes]
        # node_colors = ['red' if node in states else ('green' if node in sorts else ('yellow' if node == 26 else 'lightblue')) for node in H.nodes]

        plt.figure(figsize=(10,10))
        # pos = nx.circular_layout(H)  # Positions for all nodes
        pos = nx.circular_layout(G)  # Positions for all nodes
        # pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color=node_colors, edge_color='gray', node_size=2000, arrowsize=20)
        # nx.draw(H, pos, with_labels=True, node_color=node_colors, edge_color='gray', node_size=2000, arrowsize=20)

        plt.show()
        return p