KGCS SHACL Shapes
==================

This folder contains SHACL shape files that validate the KGCS OWL ontology (schema-level TBox consistency) and enforce core causal-chain invariants. Each file uses real KGCS namespace prefixes — no placeholder namespaces.

## Shape Files

| File | Validates |
|---|---|
| `core.shacl.ttl` | Causal-chain invariants (SH-CORE-01 through SH-CORE-07): AFFECTS target, no shortcut edges, relationship directions |
| `cpe.shacl.ttl` | Platform (cpeUri CPE 2.3 pattern, cpeNameId UUID), PlatformConfiguration (matchCriteriaId UUID, criteria CPE 2.3 pattern) |
| `cve.shacl.ttl` | Vulnerability (cveId pattern, published, source), Reference (referenceUrl) |
| `cvss.shacl.ttl` | Score (scoreId, version enum, baseScore range 0.0–10.0) |
| `cwe.shacl.ttl` | Weakness (cweId pattern, abstraction enum) |
| `capec.shacl.ttl` | AttackPattern (capecId pattern, name) |
| `attck.shacl.ttl` | Technique (attackId T####, PART_OF minCount), SubTechnique (T####.###, SUBTECHNIQUE_OF cardinality), Tactic (TA####, phaseName) |
| `d3fend.shacl.ttl` | DefensiveTechnique (d3fendId `D3-*` pattern as Warning — loader fallback exists, name) |
| `car.shacl.ttl` | DetectionAnalytic (analyticId pattern CAR-####-##-###, title) |
| `shield.shacl.ttl` | DeceptionTechnique (techniqueId DTE####, name) |
| `engage.shacl.ttl` | EngagementConcept (at least one of: activityId EAC/SAC, approachId EAP/SAP, goalId EGO/SGO — all patterned) |

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

## v1.1 Candidates — OWL label properties

Seven shape paths reference graph-layer node properties with no OWL datatype property behind them: `attack:name`, `attack:phaseName`, `car:title`, `cve:referenceUrl`, `d3fend:name`, `engage:name`, `shield:name`. The Neo4j loaders set these on every node, but the frozen v1.0 OWLs never declared them, so these constraints only bind against future ABox/graph-exported data. Candidate for OWL v1.1: declare these as datatype properties (or standardize on `rdfs:label`) so the SHACL constraints become enforceable at the OWL layer.

Also for OWL v1.1: change `capec:capecId` range from `xsd:integer` to `xsd:string` (and update `mappings/capec-to-owl-v1.0.md` accordingly in its versioned successor). KGCS design decision: all standard IDs are patterned strings (`CVE-`, `CWE-`, `T####`, `D3-`, `CAR-`, `DTE####`, `CAPEC-`); the ETL builds `"CAPEC-<n>"` and `capec.shacl.ttl` enforces the pattern. The v1.0 OWL integer range is the known outlier — audits comparing shape datatypes to OWL ranges should treat this one as intentional.

## Future design intent (from archived drafts)

Two exploratory drafts (archived in `kgcs-research/notes/shacl-constraints-draft.md` and `shacl-profiles-draft.md`) contain design intent worth considering when the corresponding extensions exist. Not implementable today — they target extensions (Incident, Risk, ThreatActor) that are not part of the frozen v1.0 baseline:

- **Extension guardrails**: evidence-backed incidents, claim-based attribution (never direct Incident -> ThreatActor), risk scores that cannot override CVSS.
- **Trust-tier SHACL profiles (SOC / Exec / AI)**: same graph, different validation contracts per consumer — SOC requires evidence and high confidence; Exec allows aggregated attribution with mandatory rationale; AI forbids cross-extension jumps and unanchored risk.

Caution: the constraints draft reuses IDs SH-CORE-01..03 with *different* semantics than the normative `core.shacl.ttl` shapes above. Any future adoption must assign fresh IDs (e.g. SH-INC-*, SH-RISK-*, SH-TA-*, SH-TRUST-*) and use canonical KGCS namespaces.

## Naming layers (OWL vs graph)

KGCS uses two naming layers: OWL properties are snake_case (`kgcs:exploited_by`, `attack:contains_by`, `attack:subtechnique_of`) while Neo4j relationships are SCREAMING_CASE (`DEMONSTRATED_BY`, `PART_OF`, `SUBTECHNIQUE_OF`). SHACL `sh:path` values must use the OWL names (the validator runs against the OWL files); shape messages may reference the graph names. Some shapes also reference graph-level node properties (`name`, `title`, `referenceUrl`, `phaseName`) that have no OWL datatype property — they only bind when validating ABox/graph-exported data, not the TBox.

## Running Validation

```bash
# Validate all shapes against OWL ontology files
python scripts/validation/validate_all_standards.py

# Validate a single standard
python scripts/validation/validate_all_standards.py --standard attck

# Run post-load Cypher integrity checks (requires Neo4j)
python scripts/validation/validate_all_standards.py --post-load
```

See `pipeline-execution-guide.md` (in `kgcs-pipeline`) for full parameters.

See `rag-to-shacl.md` (in `kgcs-pipeline`) for how RAG templates map to shape groups.
