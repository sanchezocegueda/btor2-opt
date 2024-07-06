# btor2-opt
Very basic btor2 parser, circuit miter, and code optimizer.

## Install  
```
pip install btor2-opt
```

## Overview
This repo contains two main scripts:
  - `btoropt`: Takes a `.btor2` file and a list of pass names as argument and prints out the transformed result.
  - `btormiter`: Takes a `.fir` file as input and runs it through `firrtl` and `firtool` to obtain two `.btor2` designs which are then merged into a single miter circuit before being returned to the user. Note that this requires having `firrtl` and `firtool` in your path, specifically a [version of `firtool` that has the `--btor2` flag](https://github.com/llvm/circt/pull/6947).

The rest of the code can be found in the `src` folder, which contains a basic parser for `btor2` (not entirely complete, but supports anything `firtool --btor2` can produce), an internal representation of the language and a simple pass infrastructure, where you can add any of you custom passes.  

## Supported Instructions  
This compiler currently supports the following btor2 instructions:  
| **Instruction** | **Description** |
|:---|:---|
| `<lid> sort <type> <width>` | Declares a type |
| `<lid> input <sid> <name> ` | Declares an input |
| `<lid> output <out>` | Declares an output |
| `<lid> bad <cond>` | Checks the inversion of a condition |
| `<lid> constraint <cond>` | Assumes a condition |
| `<lid> zero <sid>` | Declares a 0 constant |
| `<lid> one <sid>` | Declares a 1 constant |
| `<lid> ones <sid>` | Declares a bit-string of 1s |
| `<lid> not <sid> <cond>` | Negates a condition |
| `<lid> constd <sid> <val>` | Declares a decimal constant |
| `<lid> consth <sid> <val>` | Declares a hexadecimal constant |
| `<lid> const <sid> <val>` | Declares a binary constant |
| `<lid> state <sid> <name>` | Declares a stateful element |
| `<lid> init <sid> <state> <val>` | Initializes a state |
| `<lid> next <sid> <state> <next>` | Sets the transition logic of a state |
| `<lid> slice <sid> <op> <w> <lb>` | Extracts bits `[lb:lb+w]` from a result |
| `<lid> ite <sid> <cond> <t> <f>` | If-then-else expression |
| `<lid> implies <sid> <lhs> <rhs>` | Logical implication |
| `<lid> iff <sid> <lhs> <rhs>` | If and only if expression |
| `<lid> add/sub/mul <sid> <l> <r>` | Binary operation |
| `<lid> {s,u}div <sid> <l> <r>` | Signed or unsigned division |
| `<lid> smod <sid> <l> <r>` | Signed modulo |
| `<lid> s{l,r}l <sid> <l> <r>` | Logical shift left/right |
| `<lid> sra <sid> <l> <r>` | Arithmetic shift right |
| `<lid> and/or/xor <sid> <l> <r>` | Binary logical operators |
| `<lid> concat <sid> <l> <r>` | Concatenate two results |
| `<lid> eq/neq <sid> <l> <r>` | Equality comparators |
| `<lid> {s,u}gt <sid> <l> <r>` | Signed/Unsigned *l* \> *r* |
| `<lid> {s,u}gte <sid> <l> <r>` | Signed/Unsigned *l* ≥ *r* |
| `<lid> {s,u}lt <sid> <l> <r>` | Signed/Unsigned *l* \< *r* |
| `<lid> {s,u}lte <sid> <l> <r>` | Signed/Unsigned *l* ≤ *r* |
| `<lid> uext <sid> <opid> <w> <name>` | Unsigned width extension / aliasing |


## Adding a Pass
Simply create a new class (as its own file) in `src/passes` that inherits from `Pass`. Then in the constructor, make sure you give it a name. The pass's logic itself is written by overiding the `run(p: list[Instruction]) -> list[Instruction]` method. The pass must then be imported in `src/passes/passes.py` and instantiated in the `all_passes` list. Passes are grouped either in `transforms`, which contain all of the passes that transform the AST, and `validation`, which contains all of the passes used to gurantee the syntactic correctness of the output program.

Here is a simple example pass that renames all inputs to "inp_n".
```python
# Example pass: Simply renames all inputs to inp_<pos>
class RenameInputs(Pass):
    def __init__(self):
        super().__init__("rename-inputs")

    # I chose to have this pass not modify p in place
    # you can also simply modify p and return it
    def run(p: list[Instruction]) -> list[Instruction]:
        i = 0
        res = []
        for inst in p:
            if isinstance(inst, Input):
                res.append(Input(inst.lid, inst.sort, f"inp_{i}"))
                i += 1
            else:
                res.append(inst)
        return res

# Make sure to add an instance of the pass to the all_passes array
all_passes = [RenameInputs()]
```
This pass can then be called by running:
```sh
python3 btor2-opt.py ex.btor2 rename-inputs
```
