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
- Vulnerability: `cveId`, `published`, `lastModified`
- Weakness: `cweId`, `abstraction`
- AttackPattern: `capecId`
- Technique: `attackId`
- SubTechnique: `attackId`
- Tactic: `attackId`
- DefensiveTechnique: `d3fendId`
- DetectionAnalytic: `analyticId`
- DeceptionTechnique: `techniqueId` (SHIELD technique identifier)
- EngagementConcept: `activityId` / `approachId` / `goalId`
- Score: `scoreId`, `version`, `baseScore`

## Relationship Types (canonical)

- `AFFECTS`: (Vulnerability)-[:AFFECTS]->(PlatformConfiguration)
- `HAS_CONFIGURATION`: (Vulnerability)-[:HAS_CONFIGURATION]->(VulnerabilityConfiguration)
- `HAS_NODE`: (VulnerabilityConfiguration)-[:HAS_NODE]->(VulnerabilityConfigurationNode)
- `MATCHES_CRITERIA`: (VulnerabilityConfigurationNode)-[:MATCHES_CRITERIA]->(PlatformConfiguration)
- `CAUSED_BY`: (Vulnerability)-[:CAUSED_BY]->(Weakness)
- `HAS_SCORE`: (Vulnerability)-[:HAS_SCORE]->(Score)
- `REFERENCES`: (Vulnerability)-[:REFERENCES]->(Reference)
- `EXPLOITED_BY`: (Weakness)-[:EXPLOITED_BY]->(AttackPattern)
- `IMPLEMENTED_AS`: (AttackPattern)-[:IMPLEMENTED_AS]->(Technique)
- `PART_OF`: (Technique)-[:PART_OF]->(Tactic)
- `SUBTECHNIQUE_OF`: (SubTechnique)-[:SUBTECHNIQUE_OF]->(Technique)
- `MITIGATED_BY`: (Technique)-[:MITIGATED_BY]->(DefensiveTechnique)
- `DETECTED_BY`: (Technique)-[:DETECTED_BY]->(DetectionAnalytic)
- `COUNTERED_BY`: (Technique)-[:COUNTERED_BY]->(DeceptionTechnique)
- `DISRUPTS`: (EngagementConcept)-[:DISRUPTS]->(Technique)

## Constraints & Indexes

- Unique constraints on external IDs: `cpeUri`, `matchCriteriaId`, `cveId`, `cweId`, `capecId`, `attackId`, `d3fendId`, `analyticId`, `scoreId`, plus SHIELD/ENGAGE module identifiers (`techniqueId`, `tacticId`, `opportunityId`, `useCaseId`, `procedureId`, `activityId`, `approachId`, `goalId`, `refId`, `eav_id`).
- `uri` indexes exist for resource resolution where applicable.

## Traversal Invariants (agent requirements)

1. Causal chain MUST be followed: PlatformConfiguration ← Vulnerability → Weakness → AttackPattern → Technique → {DefensiveTechnique, DetectionAnalytic, DeceptionTechnique, EngagementConcept}.
2. No direct shortcuts are allowed (e.g., PlatformConfiguration → Weakness without passing through Vulnerability).
3. Agents must use parameterized, read-only Cypher templates supplied by the orchestrator; freeform Cypher is disallowed.
4. Every response must include `provenance` (list of source IDs and sources) and `confidence` (object per `docs/05-agents/confidence-model/spec.md`).
5. `AFFECTS` is a compatibility projection over vulnerable applicability leaves, not the complete CVE boolean expression.

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
