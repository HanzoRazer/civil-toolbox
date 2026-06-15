# Parameter Namespace

**Status:** Initial registry, Phase A.
**Companion to:** SPEC_civil_toolbox_app v0.2.1.
**Maintained by:** Ross Echols, P.E. #78195

This document defines the canonical namespace for `parameter_id` strings used across `civil_toolbox`. Every parameter referenced by `JurisdictionAuthority`, `DefaultValue`, `ParameterSchema`, `DefaultOverride`, or any validation rule MUST use an ID from this registry.

---

## 1. Why this exists

`parameter_id` is the join key for everything in the defaults system. Without a canonical namespace, drift is inevitable:

- One jurisdiction implements `mannings_n`
- Another implements `manning_n`
- A third implements `manning_coefficient`
- A fourth implements `n_value_channel`

All four describe Manning's n. None can resolve a default for the others' projects. The cost compounds with every new jurisdiction.

This document is the source of truth. A CI test (§8) validates all parameter IDs in code against this registry.

---

## 2. Naming conventions

### 2.1 Format

```
<domain>_<noun>[_<qualifier>][_<unit>]
```

Components:

| Component | Required | Rule | Examples |
|---|---|---|---|
| `domain` | Yes | One of the canonical domain prefixes (§3) | `project`, `hydrology`, `hydraulics`, `inlet`, `culvert` |
| `noun` | Yes | snake_case noun describing the parameter | `mannings_n`, `curve_number`, `design_storms` |
| `qualifier` | Optional | When the noun alone is ambiguous | `channel`, `overbank_left`, `overbank_right` |
| `unit` | Optional, see §2.3 | When unit is material to the identifier | `ft`, `acres`, `years` |

### 2.2 Rules

1. **snake_case throughout.** No camelCase, no dashes, no dots.
2. **Singular nouns.** `design_storms_years` is the exception (the parameter IS a collection of storms; the plural is semantic, not naming style).
3. **Domain prefix is mandatory.** No "global" parameters. If a parameter genuinely cuts across domains (rare), it goes in `common_*`.
4. **No abbreviations except canonical units.** `mannings_n` not `manning_co`. `freeboard_ft` not `fb_ft`.
5. **Lowercase ASCII only.** No Unicode, no special characters.
6. **Length:** 8–60 characters. Shorter is suspect (probably ambiguous); longer is unwieldy.
7. **Stable.** Once an ID is in the registry and used, it does NOT change. Deprecation requires a migration path (§7).

### 2.3 When to include units in the identifier

Include units in the identifier when:
- The parameter exists in multiple unit conventions and a unit-bare name would be ambiguous (`freeboard_ft` not `freeboard` — because ft vs m matters)
- The unit is the most distinguishing attribute (`design_storms_years` — the years are the storms)

Omit units when:
- The kernel enforces one unit everywhere and the `ParameterSchema.units` field is sufficient
- The unit is implied by the noun (`runoff_coefficient` is dimensionless; `curve_number` is dimensionless; no suffix needed)

### 2.4 Regex

```regex
^[a-z][a-z0-9_]{6,58}[a-z0-9]$
```

Plus the additional rule: must start with one of the canonical domain prefixes from §3 followed by `_`.

---

## 3. Canonical domain prefixes

| Prefix | Scope | Used by |
|---|---|---|
| `project_` | Project-level metadata, setup, lifecycle | Phase A |
| `hydrology_` | Rainfall-runoff transformation | Phase B+ |
| `hydraulics_` | Open channel flow, normal depth, step backwater | Phase B+ |
| `inlet_` | Inlet capacity (grate, curb, combination, slotted) | Existing kernel |
| `culvert_` | Culvert inlet/outlet control headwater | Existing kernel |
| `infrastructure_` | Pipe sizing, manhole, drainage structure | Existing kernel |
| `floodplain_` | BFE comparison, no-rise math, encroachment | Phase B+ |
| `gis_` | Spatial / geometric attributes | Existing kernel |
| `common_` | Cross-domain (rare; requires explicit justification) | As needed |

**No new domain prefixes without an ADR.** Adding a prefix is a deliberate decision; this list is short on purpose.

---

## 4. Phase A registry

Parameters with defined defaults, schemas, or validation rules in Phase A.

### 4.1 Project-level

| `parameter_id` | Type | Required by jurisdiction? | Default source | Notes |
|---|---|---|---|---|
| `project_name` | str | Always | None | Free text |
| `project_site_name` | str | HCFCD (optional) | None | Site / development name |
| `project_site_address` | str | None | None | Free text |
| `project_parcel_id` | str | None | None | Identifier per HCAD |
| `project_latitude_deg` | float | None | None | WGS84 decimal degrees |
| `project_longitude_deg` | float | None | None | WGS84 decimal degrees |
| `project_jurisdiction_id` | str (enum) | Always | None | One of registered jurisdictions |
| `project_design_storms_years` | tuple[int] | Always | HCFCD: `(2, 5, 10, 25, 100)`; Generic: `(10, 100)` | Return periods to analyze |
| `project_freeboard_ft` | float | HCFCD | HCFCD: `1.0` | Freeboard above design WSE |
| `project_status` | enum | System-managed | `DRAFT` on create | See SPEC §3.6 |

### 4.2 Phase B+ examples (forward-looking; NOT implemented)

Included here to validate the namespace works for the larger scope.

```
hydrology_runoff_coefficient
hydrology_curve_number
hydrology_curve_number_pre_development
hydrology_curve_number_post_development
hydrology_sheet_flow_length_ft
hydrology_time_of_concentration_min
hydrology_initial_abstraction_in
hydraulics_mannings_n_channel
hydraulics_mannings_n_overbank_left
hydraulics_mannings_n_overbank_right
hydraulics_contraction_loss_coefficient
hydraulics_expansion_loss_coefficient
hydraulics_ineffective_flow_area_ft2
floodplain_base_flood_elevation_ft
floodplain_no_rise_tolerance_ft
floodplain_finish_floor_elevation_ft
floodplain_lowest_adjacent_grade_ft
```

These are NOT in the registry until their phase actually arrives. The list above is illustrative for namespace validation only.

---

## 5. Resolution semantics

When `default_for(parameter_id, ...)` is called:

1. The ID is validated against the regex (§2.4) and the domain-prefix list (§3). Invalid → raise at registration time, not at call time.
2. Jurisdiction-specific default returned if present.
3. Otherwise `None`. Never raises for unknown parameters.

When an override is applied:

1. The ID must already exist in the registry.
2. The override value must conform to `ParameterSchema.valid_range` if defined.
3. Otherwise the override is rejected at validation, before persistence.

---

## 6. Cross-jurisdiction consistency

Different jurisdictions resolve the same `parameter_id` to different default values. They do NOT use different IDs for the same concept.

✅ Correct:
```
default_for("hydraulics_mannings_n_channel", jurisdiction="hcfcd") → 0.013
default_for("hydraulics_mannings_n_channel", jurisdiction="generic") → 0.015
```

❌ Incorrect:
```
HCFCDAuthority.default_for("hcfcd_mannings_n_channel") → 0.013
GenericAuthority.default_for("generic_mannings_n_channel") → 0.015
```

The second form makes cross-jurisdiction comparison impossible.

---

## 7. Adding, deprecating, and renaming IDs

### 7.1 Adding

1. Update this document (`PARAMETER_NAMESPACE.md`) with the new ID and its row
2. Add `ParameterSchema` entry in `civil_toolbox/design_criteria/parameters.py`
3. Add defaults for each applicable jurisdiction
4. Add test in `tests/design_criteria/test_parameter_namespace.py` asserting the ID is in registry
5. Commit registry update + schema + defaults + tests as a single PR

### 7.2 Deprecating

Parameters are not deleted from the registry. They are marked `deprecated`:

```
hydrology_old_parameter_name  [DEPRECATED 2027-03-15; replaced by hydrology_new_parameter_name]
```

The deprecated parameter's defaults and schema entries remain so historical projects continue to load. New projects cannot use deprecated parameters (validation rule).

### 7.3 Renaming

Renaming = deprecating old + adding new + writing a kernel persistence migration (`civil_toolbox/persistence/migration.py`) that translates the old ID to the new ID in saved snapshots.

---

## 8. CI validation

`tests/design_criteria/test_parameter_namespace.py` performs the following checks on every build:

1. **Registry-to-code consistency.** Every `parameter_id` referenced in `civil_toolbox` code must appear in this document. CI failure if any ID is referenced but not registered.
2. **Code-to-registry consistency.** Every `ParameterSchema` defined in `parameters.py` must have a row in §4.
3. **Format compliance.** Every ID matches the regex (§2.4) and starts with a canonical domain prefix (§3).
4. **No collisions.** No two entries in the registry share the same ID.
5. **No deprecated IDs in active use** (when a new project is created).

The registry file is parsed by the test (markdown table extraction). Format-breaking edits to this file will cause CI failure.

---

## 9. Examples — good and bad

### Good
- `project_design_storms_years` — domain prefix, descriptive noun, semantic plural
- `hydraulics_mannings_n_channel` — domain prefix, established noun, qualifier
- `floodplain_no_rise_tolerance_ft` — domain prefix, noun phrase, unit suffix
- `culvert_inlet_control_headwater_ft` — long but unambiguous

### Bad
- `n` — too short, no domain
- `MannignsN` — wrong case (typo + camelCase)
- `manning-n` — wrong separator
- `flow.rate.cfs` — wrong separator
- `hydraulic_mannings_n_channel` — wrong prefix (missing trailing `s` on domain — would not pass §3 lookup)
- `hydrologyAndHydraulicsMannings` — multiple domains, camelCase, no noun
- `bfe` — abbreviation; use `floodplain_base_flood_elevation_ft`

---

*End of PARAMETER_NAMESPACE.md. Companion to SPEC_civil_toolbox_app v0.2.1.*
