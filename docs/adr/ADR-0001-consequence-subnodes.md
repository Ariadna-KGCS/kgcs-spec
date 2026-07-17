# ADR-0001 — Consequences as sub-nodes (CWE & CAPEC)

**Status:** Accepted (2026-07-17)
**Scope:** modeling of `Common_Consequences` (CWE XSD v7.3) and `Consequences` (CAPEC XSD v3.5) in the KGCS graph
**Deciders:** Humbert Costas
**Spec artifacts:** `ontology/standards/cwe-consequences-v1.0.owl`, `ontology/standards/capec-consequences-v1.0.owl`, `shapes/cwe.shacl.ttl` v1.2, `shapes/capec.shacl.ttl` v1.1, `mappings/consequences-to-owl-v1.0.md`

## Context

Both CWE and CAPEC attach structured consequence records to their primary
entities: a repeatable group of `Scope` (1..N, enum), `Impact`
(CWE 1..N / CAPEC 0..N, enum), `Likelihood` (0..1, enum) and `Note`
(0..1, free text). The enrichment work on both standards needs a single,
consistent modeling decision before either loader is written.

Evidence measured on the real catalogs (CWE v4.20, CAPEC v3.9):

| Fact | CWE | CAPEC |
| --- | --- | --- |
| Consequence records | 1,237 (944 weaknesses) | 814 (369 patterns) |
| Multi-scope records | 36% | 38% |
| Multi-impact records | **42%** | 9% |
| Records with `Note` | **61%** | 27% |
| Records with `Likelihood` | 6% | 0.5% |
| Records with `Consequence_ID` (natural key) | **0** | **0** |
| Impact vocabulary size | 25 values | 10 values |

Three structural facts of the existing spec and graph:

1. The graph already models structured sub-records as sub-nodes with
   synthetic deterministic keys: `Score` (`scoreId`),
   `VulnerabilityConfiguration` (`vcId`), `PlatformConfiguration`
   (`matchCriteriaId`).
2. The frozen `capec-ontology-v1.0.owl` already declares
   `capec:Consequence` + `capec:hasConsequence` and the per-record
   datatype properties (`capec:scope`, `capec:technicalImpact`,
   `capec:consequenceLikelihood`).
3. The CWE side declares nothing for consequences —
   `cwe-enrichment-v1.0.owl` is node-properties-only by design.

## Decision

Model each consequence record as a **sub-node** attached to its parent
entity:

```
(:Weakness)-[:HAS_CONSEQUENCE]->(:Consequence {consequenceId, scopes, impacts, likelihood?, note?})
(:AttackPattern)-[:HAS_CONSEQUENCE]->(:Consequence {consequenceId, scopes, impacts?, likelihood?, note?})
```

- **One record = one node.** `scopes` and `impacts` are string arrays
  *inside* the sub-node, preserving exactly the grouping MITRE asserts —
  never flattened across records.
- **Synthetic deterministic key** (the `Consequence_ID` XSD attribute is
  unpopulated in both catalogs): `consequenceId = "<parentId>-C<ordinal>"`
  with the ordinal following document order (`CWE-79-C1`, `CAPEC-66-C2`).
  Same pattern family as `scoreId`/`vcId`.
- **Single graph label `:Consequence`** for both standards. Provenance is
  established by topology (which parent it hangs from); vocabularies remain
  source-separated and are validated per-standard at the OWL/SHACL layer
  (`cwe:Consequence` vs `capec:Consequence` classes).
- **Vocabularies are never normalized across standards.** CWE's 25-value
  impact enum ("Read Application Data") and CAPEC's 10-value enum
  ("Read Data") stay verbatim per source, enforced by separate `sh:in`
  facets.
- **Consequence nodes are leaf annotations, not causal-chain hops.** No
  agent query template may traverse *through* a `:Consequence` node; the
  chain `CPE → CVE/CVSS → CWE → CAPEC → ATT&CK → {…}` is unaffected.

## Alternatives considered

**A1 — Parallel arrays on the parent node** (`scopes: […]`, `impacts: […]`).
Rejected: destroys the scope×impact correlation for the ~40% of records
that are multi-valued, fabricating combinations MITRE never asserted —
the precise class of untraceable inference KGCS exists to prevent. `Note`
(61% of CWE records) has no sane home.

**A2 — Encoded record strings** (`"Confidentiality+Integrity→Read Data|note"`).
Rejected: preserves grouping but makes the data unqueryable without string
parsing in Cypher, defeats member-wise SHACL `sh:in` validation, and bloats
parent nodes with long notes. Opaque data *and* hidden semantics.

## Consequences of the decision

- **Spec:** two new versioned modules (frozen artifacts untouched):
  `cwe-consequences-v1.0.owl` (class + object property + datatype
  properties, snake_case) and `capec-consequences-v1.0.owl` (only the two
  gap properties `capec:consequence_id`, `capec:consequence_note`; class
  and enum properties already exist frozen). SHACL: `cwe.shacl.ttl` v1.2
  and `capec.shacl.ttl` v1.1 add `ConsequenceShape`s with per-standard
  vocabularies and `consequenceId` patterns.
- **Pipeline (later increment):** new uniqueness constraint on
  `Consequence.consequenceId`; loaders create sub-nodes after parent nodes,
  deduplicate in Python, and **prune ordinals beyond the current count per
  parent** on refresh (MERGE alone cannot remove records MITRE deleted).
  Post-load checks: no orphan `:Consequence`, enum membership, contiguous
  ordinals per parent.
- **Agents/contracts (later increment):** response schemas gain nested
  consequence objects; templates get membership queries
  (`'Gain Privileges' IN c.impacts`) and correlated scope×impact queries.
  Templates must treat `:Consequence` as a leaf.
- **Explorer:** `:Consequence` nodes inherit the parent standard's fixed
  color and default to hidden (leaf annotations, not chain hops).

## Known discrepancies recorded here

1. The frozen `capec-ontology-v1.0.owl` comment on
   `capec:consequenceLikelihood` lists "Always, Often, Sometimes, Rare,
   Unknown" — the CAPEC XSD `LikelihoodEnumeration` and the real catalog
   data (values observed: High, Medium) say `High, Medium, Low, Unknown`.
   The SHACL shape follows the XSD; the OWL comment is flagged as an OWL
   v1.1 candidate fix (same register as the `capec:capecId` integer range).
2. Naming layers: the new modules use snake_case OWL properties per current
   convention; the frozen CAPEC v1.0 properties on the same class are
   camelCase (`technicalImpact`). SHACL `sh:path` uses each property's
   actual OWL name. Graph-layer node properties are camelCase
   (`consequenceId`, `scopes`, `impacts`, `likelihood`, `note`) in both
   cases.
