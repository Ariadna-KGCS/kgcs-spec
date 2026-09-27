# Agent-Consumable Schema

## Purpose

Provide a machine- and human-readable summary of the Neo4j labels, key properties, relationship types, and traversal invariants that agents consume. This document is the canonical source for agent implementers and integration tests.

## Scope

- Node labels and required key properties
- Canonical relationship names and directionality
- Traversal invariants and query safety requirements
- Example JSON Schema snippet for agent responses

## Labels & Key Properties

- Platform: `cpeUri`, `cpeNameId`, `part`, `vendor`, `product`, `version`
- PlatformConfiguration: `matchCriteriaId`, `criteria`, version-bound fields, `configStatus`
- Vulnerability: `cveId`, `published`, `lastModified` — `published` and `lastModified` are stored as ISO-8601 **strings** exactly as NVD delivers them (e.g. `2024-01-15T10:00:00.000`), not as Neo4j temporal values. `WHERE v.published >= datetime('2024-01-01')` silently returns 0 rows; compare string against string (`WHERE v.published >= '2024-01-01'`). The OWL/SHACL type stays `xsd:dateTime` (semantic layer); the divergence is recorded in `shapes/README.md`.
- VulnerabilityConfiguration: `vcId`, `operator`, `negate` (NVD applicability layer; `cve-applicability-v1.0.owl`, v1.1)
- VulnerabilityConfigurationNode: `vcnId`, `operator`, `negate` (v1.1)
- Weakness: `cweId`, `abstraction`; **v1.1 enrichment** (`cwe-enrichment-v1.0.owl`, requires the enrichment-aware `load_cwe.py`): `description`, `mappingUsage`, `structure`, `status` required; `extendedDescription`, `mappingReasons`, `alternateTerms`, `likelihoodOfExploit`, `functionalAreas`, `affectedResources`, `modesOfIntroduction`, `ordinalities` optional
- AttackPattern: `capecId`
- Consequence: `consequenceId`, `scopes`, `impacts`, `likelihood`, `note` (**v1.1**, ADR-0001 sub-node of Weakness or AttackPattern; requires the consequence-aware loaders; leaf annotation, never a hop)
- Technique: `attackId`, `domains` (string list with one element in the current graph; values `enterprise` / `mobile` / `ics`, the short form of STIX `x_mitre_domains` `enterprise-attack` / `mobile-attack` / `ics-attack`, written by `load_attck.py`; OWL `attack:domain`; required since v1.1)
- SubTechnique: `attackId`, `domains` (v1.1)
- Tactic: `attackId`, `phaseName` (label, **not a key**: shared across matrices), `domains` (v1.1)
- DefensiveTechnique: `d3fendId`
- DetectionAnalytic: `analyticId`
- DeceptionTechnique: `techniqueId` (SHIELD technique identifier)
- EngagementConcept: `activityId` / `approachId` / `goalId`
- Score: `scoreId`, `version`, `baseScore`
- BuildMetadata: `specVersion`, `buildTimestamp`, `pipelineCommit`, `sourceSnapshots` (**v1.1**, `build-metadata-v1.0.owl`; exactly one node per graph, written by the loader at load time; not part of the chain). `sourceSnapshots` holds at most one `<SOURCE>=<release>` value per standard, naming the exact release loaded (`CAPEC=3.9`, `CWE=4.20`, `D3FEND=1.3.0`, and a single `ATTCK` key with a deterministic value: if all three bundles (enterprise, mobile, ics) carry an `x-mitre-collection` object with the same `x_mitre_version`, that release (`ATTCK=18.1`); otherwise `ATTCK=download:<date>;modified-max:<max modified across the three bundles>`. The `x-mitre-matrix` `x_mitre_version` (2.0 / 1.0) is that object's own version, not the ATT&CK release, and is never used. Today's STIX 2.0 bundles carry no `x-mitre-collection`, so the value is `ATTCK=download:2026-09-06;modified-max:2026-08-04`). **v1.2:** two more keys, `KEV=<catalogVersion>` (e.g. `KEV=2026.09.25`) and `EPSS=<scoreDate>;model:<modelVersion>` (e.g. `EPSS=2026-09-27;model:v2026.06.15`); SSVC is covered by `CVE=` (`shapes/build.shacl.ttl` v1.2)
- KevEntry (**v1.2**, ADR-0003, `decision-extension-v1.0.owl`; requires `load_kev.py`): `cveId` (unique on the label; exactly one entry per CVE), `vendorProject`, `product`, `vulnerabilityName`, `dateAdded`, `shortDescription`, `requiredAction`, `dueDate` (required; dates are `YYYY-MM-DD` strings, compare string to string); `knownRansomwareCampaignUse` (`Known` / `Unknown`), `forensicTriage` (`Yes` / `No`, BOD 26-04), `notes`, `cwes` (string list — strings only, never edges to Weakness) optional; `catalogVersion`, `dateReleased` = the catalog file it was loaded from. Leaf adhered to Vulnerability; refreshed in place from the current catalog
- EpssScore (**v1.2**, ADR-0003; requires `load_epss.py`): `epssId` (`<cveId>::EPSS::<scoreDate>`, unique), `cveId`, `score` (FIRST `epss`, decimal in [0, 1], verbatim precision), `percentile` ([0, 1]), `scoreDate` (`YYYY-MM-DD` string), `scoreTimestamp`, `modelVersion` (e.g. `v2026.06.15`; scores of different model versions are not comparable). One node per CVE per score date, **never overwritten**; not a CVSS `Score`. Leaf adhered to Vulnerability; a published datum, never an input to KGCS confidence
- SsvcDecision (**v1.2**, ADR-0003; requires `load_ssvc.py`, read from the NVD JSON `metrics.ssvcV203[]`): `ssvcId` (`<cveId>::SSVC::<timestamp>`, unique), `cveId`, `version` (`2.0.3`), `timestamp` (verbatim string), `exploitation` (`none` / `poc` / `active`), `automatable` (`no` / `yes`), `technicalImpact` (`partial` / `total`), `role` (`CISA Coordinator`), `source` (NVD source identifier), `sourceRole` (`adp` only in v1.2: declared ADPs, today CISA ADP `134c704f-9b21-4f2e-91b3-4a467353bcc0`). One node per CVE per ADP timestamp; exact duplicates in the feed collapse. Leaf adhered to Vulnerability

## Relationship Types (canonical)

- `AFFECTS`: (Vulnerability)-[:AFFECTS]->(PlatformConfiguration)
- `MATCHES_PLATFORM`: (PlatformConfiguration)-[:MATCHES_PLATFORM]->(Platform) — OWL `cpe:matchesPlatform`; CPEMatch expansion written by `load_cpe.py` (was missing from this list)
- `HAS_CONFIGURATION`: (Vulnerability)-[:HAS_CONFIGURATION]->(VulnerabilityConfiguration)
- `HAS_NODE`: (VulnerabilityConfiguration)-[:HAS_NODE]->(VulnerabilityConfigurationNode)
- `MATCHES_CRITERIA`: (VulnerabilityConfigurationNode)-[:MATCHES_CRITERIA]->(PlatformConfiguration)
- `CAUSED_BY`: (Vulnerability)-[:CAUSED_BY]->(Weakness) — exactly one edge per (CVE, CWE) pair. **v1.1 edge properties** (ADR-0002, `cve-weakness-provenance-v1.0.owl`; requires the provenance-aware `load_cwe.py`, which writes `CAUSED_BY`): `sources` (raw NVD `weaknesses[].source` identifiers, e.g. `nvd@nist.gov`, a CNA's, or `134c704f-9b21-4f2e-91b3-4a467353bcc0`), `sourceRoles` (`nvd`, `cna` or `adp`; `adp` = a declared ADP identifier, list in `mappings/cve-to-owl-v1.0.md`), `types` (`Primary` or `Secondary`) — string lists, index-aligned, one entry per assigning source, equal length. Lists because Neo4j has no map-valued properties. Edges from pre-v1.1 loaders carry none of the three (SHACL Warning, not an error).
- `HAS_SCORE`: (Vulnerability)-[:HAS_SCORE]->(Score)
- `REFERENCES`: (Vulnerability)-[:REFERENCES]->(Reference)
- `DEMONSTRATED_BY`: (Weakness)-[:DEMONSTRATED_BY]->(AttackPattern) — OWL `kgcs:exploited_by`; the graph edge name is `DEMONSTRATED_BY` (`load_capec.py`, SH-CORE-04). v1.0 of this document listed it as `EXPLOITED_BY`, a name no loader writes.
- `CHILD_OF`: (AttackPattern)-[:CHILD_OF]->(AttackPattern) — OWL `capec:childOf`; CAPEC abstraction hierarchy used by `inherited_via_parent_capec` mappings
- `IMPLEMENTS`: (AttackPattern)-[:IMPLEMENTS]->(Technique) — OWL `kgcs:implemented_as` (naming layers are not 1:1); written by `load_attck.py` for parent techniques only, SH-CORE-05. v1.0 of this document listed it as `IMPLEMENTED_AS`, a name no loader writes.
- `PART_OF`: (Technique)-[:PART_OF]->(Tactic) — tactic resolved by `attackId` within the same STIX bundle, never by `phaseName` alone; since v1.1 always within one ATT&CK domain (invariant 7)
- `SUBTECHNIQUE_OF`: (SubTechnique)-[:SUBTECHNIQUE_OF]->(Technique)
- `MITIGATED_BY`: (Technique)-[:MITIGATED_BY]->(DefensiveTechnique)
- `DETECTED_BY`: (Technique)-[:DETECTED_BY]->(DetectionAnalytic)
- `COUNTERED_BY`: (Technique)-[:COUNTERED_BY]->(DeceptionTechnique)
- `DISRUPTS`: (EngagementConcept)-[:DISRUPTS]->(Technique)
- `HAS_CONSEQUENCE`: (Weakness)-[:HAS_CONSEQUENCE]->(Consequence), (AttackPattern)-[:HAS_CONSEQUENCE]->(Consequence) (**v1.1**, ADR-0001)
- `HAS_KEV_ENTRY`: (Vulnerability)-[:HAS_KEV_ENTRY]->(KevEntry) — OWL `kev:has_kev_entry`; at most one per Vulnerability (**v1.2**, ADR-0003)
- `HAS_EPSS`: (Vulnerability)-[:HAS_EPSS]->(EpssScore) — OWL `epss:has_epss`; one per score date loaded (**v1.2**, ADR-0003)
- `HAS_SSVC`: (Vulnerability)-[:HAS_SSVC]->(SsvcDecision) — OWL `ssvc:has_ssvc`; one per ADP timestamp (**v1.2**, ADR-0003)

The three v1.2 edges are the **only** edges that may touch a `KevEntry`, `EpssScore` or `SsvcDecision`: no edge leaves them and no other edge reaches them (`shapes/decision.shacl.ttl`, closed shapes + adherence guards). In particular KEV `cwes` never becomes `CAUSED_BY`.

## Constraints & Indexes

- Unique constraints on external IDs: `cpeUri`, `matchCriteriaId`, `cveId`, `cweId`, `capecId`, `attackId`, `d3fendId`, `analyticId`, `scoreId`, `vcId`, `vcnId`, `consequenceId` (v1.1), `KevEntry.cveId`, `epssId`, `ssvcId` (v1.2), plus SHIELD/ENGAGE module identifiers (`techniqueId`, `tacticId`, `opportunityId`, `useCaseId`, `procedureId`, `activityId`, `approachId`, `goalId`, `refId`, `eav_id`).
- `uri` indexes exist for resource resolution where applicable.

## Traversal Invariants (agent requirements)

1. Causal chain MUST be followed: PlatformConfiguration ← Vulnerability → Weakness → AttackPattern → Technique → {DefensiveTechnique, DetectionAnalytic, DeceptionTechnique, EngagementConcept}.
2. No direct shortcuts are allowed (e.g., PlatformConfiguration → Weakness without passing through Vulnerability).
3. Agents must use parameterized, read-only Cypher templates supplied by the orchestrator; freeform Cypher is disallowed.
4. Every response must include `provenance` (list of source IDs and sources) and `confidence` (object per the confidence-model spec maintained in `kgcs-server`; the envelope shape is `contracts/agent-consumable-schema.json`).
5. `AFFECTS` is a compatibility projection over vulnerable applicability leaves, not the complete CVE boolean expression. The full expression is the applicability layer `HAS_CONFIGURATION → HAS_NODE → MATCHES_CRITERIA {vulnerable}` (`mappings/cve-applicability-to-owl-v1.0.md`); it refines the Vulnerability → PlatformConfiguration hop and is never presented as a hop of the chain.
6. `Consequence` nodes are leaf annotations: no template may traverse through one (ADR-0001).
7. `PART_OF` and `SUBTECHNIQUE_OF` never cross ATT&CK domains: every domain of the target Tactic is one of the Technique's `domains` (`attck.shacl.ttl` v1.1, `attack:PartOfDomainCoherenceShape`), and a SubTechnique shares a domain with its parent (`attack:SubtechniqueOfDomainCoherenceShape`). Graphs loaded before the loader fix violate this (59% spurious `PART_OF` on the 2026-09-26 snapshot); do not group by tactic on such a graph.
8. `CAUSED_BY` provenance is edge metadata, not a hop: filter on it (`WHERE 'nvd' IN r.sourceRoles`), never materialise it as nodes on the traversal path (ADR-0002).
9. `KevEntry`, `EpssScore` and `SsvcDecision` are leaf annotations of the Vulnerability hop (ADR-0003): read them with `OPTIONAL MATCH (v)-[:HAS_KEV_ENTRY|HAS_EPSS|HAS_SSVC]->(d)` from the Vulnerability, never traverse through them, never draw an edge from them to CWE, CAPEC, ATT&CK or a defensive standard. `EpssScore.score` is a published datum reported with its `scoreDate` and `modelVersion`; it is not an input to `confidence` and no template computes with it. The latest EPSS is `ORDER BY e.scoreDate DESC LIMIT 1`; the latest SSVC decision is `ORDER BY s.timestamp DESC LIMIT 1`.

## Example Agent Response JSON Schema (excerpt)

```json
{
  "$id": "https://kgcs.example/schema/agent-response.json",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["version","correlation_id","status","data","provenance","confidence"],
  "properties": {
    "version": { "type": "string" },
    "correlation_id": { "type": "string", "format": "uuid" },
    "status": { "type": "string", "enum": ["ok","empty","error"] },
    "data": { "type": ["object","array"] },
    "provenance": { "type": "array", "items": { "type":"object" } },
    "confidence": { "type": "object" }
  }
}
```

## Example Neo4j Index Creation (reference)

```cypher
CREATE CONSTRAINT unique_cve IF NOT EXISTS ON (v:Vulnerability) ASSERT v.cveId IS UNIQUE;
CREATE CONSTRAINT unique_cpe IF NOT EXISTS ON (p:Platform) ASSERT p.cpeUri IS UNIQUE;
```

## Recommended Machine Artifact

Deliver a JSON Schema enumerating required node labels and their key properties and a small TSV mapping of relationship names to semantics for automated validation in agents. (See `contracts/agent-consumable-schema.json` — the envelope is normative; since v1.1 its `definitions.CausedByEdgeProperties` gives the machine-readable form of the `CAUSED_BY` edge properties, and since v1.2 `definitions.KevEntryProperties`, `EpssScoreProperties` and `SsvcDecisionProperties` give the node properties of the decision leaves. The full label/relationship schema is still to be generated.)
