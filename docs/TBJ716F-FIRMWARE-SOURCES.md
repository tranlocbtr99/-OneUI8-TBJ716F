# TB-J716F stock firmware source research (2026-10-29)

## Confirmed model and support entry

Lenovo's Chinese tablet support catalog explicitly lists **小新Pad Pro 2021 (TB-J716F)**:
https://consumerservice.lenovo.com.cn/Tabletc.html

## Candidate firmware locations — UNVERIFIED, NOT APPROVED FOR FLASHING

1. Lenovo community member thread, updated 2026-09-17, lists TB-J716F at https://pan.quark.cn/s/5d10b782acb8. Thread: https://club.lenovo.com.cn/thread-7949280-1-1.html. **Member-uploaded archive, not a Lenovo-hosted verified image**. No trustworthy archive SHA-256 has been established.
2. Third-party ROM catalog https://romdevelopers.com/index.php?a=downloads&b=folder&id=48151 lists:
   - `TB-J716F_CN_OPEN_USER_Q00209.3_R_ZUI_13.0.430_ST_220113_qpst.zip` (3.12 GB as listed)
   - `TB-J716F_CN_OPEN_USER_Q00209.3_R_ZUI_12.6.211_ST_210730_qpst.zip` (2.86 GB as listed)
   These are older ZUI builds, not the user's current ZUI 15 firmware. Authenticity, contents, checksums and download access have **not** been verified.
3. Lenovo's official Software Fix / Rescue and Smart Assistant is at https://support.lenovo.com/vg/en/downloads/DS101291, but **availability for Chinese-market TB-J716F is unconfirmed**. Some Lenovo service documentation warns that Chinese mainland tablets may not be supported by manual rescue.

## Required next verification

- Find a model-exact, region-exact, build-exact ZUI 15 firmware source or collect read-only data from the tablet.
- Obtain an independently trustworthy SHA-256, and compare after downloading.
- Inspect archive format and extract vendor properties, VINTF and partition metadata **without flashing**.
- Do not feed a multi-GB archive to `vendor-firmware-inventory.yml`: it only accepts a direct small `build.prop` file.
- Do not claim a vendor compatibility verdict without framework matrices and actual device details.

**Status:** Candidate sources identified, **no firmware downloaded or authenticated**, no port or device test performed.
