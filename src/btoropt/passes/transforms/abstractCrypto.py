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

import sys
import logging

logger = logging.getLogger(__name__)

class AbstractCrypto(Pass):
    """
    This pass will abstract a crypto block into a (custom) SymEnc instruction
    """
    def __init__(self):
        super().__init__("abstract-crypto")

    def get_m(self) -> list:
        # This one gets the modules (should be a json file)
        module_path = self.args.get('module_path', None)
        if module_path is None:
            raise ValueError(f"Module path not provided. Pass {self.id} module_path argument as --module_path=<name of file>.")
        with open(module_path, 'r') as f:
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
                plaintext_signame = f"{name}.{m['plaintext']}"
                key_signame = f"{name}.{m['key']}"
                ciphertext_signame = f"{name}.{m['ciphertext']}"

                pln_inst : Instruction = None
                key_inst : Instruction = None
                cip_lid : int = None

                for inst in p:
                    if isinstance(inst, Uext) and inst.renaming and inst.name == plaintext_signame:
                        pln_inst = inst.operands[1] # The original instruction (not the alias)
                    elif isinstance(inst, Uext) and inst.renaming and inst.name == key_signame:
                        key_inst = inst.operands[1] # The original instruction (not the alias)
                    elif isinstance(inst, Uext) and inst.renaming and inst.name == ciphertext_signame:
                        cip_lid = inst.operands[1].lid # This is the actual inst we're supposed to replace (I think)
                        # sort = inst.operands[0] # We need these to be the same sort (?)

                if pln_inst is None or key_inst is None or cip_lid is None:
                    logger.error(f"Could not find all the necessary inputs for {name}, found {pln_inst}, {key_inst}, {cip_lid}")
                    sys.exit(1)
                else:
                    logger.debug(f"Found symenc at inputs: {pln_inst}, {key_inst}, output: {cip_lid}")


                symenc = SymEnc(cip_lid, pln_inst, key_inst) # Create abstract penc instruction

                p.insert(cip_lid, symenc) # Add it right after the original

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