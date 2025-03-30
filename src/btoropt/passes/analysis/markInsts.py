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

# Example pass: Simply renames all inputs to inp_<pos>

from ..genericpass import Pass
from ...program import Instruction, Sort, Next, Ite
from collections import deque

class MarkInsts(Pass):
    def __init__(self):
        super().__init__("mark-insts")

    def get_m(self) -> list[int]:
        with open(self.path, 'r') as f:
            m = [int(i) for i in f.readlines()]
        return m

    def run(self, p: list[Instruction]) -> list[Instruction]:

        ## Create an undirected graph 
        adj = [[] for i in range(len(p)+1)] # Extra entry so that we can keep the 1-indexing

        for inst in p:
            i = inst.lid
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

                adj[i].append(j)
                adj[j].append(i)

        q = deque()

        m = self.get_m()
        q.extend(m)

        marked = set()

        ## Mark dependents
        while q:
            lid = q.pop()

            if lid in marked:
                continue
            
            # Mark the message
            marked.add(lid)

            # Recursively mark all dependents
            for other_lid in adj[lid]:
                q.append(other_lid)

        print("DEBUG: marked set =", marked)

        return marked