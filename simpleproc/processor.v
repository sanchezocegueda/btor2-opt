

module encrpytor (
    input wire [31:0] data_in,
    input wire [31:0] key,
    output wire [31:0] data_out
);
    assign data_out = data_in ^ key;
endmodule


module processor (
    input wire clk,
    input wire [31:0] data_in,
    input wire [4:0] op,
    output reg [31:0] data_out
);

    reg [31:0] register;
    reg [31:0] mem;

    reg [31:0] key1;
    reg [31:0] key2;

    wire [31:0] chosen_key;
    wire [31:0] chosen_data_in;
    wire [31:0] enc_data_out;

    reg pid;
    assign chosen_key = (pid == 0) ? key1 : key2;
    assign chosen_data_in = (op == 3'b010) ? register : mem;

    always @(posedge clk ) begin
        if (op == 3'b000) begin
            // Load data into register
            register <= data_in;
        end else if (op == 3'b001) begin
            // Read data from register
            data_out <= register;
        end else if (op == 3'b010) begin
            // Write data to memory
            mem <= enc_data_out;
        end else if (op == 3'b011) begin
            // Read data from memory
            register <= enc_data_out;
        end else if (op == 3'b100) begin
            // Switch pid
            pid <= ~pid;
        end
    end

    encrpytor enc (
        .data_in(chosen_data_in),
        .key(chosen_key),
        .data_out(enc_data_out)
    );

endmodule
