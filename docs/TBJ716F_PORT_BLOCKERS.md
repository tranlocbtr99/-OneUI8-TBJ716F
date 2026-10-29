# TB-J716F One UI 8: prioritized integration blockers

Status: **engineering research only — NOT FLASHABLE**. This is a decision log, not a claim of a working port.

## P0 — Android framework/vendor interface contract (first gate)
Evidence: donor One UI 8 is Android 16 (API 36); inspected TB-J716F stock vendor has VINTF target-level 5 and 52 HAL names. Existing `tools/analyze_oneui8_framework_manifests.py` compares names only and explicitly cannot establish VINTF compatibility. Existing `tools/stage_partial_vintf_tree.py` marks its input incomplete. **No complete checkvintf pass has been demonstrated.**

Next: extract *complete* framework matrices and manifests from donor partitions and complete vendor manifests/fragments, vendor compatibility matrix, kernel version/config, relevant properties from one **specific** TB-J716F stock build. Run official `checkvintf` on the staged tree; capture exact failed HAL/instance/version and requirement before patching. Do not delete Samsung declarations or fabricate HALs to force a pass.

Exit criterion: reproducible full VINTF result with every mismatch either corrected or documented as unresolved.

## P0 — boot chain and partition feasibility
Evidence: current engineering image changes only metadata, not hardware compatibility; there is no successful TB-J716F boot test. Android 16 donor system image alone is not a complete ROM. No validated partition-capacity/AVB/boot-vendor_boot-dtbo mapping for a final package has been demonstrated.

Next: inventory actual stock GPT/dynamic partitions, slot layout, boot/vendor_boot/init_boot availability, AVB descriptors, filesystem sizes and recovery images. Do not produce flashing instructions before confirming a reliable restore path.

Exit criterion: verified device-specific image/partition mapping and rollback procedure.

## P1 — Android 16 / old vendor compatibility
Evidence: donor Android 16 framework and older stock vendor interface levels differ. Exact incompatibilities are **unknown** without full VINTF and boot logs.

Next: identify real blockers from full checkvintf, sepolicy compatibility, linker namespace and vendor library dependencies; make minimal reversible fixes. Preserve hardware HAL binaries; do not substitute QEMU HALs.

## P1 — Samsung-only services and UX
Evidence: One UI donor originates from Samsung tablet; TB-J716F lacks Samsung-specific hardware and framework dependencies.

Next: inspect donor services, feature flags, proprietary dependencies and startup behavior. Disable or shim only components proven to block boot, preserving core One UI functionality where feasible.

## Validation ladder
1. Immutable input identity and extraction correctness.
2. Complete VINTF + partition/AVB static validation.
3. Reproducible engineering image build (NOT FLASHABLE).
4. Physical boot test **only with informed user consent and tested restore route**.
5. Functional hardware regression (display, touch, Wi-Fi, Bluetooth, audio, sensors, camera, suspend).

No more generic QEMU/BusyBox experiments: they do not close these device-specific blockers.

**Highest-value next task:** complete the VINTF input set and produce an exact mismatch report; no speculative ROM patch before that.
