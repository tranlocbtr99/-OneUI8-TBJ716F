# One UI 8 / Lenovo TB-J716F — Offline validation lab

Research-only project. **No flashing, no tablet access, no boot-success claim.**

Target: Lenovo Xiaoxin Pad Pro 2021 TB-J716F, unlocked bootloader, ZUI 15 / Android 13 vendor.

## Scope
- Inspect downloaded GSI metadata and SHA-256.
- Validate ARM64 image signatures and sparse/ext4/EROFS indicators.
- Record missing prerequisites for QEMU boot.
- Never flash devices or publish a supposedly compatible ROM without actual testing.

Source research: https://github.com/Nekover2/OneUI8-Tablet-GSI

## Run
GitHub Actions > ROM preflight > Run workflow. Optionally provide a direct HTTPS image URL and an independently verified SHA-256. Downloads are opt-in; default run tests the tooling only.

A passing preflight **does not mean One UI boots**.
