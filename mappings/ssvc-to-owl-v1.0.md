# SSVC to OWL Mapping v1.0

CISA SSVC v2.0.3 decisions as republished by NVD in CVE JSON 2.0
`metrics.ssvcV203[]` → `ssvc:SsvcDecision`, adhered to `kgcs:Vulnerability`
by `HAS_SSVC` (ADR-0003, decision extension). One node per CVE per ADP
timestamp; v1.0 loads declared Authorized Data Publishers only.

## Source

- NVD CVE JSON 2.0 per-year and `modified` files already downloaded for
  the CVE loader (`nvdcve-2.0-<year>.json`), path
  `vulnerabilities[].cve.metrics.ssvcV203[]`.
- NVD schema `cve_api_json_2.0.schema`: `ssvcV203` is an array of
  `ssvc-v203` = `{ source: string, ssvcData: <ssvc-v2.0.3.json> }`, both
  required, no other property. `ssvc-v2.0.3.json` requires `options`,
  `role`, `version`; `timestamp`, `id`, `computed`, `decisionTree`,
  `decisionTreeUrl`, `generator` are optional; no enumerations are given
  in the schema (they come from the SSVC decision-tree definition).
- Verified 2026-09-27 on the raw files:

| File | entries | by CISA ADP | other sources | CVEs with 2+ entries | entries without `timestamp` |
| --- | --- | --- | --- | --- | --- |
| `nvdcve-2.0-2024.json` | 38,130 | 38,126 | `9119a7d8-…` 3, `2fdefc65-…` 1 | 4 | 1 |
| `nvdcve-2.0-2026.json` | 47,324 | 47,237 | `9119a7d8-…` 62, `ics-cert@hq.dhs.gov` 10, `87c8e6ad-…` 9, `cve@takeonme.org` 3, `44488dab-…` 2, `2ffdacf6-…` 1 | 92 | 25 |

Every entry has exactly three `options`, one key each: `exploitation ∈
{none, poc, active}`, `automatable ∈ {no, yes}`, `technicalImpact ∈
{partial, total}`. `version` is `2.0.3` on every entry. `role` is
`CISA Coordinator` (ADP and CISA-as-CNA), `CNA` (25 entries, 2026) or
`Coordinator` (1 entry, 2024). ADP entries always carry `timestamp` and
`id`, and `id` equals the owning CVE; the CNA-role entries carry neither.
Two `timestamp` lexical forms occur: `2025-04-18T15:23:16.425380Z` and
`2024-09-12T17:22:46+00:00`. There is **no `type` field** (unlike
`cvssMetric*`), so Primary/Secondary does not apply.

Example (ADP entry):

```json
{ "source": "134c704f-9b21-4f2e-91b3-4a467353bcc0",
  "ssvcData": { "timestamp": "2025-04-18T15:23:16.425380Z", "id": "CVE-2022-34821",
                "options": [ {"exploitation": "none"}, {"automatable": "no"}, {"technicalImpact": "total"} ],
                "role": "CISA Coordinator", "version": "2.0.3" } }
```

Source identities (NVD source API, 2026-09-27):
`134c704f-9b21-4f2e-91b3-4a467353bcc0` = "CISA-ADP" (the declared ADP of
ADR-0002); `9119a7d8-5eab-497f-8521-727c672e3725` = "Cybersecurity and
Infrastructure Security Agency (CISA) U.S. Civilian Government" (a CNA).

## Target Ontology

- `ontology/extensions/decision-extension-v1.0.owl` (namespace `ssvc:`,
  `docs/namespace-policy-v1.2.md`)
- Class: `ssvc:SsvcDecision`. Frozen class referenced: `kgcs:Vulnerability`.
- Graph: label `SsvcDecision`; edge `HAS_SSVC`.

## Entity Mapping

| Source Record | Target Class | Primary ID |
| --- | --- | --- |
| one `ssvcV203[]` entry whose `source` is a declared ADP | `ssvc:SsvcDecision` | `ssvc:ssvc_id` = `"<cveId>::SSVC::<ssvcData.timestamp>"` (graph `ssvcId`, unique; timestamp verbatim) |

## Field Mapping

| Source Field | OWL property | Neo4j property | Cardinality | Notes |
| --- | --- | --- | --- | --- |
| — (synthetic) | `ssvc:ssvc_id` | `ssvcId` | 1..1 | `<cveId>::SSVC::<timestamp>`; unique constraint; pattern is a Warning (loader-derived) |
| `ssvcData.id` | `ssvc:cve_id` | `cveId` | 1..1 | verbatim (equals the owning CVE on ADP entries); join key |
| `ssvcData.version` | `ssvc:version` | `version` | 1..1 | verbatim; `sh:in ("2.0.3")` — the only value NVD publishes under `ssvcV203`; a new version is a new NVD key and a spec change |
| `ssvcData.timestamp` | `ssvc:timestamp` | `timestamp` | 1..1 | `xsd:dateTime`; graph stores the string verbatim, never normalised; part of the key |
| `ssvcData.options[].exploitation` | `ssvc:exploitation` | `exploitation` | 1..1 | `none` \| `poc` \| `active` |
| `ssvcData.options[].automatable` | `ssvc:automatable` | `automatable` | 1..1 | `no` \| `yes` |
| `ssvcData.options[].technicalImpact` | `ssvc:technical_impact` | `technicalImpact` | 1..1 | `partial` \| `total` |
| `ssvcData.role` | `ssvc:role` | `role` | 1..1 | verbatim (`CISA Coordinator`) |
| `source` | `ssvc:source` | `source` | 1..1 | verbatim NVD source identifier |
| derived from `source` | `ssvc:source_role` | `sourceRole` | 1..1 | ADR-0002 rule (`nvd` \| `cna` \| `adp`); **v1.0: `adp` only** (`sh:in`) |
| `ssvcData.computed`, `decisionTree`, `decisionTreeUrl`, `generator`, `$schema` | — | — | — | optional in the SSVC schema, absent from every NVD entry verified; not mapped |

`options[]` is a list of single-key objects; the loader reads it by key,
not by position.

## Relationship Mapping

| Source Structure | Ontology Edge | Graph Edge |
| --- | --- | --- |
| entry nested in `vulnerabilities[].cve` | `ssvc:has_ssvc` (`Vulnerability` → `SsvcDecision`) | `HAS_SSVC`, one per ADP timestamp |

## Transformation Rules

1. **Scope: declared ADPs only.** Load an entry only if `source` is in the
   declared ADP list of `mappings/cve-to-owl-v1.0.md` (today
   `134c704f-9b21-4f2e-91b3-4a467353bcc0`); set `sourceRole = adp`. Other
   entries — CISA acting as CNA (`9119a7d8-…`, timestamped) and CNA-role
   entries (no `timestamp`, no `id`, hence no key) — are **dropped and
   counted** per source. Widening the scope is ADR-0003 Open question 1
   and needs a shape change (`ssvc:source_role` `sh:in`).
2. **Key and duplicates.** `MERGE (s:SsvcDecision {ssvcId})` with
   `ssvcId = <cveId>::SSVC::<timestamp>` (raw string). Exact duplicate
   entries in the same record (CVE-2026-2771 repeats each of two decisions
   four times) collapse to one node; distinct timestamps for the same CVE
   (ADP re-decisions) each keep their node. A second node for the same
   `(cveId, timestamp)` is a Violation on both (`ssvc:SsvcDecisionShape`).
3. **Never overwritten.** A decision is a dated statement; on refresh the
   loader `MERGE`s and does not `SET` an existing node. New timestamps add
   nodes.
4. **Adherence.** Only `HAS_SSVC` from the Vulnerability whose `cveId`
   equals `ssvcData.id`; `ssvc:SsvcDecisionShape` is closed and
   `ssvc:SsvcDecisionAdherenceShape` rejects any other incoming edge.
   `exploitation = active` is a CISA statement about the CVE, never an
   edge to a Technique or a Weakness.
5. **Reads existing files.** The loader re-reads the NVD JSON already on
   disk after the Vulnerability nodes exist (load order after `load_cve`),
   as `load_cwe.py` does for `weaknesses[]`. `nvdcve-2.0-modified.json`
   first, then the per-year files; a record present in both contributes
   the same set of `(cveId, timestamp)` keys, so order does not matter.
6. **Build metadata:** no key of its own; SSVC is covered by `CVE=<snapshot>`.

## Post-load invariants (pipeline, session Q18)

| Check | Shape |
| --- | --- |
| every `SsvcDecision` has exactly one incoming edge, `HAS_SSVC`, from a `Vulnerability` with the same `cveId` | `ssvc:SsvcDecisionAdherenceShape`, `ssvc:SsvcDecisionShape` (SPARQL) |
| unique `(cveId, timestamp)`; unique `ssvcId` | `ssvc:SsvcDecisionShape` (SPARQL) + graph unique constraint |
| `sourceRole = adp` on every node; per-source dropped counts reported | `ssvc:SsvcDecisionShape` (`sh:in`) |
| vocabularies of the three decision points; `version = 2.0.3` | `ssvc:SsvcDecisionShape` (`sh:in`) |
| no edge leaves an `SsvcDecision` | `ssvc:SsvcDecisionShape` (`sh:closed`) |
| expected count on the 2026-09-06 raw files: distinct ADP `(cveId, timestamp)` pairs, computed offline before the load (Q18 deltas doc) | — |

## Provenance Notes

- Publisher: CISA (ADP) via NVD. Every node carries `source`,
  `sourceRole`, `role`, `version` and `timestamp`.
- Vocabularies and cardinalities were read from the raw NVD files of the
  2026-09-06 download on 2026-09-27 (85,454 entries over the 2024 and 2026
  files), not from the SSVC specification, which the NVD schema does not
  embed. The SSVC decision-tree definition (CISA Coordinator tree v2.0.3)
  is the authority for the vocabularies; the shapes encode the values
  observed, which coincide with it.
