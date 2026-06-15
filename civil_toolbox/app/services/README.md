# App Services Layer

**Status:** Scaffold only in Phase A. No implementations yet.

## Layering rule

Services orchestrate workflow. They are the **only** layer permitted to call
both the kernel calculators/adapters and the app persistence layer in the same
operation.

```text
API / UI routes
      │  (thin: parse request, call a service, render response)
      ▼
Services            ← orchestration lives here (Phase B+)
      │
      ├─► Kernel adapters → calculators → CalculationResult   (engineering truth)
      └─► Repositories → mappers → SQLAlchemy rows            (storage)
```

### Rules

1. **Routes do not call calculators directly.** A route calls a service; the
   service calls the kernel. (Phase B enforces this; Phase A has no calc calls.)
2. **Services do not contain engineering math.** Math lives in kernel
   calculators. Services orchestrate, they do not compute.
3. **Services do not contain SQL.** Persistence goes through repositories.
4. **Kernel never imports services** (or anything else under `app/`). Enforced
   by `tests/app/test_kernel_app_boundary.py`.

## Why this is empty in Phase A

Phase A is project setup, defaults, and audit — no calculation integration. The
first real service arrives in Phase B (`app-layer-phase-b-calculation-integration`),
wiring `App Services → Domain Adapters → Calculators → CalculationResult →
Audit/Revision`. The directory and rule are committed now so that wiring has a
documented home and does not leak into routes.
