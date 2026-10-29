# TB-J716F stock firmware candidate: RomGoc

Source: https://romgoc.net/rom-dump-lenovo-xiaoxin-pad-pro-2021-tb-j716f/

Verified page listing (2026-10-29):

1. `TB-J716F_ZUI_12.5.126_Readback_Global_UBL.zip` — labeled Global readback dump, ZUI 12.5.126.
2. `TB-J716F_CN_OPEN_USER_Q00209.3_R_ZUI_12.6.211_ST_210730_qpst.zip` — labeled China QPST, ZUI 12.6.211.

These are **stock firmware candidates for device-specific reference**, NOT a Samsung One UI 8 donor. Neither is the user's installed ZUI 15 / Android 13 firmware. The site indicates some files or archive passwords require VIP access. Direct package bytes, provenance, license, SHA-256, and hardware compatibility are not yet verified.

## Engineering use

- Prefer an independently verified ZUI 15 build from the exact TB-J716F device for matching current bootloader/vendor/kernel ABI.
- Analyze older ZUI 12.x packages offline as secondary evidence for partition layout and hardware names only; do not assume their vendor images are Android 16-compatible.
- Keep the One UI 8 donor candidate separate; do not transplant Samsung bootloader, radio, firmware, kernel, or vendor images.
- No flashing, unlocking, wiping, or downloading unverified archives as part of this source registration.

## Acquisition gate

A direct authorized HTTPS archive URL and independently established SHA-256 are required before invoking `analyze-firmware-zip.yml`. The RomGoc article URL is a landing page, not an archive URL. If the archive is password protected or behind membership, do not bypass access controls.
