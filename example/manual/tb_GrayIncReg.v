module tb_GrayIncReg;

wire [7:0] graycnt;
reg enable;
reg clock;
reg reset;

initial begin
    $from_myhdl(
        enable,
        clock,
        reset
    );
    $to_myhdl(
        graycnt
    );
end

GrayIncReg dut(
    graycnt,
    enable,
    clock,
    reset
);

endmodule
