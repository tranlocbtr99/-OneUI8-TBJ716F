# One UI 8 virtual boot experiment (ARM64)

This is a **QEMU virt** experiment, not a Lenovo TB-J716F emulator.
No bootloader, firmware, physical tablet or Android partitions are written.

## Prerequisites

Install qemu-system-arm on a Linux ARM64 host (or run with slow TCG on x86_64).
Provide all four **matching virtual-machine-compatible** inputs:

- `kernel`: Linux ARM64 Image supporting QEMU virt, virtio block and console ttyAMA0.
- `initrd`: Android first-stage init ramdisk configured for the virtual device.
- `system`: verified raw ext4 One UI 8 engineering image.
- `vendor`: vendor image specifically built for this virtual machine. **Do not substitute TB-J716F stock vendor.**

The repository currently has only the system image and Lenovo stock reference
evidence. **It does not contain the virtual kernel, Android ramdisk, or matching
virtual vendor needed for a meaningful boot test.** Therefore no boot result
should be claimed until these prerequisites are satisfied.

## Run (after acquiring compatible images)

```sh
python3 tools/qemu_arm64_oneui8_boot_experiment.py \
  --kernel Image --initrd ramdisk.img \
  --system tbj716f-oneui8-engineering.img \
  --vendor virtual-vendor.img \
  --seconds 300 --log output/qemu-console.log --result output/boot-result.json
```

The script reads both virtual disks **read-only** and collects serial console
output. It does not modify the input images. A missing boot marker is not proof
the ROM is incompatible: the guest may not emit the marker. A boot marker is
not proof that Lenovo hardware will work.

## Stop/go

1. Do not run physical flash commands from this experiment.
2. Before any physical trial, separately verify device partition layout,
   rollback/recovery capability, data backups and stock firmware integrity.
3. QEMU virt does not emulate Snapdragon 870, Adreno, Lenovo display/touch
   drivers or Qualcomm hardware HALs.
