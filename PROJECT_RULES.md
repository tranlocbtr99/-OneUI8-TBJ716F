# PROJECT RULES — One UI 8 port for Lenovo TB-J716F

**Binding engineering rules.** Every future change must satisfy these gates.

## 1. Single objective
Port Samsung One UI 8 (Android 16 ARM64) to Lenovo Xiaoxin Pad Pro 2021 TB-J716F (Snapdragon 870). The Lenovo stock firmware is a hardware compatibility reference, not the target OS. Do not substitute an unrelated Linux/QEMU demo for ROM progress.

## 2. Prioritize direct impact
Before work, identify the exact ROM boot blocker or device feature being addressed, evidence of the blocker, proposed minimal change, and how it will be validated. Prefer the action with the highest expected impact on TB-J716F bootability and lowest regression/bricking risk. No speculative refactors, redundant scripts, or tangential workflows.

## 3. Evidence over assumptions
Distinguish **inspected**, **modified**, **built**, **static-validated**, **boot-tested**, and **device-tested**. Never call a ROM bootable or flashable on the basis of successful CI, ext4 packing, metadata edits, or unrelated virtual boots. Log unknowns and failures; never fabricate compatibility.

## 4. Device-specific integration order
1. Establish exact donor image and exact TB-J716F firmware partitions, hashes, Android versions, partition layout and recovery route.
2. Compare donor framework/system requirements against TB-J716F vendor VINTF/HAL, API levels, SELinux and kernel interfaces; produce an actionable blocker list.
3. Fix the highest-priority proven blockers with minimal, reversible, tracked patches; preserve stock device-specific binaries and firmware where required.
4. Rebuild with deterministic inputs, hashes, size/partition checks and automated static regression checks.
5. Only plan physical boot testing with user consent, verified stock restore/EDL path and explicit risk disclosure; no automatic flash.

## 5. Safety and release gates
Never touch real partitions or distribute a supposedly flashable image without validated layout, rollback/recovery instructions, and device testing. Keep all engineering outputs labeled NOT FLASHABLE until these gates pass. Never change unrelated devices or keys.

## 6. Efficiency
Avoid repeated downloads and full-image rebuilds when inspecting manifests or metadata suffices. Cache immutable inputs by SHA-256. Use small focused commits. Stop a line of work when it cannot materially advance this port. Reuse prior findings instead of repeating investigations.

## 7. Every change must show its value
Record: (a) observed blocker/evidence; (b) device-specific reason; (c) exact files changed; (d) test and result; (e) remaining blocker and next highest-value action. If these cannot be stated, do not commit the change.

## 8. User communication
Keep updates concise: what was actually changed, validation status, and the single next meaningful step. Do not require repetitive manual CI triggers for low-value probes. Admit uncertainty immediately.

## 9. Scope control
Pause generic QEMU/Cuttlefish experiments unless a specific, evidenced TB-J716F compatibility question requires them. No more generic kernel/BusyBox smoke tests.

## 10. Rule changes
Do not silently weaken these rules. Any exception needs a documented technical justification and the user's approval.
