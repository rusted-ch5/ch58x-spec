# Provenance policy

Specifications in this repository must identify both their source class and
their validation boundary.

Accepted inputs are public WCH documentation and examples, permissively
licensed open-source drivers, independently recorded executable behavior, and
controlled hardware observations. Proprietary source trees, firmware
libraries, object files, and extracted binaries are not committed.

Each machine-readable block records:

- the supported chip or chip family;
- the evidence label for every register and field;
- source references using URLs, revisions, or experiment identifiers;
- unresolved behavior and known chip differences.

Fresh implementation code must be written from the resulting specification,
not copied from vendor libraries.
