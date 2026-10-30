# TB-J716F stock firmware: rawprogram reference audit

Source: GitHub Actions run 40999219244, artifact 12953095300 (`tbj716f-stock-partition-inventory`).

## Evidence

The artifact contains `archive-contents.txt`, seven rawprogram XML documents and `super-program-entries.json`. The archive-contents listing describes the original stock package; the artifact itself does **not** contain partition image bytes.

- `rawprogram0.xml` and `rawprogram_fullupgrade.xml` each reference `super.img`, `metadata.img` and `userdata.img`.
- The archive listing instead contains `super_1.img` through `super_6.img`, `metadata_1.img` and `metadata_2.img`, and `userdata_1.img` through `userdata_10.img`.
- `rawprogram1.xml`, `rawprogram2.xml`, `rawprogram3.xml`, `rawprogram4.xml` and `rawprogram5.xml` have no other unresolved non-empty filename references in the listing.
- The `super` entry has `physical_partition_number=0`, `start_sector=217896`, `num_partition_sectors=2097152`, `SECTOR_SIZE_IN_BYTES=4096`, `sparse=true`. Its nominal extent is 8 GiB.

## Interpretation and blockers

This is a **filename/reference discrepancy**, not proof of a corrupt or incomplete firmware archive. A packaging-specific sparse/chunk mapping or a different rawprogram XML may explain it. Do not concatenate `super_*.img` or flash a generated `super.img` until the exact encoding, offsets and intended XML mapping are verified.

The artifact does not include `super` metadata, vendor image bytes, HAL manifests or a boot test. Therefore VINTF compatibility, One UI 8 bootability and flash safety remain **unverified**.

## Next validation

1. Acquire the authorized full stock archive and verify its SHA-256.
2. Inventory all `rawprogram*.xml` including `rawprogram_unsparse0*.xml` and any packaging manifests.
3. Inspect sparse headers and chunk offsets of each `super_*.img` read-only; determine how the flashing package maps them.
4. Extract read-only LP metadata with `lpdump` from a verified reconstructed image only if reconstruction is justified.
5. Compare stock vendor VINTF/HAL and the pinned One UI donor; keep any engineering image explicitly NOT FLASHABLE.

No device flashing, AVB bypass or partition writing was performed.
