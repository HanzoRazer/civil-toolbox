# Task Spec — Headless Run · civil-toolbox

Repo-specific headless runner for **civil-toolbox** (drainage analysis workstation).
Use for GREEN/YELLOW tasks you kick off at the desk and monitor via Remote Control.

Runs on this machine — dies on the 48h reboot, so keep it short enough to finish in one
window, or make it restartable (idempotent + reads its own `SPRINT_LOG` to resume).

Fill the brackets, paste the command block into PowerShell.

---

## Repo facts (already filled in)

- **Repo path:**      `C:\Users\thepr\Downloads\civil-toolbox`
- **Language:**       Python — PEP 8, type hints, dataclasses for data models
- **Test runner:**    `pytest` from repo root
- **Test layout:**    `tests/{adapters,calculators,comparison,design_criteria,domain,gis,hydraulics,infrastructure,infrastructure_sizing,persistence,rainfall,reporting}`
- **Package:**        `civil_toolbox/` (mirrors the test layout)
- **Standards:**      [ENGINEERING_STANDARDS.md](ENGINEERING_STANDARDS.md), [CLAUDE.md](CLAUDE.md), [ARCHITECTURE.md](ARCHITECTURE.md)

### Non-negotiable repo guardrails (cite these in the prompt)

1. **Calculation kernels are pure** — `civil_toolbox/calculators/` has no I/O, no state, no UI.
2. **Units are explicit** — no bare floats; use suffixes `_ft`, `_acres`, `_in_per_hr`, `_cfs`, `_cf`, `_ft_per_ft`, `_min`/`_hr`.
3. **Results are auditable** — every output traces to inputs + method (`CalcResult` contract).
4. **Reporting does not calculate** — `civil_toolbox/reporting/` only formats existing data.
5. **Methods cite a reference** — every engineering method pins ≥1 authoritative source.
6. **Scan before you edit** — read the whole target file before modifying it.
7. **Verify the live path** — run the actual execution path before claiming a feature works.

---

## Spec (fill the brackets)

- **Sprint ID:**        [e.g. RATIONAL-VALIDATION-1]
- **Task (one line):**  [e.g. "Run the suite, fix failing rational_method tests via isolation, not by loosening tolerances"]
- **Layer/scope:**      [e.g. calculators/rational_method  | comparison  | reporting]
- **Color (rubric):**   [GREEN / YELLOW]
- **Stop condition:**   [e.g. "all tests green OR 5 turns elapsed"]
- **Reversible?**       [must be yes — runs on a branch, review diff before merge]
- **Tools needed:**     [Read,Grep,Glob  | add Write,Edit only if it writes | Bash(git commit:*) if it commits]

---

## Command (PowerShell, on the always-on box)

```powershell
cd C:\Users\thepr\Downloads\civil-toolbox
git checkout -b auto/[SPRINT-ID]/[task-slug]

claude -p "[TASK].
Repo: civil-toolbox. Standards: ENGINEERING_STANDARDS.md and CLAUDE.md key principles.
Before modifying any file, read it in full first.
Calculation kernels in civil_toolbox/calculators/ stay pure — no I/O, no state.
Keep units explicit (suffixes _ft, _acres, _in_per_hr, _cfs, _cf); no bare floats in APIs.
Preserve the CalcResult audit trail (value, units, formula_id, references, inputs, derivation).
Reporting only formats data — never add calculations there.
Verify the live execution path (run pytest for the touched layer) before claiming anything works.
Append one factual line per step to docs/sprints/[SPRINT-ID]/SPRINT_LOG.md — observable facts only, no interpretation.
Commit atomically using Conventional Commits: type(scope): description.
Stop when: [STOP CONDITION]." `
  --allowedTools "[Read,Grep,Glob,...]" `
  --max-turns [N] `
  --permission-mode plan   # start in plan (read-only) to preview; drop this flag to execute
```

### Verify the touched layer (drop into the prompt or run manually)

```powershell
pytest                              # full suite
pytest tests/calculators/           # one layer
pytest tests/comparison/            # comparison layer
pytest tests/reporting/             # reporting layer
pytest -v --tb=short                # verbose, short tracebacks
```

---

## Worked example (copy, then tweak)

```powershell
cd C:\Users\thepr\Downloads\civil-toolbox
git checkout -b auto/RATIONAL-VALIDATION-1/fix-tolerance-failures

claude -p "Run pytest tests/calculators/ and fix the failing rational_method validation tests.
Repo: civil-toolbox. Standards: ENGINEERING_STANDARDS.md and CLAUDE.md key principles.
Diagnose by isolating the failure — do NOT loosen test tolerances or edit benchmark expected values to pass.
Before modifying any file, read it in full first.
rational_method.py is a pure kernel: no I/O, no state. Keep units explicit (_in_per_hr, _acres, _cfs).
Preserve the CalcResult audit trail on every return.
Verify by re-running pytest tests/calculators/ before claiming success.
Append one factual line per step to docs/sprints/RATIONAL-VALIDATION-1/SPRINT_LOG.md — facts only.
Commit atomically: fix(calculators): <what changed>.
Stop when: tests/calculators green OR 5 turns elapsed." `
  --allowedTools "Read,Grep,Glob,Edit,Bash(pytest:*),Bash(git commit:*)" `
  --max-turns 5 `
  --permission-mode plan
```

---

## Notes

- Start in `--permission-mode plan` for anything YELLOW — it shows the plan without touching files. Drop the flag to execute.
- `--max-turns` is your cost + runaway fence. Mechanical task: 3–5. Don't leave it unbounded.
- `docs/sprints/<SPRINT-ID>/` does not exist yet — the run creates it on first `SPRINT_LOG.md` write (needs `Write`/`Edit` in `--allowedTools`).
- To monitor from your phone: start a session, then `/rc` inside it, scan the QR. (Single connection at a time; rough preview — fine for watching, not for hot-fixing.)
- When back at the desk: review the diff on the branch before merging. **Never auto-merge to main.**

---

## Worked Example 2 — CalculationResult audit-trail completeness · civil-toolbox

A second GREEN candidate. It hardens the **"results are auditable"** guardrail by proving that
every `CalculationResult` an adapter emits carries a complete audit trail — so a result with no
`references`, empty `units`, or empty `outputs` fails CI instead of shipping.

### Where the audit trail actually lives (read this first)

This was reconciled against the real source — the contract differs from the illustrative
`CalcResult` snippet in [ENGINEERING_STANDARDS.md](ENGINEERING_STANDARDS.md):

- **Calculator kernels are pure and carry NO audit trail.** `civil_toolbox/calculators/` returns
  bare numeric dataclasses (`RationalMethodResult`, `TR55RunoffResult`, `SheetFlowResult`,
  `TimeOfConcentrationResult`). That is guardrail #1 — do **not** write a test demanding kernels
  carry references; that would fight the architecture.
- **The audit trail is built one layer up, in adapters.** `civil_toolbox/adapters/` uses
  [`ResultBuilder`](civil_toolbox/adapters/result_builder.py) to construct
  [`CalculationResult`](civil_toolbox/domain/calculation.py) and attach `references`, `units`,
  `inputs`, `outputs`. **That is the correct target for a completeness test.**
- **Real `CalculationResult` fields:** `method` (required, enforced in `__post_init__`),
  `inputs: dict`, `outputs: dict`, `units: dict`, `assumptions: list`, `warnings: list`,
  `references: list[EngineeringReference]`, `metadata: dict`.
  There is **no** `value`, `formula_id`, or `derivation` field.

### The one reconciliation point left

Adapters can't be called with zero args — `RationalMethodAdapter.calculate(...)` needs a
`DrainageArea` + `StormEvent`. So the test is **fixture-driven**: each adapter gets a minimal
in-memory domain entity, then we assert the emitted `CalculationResult` is complete. The
rational-method seed below is concrete and correct against
[adapters/rational_method.py](civil_toolbox/adapters/rational_method.py); confirm the
`DrainageArea` / `StormEvent` constructor kwargs against
[civil_toolbox/domain/](civil_toolbox/domain/) on first run, then extend the fixture table to
`tr55` and `time_of_concentration` following the same shape.

---

## Part A — the test the agent should produce

```python
# tests/contracts/test_calculation_result_completeness.py
"""
Contract test: every CalculationResult emitted by an adapter must carry a complete,
non-empty audit trail. Guards the "results are auditable" guardrail
(ENGINEERING_STANDARDS.md) against silent degradation.

Audit trail lives at the ADAPTER -> CalculationResult seam, NOT in calculator kernels
(kernels are pure by design — guardrail #1). Targets are exercised, not introspected,
because adapters require domain-entity inputs.
"""
from __future__ import annotations

import pytest

from civil_toolbox.domain.calculation import CalculationResult
from civil_toolbox.domain.drainage import DrainageArea
from civil_toolbox.domain.storm import StormEvent
from civil_toolbox.adapters.rational_method import RationalMethodAdapter

# Fields that must be present AND non-empty on every emitted CalculationResult.
# (method is already enforced non-empty by CalculationResult.__post_init__.)
NON_EMPTY_FIELDS = ("method", "inputs", "outputs", "units", "references")


def _rational_method_result() -> CalculationResult:
    """Exercise the rational-method adapter with a minimal valid fixture.

    Reconcile these constructor kwargs with the real DrainageArea / StormEvent
    dataclasses on first run, then add tr55 / time_of_concentration fixtures below.
    """
    area = DrainageArea(name="A1", area_acres=10.0, runoff_coefficient=0.65)
    storm = StormEvent(name="10yr", rainfall_intensity_in_per_hr=4.5)
    return RationalMethodAdapter.calculate(area, storm)


# (label, factory) — one entry per adapter construction path. Extend this list;
# do NOT collapse it to a single case (a one-adapter test gives false coverage).
RESULT_FACTORIES = [
    ("rational_method", _rational_method_result),
    # ("tr55", _tr55_result),
    # ("time_of_concentration", _toc_result),
]


def test_factory_table_is_populated():
    """Fail loudly if coverage has been gutted to nothing — no vacuous green."""
    assert RESULT_FACTORIES, "No adapter fixtures registered — reconcile coverage."


@pytest.mark.parametrize(
    "label,factory", RESULT_FACTORIES, ids=[f[0] for f in RESULT_FACTORIES]
)
def test_calculation_result_audit_trail_complete(label, factory):
    result = factory()

    assert isinstance(result, CalculationResult), f"{label}: not a CalculationResult"

    for field_name in NON_EMPTY_FIELDS:
        val = getattr(result, field_name)
        assert val, f"{label}: '{field_name}' is empty — incomplete audit trail"

    # References must cite at least one authoritative source (guardrail #5).
    assert len(result.references) >= 1, (
        f"{label}: no references — every method must cite >= 1 source"
    )
    # Units must cover every output quantity (no bare floats in the audit record).
    for output_name in result.outputs:
        assert output_name in result.units, (
            f"{label}: output '{output_name}' has no unit in the audit record"
        )
```

---

## Part B — the headless command to delegate writing it

```powershell
cd C:\Users\thepr\Downloads\civil-toolbox
git checkout -b auto/CALCRESULT-CONTRACT-1/completeness-test

claude -p "Create tests/contracts/test_calculation_result_completeness.py asserting that every
CalculationResult emitted by an adapter carries a complete, non-empty audit trail (method, inputs,
outputs, units, references), with references citing at least one source and every output having a unit.
Repo: civil-toolbox. Standards: ENGINEERING_STANDARDS.md and CLAUDE.md key principles.
CRITICAL ARCHITECTURE FACT: the audit trail lives at the adapter -> CalculationResult seam
(civil_toolbox/adapters/ via ResultBuilder), NOT in calculator kernels. Calculator kernels in
civil_toolbox/calculators/ are pure and return bare numeric dataclasses by design (guardrail #1) —
do NOT assert kernels carry references; that contradicts the architecture.
FIRST, read civil_toolbox/domain/calculation.py (the real CalculationResult), the DrainageArea and
StormEvent domain dataclasses, and at least one adapter, in full. Reconcile the fixture constructor
kwargs against the real dataclasses before writing.
The test must exercise adapters with minimal fixtures (they need domain-entity inputs); cover at
least rational_method, tr55, and time_of_concentration. It must fail loudly if the fixture table is
empty (no vacuous green). Do NOT modify any adapter or kernel to make the test pass — if an adapter
genuinely omits references or units, leave it failing and log it; that is a real finding.
Verify by running pytest tests/contracts/ before claiming success.
Append one factual line per step to docs/sprints/CALCRESULT-CONTRACT-1/SPRINT_LOG.md, creating the
dir and writing the first line only AFTER the first diagnostic step — observable facts only.
Commit atomically: test(contracts): add CalculationResult audit-trail completeness check.
Stop when: tests/contracts collected and the test runs (pass or with logged real findings) OR 6 turns elapsed." `
  --allowedTools "Read,Grep,Glob,Write,Edit,Bash(pytest:*),Bash(git commit:*)" `
  --max-turns 6 `
  --permission-mode plan
```

---

## Why this one is GREEN

- **Reversible:** new test file on a branch; `git revert` erases it cleanly.
- **Machine-verifiable:** the test either collects and runs, or it doesn't.
- **Architecture-aligned:** it targets the adapter seam where the audit trail is actually built,
  so it reinforces guardrail #1 (pure kernels) instead of fighting it.
- **Fabrication-fenced:** the prompt forbids the two cheats — modifying an adapter to pass, and a
  vacuously-green table that covers nothing. An adapter that legitimately omits references surfaces
  as a *finding you wanted*, not a failure to hide.

Run it in plan mode first. The tell that it guessed instead of reading: if the preview shows the
agent writing the test before it has opened `domain/calculation.py` and the domain entity classes,
stop it — the fixture kwargs will be wrong and the whole suite will error on collection.
```
