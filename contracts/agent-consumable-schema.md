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
- Technique: `attackId`
- SubTechnique: `attackId`
- Tactic: `attackId`
- DefensiveTechnique: `d3fendId`
- DetectionAnalytic: `analyticId`
- DeceptionTechnique: `techniqueId` (SHIELD technique identifier)
- EngagementConcept: `activityId` / `approachId` / `goalId`
- Score: `scoreId`, `version`, `baseScore`
- BuildMetadata: `specVersion`, `buildTimestamp`, `pipelineCommit`, `sourceSnapshots` (**v1.1**, `build-metadata-v1.0.owl`; exactly one node per graph, written by the loader at load time; not part of the chain)

## Relationship Types (canonical)

- `AFFECTS`: (Vulnerability)-[:AFFECTS]->(PlatformConfiguration)
- `MATCHES_PLATFORM`: (PlatformConfiguration)-[:MATCHES_PLATFORM]->(Platform) — OWL `cpe:matchesPlatform`; CPEMatch expansion written by `load_cpe.py` (was missing from this list)
- `HAS_CONFIGURATION`: (Vulnerability)-[:HAS_CONFIGURATION]->(VulnerabilityConfiguration)
- `HAS_NODE`: (VulnerabilityConfiguration)-[:HAS_NODE]->(VulnerabilityConfigurationNode)
- `MATCHES_CRITERIA`: (VulnerabilityConfigurationNode)-[:MATCHES_CRITERIA]->(PlatformConfiguration)
- `CAUSED_BY`: (Vulnerability)-[:CAUSED_BY]->(Weakness)
- `HAS_SCORE`: (Vulnerability)-[:HAS_SCORE]->(Score)
- `REFERENCES`: (Vulnerability)-[:REFERENCES]->(Reference)
- `DEMONSTRATED_BY`: (Weakness)-[:DEMONSTRATED_BY]->(AttackPattern) — OWL `kgcs:exploited_by`; the graph edge name is `DEMONSTRATED_BY` (`load_capec.py`, SH-CORE-04). v1.0 of this document listed it as `EXPLOITED_BY`, a name no loader writes.
- `CHILD_OF`: (AttackPattern)-[:CHILD_OF]->(AttackPattern) — OWL `capec:childOf`; CAPEC abstraction hierarchy used by `inherited_via_parent_capec` mappings
- `IMPLEMENTS`: (AttackPattern)-[:IMPLEMENTS]->(Technique) — OWL `kgcs:implemented_as` (naming layers are not 1:1); written by `load_attck.py` for parent techniques only, SH-CORE-05. v1.0 of this document listed it as `IMPLEMENTED_AS`, a name no loader writes.
- `PART_OF`: (Technique)-[:PART_OF]->(Tactic)
- `SUBTECHNIQUE_OF`: (SubTechnique)-[:SUBTECHNIQUE_OF]->(Technique)
- `MITIGATED_BY`: (Technique)-[:MITIGATED_BY]->(DefensiveTechnique)
- `DETECTED_BY`: (Technique)-[:DETECTED_BY]->(DetectionAnalytic)
- `COUNTERED_BY`: (Technique)-[:COUNTERED_BY]->(DeceptionTechnique)
- `DISRUPTS`: (EngagementConcept)-[:DISRUPTS]->(Technique)
- `HAS_CONSEQUENCE`: (Weakness)-[:HAS_CONSEQUENCE]->(Consequence), (AttackPattern)-[:HAS_CONSEQUENCE]->(Consequence) (**v1.1**, ADR-0001)

## Constraints & Indexes

- Unique constraints on external IDs: `cpeUri`, `matchCriteriaId`, `cveId`, `cweId`, `capecId`, `attackId`, `d3fendId`, `analyticId`, `scoreId`, `vcId`, `vcnId`, `consequenceId` (v1.1), plus SHIELD/ENGAGE module identifiers (`techniqueId`, `tacticId`, `opportunityId`, `useCaseId`, `procedureId`, `activityId`, `approachId`, `goalId`, `refId`, `eav_id`).
- `uri` indexes exist for resource resolution where applicable.

## Traversal Invariants (agent requirements)

1. Causal chain MUST be followed: PlatformConfiguration ← Vulnerability → Weakness → AttackPattern → Technique → {DefensiveTechnique, DetectionAnalytic, DeceptionTechnique, EngagementConcept}.
2. No direct shortcuts are allowed (e.g., PlatformConfiguration → Weakness without passing through Vulnerability).
3. Agents must use parameterized, read-only Cypher templates supplied by the orchestrator; freeform Cypher is disallowed.
4. Every response must include `provenance` (list of source IDs and sources) and `confidence` (object per the confidence-model spec maintained in `kgcs-server`; the envelope shape is `contracts/agent-consumable-schema.json`).
5. `AFFECTS` is a compatibility projection over vulnerable applicability leaves, not the complete CVE boolean expression. The full expression is the applicability layer `HAS_CONFIGURATION → HAS_NODE → MATCHES_CRITERIA {vulnerable}` (`mappings/cve-applicability-to-owl-v1.0.md`); it refines the Vulnerability → PlatformConfiguration hop and is never presented as a hop of the chain.
6. `Consequence` nodes are leaf annotations: no template may traverse through one (ADR-0001).

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

Deliver a JSON Schema enumerating required node labels and their key properties and a small TSV mapping of relationship names to semantics for automated validation in agents. (See `contracts/agent-consumable-schema.json` — to be generated.)
