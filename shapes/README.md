KGCS SHACL Shapes
==================

This folder contains SHACL shape files that validate the KGCS OWL ontology (schema-level TBox consistency) and enforce core causal-chain invariants. Each file uses real KGCS namespace prefixes — no placeholder namespaces.

## Shape Files

| File | Validates |
|---|---|
| `core.shacl.ttl` | Causal-chain invariants (SH-CORE-01 through SH-CORE-07): AFFECTS target, no shortcut edges, relationship directions |
| `cpe.shacl.ttl` | Platform (cpeUri CPE 2.3 pattern, cpeNameId UUID), PlatformConfiguration (matchCriteriaId UUID, criteria CPE 2.3 pattern) |
| `cve.shacl.ttl` (v1.1) | Vulnerability (cveId pattern, published, source), Reference (referenceUrl); NVD applicability layer: VulnerabilityConfiguration / VulnerabilityConfigurationNode keys, exactly one HAS_NODE parent, MATCHES_PLATFORM targets resolve to canonical Platforms, every AFFECTS backed by a non-negated vulnerable leaf (SHACL-SPARQL) — one to one with the pipeline post-load checks |
| `cvss.shacl.ttl` | Score (scoreId, version enum, baseScore range 0.0–10.0) |
| `cwe.shacl.ttl` (v1.2) | Weakness (cweId pattern, abstraction enum; v1.1 enrichment properties with XSD-required fields `minCount 1` and enum facets), Consequence sub-nodes (v1.2, ADR-0001, CWE 25-value impact vocabulary) |
| `capec.shacl.ttl` (v1.1) | AttackPattern (capecId pattern, name), Consequence sub-nodes (ADR-0001, CAPEC 10-value impact vocabulary) |
| `attck.shacl.ttl` | Technique (attackId T####, PART_OF minCount), SubTechnique (T####.###, SUBTECHNIQUE_OF cardinality), Tactic (TA####, phaseName) |
| `d3fend.shacl.ttl` | DefensiveTechnique (d3fendId `D3-*` pattern as Warning — loader fallback exists, name) |
| `car.shacl.ttl` | DetectionAnalytic (analyticId pattern CAR-####-##-###, title) |
| `shield.shacl.ttl` | DeceptionTechnique (techniqueId DTE####, name) |
| `engage.shacl.ttl` | EngagementConcept (at least one of: activityId EAC/SAC, approachId EAP/SAP, goalId EGO/SGO — all patterned) |
| `build.shacl.ttl` | BuildMetadata (specVersion semver, buildTimestamp, pipelineCommit hex, sourceSnapshots `<SOURCE>=<snapshot>`) |

## Key Invariants (core.shacl.ttl)

- `SH-CORE-01`: `AFFECTS` must target `PlatformConfiguration`, never `Platform` directly.
- `SH-CORE-02`: No direct `Vulnerability → Technique` shortcut (must go through CWE → CAPEC).
- `SH-CORE-03`: `CAUSED_BY` must target `Weakness`.
- `SH-CORE-04`: `exploited_by` (graph: `DEMONSTRATED_BY`) source must be `Weakness`.
- `SH-CORE-05`: `IMPLEMENTS` source must be `AttackPattern`.
- `SH-CORE-06`: Every `Technique` has at least one `PART_OF` edge to a `Tactic`.
- `SH-CORE-07`: Every `SubTechnique` has exactly one `SUBTECHNIQUE_OF` parent.

## v1.1 Candidates — D3FEND semantic constraints

`d3fend.shacl.ttl` v1.0 validates identity only (`d3fendId`, `name`). Design intent from an exploratory draft (archived in `kgcs-research/notes/d3fend-shacl-shapes-v1.0-draft.md`) proposes semantic constraints for a future `d3fend.shacl.ttl` v1.1:

- `countersTechnique`: every DefensiveTechnique must counter >= 1 ATT&CK Technique.
- `producesEffect`: mandatory, from a controlled DefensiveEffect vocabulary (Detect, Prevent, Delay, Degrade, Disrupt, Contain, Restore, Reveal).
- `actsOnArtifact`: mandatory reference to a concrete DigitalArtifact.
- Forbidden direct links: DefensiveTechnique -> Vulnerability/Weakness/AttackPattern (complements SH-CORE shortcut rules on the defensive side).

Any v1.1 implementation must use canonical KGCS namespaces and valid SHACL (the draft used placeholder prefixes and non-standard `sh:path ?p` patterns). New versioned file; v1.0 stays frozen.

## Alignment modules and inference mode (v1.1)

Two cross-cutting modules in `ontology/extensions/` make the shapes resolvable without touching any frozen file:

- `graph-labels-v1.0.owl` declares the seven label properties the loaders set and the shapes constrain but no v1.0 module declared (`attack:name`, `attack:phaseName`, `car:title`, `cve:referenceUrl`, `d3fend:name`, `engage:name`, `shield:name`). Every `sh:path` now resolves to a declared OWL term (`tests/test_shapes.py::test_every_shape_reference_resolves_to_declared_owl_term`).
- `attck-core-alignment-v1.0.owl` asserts `attack:Technique ≡ kgcs:Technique`, `attack:Tactic ≡ kgcs:Tactic`, `attack:contains_by ≡ kgcs:belongs_to` (same direction in both frozen files) and `attack:subtechnique_of ⊑ kgcs:subtechnique_of`. Without it, `attck.shacl.ttl` and SH-CORE-06/07 (`sh:class attack:*`) contradict SH-CORE-05 (`sh:class kgcs:Technique`) on any single-typed node.

The alignment only takes effect under materialisation. The harness fixes the mode: OWL-RL closure over *data + alignment modules only*, then pySHACL with `inference="none"` (`tests/conftest.py`, `INFERENCE_MODE = "alignment-owlrl"`). Full RDFS/OWL-RL over the frozen TBox is not usable: `attack:attackId` carries eleven `rdfs:domain` classes, so every subject of `attackId` would be inferred a Technique, a Tactic, a Group … and every `TechniqueShape` constraint would fire on Tactics. Consumers validating exported graph data must reproduce this mode.

## Known v1.0 deviations (recorded, not fixed — successors only)

- `capec:capecId`: OWL v1.0 range `xsd:integer`; KGCS IDs are patterned strings (`CVE-`, `CWE-`, `T####`, `D3-`, `CAR-`, `DTE####`, `CAPEC-`), the ETL builds `"CAPEC-<n>"` and `capec.shacl.ttl` enforces `^CAPEC-\d+$`. Allow-listed in `tests/test_shapes.py` (`DATATYPE_DEVIATIONS`); fix = `capec-ontology-v1.1.owl` successor.
- `capec:consequenceLikelihood`: frozen OWL comment lists "Always, Often, Sometimes, Rare, Unknown"; the CAPEC XSD and the shapes use High, Medium, Low, Unknown (ADR-0001). Same successor.
- `attack:SubTechnique`: the frozen ATT&CK module declares `attack:SubTechnique ⊑ attack:Technique`; the graph keeps `SubTechnique` as a separate label with no `PART_OF` and no `IMPLEMENTS`, and `attck.shacl.ttl` follows the graph (`^T\d{4}$` on Technique, `^T\d{4}\.\d{3}$` on SubTechnique). Under full OWL semantics the alignment equivalence would make sub-techniques `kgcs:Technique` and the Technique identity pattern would fail on them; the alignment module therefore asserts nothing about `attack:SubTechnique` and the harness closure excludes the frozen hierarchy. OWL v1.1 candidate: drop or re-scope the subclass axiom in an ATT&CK successor.
- SHIELD: `shield:DefensiveTechnique ⊑ kgcs:DefensiveTechnique` (frozen) while the graph label, `contracts/agent-consumable-schema.md` and `shield.shacl.ttl` use `kgcs:DeceptionTechnique` (`COUNTERED_BY`). Decided 2026-09-06: document only; fix in a SHIELD successor.
- D3FEND: the frozen module declares `d3fend:references_cwe` / `d3fend:cwe_addressed_by` and `d3fend:counters_attack_pattern` / `capec_referenced_by` (DefensiveTechnique ↔ Weakness / AttackPattern). No loader writes them, and the archived D3FEND draft would forbid exactly these links. Whether they are the "third-party curated edge with explicit provenance" exception or forbidden shortcuts is an open policy call; the D3FEND v1.1 shapes (above) depend on it.
- Engage and SHIELD modules embed example individuals inside the TBox (`engage:EGO0001`, `engage:EAP0001`, `engage:EAC0001`, `shield:DTE0001`, `shield:DTA0001`, `shield:DOS0027`, `shield:DUC0040`, `shield:DPR0001`). `engage:EAC0001` lacks `engage:name` and yields one pre-existing `sh:Warning` when the OWL files are validated as data (`tests/test_shapes.py::test_tbox_as_data_has_no_violations` tolerates exactly that one Warning).

## Future design intent (from archived drafts)

Two exploratory drafts (archived in `kgcs-research/notes/shacl-constraints-draft.md` and `shacl-profiles-draft.md`) contain design intent worth considering when the corresponding extensions exist. Not implementable today — they target extensions (Incident, Risk, ThreatActor) that are not part of the frozen v1.0 baseline:

- **Extension guardrails**: evidence-backed incidents, claim-based attribution (never direct Incident -> ThreatActor), risk scores that cannot override CVSS.
- **Trust-tier SHACL profiles (SOC / Exec / AI)**: same graph, different validation contracts per consumer — SOC requires evidence and high confidence; Exec allows aggregated attribution with mandatory rationale; AI forbids cross-extension jumps and unanchored risk.

Caution: the constraints draft reuses IDs SH-CORE-01..03 with *different* semantics than the normative `core.shacl.ttl` shapes above. Any future adoption must assign fresh IDs (e.g. SH-INC-*, SH-RISK-*, SH-TA-*, SH-TRUST-*) and use canonical KGCS namespaces.

## Naming layers (OWL vs graph)

KGCS uses two naming layers: OWL properties are snake_case (`kgcs:exploited_by`, `attack:contains_by`, `attack:subtechnique_of`) while Neo4j relationships are SCREAMING_CASE (`DEMONSTRATED_BY`, `PART_OF`, `SUBTECHNIQUE_OF`). SHACL `sh:path` values must use the OWL names; shape messages may reference the graph names. Graph-layer node properties (`name`, `title`, `referenceUrl`, `phaseName`) are declared by `ontology/extensions/graph-labels-v1.0.owl` since v1.1. Edge properties (`MATCHES_CRITERIA.vulnerable`) have no plain-triple form: `cve-applicability-v1.0.owl` maps them to sub-properties.

## Running Validation

In this repo (spec self-validation, no graph needed):

```bash
pip install -r requirements-dev.txt
python -m pytest            # parse, meta-SHACL, alignment, contracts, ABox fixture + negatives, doc links
```

Validating the OWL files alone as data is vacuous — the TBox holds (almost) no instances, so `sh:targetClass` shapes never bind. The harness therefore validates `tests/fixtures/kgcs-abox.ttl` (one individual per node shape; `test_every_node_shape_has_a_focus_node_in_fixture` fails if any shape has none) and every mutation in `tests/fixtures/negative/` against the results listed in `manifest.json`. A new shape is not done until it has a focus node and a negative case.

In `kgcs-pipeline` (pinned spec copy + live graph):

```bash
python validation/validate_all_standards.py                 # shapes vs spec/ontology (TBox)
python validation/validate_all_standards.py --standard attck
python validation/validate_all_standards.py --post-load     # Cypher integrity checks (requires Neo4j)
```
