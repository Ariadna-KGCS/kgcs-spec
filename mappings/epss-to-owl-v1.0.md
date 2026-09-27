# EPSS to OWL Mapping v1.0

FIRST Exploit Prediction Scoring System daily scores → `epss:EpssScore`,
adhered to `kgcs:Vulnerability` by `HAS_EPSS` (ADR-0003, decision
extension). One node per CVE per score date, never overwritten.

## Source

- Daily CSV, gzip: `https://epss.empiricalsecurity.com/epss_scores-current.csv.gz`
  (stable URL for the current day; redirects, so follow them) and the
  dated files `epss_scores-<YYYY-MM-DD>.csv.gz`. Complete daily history
  since 2021-04-14 at `github.com/empiricalsec/epss_scores`
  (`https://www.first.org/epss/data`).
- API (not used by the loader; same values at 9 decimals):
  `https://api.first.org/data/v1/epss?cve=…` → `{cve, epss, percentile, date}`.
- Verified 2026-09-27 on the current file (380,066 rows):

```text
#model_version:v2026.06.15,score_date:2026-09-27T12:00:21Z
cve,epss,percentile
CVE-1999-0001,0.03351,0.88245
CVE-1999-0002,0.27858,0.98035
```

Line 1 is a comment with two `key:value` pairs; line 2 is the header;
values have 5 decimals and lie in [0, 1] (0 rows out of range on the
verified file). Model versions published so far: v2022.01.01 (from
2022-02-04), v2023.03.01 (2023-03-07), v2025.03.14 (2025-03-17),
v2026.06.15 (2026-06-15). Files before 2022-02-04 (EPSS v1) have no
header line and are not loadable by this mapping.

## Target Ontology

- `ontology/extensions/decision-extension-v1.0.owl` (namespace `epss:`,
  `docs/namespace-policy-v1.2.md`)
- Class: `epss:EpssScore` (disjoint with `kgcs:VulnerabilityScore`: not a
  CVSS score). Frozen class referenced: `kgcs:Vulnerability`.
- Graph: label `EpssScore`; edge `HAS_EPSS`.

## Entity Mapping

| Source Record | Target Class | Primary ID |
| --- | --- | --- |
| one CSV row of one daily file | `epss:EpssScore` | `epss:epss_id` = `"<cve>::EPSS::<scoreDate>"` (graph `epssId`, unique) |

## Field Mapping

| Source Field | OWL property | Neo4j property | Cardinality | Notes |
| --- | --- | --- | --- | --- |
| — (synthetic) | `epss:epss_id` | `epssId` | 1..1 | `<cve>::EPSS::<YYYY-MM-DD>`; unique constraint; pattern is a Warning (loader-derived) |
| column `cve` | `epss:cve_id` | `cveId` | 1..1 | verbatim; join key, not unique on this label |
| column `epss` | `epss:score` | `score` | 1..1 | `xsd:decimal` in [0, 1], **verbatim precision** (no rounding, no rescaling) |
| column `percentile` | `epss:percentile` | `percentile` | 1..1 | `xsd:decimal` in [0, 1], verbatim |
| header `score_date`, date part | `epss:score_date` | `scoreDate` | 1..1 | `xsd:date`; part of the key; equals the date in the file name |
| header `score_date`, verbatim | `epss:score_timestamp` | `scoreTimestamp` | 0..1 | `xsd:dateTime` (e.g. `2026-09-27T12:00:21Z`) |
| header `model_version` | `epss:model_version` | `modelVersion` | 1..1 | verbatim (`vYYYY.MM.DD`, pattern is a Warning); travels with every node |

## Relationship Mapping

| Source Structure | Ontology Edge | Graph Edge |
| --- | --- | --- |
| column `cve` join to the Vulnerability with the same `cveId` | `epss:has_epss` (`Vulnerability` → `EpssScore`) | `HAS_EPSS`, one per score date loaded |

## Transformation Rules

1. **Append-only.** `MERGE (e:EpssScore {epssId})`; on match, **no `SET`**.
   A score date is loaded once; reloading the same file is a no-op. This
   is the CVSS rule ("do not overwrite older CVSS versions; emit one score
   node per versioned score entry", `cvss-to-owl-v1.0.md`) with the score
   date in the role of the version. `count(EpssScore)` never decreases
   across loads.
2. **One node per (CVE, score date)**; a second node for the same pair is a
   Violation on both (`epss:EpssScoreShape`, SPARQL).
3. **Model version travels with the node.** Scores from different
   `model_version`s are not comparable (each model release shifted every
   score); no consumer may compare or aggregate across versions without
   reading `modelVersion`. KGCS itself never does: no shape, rule, loader
   or contract field derives anything from `score` (ADR-0003 D2, the
   probabilistic-semantics boundary).
4. **Adherence.** Only `HAS_EPSS` from the Vulnerability with the same
   `cveId`; `epss:EpssScoreShape` is closed and
   `epss:EpssScoreAdherenceShape` rejects any other incoming edge.
   Rows whose `cve` has no `Vulnerability` node are dropped and counted.
5. **History depth is a load parameter**, not a mapping rule: one file
   (the snapshot day) or a back-fill of dated files (ADR-0003 Open
   question 3). Either way each file yields its own nodes.
6. **Build metadata:** `sourceSnapshots` gains
   `EPSS=<scoreDate>;model:<modelVersion>` (`shapes/build.shacl.ttl` v1.2).

## Post-load invariants (pipeline, session Q18)

| Check | Shape |
| --- | --- |
| every `EpssScore` has exactly one incoming edge, `HAS_EPSS`, from a `Vulnerability` with the same `cveId` | `epss:EpssScoreAdherenceShape`, `epss:EpssScoreShape` (SPARQL) |
| unique `(cveId, scoreDate)`; unique `epssId` | `epss:EpssScoreShape` (SPARQL) + graph unique constraint |
| `0 <= score <= 1`, `0 <= percentile <= 1` | `epss:EpssScoreShape` |
| `count(EpssScore)` after load >= before load | — (loader report) |
| no edge leaves an `EpssScore` | `epss:EpssScoreShape` (`sh:closed`) |

## Provenance Notes

- Publisher: FIRST (EPSS SIG); files served by Empirical Security. Every
  node carries `scoreDate`, `scoreTimestamp` and `modelVersion`.
- Header format, column names, precision and value range were verified on
  the 2026-09-27 file; the raw file is not stored in this repo.
