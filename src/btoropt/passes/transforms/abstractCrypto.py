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
from ...program import Instruction, Sort, Next, Ite, Uext, SymEnc, get_inst
from collections import deque
import json

class AbstractCrypto(Pass):
    """
    This pass will abstract a crypto block into a (custom) penc instruction
    """
    def __init__(self):
        super().__init__("abstract-crypto")

    def get_m(self) -> list[int]:
        # This one gets the modules (should be a json file)
        with open(self.path, 'r') as f:
            m = json.load(f) # assuming this is a JSON that has an array of module objects
        return m

    def run(self, p: list[Instruction]) -> list[Instruction]:
        
        modules = self.get_m()

        to_abstract = []

        for m in modules:
            mtype = m['type']

            if mtype == 'symenc':
                # symmetric encryption block
                name = m['name']
                plaintext = m['plaintext']
                key = m['key']
                ciphertext = m['ciphertext']

                inames = [name + '.' + x for x in [plaintext, key, ciphertext]]
                # TODO: What Sort should we use?
                for inst in p:
                    if isinstance(inst, Uext) and inst.renaming and inst.name == name + '.' + plaintext:
                        m = inst.operands[1] # The original instruction (not the alias)
                    elif isinstance(inst, Uext) and inst.renaming and inst.name == name + '.' + key:
                        k = inst.operands[1] # The original instruction (not the alias)
                    elif isinstance(inst, Uext) and inst.renaming and inst.name == name + '.' + ciphertext:
                        lid = inst.operands[1].lid # This is the actual inst we're supposed to replace (I think)
                        sort = inst.operands[0] # We need these to be the same sort (?)

                symenc = SymEnc(lid, sort, m, k) # Create abstract penc instruction

                p.insert(lid, symenc) # Add it right after the original

                # Replace occurrence of module output with abstract penc
                for inst in p:
                    for i in range(len(inst.operands)):
                        other_inst = inst.operands[i]
                        if isinstance(other_inst, Instruction) and other_inst.lid == symenc.lid:
                            inst.operands.pop(i)
                            inst.operands.insert(i, symenc)
            
            elif mtype == 'asymenc':
                # TODO: asymmetric encryption block
                pass


            elif mtype == 'asymdec':
                # TODO: asymmetric decryption block
                pass


        # Reorder everything so that instructions are in order
        # (Ripped from CheckLidOrdering)
        res = []

        for i in range(len(p)):
            inst = p[i]
            inst.lid = i + 1
            res.append(inst)

        return res