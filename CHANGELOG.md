# Changelog — kgcs-spec

All notable changes to the KGCS standard. Consumers (`kgcs-pipeline`, `kgcs-server`) pin releases from this file's tags.

## [Unreleased]

### Fixed

- Full OWL<->SHACL alignment audit across all 10 standards. Corrected remaining contradictions: `sh:class kgcs:Tactic/kgcs:Technique` -> `attack:Tactic/attack:Technique` on `attack:contains_by`/`attack:subtechnique_of` paths (no alignment axioms exist between attack:* and core classes); `cve:published` `xsd:string` -> `xsd:dateTime` (OWL range). Seven graph-layer-only paths (`name`, `title`, `referenceUrl`, `phaseName`) documented as OWL v1.1 candidates in `shapes/README.md`. `capec:capecId` stays a patterned string (`^CAPEC-\d+$`) per KGCS design decision — all standard IDs are patterned; the OWL v1.0 `xsd:integer` range is flagged as the deviation and an OWL v1.1 candidate.

- `shapes/core.shacl.ttl`, `shapes/attck.shacl.ttl`: SHACL paths referenced nonexistent OWL terms, making SH-CORE-04/06/07 (and their attck equivalents) vacuous — they silently passed. Corrected to canonical OWL names: `kgcs:demonstrated_by` -> `kgcs:exploited_by`, `kgcs:part_of` -> `attack:contains_by`, `attack:subtechniqueOf` -> `attack:subtechnique_of`, `sh:targetClass kgcs:SubTechnique` -> `attack:SubTechnique`. Graph-layer relationship names (DEMONSTRATED_BY, PART_OF, SUBTECHNIQUE_OF) are unchanged. `rule-engine-specification-v1.0.md` needed no changes — its names were already canonical.

### Added

- **CWE enrichment module v1.0** (`ontology/standards/cwe-enrichment-v1.0.owl`): 12 new datatype properties on `kgcs:Weakness` extracted from the MITRE CWE XML catalog (XSD v7.3) — `description`, `extended_description`, `mapping_usage`, `mapping_reasons`, `structure`, `status`, `alternate_terms`, `likelihood_of_exploit`, `functional_areas`, `affected_resources`, `modes_of_introduction`, `ordinalities`. Node properties only: no new classes, no object properties, no topology change; `cwe-ontology-v1.0.owl` remains frozen and untouched. Mapping rules (StructuredText flattening, dedup, deprecated-entry policy, idempotent refresh) in `mappings/cwe-enrichment-to-owl-v1.0.md`.
- `shapes/cwe.shacl.ttl` v1.1: property shapes for the enrichment module. XSD-required fields (`description`, `mapping_usage`, `structure`, `status`) are `sh:minCount 1` — a graph loaded by a pre-enrichment loader fails validation until re-ingested with the enrichment-aware `load_cwe.py`. Enum facets constrained with `sh:in` mirroring the XSD enumerations.
- ID format patterns completed across all standards. New `sh:pattern` constraints (severity Warning): `cpe:cpeUri`/`cpe:criteria` (CPE 2.3 prefix), `cpe:cpeNameId`/`cpe:matchCriteriaId` (NVD UUID), `d3fend:d3fendId` (`^D3-[A-Z]+$`; Warning because load_d3fend.py has a documented URI-fragment fallback), `engage:approachId` (`^[ES]AP\d{4}$`), `engage:goalId` (`^[ES]GO\d{4}$`). Patterns derived from loader source contracts; raw NVD/Engage data not re-verified in this environment. Already-patterned IDs (attackId, cveId, scoreId, cweId, capecId, analyticId, techniqueId, activityId) confirmed consistent.

### Removed

- `shapes/SHACL-constraints.md`, `shapes/SHACL-profiles.md`: legacy chat-derived drafts (placeholder namespaces, SH-CORE ID collisions with `core.shacl.ttl`, dependencies on nonexistent Incident/Risk/ThreatActor extensions). Archived in `kgcs-research/notes/`; rescued design intent tracked in `shapes/README.md`.
- `shapes/d3fend-shacl-shapes-v1.0.md`: legacy chat-derived draft (placeholder `example.org` namespaces, invalid SHACL, conflicted with normative `d3fend.shacl.ttl`). Archived in `kgcs-research/notes/d3fend-shacl-shapes-v1.0-draft.md`; its design intent is tracked as v1.1 candidates in `shapes/README.md`.

## [1.0.0] — 2026-07-06

First release under the Ariadna umbrella. Content is the frozen KGCS v1.0 baseline, migrated verbatim from the seed repo (OWL artifacts byte-identical, verified by checksum).

### Included

- **Ontology (frozen):** core ontology; 10 standard modules (CPE, CVE, CVSS, CWE, CAPEC, ATT&CK, D3FEND, CAR, SHIELD, ENGAGE); asset extension.
- **Shapes:** SHACL shapes per standard, constraint/profile docs, rule-engine specification v1.0.
- **Mappings:** standard→OWL mapping docs for all 10 standards + coverage matrix.
- **Contracts:** agent-consumable graph schema (doc + JSON Schema), request schema, per-agent response schemas (systems, offensive, defensive).
- **Docs:** core and asset-extension ontology specs, namespace policy v1.0, glossary, extension guide.

### Changed vs. seed layout

- OWL files consolidated under `ontology/{core,standards,extensions}/` (flat per-standard files; contents untouched).
- JSON contracts moved from `docs/04-graph/schemas/` to `contracts/`; internal path references updated.
- `D3FEND SHACL Shapes v1.0.md` renamed to `d3fend-shacl-shapes-v1.0.md` (filename normalization only).
