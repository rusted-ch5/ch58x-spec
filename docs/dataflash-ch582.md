# CH582 DataFlash command interface

CH582 exposes 32 KiB of DataFlash at physical address range
`0x0007_0000..0x0007_8000`. Internal controller transactions address the same
storage through an alias formed by setting address bit 19.

The controller at `0x4000_1800` uses a byte-oriented serial command protocol.
Observed command values are:

| Command | Value | Operation |
| --- | ---: | --- |
| write enable | `0x06` | enable the following mutating command |
| read status | `0x05` | read device status until ready |
| data read | `0x0b` | address plus two dummy bytes, then payload |
| page program | `0x02` | program one bounded page transaction |
| erase 256 bytes | `0x81` | erase one aligned 256-byte sector |
| controller reset | `0xff` | return the serial interface to idle state |

## Execution placement

Once a command is active, fetching subsequent instructions from code flash can
stall the core. Command setup, polling, payload transfer, cleanup, and protected
configuration restoration therefore execute from SRAM-backed `.highcode`.
This is an execution requirement, not merely a performance optimization.

The implementation must bound both controller-byte polling and status-ready
polling. Timeout cleanup disables the interface and restores the original
global flash configuration before returning an error.

## Alignment and page rules

The exercised erase and program units are both 256 bytes. Erase addresses must
be 256-byte aligned, and one page-program command must not cross a page
boundary. Bounds and alignment are checked before protected configuration is
changed.

## Validation boundary

A standalone CH582M case has exercised erase, program, exact readback, factory
row reads, and persistence across a PFIC system reset. The result applies to
the recorded target, firmware, address window, and command sequence; it is not
a characterization of flash endurance or retention lifetime.
