

processor.btor: processor.v
	yosys -p "read_verilog $^; hierarchy -top processor; hierarchy -check; proc; opt; memory; flatten; opt; clk2fflogic; write_btor $@"

processor_formal.btor: processor.v
	yosys -p "read_verilog $^; hierarchy -top processor; hierarchy -check; proc; opt; memory; flatten; opt; dffunmap; chformal -assume -early; write_btor $@"