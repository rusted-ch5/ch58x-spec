# ch58x-spec

`ch58x-spec` records open, evidence-labeled register specifications for WCH
CH58x peripherals that are absent from, or incomplete in, the public device
descriptions.

Each register block is added independently with its provenance, confidence,
validation status, and a machine-readable description.

## Scope

- register addresses, widths, reset assumptions, and known bit meanings;
- behavior needed by independently implemented Rust drivers;
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
```

## License

Licensed under either the Apache License, Version 2.0 or the MIT License, at
your option.
