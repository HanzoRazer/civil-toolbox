"""Calculator domain adapters for Civil Toolbox.

Adapters connect the calculation engine to domain entities, producing
auditable CalculationResult objects that can be attached to Scenarios.

Adapters:
- RationalMethodAdapter: Peak runoff from DrainageArea + StormEvent
- TR55Adapter: Runoff depth from DrainageArea + StormEvent
- TimeOfConcentrationAdapter: Tc from FlowPath segments
- KinematicWaveAdapter: Sheet flow time from FlowPath segments
"""
