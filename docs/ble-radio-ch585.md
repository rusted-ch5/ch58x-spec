# CH585 LE 1M radio operation contract

Status: inferred register behavior; requires per-image hardware acceptance.
Register locations are defined in `spec/ble-bb-ch585.json` and
`spec/ble-lle-ch585.json`. The rules below apply to the legacy LE 1M profile.

## RF-INIT: initialization

Own the radio, DMA storage, timer and interrupt sources exclusively. Complete
analog initialization, then digital baseband initialization, then calibration.
Calibration must precede advertising or connection work. The four calibration
sample indices are visited in the order 0, 2, 1, 3 (2401, 2480, 2440, 2522 MHz).
A calibration timeout is an error; no default per-device result is substituted.

LLE TX and RX pointers are distinct, at offsets `0x78` and `0x7c`.
Initialize the LE 1M timing words as follows:

| Offset | Value |
| --- | --- |
| `0x14` | `0x8c` |
| `0x1c` | `0x76` |
| `0x24` | `0x8c` |
| `0x2c` | `0x6e` |
| `0x34` | `0x8c` |
| `0x3c` | `0x6e` |
| `0x44` | `0x8c` |
| `0x4c` | `0x76` |

Clear LLE config bits 4:0, then write the 16-bit value 1 at offset `0x06`.
Clear offset `0x54`, acknowledge stale LLE status, and enable the selected
interrupt sources. Access width and write order are part of the contract.
For PA code `0x15`, RFEND offset `0x5c` bits 26:24 select profile 1; this
register preset alone is not a calibrated transmit-power measurement.

## RF-DMA: lengths and ownership

DMA storage contains the two-byte LL header followed by contiguous payload.
Clear unused TX storage before exposing its address to the radio. Enforce both
the physical allocation and the selected protocol limit before copying RX.
Legacy advertising permits at most 37 payload bytes; the plaintext checkpoint
permits at most 27 Data PDU payload bytes. These are profile limits, not the
maximum CH585 DMA capacity. SCAN_REQ and CONNECT_IND payloads must have exactly
12 and 34 bytes, respectively.

An RX capture indication means reception started. It does not make the DMA
payload complete or authorize acknowledging an outstanding transmit owner.
Read DMA written by hardware with the required compiler/memory ordering.

## RF-CAPTURE: status and acknowledgement

Snapshot status before W1C writes. A capture acknowledgement at BB offset
`0x38` writes only bit 6 from the captured status. It must preserve CRC-error
bit 5 until the RX outcome has consumed it. LLE capture uses bit 17. TX complete
uses LLE bit 1 and is acknowledged with W1C. CRC-invalid reception must not
acknowledge an owner, deliver ACL bytes or extend supervision.

## RF-TIMING: countdowns and turnaround

With `packet_bytes` including the two LL header bytes and CTE disabled:

* TX duration countdown: `((packet_bytes + 2) * 8 + 0xee) * 2`.
* RX capture countdown: `(maximum_payload_bytes + 5) * 16 + 0x3c`.
* RX-to-TX timing offset: `0x76`.
* LE 1M transition countdown: `0x18e`.

For standalone TX, first wait for the `0xa0` settle countdown to expire,
then configure the duration countdown and launch command 2. Every wait has a
finite bound and an error path that quiesces the operation.

Prepare the response and establish its immutable owner before turnaround.
For the staged RX-to-TX release, set the TX pointer and timing, acknowledge the
RX-to-TX source, select the BB transmit control, configure TX synthesizer and
PHY, then activate the operation. No packet construction, logging, Host/GATT
processing or blocking queue operation belongs in this timing window.

## RF-RANDOM: random input

A caller-seeded PRNG does not provide independent entropy. A bounded ADC/jitter
collector must restore ADC configuration on every exit and fail on timeout or
insufficient variation. A health check is not cryptographic qualification.
Security use requires an explicitly accepted entropy source. A failed seed
operation must not substitute a fixed seed.

## Acceptance

The literal timing, length and W1C examples in `conformance/ble-v1.json` establish
host arithmetic behavior only. Register ordering requires an MMIO trace check;
advertising, IFS, CRC/retry and connection timing require a probe-free peer test.
Calibration and clock checks are separate prerequisites.
