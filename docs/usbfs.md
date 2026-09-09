# CH58x USBFS behavior

The CH58x USB full-speed device controller is based at `0x4000_8000` and uses
PFIC interrupt 22. CH581/CH582/CH583 and CH585 share the control and endpoint
state model, but their endpoint DMA register encoding differs.

## Endpoint DMA addresses

CH581/CH582/CH583 expose 16-bit endpoint DMA registers. The value is the low
16-bit offset of an address in the SRAM bank beginning at `0x2000_0000`.

CH585 exposes 32-bit registers at the same offsets. Only bits 16:0 are defined,
encoding an offset into its 128 KiB SRAM. A portable driver must not reuse the
CH582 halfword write on CH585: doing so silently truncates valid upper SRAM
offsets.

## Interrupt ordering

`INT_FG` is write-one-to-clear. The interrupt handler must snapshot `INT_ST`
and `RX_LEN` before clearing the transfer flag. A completed OUT packet is
accepted only when `TOGGLE_OK` is set; a duplicate with the wrong data PID must
not be delivered to the class driver.

CH585 has been observed returning `INT_ST = 0xbd` for a valid EP0 SETUP packet.
When `SETUP_ACTIVE` is set, the low endpoint nibble is not authoritative and
must not be rejected before the SETUP condition is decoded.

## Endpoint lifecycle

The endpoint control byte combines receive and transmit response state with
their expected/prepared data PID. Endpoints 1 through 3 also expose automatic
toggle control. Manual toggle remains useful for drivers that need explicit
clear-halt and multi-packet recovery semantics.

After bus reset, software must restore address zero, endpoint response state,
and DATA0 toggle state. Clearing an endpoint halt also returns the affected
direction to DATA0.

## Validation boundary

The common control path has been exercised by standalone USB enumeration,
control-transfer, CDC, and HID cases on recorded CH582M and CH585M boards. This
establishes the described USB controller behavior for those artifacts; it does
not validate every CH58x package, board layout, clock source, or endpoint mode.
