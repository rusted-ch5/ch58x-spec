# CH585 controller security contract

Status: target requirements; full-profile acceptance is pending.
This contract covers Controller encryption and ownership. SMP, bonding storage
and application authorization require additional Host-level acceptance.

## SEC-AES: block primitive

The block primitive accepts a 16-byte AES-128 key and a 16-byte input in
conventional AES octet order. It returns the 16-byte encrypted block in the
same order. The register backend groups four octets into each little-endian
32-bit store or load; it must not reverse the whole array at this boundary.

The candidate AES block is at `0x4000c300`. Its 32-bit command/status offsets
are `0x00`/`0x04`; input/output words occupy `0x18..0x24` and key words occupy
`0x28..0x34`. The LLE mode word at `0x4000c250` gates the crypto path with bit 7.
These register interpretations are inferred pending published register-level
acceptance of the implementing image.

Serialize the transaction with radio ownership. Quiesce live packet operation
before standalone AES, preserve the prior crypto gate, set the gate, reset by
writing command `0x100` then zero, and load the key and data. Clear status bit 1
and arm status bit 0 using separate writes; then set command bit 0.

Poll with a finite bound. If status bit 0 is clear, read the result. If result
bit 1 is set while bit 0 remains set, acknowledge bit 0 and verify it clears
before returning to Code Flash. Reset on timeout and restore the crypto gate
on both success and failure. Keep the transaction and its reachable helpers
in SRAM under one bounded critical section. Do not suspend, log or format
inside that section. An error must not expose a successful-looking output.

## SEC-CCM: octets, nonce and authentication

Use AES-CCM with a 13-byte nonce, a four-byte MIC and two-byte message-length
encoding. Bluetooth HCI/LL key fields are least-significant-octet first.
Session-key derivation reverses the 16-byte LTK and SKD into the AES primitive's
octet order, encrypts, then reverses the result back into the HCI/LL key order.
CCM converts that session key to AES order at its own boundary.

The nonce comprises five little-endian packet-counter octets followed by eight
IV octets. The packet counter is 39 bits; bit 7 of nonce octet 4 is 1 for
Central-to-Peripheral and 0 for Peripheral-to-Central. Reject counter overflow
before mutation. The authenticated header octet is `header & 0xe3`, excluding
NESN, SN and MD. Authentication uses the plaintext length, not the wire length
including MIC. The selected PHY/DMA profile imposes its own length limit.

Authenticate before delivering plaintext. MIC mismatch must not advance receive
sequence state, refresh supervision, accept an ACK or release ACL credits.
The caller must not observe unauthenticated plaintext on MIC or cipher error.
Compare all four MIC octets without data-dependent early exit.

## SEC-OWNER: packet counters and retry

Maintain independent TX/RX packet counters per connection and direction. A
fresh authenticated payload owns one counter value. A retransmission retains
the same owner, counter, ciphertext and MIC; SN/NESN/MD changes do not create a
new payload owner. An Empty PDU carries no encrypted payload and does not
consume a counter. A duplicate accepted packet must not be delivered twice.

Bind cached encryption to the connection generation, owner identity, key, IV,
direction, packet counter, authenticated header, length and complete payload.
Reset, termination and rekey invalidate incompatible cached state. A queue-full
or encryption failure must preserve ownership until it is explicitly retired.

## SEC-HCI: procedures and capability reporting

LE Encrypt (`0x2017`) takes 16 key octets and 16 plaintext octets and returns
status plus 16 encrypted octets via Command Complete. Normalize HCI octet order
at this boundary. LE Start Encryption (`0x2019`) takes a two-byte handle,
eight-byte Rand, two-byte EDIV and 16-byte LTK and uses Command Status followed
by the applicable encryption event.

LE Long Term Key Request Reply (`0x201a`) takes handle plus 16-byte LTK;
Negative Reply (`0x201b`) takes only the handle. Their Command Complete return
includes status and handle. Replies are legal only for the active request and
connection generation. Wrong handles, wrong lengths and stale replies must
not mutate encryption state. A successful reply is not proof that encryption
has completed. Publish the encryption feature only after the implemented
procedure and security gates pass.

## Acceptance

Required gates include FIPS-197 AES-128, Bluetooth session-key and bidirectional
CCM vectors; independent peer encryption; wrong key, IV, direction, counter and
MIC rejection; retry identity; duplicate suppression; LL control during data;
rekey, reconnect and reset. Include injected primitive failures and queue
exhaustion. Run active encrypted traffic with checksums and owner accounting.
PHY/DMA packet CCM requires its own live-operation acceptance even when
software CCM backed by the AES block already passes.
