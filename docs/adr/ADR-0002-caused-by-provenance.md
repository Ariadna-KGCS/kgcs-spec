# ADR-0002 — CAUSED_BY provenance as aligned edge lists

**Status:** Accepted (2026-09-26)
**Scope:** provenance of the Vulnerability → Weakness relation (`kgcs:caused_by`, graph `CAUSED_BY`) from NVD CVE JSON 2.0 `weaknesses[]`
**Deciders:** Humbert Costas
**Spec artifacts:** `ontology/standards/cve-weakness-provenance-v1.0.owl`, `shapes/cve.shacl.ttl` v1.2, `mappings/cve-to-owl-v1.0.md` (v1.1 section), `contracts/agent-consumable-schema.md`, `contracts/agent-consumable-schema.json` (`definitions.CausedByEdgeProperties`)

## Context

Each NVD CVE record lists its weaknesses as entries
`{source, type, description[{value: "CWE-n"}]}`. `source` is the raw
identifier of the assigner, and `type` is `Primary` or `Secondary`. There
are three kinds of assigner:

- NVD itself (`nvd@nist.gov`);
- the CVE's CNA (an e-mail or a UUID);
- an Authorized Data Publisher (ADP), which enriches records it neither
  assigned nor analysed. CISA's ADP is the one that matters today.

The same CWE is often assigned by more than one of them, and they often
disagree.

The v1.0 loader keeps only the CWE: one `CAUSED_BY` edge per (CVE, CWE)
pair, with `source` and `type` discarded. The 2026-09-26 graph-quality
review (`kgcs-research`, CWE working note §0b) measured what that loses on
the snapshot co-occurrence used by experiment E1:

- 11,869 of 31,962 multi-CWE CVEs (37%) carry one CWE per source, with the
  sources disagreeing;
- 35.6% of co-occurrence weight exists only *between* sources.

NVD mostly marks Primary, the others mostly Secondary. Without this
provenance, a single-source robustness control for E1 is impossible.

Assigner mix in the raw data (NVD JSON 2.0 per-year files without
`modified`, `CWE-n` values, before loader filters; HC, 2026-09-26):

| | Count |
| --- | --- |
| (CVE, CWE) pairs | 345,368 |
| assignments | 384,480 |
| distinct sources | 453 |
| `nvd@nist.gov` assignments | 179,342 |
| CISA ADP (`134c704f-9b21-4f2e-91b3-4a467353bcc0`) assignments | 38,420 — second-largest source, all Secondary |
| pairs that exist **only** because of the CISA ADP | 25,357 |

Hard constraint: every experiment gate so far counts `CAUSED_BY` edges
(331,107 on kgcs-demo, 2026-09-26). The fix must not change that count.

## Decision

Keep **exactly one `CAUSED_BY` edge per (CVE, CWE) pair**. Carry the
provenance on it as three **index-aligned list properties**, one entry per
`weaknesses[]` entry that names this CWE, in the same order in all three:

```
(v:Vulnerability)-[:CAUSED_BY {
    sources:     ["nvd@nist.gov", "secalert@redhat.com", "134c704f-9b21-4f2e-91b3-4a467353bcc0"],
    sourceRoles: ["nvd",          "cna",                 "adp"],
    types:       ["Primary",      "Secondary",           "Secondary"]
}]->(w:Weakness)
```

- `sources`: raw `weaknesses[].source`, verbatim.
- `sourceRoles`: a closed vocabulary of three values, derived from the
  source string:
  - `nvd` if the source is `nvd@nist.gov`;
  - `adp` if the source is in the **declared ADP list**;
  - `cna` otherwise.
- `types`: `weaknesses[].type`, `Primary` or `Secondary`.
- **Declared ADP list.** It lives in the spec, not the loader:
  `mappings/cve-to-owl-v1.0.md` and the header of
  `cve-weakness-provenance-v1.0.owl`. Today it has one entry,
  `134c704f-9b21-4f2e-91b3-4a467353bcc0` (CISA ADP). Adding an entry is a
  spec change with a CHANGELOG entry.
- **Order:** document order of `weaknesses[]`. Exact duplicate
  `(source, type)` entries collapse to one; a source that assigns the same
  CWE as both Primary and Secondary keeps two entries.
- **Refresh:** the loader *replaces* the three lists on every load
  (`MERGE` the edge, then `SET r.sources = …, r.sourceRoles = …,
  r.types = …`); it never appends. Loads stay idempotent.
- **Unchanged filters:** `NVD-CWE-Other` / `NVD-CWE-noinfo` placeholders,
  and CWE ids that are not Weaknesses in the loaded CWE XML
  (Categories/Views), still produce no edge. The edge count is therefore
  unchanged.

**Why lists, not a map.** Neo4j property values are scalars or homogeneous
lists of scalars. Map-valued properties and lists of maps do not exist, so
`{source, role, type}` records cannot be stored as one property. Three
aligned lists are the closest faithful form: they keep the per-assignment
grouping by position.

**RDF form.** For `MATCHES_CRITERIA.vulnerable`, the repo encodes an edge
property as sub-properties (`cve-applicability-v1.0.owl`). That works for
a boolean but not for three ordered lists that can hold duplicates, so the
edge is reified. There is one `cve:CausedByStatement` (a subclass of
`rdf:Statement`) per `kgcs:caused_by` triple, with `rdf:subject` /
`rdf:predicate` / `rdf:object` naming the edge. Its properties
`cve:weaknessSources`, `cve:weaknessSourceRoles` and `cve:weaknessTypes`
hold `rdf:List` values. Plain multi-valued RDF properties are unordered
sets and would collapse `["Secondary", "Secondary"]`.

**Validation** (`shapes/cve.shacl.ttl` v1.2, `cve:CausedByStatementShape`):
- the three lists are non-empty and have equal length;
- roles are in `{nvd, cna, adp}` and types in `{Primary, Secondary}`;
- there is one statement per (CVE, CWE) pair, and every statement
  annotates an edge that exists.

A `CAUSED_BY` edge with no provenance is a **Warning**
(`cve:CausedByProvenanceCoverageShape`), not a Violation, so graphs from
pre-v1.1 loaders still validate. SHACL does not check that each role
agrees with the source at the same position; that is a loader rule and a
v1.2 candidate. The pipeline post-load equivalent is
`size(r.sources) = size(r.sourceRoles) = size(r.types)` for every
`CAUSED_BY`, plus the unchanged edge count.

## Alternatives considered

**A1 — One edge per assignment** (`(v)-[:CAUSED_BY {source, type}]->(w)`,
parallel edges). Scalar properties, simplest Cypher. Rejected: the edge
count rises above 331,107, which invalidates every existing experiment gate
and silently double-counts co-occurrence unless every query adds
`DISTINCT`.

**A2 — Assignment sub-nodes** (`(v)-[:HAS_WEAKNESS_ASSIGNMENT]->(a)-[:ASSIGNS]->(w)`).
Rejected: it puts a node inside the Vulnerability → Weakness hop of the
causal chain, and every chain traversal would have to learn to skip it.
ADR-0001 sub-nodes are leaves; this would not be.

**A3 — Encoded strings** (`["nvd@nist.gov|Primary", …]`). Rejected for the
same reason as ADR-0001 A2: string parsing in Cypher and no member-wise
vocabulary validation.

**A4 — Role-specific edge flags** (`nvdPrimary: true`, `cnaSecondary: true`).
Rejected: this drops the raw source identifier, which the single-source
controls need in order to tell CNAs apart.

**A5 — Two roles only (`nvd` | `cna`, ADP folded into `cna`).** This was
the first draft of this ADR. Rejected: CISA ADP is not a CNA; it is the
second-largest source; and 25,357 pairs exist only because of it. Folding
it into `cna` would attribute ADP enrichment to the CNAs and blur exactly
the NVD-vs-CNA disagreement this ADR exists to expose.

## Consequences

- **Spec:** new module `cve-weakness-provenance-v1.0.owl` (frozen modules
  untouched); `cve.shacl.ttl` v1.2; contract lists the edge properties and
  the three roles.
- **Pipeline:** `CAUSED_BY` is written by **`load_cwe.py`** (load step 4),
  not `load_cve.py`. `load_cwe.py` re-reads `weaknesses[]` from the NVD
  JSON files (`nvdcve-2.0-modified.json` first, then the per-year files)
  after the Weakness nodes exist. `_iter_caused_by_records` must yield
  `source` and `type` alongside the CWE, and the loader aggregates them
  per (CVE, CWE) before the `MERGE` so that each edge gets its three lists
  in one `SET`. The CAUSED_BY count gate stays valid. Graph exports and
  snapshots used by experiments must include the three lists, because the
  E1 single-source control (i) depends on them.
- **Research (`kgcs-research`):** E1 robustness variant V2 counted every
  non-NVD source as CNA, ADP included. Its label becomes **"non-NVD
  (CNA + ADP)"**; its numbers are unchanged. A CNA-only variant becomes
  possible once the lists are loaded.
- **Agents:** `CAUSED_BY` stays a single hop; templates can filter it,
  e.g. `WHERE 'nvd' IN r.sourceRoles` or
  `WHERE any(i IN range(0, size(r.types)-1) WHERE r.sourceRoles[i] = 'nvd' AND r.types[i] = 'Primary')`.
- **Closed:** the CISA ADP question left open in the first draft is
  answered by the third role `adp` and the declared ADP list (A5, figures
  above).
