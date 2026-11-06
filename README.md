# ch58x-spec

`ch58x-spec` records open, evidence-labeled register specifications for WCH
CH58x peripherals that are absent from, or incomplete in, the public device
descriptions.

Each register block is added independently with its provenance, confidence,
validation status, and a machine-readable description.

Bluetooth work uses [CH585M as the primary C/Rust specification](docs/ble-architecture.md).
The [CH582M single-Peripheral adaptation](docs/ble-ch582-experimental.md) is
explicitly experimental and resource-limited. Current plaintext checkpoints
are not the definition of the full CH585 target.

The [HCI contract](protocol/ch585-ble-hci.json) records field offsets, units,
state/error behavior and capability requirements. [Shared vectors](conformance/ble-v1.json)
must execute against both production implementations. See the [primary target](profiles/ch585-full.json)
for open requirements; no full-profile conformance is claimed yet.
[Radio operations](docs/ble-radio-ch585.md) and [security](docs/ble-security.md)
define the corresponding sequencing and acceptance requirements.

## Scope

- register addresses, widths, reset assumptions, and known bit meanings;
- language-neutral behavior needed by peripheral drivers;
- evidence from public examples, permissively licensed implementations,
  disassembly observations, and controlled hardware experiments;
- explicit separation between confirmed facts, correlations, and hypotheses.

## Evidence labels

Every register or behavior uses one of these labels:

- `documented`: present in public WCH documentation;
- `source-correlated`: supported by multiple public source implementations;
- `binary-observed`: recovered from executable behavior without copying vendor
  source or binary material;
- `hardware-observed`: exercised on named hardware with a recorded procedure;
- `inferred`: a bounded interpretation that still needs confirmation.

An address alone does not establish all bit meanings. Hardware acceptance for
one chip or board is not automatically generalized to the whole CH58x family.

## Layout

```text
schema/       JSON Schema for machine-readable register blocks
spec/         one JSON register description per peripheral
docs/         behavior notes and evidence records
tools/        validation and generation helpers
protocol/     HCI field and ownership contracts
profiles/     CH585 target and independent experimental adaptations
conformance/  language-neutral inputs and expected results
```

## License

Licensed under either the Apache License, Version 2.0 or the MIT License, at
your option.
