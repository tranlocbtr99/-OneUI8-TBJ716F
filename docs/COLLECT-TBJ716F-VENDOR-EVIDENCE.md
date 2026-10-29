# Collect TB-J716F vendor evidence without flashing

This project cannot infer TB-J716F vendor compatibility from generic QEMU boot or synthetic Android properties. A successful Android 16 GSI on another device is also not proof.

## Preferred evidence: read-only ADB commands on an already running TB-J716F

Run from a trusted computer with platform-tools, with USB debugging explicitly authorized on the tablet. These commands do **not** unlock, wipe, or flash the device:

```sh
adb devices
adb shell getprop ro.product.device
adb shell getprop ro.product.vendor.device
adb shell getprop ro.vendor.build.version.sdk
adb shell getprop ro.vndk.version
adb shell getprop ro.vendor.api_level
adb shell getprop ro.product.first_api_level
adb shell getprop ro.boot.dynamic_partitions
adb shell getprop ro.boot.slot_suffix
adb shell cat /vendor/build.prop > vendor-build.prop
adb shell cat /vendor/etc/vintf/manifest.xml > vendor-manifest.xml
```

Do not publish complete `adb shell getprop` output, serial numbers, Wi-Fi MAC addresses, IMEI, account data, or other device identifiers. Inspect and redact any collected files before uploading them to a public repository. Some vendor files may be inaccessible or absent depending on build.

Run the local parser:

```sh
python3 tools/vendor_inventory.py --vendor-build-prop vendor-build.prop --manifest vendor-manifest.xml --output vendor-compatibility.json
```

**Important:** The parser creates an inventory, not a definitive VINTF compatibility result. A full evaluation needs the device manifest, framework compatibility matrix, shipping API level, SELinux policy and actual Android 16 system image.

## When no PC or physical device access is available

Locate an authorized, publicly distributable **exact TB-J716F** stock firmware release. Record the original publisher, version, region, file hash, date and image type. Do not substitute TB710FU or another Lenovo model. Do not use unverified third-party flash packages as a trusted source. Firmware archives often contain `super.img` / `vendor.img`, not a standalone `vendor/build.prop`; the existing `vendor-firmware-inventory.yml` workflow only accepts a direct text property file and **cannot** extract it from an archive.

### Evidence checklist
- [ ] Verified source for exact TB-J716F firmware
- [ ] Verified original archive SHA-256
- [ ] Extracted vendor properties and VINTF manifests
- [ ] Confirmed stock vendor API / VNDK / FCM level
- [ ] Inspected dynamic partition sizes and layout
- [ ] Compared HAL declarations against candidate Android 16 framework
- [ ] Device-specific recovery/backup plan
- [ ] Only then consider non-destructive boot feasibility testing

Never flash a GSI/One UI image based solely on this checklist.
