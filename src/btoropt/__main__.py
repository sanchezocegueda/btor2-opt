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

from .program import *
from .passes.allpasses import *
from .parser import *
import sys
import itertools

options = ["modular"]

def main():
    # Retrieve flags
    if len(sys.argv) < 3:
        print("Usage: btoropt [optional](--modular) <file.btor2> <pass_names_in_order> ...")
        exit(1)

    # Check options
    base = 1
    modular = False
    if "--" in sys.argv[1].strip():
        option = sys.argv[1].strip().strip("--")
        if option not in options:
            print(f"Invalid option given: {option}")
            exit(1)
        modular = True
        base += 1
        

    # Retrieve design
    btor2str: list[str] = []
    with open(sys.argv[base], "r") as f:
        btor2str = f.readlines()

    # Parse the design
    btor2 = None
    if modular:
        btor2 = parse_file(btor2str)
    else:
        btor2 = parse(btor2str)
    
    assert btor2 is not None

    base += 1

    # Retrieve passes
    pipeline : list[Pass] = []

    # Check that the given pass names are valid
    num_args = len(sys.argv)
    curr_arg_idx = base

    while curr_arg_idx < num_args:
        p_name = sys.argv[curr_arg_idx]
        p = find_pass(all_passes, p_name)
        if p is None:
            print(f"Invalid pass given as argument: {p_name}")
            exit(1)
        curr_arg_idx += 1

        path_args = {}
        # Check if the pass has any arguments
        while curr_arg_idx < num_args:
            curr_arg = sys.argv[curr_arg_idx]
            if curr_arg.startswith("--"):
                stripped_arg = curr_arg.strip("--").split("=")
                name = stripped_arg[0]
                value = stripped_arg[1] if len(stripped_arg) > 1 else None
                path_args[name] = value
                curr_arg_idx += 1
            else:
                break
            
        p.set_args(path_args)
        pipeline.append(p)    

    # Run all passes in the pipeline
    for p in pipeline:
        if modular: 
            btor2 = p.runOnProgram(btor2)
        else:
            print(p.id)
            btor2 = p.run(btor2)
            # s = set()
            # for inst in btor2:
            #     s.add(type(inst))
            
            # print(s)

    # Show the result to the user
    if(modular):
        print(serialize_p(btor2))
    else:
        print("Success")
        pretty_print(btor2)

if __name__ == "__main__":
    main()
