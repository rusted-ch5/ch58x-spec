# CH585 USBHS behavior

CH585 contains an independent high-speed USB device controller at
`0x4000_9000`, using PFIC interrupt 37. Its endpoint model is not a wider copy
of the USBFS block and should be implemented as a separate backend.

## Enable sequence

The USBHS PLL at `0x4000_9200` and the USBHS pin function in the system pin
configuration must be enabled before the controller and PHY. A driver then
resets the link and serial interface engine, selects high-speed device mode,
configures endpoint DMA and length registers, clears pending flags, enables
the required interrupts, and activates DMA, PHY, and device operation.

The PLL and system pin registers are outside the USBHS register block and will
be described with the system-control specification.

## Endpoint layout

There are eight endpoint slots. EP0 owns one shared DMA bank. Endpoints 1
through 7 have separate receive and transmit DMA registers. DMA values use a
17-bit offset into CH585's 128 KiB SRAM rather than a complete CPU address.

Each endpoint has a maximum receive length, current receive length, transmit
length, and one-byte control register per direction. The response encoding is:

- `0`: NAK;
- `1`: STALL;
- `2`: ACK.

The receive control byte also reports SETUP on EP0, and both directions expose
their DATA0/DATA1 state.

## Interrupt handling

The handler must read `INT_FG`, `INT_ST`, and the endpoint length/control state
before clearing the write-one-to-clear event. Transfer completion identifies
the endpoint in bits 2:0 and the IN direction in bit 4. Bus reset invalidates
outstanding endpoint operations and returns the device address and endpoint
state to their initial values.

## Validation boundary

The described layout has been used by standalone CH585M control, bulk,
interrupt, reset, and sustained interrupt-IN experiments. These results apply
to the recorded fixture and exact firmware; they are not a USB electrical or
protocol certification and do not establish behavior for another chip family.
