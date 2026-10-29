# One UI 8 donor candidate: MysticTech Galaxy Tab S9 GSI

Primary upstream engineering reference:
https://github.com/Nekover2/OneUI8-Tablet-GSI

## Why this donor

Upstream describes an **Android 16 / One UI 8** arm64 Galaxy Tab S9 (SM-X710, qssi) GSI, with a non-Samsung compatibility patch set and actual boot testing on a Lenovo **TB710FU**. The donor is a substantially closer starting point than a raw Samsung tablet OTA.

Important: **TB710FU is NOT TB-J716F.** The former has Snapdragon 8 Gen 3 and Android 16 vendor; our target is Snapdragon 870 and may have an older vendor interface. Upstream success does not establish compatibility on TB-J716F.

Upstream publishes this patched compressed-image identity (not yet downloaded or independently checked here):

- File: `OneUI8-GSI-arm64-A16-MysticTech-TabS9-nonsamsung-fix-20260813.img.zst`
- Size: 2,683,294,844 bytes
- Upstream SHA-256: `b9155186e0bf0ef88ef30181395c7be85f854edfe7bddccf6029a8941b8274b1`
- Expanded image: 6,845,104,128 bytes
- Expanded MD5 (upstream): `6946aa3fdcafa3475c1809b640f0df5c`
- Source fingerprint stated by upstream: `samsung/gts9wifizc/qssi:16/BP2A.250605.031.A3/X710ZCS5DZA1`

The upstream repository explicitly says its scripts/patches contain no Samsung or Lenovo proprietary firmware. Inspect its license and preserve attribution. Never redistribute a proprietary ROM image without authorization.

## Prioritized TB-J716F port work

1. **Donor provenance and reproducibility:** inspect upstream `MANIFEST.md`, `BUG-REPORT.md`, `docs/patching.md`, `patches/`; verify actual donor hash when authorized image is available. Do not reapply patches to an already patched image.
2. **Static cross-device checks:** Android framework vs vendor VINTF, architecture, kernel version, vendor API/VNDK, dynamic partition size and A/B layout, boot/init/fstab and SELinux. Missing device evidence must be reported as unknown, not passed.
3. **Carry portable fixes selectively:** health service null guards, audio effects config, Samsung SystemUI DeX check, USB config, Wi-Fi-only UI, setup language. Each patch must have exact-build preconditions and regression tests; some are already present in the patched image.
4. **Adapt TB-J716F separately:** tablet density/rotation/display, touch, audio, Wi-Fi/Bluetooth, cameras, sensors, encryption and power; verify device-specific HAL interfaces rather than transplanting TB710FU configurations.
5. **First boot:** only after verified recovery and backup route; collect serial/ADB/logcat/init/kernel/tombstone evidence, then fix the first observed blocker. Do not flash bootloader/modem/other-device vendor.
6. **Release gate:** successful real TB-J716F boot and hardware validation. Generic ARM64 QEMU Linux smoke tests are not sufficient.

## Current status

**DONOR IDENTIFIED; IMAGE NOT ACQUIRED OR VERIFIED; DEVICE COMPATIBILITY UNKNOWN; NO FLASHABLE ROM.**

ZUI 15 is not a blocker. Lenovo stock packages remain hardware-reference inputs only.
