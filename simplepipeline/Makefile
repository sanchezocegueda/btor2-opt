


two_stage.btor: two_stage.v
	yosys -p "read_verilog $^; hierarchy -top two_stage; hierarchy -check; proc; opt; memory; flatten; opt; clk2fflogic; write_btor $@"

one_stage.btor: one_stage.v
	yosys -p "read_verilog $^; hierarchy -top one_stage; hierarchy -check; proc; opt; memory; flatten; opt; clk2fflogic; write_btor $@"
three_stage.btor: three_stage.v
	yosys -p "read_verilog $^; hierarchy -top three_stage; hierarchy -check; proc; opt; memory; flatten; opt; clk2fflogic; write_btor $@"

two_stage_formal.btor: two_stage.v
	yosys -p "read_verilog $^; hierarchy -top two_stage; hierarchy -check; proc; opt; memory; flatten; opt; chformal -assume -early; write_btor $@"

two_stage_formal.btor: two_stage.v
	yosys -p "read_verilog $^; hierarchy -top two_stage; hierarchy -check; proc; opt; memory; flatten; opt; chformal -assume -early; write_btor $@"