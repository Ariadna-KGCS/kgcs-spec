# CWE Enrichment to OWL Mapping v1.0

Companion to `cwe-to-owl-v1.0.md` (frozen). Covers only the node-property
enrichment introduced by `ontology/standards/cwe-enrichment-v1.0.owl`.

## Source

- MITRE CWE XML catalog (`data/raw/CWE/cwec_v*.xml`), Core Definition XSD v7.3
  (`data/schemas/CWE/cwe_schema_latest.xsd`)
- Scope: `Weakness` elements only. Categories, Views, External_References and
  all relationship-bearing elements (`Related_Weaknesses`,
  `Related_Attack_Patterns`, `Observed_Examples`) are **out of scope** for this
  module — they are candidates for later increments and must not be loaded
  from here.

## Target Ontology

- `ontology/standards/cwe-enrichment-v1.0.owl`
- Core class: `kgcs:Weakness` (unchanged; this module adds datatype
  properties only)

## Field Mapping

| XSD source (WeaknessType) | Ontology property (OWL) | Neo4j property | Cardinality | XSD vocabulary |
| --- | --- | --- | --- | --- |
| `Description` | `cwe:description` | `description` | 1..1 | free text |
| `Extended_Description` | `cwe:extended_description` | `extendedDescription` | 0..1 | StructuredText → flattened |
| `Mapping_Notes/Usage` | `cwe:mapping_usage` | `mappingUsage` | 1..1 | UsageEnumeration (4) |
| `Mapping_Notes/Reasons/Reason/@Type` | `cwe:mapping_reasons` | `mappingReasons` | 0..N | ReasonEnumeration (12) |
| `@Structure` | `cwe:structure` | `structure` | 1..1 | StructureEnumeration (3) |
| `@Status` | `cwe:status` | `status` | 1..1 | StatusEnumeration (6) |
| `Alternate_Terms/Alternate_Term/Term` | `cwe:alternate_terms` | `alternateTerms` | 0..N | free text (terms only) |
| `Likelihood_Of_Exploit` | `cwe:likelihood_of_exploit` | `likelihoodOfExploit` | 0..1 | LikelihoodEnumeration (4) |
| `Functional_Areas/Functional_Area` | `cwe:functional_areas` | `functionalAreas` | 0..N | FunctionalAreaEnumeration (20) |
| `Affected_Resources/Affected_Resource` | `cwe:affected_resources` | `affectedResources` | 0..N | ResourceEnumeration (5) |
| `Modes_Of_Introduction/Introduction/Phase` | `cwe:modes_of_introduction` | `modesOfIntroduction` | 0..N | PhaseEnumeration (17) |
| `Weakness_Ordinalities/Weakness_Ordinality/Ordinality` | `cwe:ordinalities` | `ordinalities` | 0..N | OrdinalityEnumeration (3) |

Naming layers as per KGCS convention: OWL properties snake_case, Neo4j node
properties camelCase. SHACL `sh:path` always uses the OWL names
(`shapes/cwe.shacl.ttl` v1.1).

## Transformation Rules

1. **StructuredText flattening** (`Extended_Description`): concatenate all
   text nodes of the element subtree (`itertext()`), collapse consecutive
   whitespace to single spaces, strip. Embedded XHTML markup is discarded;
   list/paragraph boundaries become plain spaces. Empty result → property
   omitted.
2. **Multi-valued fields** are loaded as Neo4j string arrays, deduplicated in
   Python preserving first-seen document order. Empty arrays are omitted
   (property absent), never stored as `[]`.
3. **Modes of introduction**: only `Phase` is loaded; per-introduction `Note`
   text is discarded. Duplicate phases (multiple introductions in the same
   phase) collapse to one value.
4. **Alternate terms**: only `Term` strings are loaded; per-term
   `Description` is discarded.
5. **Ordinalities**: only the `Ordinality` enum is loaded; per-ordinality
   `Description` is discarded.
6. **Deprecated entries** (`@Status="Deprecated"` / `"Obsolete"`) are loaded
   with their status flag — legacy NVD `CAUSED_BY` edges may target them.
   Agent-facing query templates must filter on `status` and honor
   `mappingUsage` (`Prohibited`/`Discouraged`).
7. **Idempotent refresh**: enrichment properties are written with
   `ON CREATE SET` + `ON MATCH SET` so re-ingesting a newer CWE catalog
   updates existing nodes. `cweId` remains the immutable merge key.

## Provenance Notes

- All properties in this module are first-party MITRE CWE editorial content;
  provenance is the CWE catalog version recorded by the loader.
- `likelihood_of_exploit` is a weakness-level editorial signal. It must not
  be merged or confused with vulnerability-level CVSS scores or
  probabilistic exploit feeds (EPSS): distinct sources, distinct semantics.
- `mapping_usage` exists to qualify CVE→CWE mapping legitimacy; it feeds
  agent confidence logic but never creates or removes edges.
