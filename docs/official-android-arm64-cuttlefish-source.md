# Verified source for ARM64 Android virtual-device images

Source: https://ci.android.com/
Official documentation: https://source.android.com/docs/devices/cuttlefish/get-started

Recommended baseline:
- Branch: aosp-android-latest-release
- Target: aosp_cf_arm64_only_phone-userdebug
- Artifact: aosp_cf_arm64_only_phone-img-<BUILD_ID>.zip
- Matching artifact from SAME build: cvd-host_package.tar.gz

These are official AOSP Cuttlefish virtual-device images. They are NOT
Lenovo TB-J716F firmware, and do not emulate Snapdragon 870.

Important:
- Do not invent a build ID, checksum or artifact URL.
- AOSP CI artifacts may require browser access or credentials.
- A complete Cuttlefish boot requires its host launcher, disk layout,
  boot/vendor_boot, super partitions, AVB and matching images.
- A random QEMU virt kernel + vendor.img is NOT equivalent to Cuttlefish.
- Current GitHub ARM runner has no /dev/kvm; native Cuttlefish may not launch.
- The One UI 8 donor system is not a verified drop-in Cuttlefish replacement.
- Any modified image is engineering-only, NEVER flashable.

Next gate: select one concrete public Android 16 ARM64 Cuttlefish build,
record its exact artifact names, URLs, SHA256, and verify archive contents
before changing partitions or attempting a boot.
