# CH585 protected access and clock handoff

CH585 protected registers use an unlock port at `0x4000_1040`. Consecutive
writes of `0x57` and `0xa8`, followed by the required instruction-ordering
barrier, open the write window. Writing zero closes it.

The short automatic timeout is useful for ordinary isolated register writes.
Clock startup is different: oscillator settling and the clock/Flash handoff
cannot be divided into unrelated short transactions. The public startup
sequence clears `SAFE_MODE_CTRL.AUTO_TIMEOUT_ENABLE`, performs the bounded
clock transition from SRAM, restores the timeout, and explicitly closes the
protected window.

The accepted 62.4 MHz external-crystal path powers the 32 MHz crystal and PLL,
selects the corresponding documented PLL/divider encoding, configures Flash
timing, and records the resulting system frequency for peripheral drivers.

Cold-start tests must not assume reset defaults left by a debugger or
bootloader. In particular, reload the watchdog before oscillator delays and
explicitly choose the 32 kHz source.

The described sequence has been exercised on a recorded CH585M EVT fixture.
It does not establish timing margins for every crystal, voltage, temperature,
or board layout.
