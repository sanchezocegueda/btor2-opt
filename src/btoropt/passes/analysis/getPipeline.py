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

class GetPipeline(Pass):
    def __init__(self):
        super().__init__("get-pipeline")

    def run(self, p: list[Instruction]) -> list[Instruction]:

        map = {} # maps state registers to a list of state registers 

        d = defaultdict(list)

        nextq = deque()

        marked = set()

        for inst in p:
            if isinstance(inst, Next):
                nextq.append(inst)

        while nextq:
            nextinst = nextq.pop()

            stack = deque()

            stateinst = nextinst.operands[1]

            stack.append(nextinst.operands[2])
            visited = set()

            while stack:
                curr = stack.popleft()
                if curr in visited:
                    continue
                else:
                    visited.add(curr)
            
                if isinstance(curr, State):
                    d[stateinst.lid].append(curr.lid)
                else:
                    for o in curr.operands:
                        if isinstance(o, Instruction):
                            stack.append(o)


        print(d)

        return p