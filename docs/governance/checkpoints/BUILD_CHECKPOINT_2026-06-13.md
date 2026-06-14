# Build Checkpoint — 2026-06-13 12:13

A point-in-time, verified snapshot of the `main` build and its governance state.

## Build state (verified)

| Item | Value |
|------|-------|
| Branch | `main` |
| Head commit | `dc163f7` (Merge PR #16 — inlet-capacity-foundation) |
| Working tree | clean; no open PRs |
| Test suite (local, 2026-06-13) | **2147 passed, 4 skipped** (Python 3.14) |
| Tests collected | 2151 |
| Last CI on `main` | `success` — PR #16 merge run, 2026-06-04 |

> Note: no commits have landed on `main` since the PR #16 merge (2026-06-04),
> so the build is unchanged since then. The pass count above is a fresh local
> run taken at checkpoint time; cross-version (3.10/3.11/3.12) coverage was last
> exercised by CI on the #16 merge.

## Branch protection (active, enforcing)

| Setting | Value |
|---------|-------|
| Required checks | `test (3.10)`, `test (3.11)`, `test (3.12)` |
| Strict (up-to-date before merge) | `true` |
| Enforce admins | `false` (solo-maintainer override retained) |

## Foundations merged

| Series | PR | Notes |
|--------|----|-------|
| GIS workflow foundation | — | Spatial features / GeoJSON |
| Hydraulic grade line (HGL) foundation | #14 | HGL/EGL profiles; also first CI gate |
| Culvert analysis foundation | #15 | Inlet/outlet control headwater; reuses barrel capacity |
| Inlet capacity foundation | #16 | Grate/curb/combination/slotted capture; applies clogging factor |

The runoff → inlet → pipe → culvert → outfall chain now has all major hydraulic
analysis kernels in place.

## Governance milestones observed

- **First CI gate** introduced with PR #14 (2026-06-02).
- **Branch protection** enabled 2026-06-02 (after #14; #14 itself was pre-protection).
- **First enforced merge**: PR #15 (2026-06-03) — gate observed `BLOCKED` → `CLEAN` → merged.
- **Second enforced merge**: PR #16 (2026-06-04) — same enforced path.
- Governance loop demonstrated end-to-end: spec → implementation → tests →
  multi-version CI → branch protection → merge → post-merge verification.

## Open threads (none blocking)

1. **Next series:** `hydraulic-grade-line-reporting-integration` — wire the merged
   HGL foundation into the reporting layer. Remaining work is integration/reporting,
   not new analysis kernels.
2. **Adapter coverage-sync test** — a test that walks `civil_toolbox/adapters/`
   and fails if any adapter lacks a `CalculationResult` completeness fixture.
   Still open from the contract-test sprint.
3. **Engineering analysis standardization** — standalone result models now exist
   for `HydraulicProfileResult`, `CulvertAnalysisResult`, and `InletCapacityResult`,
   each built adapter-ready. Future architectural decision: whether these remain
   standalone indefinitely or gain `CalculationResult` adapters for uniform audit
   coverage. Not a current action item and not a blocker — a visible convergence
   point. (Relates to thread 2: a coverage-sync test would only bind these once
   they route through adapters.)

## Honesty notes

- Cross-version greens (3.10–3.12) are from the 2026-06-04 CI run; today's
  re-verification is local (Python 3.14) only. Re-running CI requires a push.
- The foundation series' per-commit histories are buildable by construction
  (dependency-ordered, minimal `__init__` until the exports step), not
  individually bisect-executed. Each merged tree is fully CI-verified.

## Assessment

> Civil Toolbox has completed its first full hydraulic-analysis foundation stack,
> is operating under demonstrated protected-merge governance, and has transitioned
> from foundation construction into subsystem integration.

Sprint state: **STABILIZED** — no failing tests, no blocked foundations, no
unmerged foundation branches, no open PRs. The three deferred adapter seams
(Open Thread 3) are intentional future convergence, not cleanup debt. The repo is
positioned for the next capability series (`hydraulic-grade-line-reporting-integration`).
