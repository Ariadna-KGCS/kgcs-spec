# Consequences to OWL Mapping v1.0 (CWE & CAPEC)

Companion to `cwe-to-owl-v1.0.md` and `capec-to-owl-v1.0.md` (both frozen).
Covers only the consequence sub-node modeling introduced by
`ontology/standards/cwe-consequences-v1.0.owl` and
`ontology/standards/capec-consequences-v1.0.owl` per **ADR-0001**
(`docs/adr/ADR-0001-consequence-subnodes.md`).

## Source

- MITRE CWE XML catalog (`data/raw/CWE/cwec_v*.xml`), Core Definition XSD
  v7.3: `Weakness/Common_Consequences/Consequence`
- MITRE CAPEC XML catalog (`data/raw/CAPEC/capec_latest.xml`), Core Attack
  Pattern XSD v3.5: `Attack_Pattern/Consequences/Consequence`
- Scope: consequence records only. One record = one sub-node; the record's
  internal Scope × Impact grouping is preserved and **never flattened
  across records** (see ADR-0001 for the evidence: ~40% of records are
  multi-valued).

## Target Ontology

- CWE: `cwe:Consequence` class + `cwe:has_consequence`
  (`cwe-consequences-v1.0.owl`, all new)
- CAPEC: `capec:Consequence` + `capec:hasConsequence` + content properties
  (frozen in `capec-ontology-v1.0.owl`); gap properties
  `capec:consequence_id`, `capec:consequence_note`
  (`capec-consequences-v1.0.owl`)
- Graph: single label `:Consequence` for both standards, edge
  `HAS_CONSEQUENCE` from the parent. Provenance by topology.

## Field Mapping

| XSD source (Consequence) | OWL property (CWE) | OWL property (CAPEC) | Neo4j property | Cardinality | Vocabulary |
| --- | --- | --- | --- | --- | --- |
| — (synthetic) | `cwe:consequence_id` | `capec:consequence_id` | `consequenceId` | 1..1 | `^(CWE\|CAPEC)-\d+-C\d+$` |
| `Scope` | `cwe:scope` | `capec:scope` (frozen) | `scopes` (array) | 1..N | ScopeEnumeration (9, identical wording in both XSDs) |
| `Impact` | `cwe:technical_impact` | `capec:technicalImpact` (frozen) | `impacts` (array) | CWE 1..N / **CAPEC 0..N** | TechnicalImpactEnumeration — **CWE 25 values, CAPEC 10 values, never merged** |
| `Likelihood` | `cwe:consequence_likelihood` | `capec:consequenceLikelihood` (frozen) | `likelihood` | 0..1 | LikelihoodEnumeration (High, Medium, Low, Unknown) |
| `Note` | `cwe:consequence_note` | `capec:consequence_note` | `note` | 0..1 | StructuredText → flattened |
| `@Consequence_ID` | — | — | — | — | unpopulated in both real catalogs; not loaded |

Naming layers as per KGCS convention: SHACL `sh:path` uses each property's
actual OWL name — snake_case for the new modules, camelCase for the three
frozen CAPEC content properties (recorded mix, see ADR-0001). Neo4j node
properties are camelCase; the multi-valued record fields pluralize at the
graph layer (`scopes`, `impacts`).

## Transformation Rules

1. **Key synthesis:** `consequenceId = f"{parentId}-C{ordinal}"` with the
   ordinal counting `Consequence` elements of the parent in XML document
   order, starting at 1. Deterministic across runs on the same catalog.
2. **Record integrity:** each record's `Scope`/`Impact` values load as
   arrays *on that record's node*, deduplicated in Python preserving
   document order. Values from different records of the same parent are
   never combined.
3. **StructuredText flattening** (`Note`): same rule as
   `cwe-enrichment-to-owl-v1.0.md` — `itertext()`, collapse whitespace,
   strip; empty result → property omitted.
4. **Idempotent refresh with pruning:** nodes `MERGE` on `consequenceId`
   with `SET` for content on create and match. After loading a parent's
   records, delete that parent's `:Consequence` nodes whose ordinal exceeds
   the current record count (parameterized Cypher per parent) — `MERGE`
   alone cannot remove records MITRE deleted between catalog releases.
5. **Load order:** consequence sub-nodes load in the parent standard's ETL
   step, after the parent nodes exist (CWE step and CAPEC step
   respectively). Constraint `Consequence.consequenceId IS UNIQUE` is
   created by `init_constraints.py` before any load.
6. **Leaf annotation:** no ETL, query template, or doc may introduce edges
   *from* a `:Consequence` to anything other than its parent, and no
   traversal may pass through one. The causal chain is unaffected.

## Provenance Notes

- All content is first-party MITRE editorial data; provenance is the
  catalog version recorded by the loader plus the parent standard
  (topology).
- Scope wording is identical in both XSDs (9 values), but impact
  vocabularies differ in granularity (CWE "Read Application Data" vs CAPEC
  "Read Data"). Agents quoting consequences must attribute them to the
  standard they came from and must not treat cross-standard impact strings
  as comparable enum values.
- `likelihood` is a per-record relative editorial signal (sparse: ~6% CWE,
  ~0.5% CAPEC). It is unrelated to CWE's weakness-level
  `likelihood_of_exploit`, to CAPEC's pattern-level `attackLikelihood`,
  and to CVSS/EPSS.

## Post-load invariants (pipeline)

1. Zero orphan `:Consequence` nodes (every one has exactly one incoming
   `HAS_CONSEQUENCE`).
2. `scopes` non-empty on every node; `impacts` non-empty on every node
   whose parent is a `Weakness` (CWE XSD requires Impact; CAPEC does not).
3. All enum values within the owning standard's vocabulary.
4. Ordinals contiguous per parent (`C1..Cn`, no gaps after pruning).
