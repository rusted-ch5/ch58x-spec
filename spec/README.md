# Register descriptions

Each JSON file describes one independently reviewable register block and must
pass `python3 tools/validate.py`.

Offsets are byte offsets from `base_address`. Fields are listed only when their
meaning has evidence; unknown and reserved bits are intentionally omitted.

Uniform repeated registers may use `register_arrays`. The `{n}` placeholder in
the name expands from zero through `count - 1`; `offset` identifies instance
zero and `stride` is measured in bytes. `index_base` changes the first value
substituted for `{n}` without changing the offset calculation.
