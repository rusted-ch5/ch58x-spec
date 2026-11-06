# Experimental CH582M adaptation

CH585M is the primary C/Rust Bluetooth specification. This document records
the separate CH582M adaptation and must not reduce the primary target.

The design motivation is the 32 KiB SRAM budget, particularly the combination
of Embassy task futures, BLE Controller/Host queues, GATT/security state and
USB. Select one BLE Peripheral and a measured resource budget. A fully enabled
BLE+USB configuration is not admitted merely because separate BLE-only and
USB-only images fit. USB coexistence requires its own memory and physical gate.

The adaptation must be explicitly experimental and independently selectable;
no default CH585 build may select it. Unsupported combinations must fail before
linking. Keep its buffers, connection count, chip timer and radio operations in
the adaptation module. Keep portable HCI validation and LL ownership semantics
shared. Reduced memory is not permission to weaken MIC, sequence or credit
correctness.

## Register deltas requiring separate admission

These candidate register differences are inferred and require CH582 validation.
They are outside the stable CH585 register JSON. Verify each before admitting
the experimental backend.

| Item | CH582 observation | CH585 admitted implementation |
| --- | --- | --- |
| BB mode mask | `0x180`, idle `0x80`, active `0x100` | `0x300`, idle `0x100`, active `0x200` |
| LLE idle/RX/TX modes | `0x80` / `0xd9` / `0xda` | `0x30000` / `0x30158` / `0x30258` |
| TX/RX pointer offsets | `+0x70` / `+0x74` | `+0x78` / `+0x7c` |
| Capture bit | bit 13 | bit 17 |
| Transition countdown | `0x196` | `0x18e` |
| BB RX status clearing | clear-by-zero candidate; requires validation | W1C; capture bit 6 must not clear CRC bit 5 |
| SysTick CNT/CMP | stable split-word 64-bit access on RV32 | 32-bit counter with software epoch |

These values remain `inferred` until reproducible CH582 observations are
attached. Encryption, RF calibration, timing and DMA layout require chip-specific
validation even where peripheral base addresses match.

Acceptance requires an identified CH582 board, its own verified firmware start,
radio/clock tests and peer-driven BLE integrity/reconnect tests. CH585 results and a compiler-selected `ch582` feature do not satisfy that gate.
