# CH585M-first Bluetooth controller contract

Status: specification and conformance work in progress, 2026-11-07.

CH585M defines the primary controller architecture for both Rust and Zephyr C.
CH582M is a separately selected experimental adaptation. The small CH582M
Embassy configuration must not become the default feature or buffer budget of
CH585M. In particular, the single-Peripheral configuration addresses the SRAM
cost of combining a full BLE controller/Host with USB; it is not a statement
that the CH582 radio protocol only permits a single Peripheral.

## Specification layers

1. `spec/ble-*-ch585.json`: admitted register addresses, widths, access rules
   and evidence. Unknown fields stay unknown. A register observation is not an
   interoperability or performance result.
2. `protocol/ch585-ble-hci.json`: HCI field layouts, state and ownership rules,
   units, supported-command reporting and error behavior.
3. `profiles/ch585-full.json`: the primary implementation target. A required
   feature is not advertised until its protocol, memory and physical gates pass.
4. `profiles/experimental/ch582-peripheral.json`: explicit resource reductions
   and chip differences, with independent tests and no implicit fallback.
5. `conformance/`: language-neutral inputs and literal expected results. Both
   implementations execute these vectors using their production functions.

Implementations are evaluated against the selected profile. Missing behavior
remains an implementation gap and does not reduce the primary target. Capability
reporting must describe the implemented and accepted subset.

## Primary CH585M target

The target includes legacy advertising and scanning, Central initiation and
Peripheral acceptance, connection scheduling, encryption and MIC rejection,
multiple PDUs per connection event, parameter/channel-map control procedures,
complete HCI capability/credit reporting and USB/BLE coexistence. Each requires
ordinary Host-path validation; a synthetic ATT echo or diagnostic RF fast path
does not satisfy application integration.

LE 2M and data-length extension are separately tracked implementation targets.
Neither may be advertised by changing a feature bit or raising a buffer length
alone. PHY timing, packet/DMA bounds, negotiation, retries and interoperability
must also be implemented. Other Bluetooth-version features (including Coded PHY,
extended/periodic advertising and isochronous transport) require a separate
hardware and requirements decision; the chip's advertised Bluetooth version is
not evidence that this independent controller implements every optional feature.

A plaintext Peripheral checkpoint is an intermediate acceptance scope. Its
27-byte ACL allocation and single connection do not constrain the full target.
Declare queue and connection budgets per build and measure them against CH585's
128 KiB SRAM. CH582's 32 KiB resource profile is independently selected.

## Module boundary

Rust keeps the portable protocol core separate from controller queues, the
CH585 radio/MMIO backend, and an opt-in CH582 backend/resource module. Zephyr
keeps HCI parsing and parameter validation separate from controller state,
LL scheduling and the chip radio. A CH582 selection must not compile CH585
register addresses/modes through fallback macros, and an unsupported feature
combination must fail at configuration/build time.

HCI-facing parameter semantics and error contracts are shared by C and Rust.
Physical queue depths may differ when reported honestly through HCI credits and
the build manifest. Queue depths, event capacity, static state, task futures,
stack guard, sampled SP and final watermark are reported independently.

Security belongs at the correct layer: HCI/LL encryption, AES/CCM, packet
counters, retransmission nonce ownership and MIC failures are Controller
requirements. SMP pairing, key distribution, bonding storage and GATT/HIDS
belong to the Host/application and need end-to-end acceptance in addition.

## Acceptance and publication

Each requirement has a stable ID. Each C/Rust result identifies the spec hash,
source revision plus dirty-file hashes, exact compiler/configuration and vector
IDs. Different implementations agreeing with one another is insufficient:
both must match the independent expected result. Include negative inputs,
length boundaries, illegal states, stale handles, queue exhaustion, reset and
credit ownership. Do not count a source-string match as executing a function.

After host contract checks: build/link/stack audit, verified flash/start,
short independent-peer correctness, then active-traffic endurance and separate
security/USB/HID gates. Record not-run and failed requirements explicitly.
CH585 results cannot accept the experimental CH582 port. Every changed image
requires the applicable acceptance gates to be repeated.

The specification can be published with open implementation requirements. It
must not label either implementation fully conformant until all mandatory
requirements for the declared profile have passed.

## References

- [WCH CH585 product description](https://wch-ic.com/products/CH585.html):
  hardware resources; not an independent-stack qualification.
- [Bluetooth Core 6.0, Vol 4 Part E](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-60/out/en/host-controller-interface/host-controller-interface-functional-specification.html):
  HCI packet and command semantics; pin command sections in the JSON contract.
