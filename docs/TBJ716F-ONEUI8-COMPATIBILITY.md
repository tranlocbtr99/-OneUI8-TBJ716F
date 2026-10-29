# TB-J716F → One UI 8: compatibility evidence (research only)

Updated: 2026-10-29

## Confirmed from cited public sources
- Hardware: Lenovo Xiaoxin Pad Pro 2021 TB-J716F, Qualcomm Snapdragon 870 (SM8250-AC), arm64. Device tree: https://github.com/ISNing/android_device_lenovo_J716F
- Stock layout uses dynamic partitions. TWRP device page: https://twrp.me/lenovo/xiaoxinpadpro2021.html
- A community report describes Android 16 crDroid GSI running on TB-J716F with stock vendor; this is **not** a One UI 8 validation: https://t.co/lz4tqeQrvd
- Landscape display orientation may require GSI-specific fixes: https://github.com/pavel-kalmykov/tb-j716f-rotation-fix
- A separate One UI 8 GSI patch project reports success on **TB710FU**, a different Snapdragon 8 Gen 3 tablet with Android 16 stock/vendor API 34: https://github.com/Nekover2/OneUI8-Tablet-GSI
- Its author states the patched One UI 8 image is arm64-only and Samsung framework patches target missing Samsung vendor HALs. No TB-J716F validation exists in that project.

## Risks / unknowns
1. TB-J716F's exact current stock vendor API level, VNDK, VINTF manifests and FCM compatibility have not been collected.
2. Android 16 framework vs Android 13-era stock vendor needs a VINTF/SELinux/KeyMint compatibility review.
3. Samsung framework assumptions (health, audio effects, SystemUI, USB, telephony) need review against TB-J716F vendor.
4. Display rotation, camera, audio, fingerprint, stylus, DRM, graphics, Wi-Fi/Bluetooth remain unverified for One UI 8.
5. Partition sizing, filesystem and DSU support must be measured on the **actual device** before any deployment planning.
6. No signed, device-tested, recoverable ROM build is available.

## Current verified results
- ARM64 UEFI shell in QEMU: pass (separate experiment).
- ARM64 Ubuntu Linux kernel execution in QEMU: pass.
- ARM64 initramfs /init userspace execution in QEMU: pass.
- Android 16 userspace boot in QEMU: not tested.
- One UI 8 boot on TB-J716F: not tested.
- Physical tablet flash: not performed.

## Safe research gate
Do not create a flashable ZIP, change partitions, or assert device compatibility until vendor properties, partition sizes, VINTF manifests, kernel requirements and recovery/backup plan are validated. The OneUI8-Tablet-GSI project's DSU instructions are specific to TB710FU and may wipe /data; do not reuse them blindly on TB-J716F.
