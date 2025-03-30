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

from ..genericpass import Pass
from ...program import Instruction, Sort, Next, Ite, Uext, Penc
from collections import deque
import json

# NOTE: This requires changing the formatting of the JSON file (so it is deprecated for now)
class FindPorts(Pass):
    def __init__(self):
        super().__init__("find-ports")

    def get_m(self) -> list[int]:
        # This one gets the modules (should be a json file)
        with open(self.path, 'r') as f:
            m = json.load(f) # assuming this is a JSON that has an array of module objects
        return m


    # NOTE: This is horribly slow
    def run(self, p: list[Instruction]) -> list[Instruction]:
        
        modules = self.get_m()

        inPorts = []
        outPorts = []

        for m in modules:
            mtype = m['type']

            mname = m['name']
            
            # Find input port aliases
            for pname in m["inputPorts"]:
                iname = mname + '.' + pname

                for inst in p:
                    if isinstance(inst, Uext) and inst.renaming and inst.name == iname:
                        inPorts.append(inst)

            # Find output port aliases
            for pname in m["outputPorts"]:
                oname = mname + '.' + pname

                for inst in p:
                    if isinstance(inst, Uext) and inst.renaming and inst.name == oname:
                        outPorts.append(inst)


        return p 