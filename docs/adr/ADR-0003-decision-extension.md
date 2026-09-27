# ADR-0003 — Decision extension: KEV, EPSS and SSVC adhered to Vulnerability

**Status:** Accepted (2026-09-27, HC)
**Scope:** modelling of three published decision inputs in the KGCS graph: the CISA Known Exploited Vulnerabilities catalog (KEV), the FIRST Exploit Prediction Scoring System daily score (EPSS) and the CISA Stakeholder-Specific Vulnerability Categorization decision (SSVC v2.0.3) as republished by NVD in `metrics.ssvcV203[]`
**Deciders:** Humbert Costas
**Spec artifacts:** `ontology/extensions/decision-extension-v1.0.owl`, `shapes/decision.shacl.ttl`, `shapes/build.shacl.ttl` v1.2, `mappings/kev-to-owl-v1.0.md`, `mappings/epss-to-owl-v1.0.md`, `mappings/ssvc-to-owl-v1.0.md`, `mappings/mapping-coverage-matrix-v1.2.md`, `docs/namespace-policy-v1.2.md`, `contracts/agent-consumable-schema.md` (invariant 9), `contracts/agent-consumable-schema.json` (`definitions.KevEntryProperties`, `EpssScoreProperties`, `SsvcDecisionProperties`)

## Context

KGCS v1.1 describes *what* a vulnerability is (CVE), how severe it is
(CVSS), what weakness causes it and how it is exploited and mitigated
(the causal chain). It says nothing about what the world has *decided*
about it: whether it is known to be exploited, how likely exploitation is
in the near term, and what a coordinator recommends. Three public sources
publish exactly that, each under its own governance:

- **CISA KEV** — a catalog of CVEs with confirmed exploitation, each with a
  date of addition, a due date for federal remediation (BOD 22-01 / BOD
  26-04), a required action, a ransomware flag and, since 2026, a forensic
  triage flag. Verified on 2026-09-27: catalog `2026.09.25`, 1,726
  entries; schema `known_exploited_vulnerabilities_schema.json`.
- **FIRST EPSS** — a daily probability, for every CVE, of exploitation
  activity in the next 30 days, with a percentile, published as a CSV whose
  first line names the model version and the score date. Verified on the
  file of 2026-09-27: header
  `#model_version:v2026.06.15,score_date:2026-09-27T12:00:21Z`, 380,066
  rows, values in [0, 1] with 5 decimals. Model versions so far:
  v2022.01.01, v2023.03.01, v2025.03.14, v2026.06.15; each change shifted
  every score.
- **CISA SSVC** — CISA's Authorized Data Publisher (ADP,
  `134c704f-9b21-4f2e-91b3-4a467353bcc0`, the ADP of ADR-0002) publishes
  three SSVC v2.0.3 decision points per CVE into the NVD record. Verified on
  the raw NVD per-year files (2026-09-27): 38,130 entries in the 2024 file
  (38,126 by the ADP), 47,324 in the 2026 file (47,237 by the ADP). Entry
  shape `{source, ssvcData: {timestamp, id, options: [{exploitation},
  {automatable}, {technicalImpact}], role, version}}`; always three
  options; `version` always `2.0.3`; vocabularies `exploitation ∈ {none,
  poc, active}`, `automatable ∈ {no, yes}`, `technicalImpact ∈ {partial,
  total}`. The v1.1 loader ignores the key (`load_cvss.py` reads only
  `cvssMetric*`).

The 2026 context makes these inputs central rather than optional: NIST
announced (2026-04-15) that NVD enrichment (CPE, CVSS, CWE) continues only
for KEV, federal and critical software, so the KEV membership of a CVE now
also decides whether the chain hop `CVE → CWE` will be populated by NVD at
all (`kgcs-research` decision D-Q7).

Two rules of this repo constrain how the inputs may enter:

1. **Hard Rule 2** (`CLAUDE.md`): the causal chain `CPE → CVE/CVSS → CWE →
   CAPEC → ATT&CK → defences` is the standard; no shortcut edges. KEV
   entries carry `cwes[]`, EPSS is used downstream to rank CWEs, and SSVC's
   `exploitation` is a statement about ATT&CK-like activity. Each is a
   temptation to draw an edge into the chain.
2. **The probabilistic-semantics boundary** of the asset extension
   (`docs/asset-extension-ontology-v1.0.md` §2: "MUST NOT introduce
   probabilistic semantics"). EPSS *is* a probability. The glossary adds
   that *Coverage* is "not a probability" and that *Confidence* must carry
   basis and provenance.

Experiments E2 (KEV membership from topology) and E4 (SSVC concordance)
in `kgcs-research` need these nodes on the v1.2 graph (`kgcs-v12`,
sessions Q18–Q20), with a temporal partition, so the score date and the
decision timestamp must be first-class.

## Decision

### D1 — Adhered leaf nodes, one edge each, from Vulnerability only

Three new classes, each a **leaf annotation of the CVE hop**:

```
(v:Vulnerability)-[:HAS_KEV_ENTRY]->(k:KevEntry)      0..1 per CVE
(v:Vulnerability)-[:HAS_EPSS]->(e:EpssScore)          0..n per CVE, one per score date
(v:Vulnerability)-[:HAS_SSVC]->(s:SsvcDecision)       0..n per CVE, one per ADP timestamp
```

OWL: `kev:KevEntry`, `epss:EpssScore`, `ssvc:SsvcDecision`;
`kev:has_kev_entry`, `epss:has_epss`, `ssvc:has_ssvc`, all with domain
`kgcs:Vulnerability`. **No inverse properties** (an inverse would be an edge
leaving the leaf). The classes are declared disjoint with the chain classes
and with `kgcs:VulnerabilityScore` (EPSS is not a CVSS `Score`).

*Adhered* means, operationally:

- **No outgoing edge.** The node shapes are `sh:closed`: a decision node may
  carry only its own datatype properties. `KevEntry → Weakness`,
  `SsvcDecision → Technique`, `EpssScore → anything` are Violations
  (`kev-edge-to-weakness.ttl`, `ssvc-edge-to-technique.ttl`).
- **No incoming edge but the has_\* edge from a Vulnerability.** An
  *AdherenceShape* per class (SHACL-SPARQL) reports any other predicate or
  any subject that is not a Vulnerability (`kev-incoming-from-weakness.ttl`,
  `epss-incoming-from-technique.ttl`, `ssvc-incoming-from-weakness.ttl`).
- **Same CVE on both ends.** Every leaf carries the source's own CVE
  identifier (`cveID`, CSV `cve`, `ssvcData.id`) and a SPARQL constraint
  requires it to equal the adhering Vulnerability's `cveId`
  (`epss-cve-mismatch.ttl`).
- **KEV `cwes[]` stays a string list on the KevEntry.** It is CISA's
  statement, not NVD's or the CNA's; turning it into `CAUSED_BY` would add a
  fourth assigner to the ADR-0002 provenance model and, worse, let a
  decision source write the chain. Whether it should one day become a
  fourth `sourceRoles` value (`kev`) is Open question 2.
- **Never a hop.** Agent templates read the leaves with `OPTIONAL MATCH`
  from the Vulnerability and never traverse *through* them (contract
  invariant 9, the same register as ADR-0001 Consequences and ADR-0002
  provenance).

### D2 — EPSS as a dated, versioned, append-only datum (the boundary)

The asset extension's "MUST NOT introduce probabilistic semantics" is
read, for this extension, as: **KGCS may store a probability that a named
third party published, with its date and model version, exactly as it
stores a CVSS base score; KGCS may not compute, combine, propagate or
interpret one.** Concretely:

- `EpssScore` holds `score` and `percentile` **verbatim** (CSV precision),
  `scoreDate` (date part of the header `score_date`, equal to the file
  date), `scoreTimestamp` (header value verbatim) and `modelVersion`
  (header `model_version`). Every node therefore states which model
  produced it; scores of different model versions are not comparable and
  the graph never pretends they are.
- **One node per CVE per score date**, key `epssId = <cveId>::EPSS::<scoreDate>`,
  **never overwritten**: the loader `MERGE`s on `epssId` and never `SET`s an
  existing node. This is the CVSS pattern (`cvss-to-owl-v1.0.md`: "Do not
  overwrite older CVSS versions; emit one score node per versioned score
  entry"), with the date playing the role of the version. Duplicate
  (CVE, date) is a Violation (`epss-duplicate-date.ttl`).
- **Nothing in Core references EPSS.** No class, property, shape, rule or
  contract field in `kgcs:` or in the chain modules mentions it; the
  confidence model of `kgcs-server` does not consume it (its `basis`
  vocabulary is unchanged). No SHACL rule, no rule-engine rule and no
  loader derives anything from an EPSS value. An agent may *report* the
  score next to a CVE, with its date and model version, as it reports a
  CVSS score.
- The asset extension itself is untouched; its boundary sentence still
  governs the asset layer. This ADR states the parallel rule for the
  decision layer.

### D3 — SSVC: one decision per CVE per ADP timestamp, ADP provenance only

- `SsvcDecision` carries `version` (must be `2.0.3`: the only value NVD
  publishes under the `ssvcV203` key; a new SSVC version is a new NVD key
  and therefore a spec change), `timestamp` (verbatim; two lexical forms
  occur, `…T15:23:16.425380Z` and `…T17:22:46+00:00`, both valid
  `xsd:dateTime`), `exploitation`, `automatable`, `technicalImpact` (the
  three `options[]`, closed vocabularies above), `role` (verbatim, "CISA
  Coordinator"), `source` (the raw NVD source identifier) and `sourceRole`
  (the ADR-0002 rule: `nvd` | `cna` | `adp`).
- Key `ssvcId = <cveId>::SSVC::<timestamp>` with the raw timestamp string.
  **One node per CVE per timestamp**; exact duplicate entries in the feed
  (CVE-2026-2771 repeats each of its two decisions four times) collapse to
  one, as ADR-0002 collapses exact duplicate `(source, type)` pairs. A CVE
  legitimately has several decisions when the ADP re-decides (2 CVEs with
  differing option sets in the 2026 file); each keeps its node.
- **v1.0 scope: declared ADPs only** (`sourceRole = adp`, today CISA ADP).
  The raw data also contains: entries by CISA acting as CNA
  (`9119a7d8-5eab-497f-8521-727c672e3725`, "Cybersecurity and
  Infrastructure Security Agency (CISA) U.S. Civilian Government", 3
  entries in 2024, 62 in 2026, with timestamps) and CNA-role entries
  (`ics-cert@hq.dhs.gov`, `87c8e6ad-…`, `cve@takeonme.org`; 25 in 2026)
  that carry **no `timestamp` and no `id`** and so cannot take the key.
  The loader drops both kinds and reports the counts (`ssvc-source-role-cna.ttl`).
  Open question 1 asks whether the timestamped CISA-as-CNA entries should
  enter with `sourceRole = cna`.

### D4 — KEV: one entry per CVE, refreshed in place, catalog version as provenance

- `KevEntry` carries the eight fields the CISA schema requires (`cveID`,
  `vendorProject`, `product`, `vulnerabilityName`, `dateAdded`,
  `shortDescription`, `requiredAction`, `dueDate`) plus the optional
  `knownRansomwareCampaignUse` (`Known` | `Unknown`), `forensicTriage`
  (`Yes` | `No`, BOD 26-04, new in 2026), `notes` and `cwes[]`, and the
  file-level `catalogVersion` / `dateReleased` as the provenance of the
  refresh.
- **Exactly one KevEntry per CVE**, keyed by the CVE identifier itself
  (`cveId`, unique on the label); KEV entries are never removed from the
  catalog and are edited in place by CISA (due dates, ransomware flag), so
  the loader `MERGE`s on `cveId` and `SET`s all fields on every load. A
  second entry for the same CVE is a Violation on both entries and on the
  Vulnerability (`kev-duplicate-entry.ttl`).
- `dateAdded` and `dueDate` are `xsd:date` (CISA `format: date`); the graph
  stores the `YYYY-MM-DD` strings verbatim, as it does for `published`.

### D5 — Namespaces and module placement

One namespace per publisher's standard — `kev:`, `epss:`, `ssvc:` — because
Hard Rule 5 forbids mixing source-specific identifiers across taxonomies,
and the three sources are governed, versioned and released independently.
One module file, `ontology/extensions/decision-extension-v1.0.owl`, whose
ontology IRI is `decision:DecisionExtensionOntology`; `decision:` also
names the shape-graph nodes (`decision:DecisionShapesPrefixes`,
`decision:VulnerabilityDecisionEdgesShape`) and declares no OWL term, like
`labels:` and `align:`. Registered in `docs/namespace-policy-v1.2.md`.

### D6 — Build metadata

`shapes/build.shacl.ttl` v1.2 adds `KEV` and `EPSS` to the `sourceSnapshots`
vocabulary: `KEV=<catalogVersion>` (e.g. `KEV=2026.09.25`) and
`EPSS=<scoreDate>;model:<modelVersion>` (e.g.
`EPSS=2026-09-27;model:v2026.06.15`). SSVC needs no key: it is read from
the NVD CVE files and covered by `CVE=…`. The frozen OWL comment on
`build:source_snapshot` lists the ten v1.0 sources; the shape pattern is
the normative vocabulary (recorded in `mappings/mapping-coverage-matrix-v1.2.md`).

### Validation (`shapes/decision.shacl.ttl`)

Seven node shapes: `decision:VulnerabilityDecisionEdgesShape` (edge
targets, `HAS_KEV_ENTRY` max 1), `kev:KevEntryShape`, `epss:EpssScoreShape`,
`ssvc:SsvcDecisionShape` (closed; fields; uniqueness and CVE identity by
SPARQL) and the three `*AdherenceShape`s (incoming-edge guard by SPARQL).
Sixteen negative fixtures, at least two per shape, pinned in
`tests/fixtures/negative/manifest.json`. `sh:closed` ignores `rdf:type`
and `owl:sameAs` because the harness closure asserts a reflexive
`owl:sameAs` on every node (`tests/conftest.py`).

## Alternatives considered

**A1 — EPSS as a property on Vulnerability** (`v.epss`, `v.epssDate`).
Simplest for agents. Rejected: it can only hold one date, so every refresh
overwrites history and the temporal partition of E2/E4 becomes impossible;
it also puts a probability on a Core class, which is the boundary this ADR
exists to keep.

**A2 — EPSS as a `cvss:Score` / `kgcs:VulnerabilityScore` with `version =
"EPSS"`.** Reuses `HAS_SCORE`. Rejected: `cvss.shacl.ttl` closes `version`
to `2.0 | 3.0 | 3.1 | 4.0` and `baseScore` to `[0, 10]`; a probability is not
a severity; and Rule 5 forbids mixing FIRST's identifiers into the CVSS
taxonomy. `EpssScore` is declared disjoint with `VulnerabilityScore` to
make the separation checkable.

**A3 — KEV as a boolean on Vulnerability** (`v.inKev = true`). Rejected:
loses `dateAdded`, `dueDate`, the ransomware and triage flags and the
catalog version, all of which E2 and UC1 need; and it is not refreshable
with provenance.

**A4 — KEV `cwes[]` as `CAUSED_BY` edges with `sourceRoles = ["kev"]`.**
Keeps one CWE model. Rejected for v1.2: it lets a decision source write
the chain, changes the `CAUSED_BY` count every experiment gate depends on,
and CISA's `cwes` are not NVD `weaknesses[]` entries (no `type`). Kept as
Open question 2 for a later ADR, in the same register as D3FEND's
`references_cwe` (`shapes/README.md`, policy call pending).

**A5 — SSVC as three properties on Vulnerability** (`v.ssvcExploitation` …).
Rejected: loses the timestamp history (re-decisions exist), the ADP
provenance and the version; same objection as A1.

**A6 — One `decision:` namespace for all terms.** Fewer prefixes.
Rejected: KEV, EPSS and SSVC are three standards with three owners; Rule 5.

**A7 — Single generic `Decision` class with a `kind` property.** Rejected:
the three have disjoint field sets and vocabularies; one class would need
conditional shapes and would invite cross-source comparisons the data does
not support.

**A8 — Loading all SSVC sources (ADP, CISA-as-CNA, CNAs) in v1.0.**
Rejected for v1.0: CNA-role entries have no timestamp, so no key; and the
card's requirement is "provenance = CISA ADP". Timestamped non-ADP entries
are Open question 1.

## Consequences

- **Spec:** new module and shape file; `build.shacl.ttl` v1.2;
  `namespace-policy-v1.2.md`; contract labels `KevEntry`, `EpssScore`,
  `SsvcDecision` and edges `HAS_KEV_ENTRY`, `HAS_EPSS`, `HAS_SSVC`;
  invariant 9. No frozen file is modified. `mapping-coverage-matrix-v1.2.md`
  gains an explicit *Exclusions* table (VEX, CSAF, purl/SBOM, OCSF, Sigma,
  and the KEV/EPSS/SSVC fields deliberately not mapped).
- **Pipeline (session Q18, not done here):** downloaders `cisa_kev`
  (`known_exploited_vulnerabilities.json`) and `first_epss`
  (`epss_scores-current.csv.gz`, redirect-following, or the dated file);
  loaders `load_kev.py` (MERGE on `cveId`, SET all fields, `catalogVersion`
  from the file header), `load_epss.py` (MERGE on `epssId`, never SET an
  existing node; `scoreDate`/`modelVersion` from line 1), `load_ssvc.py`
  (reads `metrics.ssvcV203[]` from the NVD JSON already on disk, ADP
  sources only, exact duplicates collapsed, dropped counts reported);
  unique constraints `KevEntry.cveId`, `EpssScore.epssId`,
  `SsvcDecision.ssvcId`; post-load checks: every decision node has exactly
  one incoming edge and it comes from a Vulnerability; `count(EpssScore)`
  never decreases across loads; `BuildMetadata.sourceSnapshots` gains
  `KEV=` and `EPSS=`. **Chain loaders must show an empty diff** (Q18 exit
  criterion). Vulnerabilities in KEV or EPSS that are not in the graph
  (rejected/reserved CVEs) are dropped and counted, never created.
- **Research (`kgcs-research`):** E2 and E4 read `dateAdded`, `scoreDate`
  and `timestamp` for the temporal partition; UC1 (paper §6) shows a real
  CVE with its three leaves "as loaded, with the score date". The snapshot
  v12 gate must include the three exports and prove the chain exports are
  hash-identical to v11 (session Q19).
- **Agents (`kgcs-server`):** templates may `OPTIONAL MATCH (v)-[:HAS_KEV_ENTRY]->(k)`
  and return `k.dateAdded`, `k.dueDate`, `k.knownRansomwareCampaignUse`;
  may return the latest `EpssScore` by `scoreDate` **with** `modelVersion`;
  must not compute with `score`; must not traverse through any of the
  three. The confidence model is unchanged.
- **Explorer:** the three labels get a "decision" colour family and default
  to hidden, like `Consequence`.

## Open questions for HC (block Accepted)

1. **Non-ADP SSVC entries.** Load the timestamped entries by CISA-as-CNA
   (`9119a7d8-…`, role "CISA Coordinator", 62 entries in the 2026 file)
   with `sourceRole = cna`, or keep v1.0 to declared ADPs only (proposed)?
   CNA-role entries without timestamp stay out either way (no key).
2. **KEV `cwes[]`.** Strings on the KevEntry only (proposed, A4 rejected),
   or a future `sourceRoles` value `kev` on `CAUSED_BY` (would change the
   edge count; needs its own ADR after the D3FEND `references_cwe` policy
   call)?
3. **EPSS history depth for `kgcs-v12`.** One score date per CVE (the
   snapshot day; proposed for Q18) or a back-fill of daily files from
   `github.com/empiricalsec/epss_scores` for the E2/E4 temporal partition?
   The model decides the size of the load and whether Q20 needs history.
4. **`scoreDate` source.** Date part of the header `score_date` (proposed;
   verified equal to the file date) rather than the file name, so that
   `epss_scores-current.csv.gz` is loadable.
5. **Build-metadata value for EPSS.** `EPSS=<scoreDate>;model:<modelVersion>`
   (proposed) or two keys (`EPSS=` and `EPSS-MODEL=`)?
6. **`forensicTriage`.** Included as an optional field (verified in the
   CISA schema and the 2026.09.25 catalog); confirm, since it is a 2026
   addition tied to BOD 26-04.
7. **`decision:` prefix scope.** Ontology IRI and shape-graph nodes only
   (proposed, as `labels:`/`align:`), or drop the shape nodes into `kev:`?
8. **`knownRansomwareCampaignUse` severity.** Absence is a Warning because
   the CISA schema marks it optional, although every current entry has it;
   promote to Violation?
9. **`EpssScore ⊥ VulnerabilityScore`.** The disjointness axiom is the only
   OWL statement this module makes about a Core class; confirm it is
   wanted (it is not modification of Core, only a constraint between a new
   class and a frozen one).
