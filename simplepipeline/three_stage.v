module three_stage (
    input wire clk,
    input wire [31:0] data_in,
    output reg [31:0] data_out
);

    reg [31:0] stage_1;
    reg [31:0] stage_2;


    always @(posedge clk) begin
        stage_1 <= data_in;
        stage_2 <= stage_1;
        data_out <= stage_2;
    end

endmodule
