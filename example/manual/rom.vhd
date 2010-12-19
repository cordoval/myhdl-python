-- File: rom.vhd
-- Generated by MyHDL 0.7
-- Date: Sun Dec 19 16:52:33 2010


library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;
use std.textio.all;

use work.pck_myhdl_07.all;

entity rom is
    port (
        dout: out unsigned(7 downto 0);
        addr: in unsigned(3 downto 0)
    );
end entity rom;
-- ROM model 

architecture MyHDL of rom is


begin




ROM_READ: process (addr) is
begin
    case to_integer(addr) is
        when 0 => dout <= "00010001";
        when 1 => dout <= "10000110";
        when 2 => dout <= "00110100";
        when others => dout <= "00001001";
    end case;
end process ROM_READ;

end architecture MyHDL;
