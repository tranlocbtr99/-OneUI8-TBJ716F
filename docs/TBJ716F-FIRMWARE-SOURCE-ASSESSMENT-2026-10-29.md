# TB-J716F firmware source assessment (2026-10-29)

## Available public references

| Source | Evidence | What it does NOT establish |
| --- | --- | --- |
| RomGoc: https://romgoc.net/rom-dump-lenovo-xiaoxin-pad-pro-2021-tb-j716f/ | Listings for TB-J716F ZUI 12.5.126 readback and ZUI 12.6.211 QPST | No authenticated ZUI 15 image or checksum |
| RomDevelopers: https://romdevelopers.com/index.php?a=downloads&b=folder&id=48151 | TB-J716F ZUI 13.0.430 (3.12 GB) and ZUI 12.6.211 (2.86 GB) listings | Download authenticity, vendor compatibility and verified hashes unknown |
| AndroidFileHost: https://androidfilehost.com/?flid=339312&w=files | Stock recovery images labeled TB-J716F ZUI 13.1.560 and ZUI 14.0.266 | Recovery image is not a complete vendor/boot/system firmware set |
| Lenovo community member: https://club.lenovo.com.cn/thread-7949280-1-1.html | TB-J716F Quark share https://pan.quark.cn/s/5d10b782acb8 | No independent manifest, checksum or ZUI 15 build identity |

## Key decision

No independently verifiable **full TB-J716F ZUI 15** firmware package was located in these sources. A 2023 community discussion about ZUI 15 OTA/beta does not establish a public full firmware archive: https://www.reddit.com/r/androidtablets/comments/17fatid .

For the One UI 8 port, keep two separate evidence tracks:

1. **Device stock base**: verified TB-J716F vendor, kernel, boot and firmware; ideally a read-only capture of the device's currently installed build.
2. **One UI 8 system donor**: a separately identified image with source model, Android release, license, partition structure and SHA-256.

Do not substitute ZUI 12.x or 13.x for the user's current vendor by default, and do not claim a generic GSI boot proves hardware support. No flash should occur until verified rollback/recovery and device-specific compatibility evidence exist.

## Acquisition requirements

For each candidate record canonical download URL, exact model, filename, file size, cryptographic digest, origin and authorization. If a source requires payment, password or membership, use normal authorized access only.
