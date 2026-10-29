# Port strategy — One UI 8 first, Lenovo stock ROM as hardware reference

Decision by project owner, 2026-10-29: **Do not block the project on ZUI 15**.

## Target

Port Samsung One UI 8 / Android 16 tablet-oriented userspace to Lenovo Xiaoxin Pad Pro 2021 TB-J716F (Snapdragon 870). The target deliverable is a bootable, device-tested One UI 8 ROM, not a ZUI upgrade.

## Source roles

1. **One UI 8 donor (primary)**: the Samsung system/framework/application image selected for the port. Confirm the actual donor package, its source device, Android version, checksum, provenance and legal redistribution terms before modifying it.
2. **TB-J716F stock firmware (reference)**: any verified exact-model Lenovo stock package (including older ZUI versions) can supply partition-layout, device-tree, hardware and VINTF evidence. It is not the main OS or a prerequisite ZUI 15 base.
3. **TB-J716F device-specific runtime**: working boot chain, kernel, vendor HALs, firmware, device trees and SELinux policies must be sourced or adapted for the actual hardware; old Lenovo packages are not automatically interchangeable.

## Engineering milestones

- M0: verify and inventory the One UI 8 donor image; record checksum and source model.
- M1: compare donor partitions, architecture, framework VNDK/VINTF requirements and TB-J716F device capabilities.
- M2: build an initial system-only adaptation; avoid Samsung bootloader/modem/vendor flashing.
- M3: validate boot chain, dynamic partitions, AVB/vbmeta, init, fstab, SELinux and log collection using safe, documented recovery paths.
- M4: achieve Android boot, ADB and UI, then bring up display/touch, Wi-Fi/Bluetooth, audio, sensors, camera, DRM, encryption and power management.
- M5: tablet UI, Samsung framework dependencies, performance, regression testing and reproducible release.

## Hard gates and non-claims

No verified One UI 8 donor ZIP or device boot evidence is yet available in the repo. A successful Linux QEMU test is not Android or One UI boot. The repo must not label an artifact flash-ready without device-specific validation, rollback/recovery plan and explicit user authorization for destructive operations.

ZUI 15 acquisition is **optional**, not a project blocker. Lenovo stock firmware remains a compatibility reference only.
