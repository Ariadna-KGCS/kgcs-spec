# ADR-0004 — ATLAS module: a parallel matrix beside ATT&CK, bridged only by ADAPTED_FROM

**Status:** Accepted (2026-09-27, HC)
**Scope:** modelling of MITRE ATLAS (Adversarial Threat Landscape for AI Systems) tactics, techniques, sub-techniques and mitigations in the KGCS graph, and of the one relation ATLAS declares towards ATT&CK
**Deciders:** Humbert Costas
**Spec artifacts:** `ontology/standards/atlas-ontology-v1.0.owl`, `shapes/atlas.shacl.ttl`, `shapes/build.shacl.ttl` v1.2 (`ATLAS` key), `mappings/atlas-to-owl-v1.0.md`, `mappings/mapping-coverage-matrix-v1.2.md`, `docs/namespace-policy-v1.2.md`, `contracts/agent-consumable-schema.md` (invariant 10), `contracts/agent-consumable-schema.json` (`definitions.AtlasTacticProperties`, `AtlasTechniqueProperties`, `AtlasMitigationProperties`, `AdaptedFromEdgeProperties`)

## Context

ATT&CK describes adversary behaviour against enterprise, mobile and ICS
systems. MITRE ATLAS describes adversary behaviour against **AI-enabled
systems** (model access, poisoning, evasion, prompt injection, agent tool
abuse) with the same shape: tactics, techniques, sub-techniques,
mitigations and case studies. KGCS decision D-Q8 (`kgcs-research`,
2026-09-27) brings ATLAS into spec v1.2.0 as a parallel matrix, without
extending the causal chain.

**Source, verified on 2026-09-27** (`mitre-atlas/atlas-data`, full profile in
`mappings/atlas-to-owl-v1.0.md`):

- `dist/ATLAS-latest.yaml` is a symlink to `dist/v6/ATLAS-latest.yaml`,
  itself a symlink to `dist/v6/ATLAS-2026.09.yaml`. Format `6.0.0`, content
  release `2026.09` (`collection.version`), released 2026-09-15
  (`dist/manifest.yaml`); byte-identical to the `v2026.09` GitHub release
  asset. The session plan named content `2026.05`; four monthly releases
  have shipped since.
- `stix-atlas.json` is **not** in `atlas-data/dist/`. It is a release asset
  of `v2026.09` (STIX 2.1, generated from the same YAML by
  `tools/atlas_to_stix.py`). The copy in `mitre-atlas/atlas-navigator-data`
  is stale (collection `0.1`, 170 techniques, no ATT&CK references) and
  must not be used.
- Format 6.0.0 keys objects by id: `tactics` 16 (`AML.TA####`),
  `techniques` 208 (120 `AML.T####`, 88 `AML.T####.###`), `mitigations` 40
  (`AML.M####`), `case-studies` 73 (`AML.CS####`), and a separate
  `relationships` map (1,355 entries) typed `achieves` (technique →
  tactic, 225), `specializes` (sub-technique → technique, 88; always the
  id prefix), `mitigates` (mitigation → technique, 361), `employs` (case
  study → technique, 665) and `sequences` (matrix → tactic with
  `position`, 16).
- **The field that declares adaptation from ATT&CK is `attack-reference`**
  (`{id, url}`), an optional attribute of the ATLAS object itself: on 44
  techniques (31 top-level, 13 sub-techniques; 39 distinct ATT&CK targets),
  on 14 tactics and on 4 mitigations. In STIX it is the
  `external_references[]` entry with `source_name = "mitre-attack"`
  (62 = 44 + 14 + 4). There is no relationship object for it and no
  other field (`description` prose aside) that links ATLAS to ATT&CK.

Rules of this repo that constrain the design:

1. **Hard Rule 2.** The chain `CPE → CVE/CVSS → CWE → CAPEC → ATT&CK →
   {D3FEND, CAR, SHIELD, ENGAGE}` is the standard; no shortcut edges.
   ATLAS techniques look like ATT&CK techniques, so the temptations are
   `CAPEC → ATLAS` (IMPLEMENTS), `ATLAS → D3FEND` (MITIGATED_BY) and
   treating an ATLAS technique *as* a `Technique`.
2. **Hard Rule 5.** Source-specific identifiers never mix across
   taxonomies: `AML.T0050` is not `T1059`, even when ATLAS says one was
   adapted from the other.
3. **Hard Rule 1.** `attck-ontology-v1.0.owl` is frozen; ATLAS cannot be
   added to it.

## Decision

### D1 — Parallel matrix in its own namespace, four labels

A new standard-scoped module `ontology/standards/atlas-ontology-v1.0.owl`
in a new namespace `atlas:` (`http://www.motherhacker.me/kgcs/ontology/atlas#`,
registered in `docs/namespace-policy-v1.2.md`):

| OWL class | Graph label | Source | Key |
| --- | --- | --- | --- |
| `atlas:AtlasTactic` | `AtlasTactic` | `tactics` | `atlasId` `AML.TA####` |
| `atlas:AtlasTechnique` | `AtlasTechnique` | `techniques` without a `specializes` edge | `atlasId` `AML.T####` |
| `atlas:AtlasSubTechnique` | `AtlasSubTechnique` | `techniques` with a `specializes` edge | `atlasId` `AML.T####.###` |
| `atlas:AtlasMitigation` | `AtlasMitigation` | `mitigations` | `atlasId` `AML.M####` |

The four classes are pairwise disjoint and disjoint with the ATT&CK and
Core classes they resemble (`kgcs:Technique`, `kgcs:Tactic`,
`attack:SubTechnique`, `kgcs:AttackPattern`, `kgcs:DefensiveTechnique`).
Labels carry the `Atlas` prefix so no Cypher `MATCH (t:Technique)` ever
returns an ATLAS node. `AtlasSubTechnique` is **not** declared a subclass of
`AtlasTechnique`: the graph keeps separate labels, and the ATT&CK module's
`SubTechnique ⊑ Technique` axiom is exactly the OWL-vs-graph contradiction
recorded in `attck-core-alignment-v1.0.owl`; this module does not repeat it.
Datatype properties are camelCase and equal to the graph property names,
as in the ATT&CK module (`atlasId`, `name`, `description`, `maturity`,
`platforms`, `createdDate`, `modifiedDate`, `matrixPosition`, `categories`,
`lifecyclePhases`).

### D2 — Edges inside ATLAS: PART_OF, SUBTECHNIQUE_OF, MITIGATES (ATLAS-scoped)

```
(:AtlasTechnique|AtlasSubTechnique)-[:PART_OF]->(:AtlasTactic)          source: achieves
(:AtlasSubTechnique)-[:SUBTECHNIQUE_OF]->(:AtlasTechnique)              source: specializes
(:AtlasMitigation)-[:MITIGATES]->(:AtlasTechnique|AtlasSubTechnique)    source: mitigates
```

OWL: `atlas:part_of`, `atlas:subtechnique_of` (functional),
`atlas:mitigates` — new properties in `atlas:`, **not** aligned to
`attack:contains_by`, `kgcs:belongs_to`, `attack:subtechnique_of` or
`kgcs:mitigated_by`. The graph relationship *types* `PART_OF` and
`SUBTECHNIQUE_OF` are reused because they mean the same thing inside a
matrix; they are **scoped by label**: an ATLAS `PART_OF` always goes from an
`Atlas*` node to an `AtlasTactic`, never to or from an ATT&CK node
(`shapes/atlas.shacl.ttl`). `MITIGATES` keeps the source's direction
(mitigation → technique), unlike the chain's `MITIGATED_BY` (technique →
D3FEND), because it is a different relation from a different publisher.

- `PART_OF` is written for **every** `achieves` entry, including the 94 on
  sub-techniques. This differs from the ATT&CK graph, where
  `SubTechnique` nodes carry no `PART_OF`; the ATLAS source states the
  sub-technique's tactic explicitly, and in 2026.09 every sub-technique's
  tactics are a subset of its parent's (0 exceptions; a Warning shape
  guards it). Open question 2.
- `sequences` (matrix → tactic, `position`) becomes the datatype property
  `matrixPosition` on `AtlasTactic` (1–16). There is no matrix node: ATLAS
  has one matrix.
- `mitigates[].description` (present on all 361) is not mapped in v1.0
  (Exclusions).

### D3 — Not a hop of the chain: no CAPEC → ATLAS, no ATLAS → defences

ATLAS is beside ATT&CK, not after CAPEC and not before D3FEND:

- **Closed shapes.** The four node shapes are `sh:closed`: an ATLAS node may
  carry only its own datatype properties and the ATLAS edges above, plus
  `ADAPTED_FROM`. `AtlasTechnique → DefensiveTechnique` (`kgcs:mitigated_by`),
  `→ DetectionAnalytic`, `→ DeceptionTechnique`, `→ Weakness` … are
  Violations (`atlas-technique-to-d3fend.ttl`).
- **Boundary guard.** `atlas:AtlasBoundaryShape` (SHACL-SPARQL on
  `?s ?p $this`) rejects any edge **into** an ATLAS node whose subject is
  not an ATLAS node or whose predicate is not an ATLAS edge.
  `AttackPattern -[IMPLEMENTS]-> AtlasTechnique` (`capec-implements-atlas.ttl`)
  and `Technique -[SUBTECHNIQUE_OF]-> AtlasTechnique` are Violations.
- No ATLAS term is aligned to a Core term; no alignment module is added.
  Agent templates never mix `Technique` and `AtlasTechnique` in one path
  except through `ADAPTED_FROM` (contract invariant 10).

### D4 — ADAPTED_FROM: the only cross-standard edge, with the source field as provenance

```
(:AtlasTechnique|AtlasSubTechnique)-[:ADAPTED_FROM {sourceField, attackReferenceId, attackReferenceUrl}]->(:Technique|SubTechnique)
```

- Written **only** where the ATLAS object carries `attack-reference`; never
  inferred from names, descriptions or tactic overlap. One edge per ATLAS
  technique (the field is single-valued); a target may receive several
  (`T1596` ← 3, `T1595` ← 3, `T1211` ← 2).
- Target resolution: the ATT&CK `attackId` equal to `attack-reference.id`,
  `Technique` for `T####`, `SubTechnique` for `T####.###`. Levels need not
  match (31 technique → technique, 8 sub → sub, 5 sub → technique). The
  shared bridge rule of `attck-to-owl-v1.0.md` (v1.1) applies unchanged:
  revoked targets are remapped along `revoked-by`, deprecated targets are
  dropped, and unresolved ids are dropped and counted.
- Provenance on the edge: `sourceField` (always `"attack-reference"`),
  `attackReferenceId` and `attackReferenceUrl` (both verbatim from the
  source). In RDF the edge is reified as one `atlas:AdaptedFromStatement`
  per `atlas:adapted_from` triple, the ADR-0002 `CAUSED_BY` pattern.
  Missing provenance is a Violation (there are no legacy ADAPTED_FROM
  edges); a target whose `attackId` differs from `attackReferenceId` is a
  Warning (legitimate only after a revoked-by remap).
- `atlas:adapted_from` has no inverse: ATT&CK nodes gain no outgoing edge,
  and the ATT&CK shapes are unchanged.
- Resolution on `kgcs-v11` (2026-09-27): 38 of 39 distinct targets exist
  (30 `Technique`, 8 `SubTechnique`, all `enterprise`); `T1656`
  (Impersonation, cited by `AML.T0073`) is absent from the loaded ATT&CK
  bundles. Expected on a `kgcs-v11`-equivalent chain: **43 edges** from 44
  source rows, 1 unresolved.

### D5 — Scope of module v1.0

In: the four classes, the four edges, the properties in D1.
Out (listed in the Exclusions table of the coverage matrix):

- **Case studies** (`AML.CS####`, 73: 50 `Exercise`, 23 `Incident`; 665
  `employs` edges with `tactic`, `step-id`, `leads-to` procedure steps).
  They are incidents and red-team exercises: the ATLAS analogue of ATT&CK
  Groups/Campaigns, which KGCS does not load either. **Candidate** for an
  `AtlasCaseStudy` module (v1.1 of this module, own ADR): label
  `AtlasCaseStudy`, edge `EMPLOYS` with the step metadata as edge
  properties, `type`, `date` + `date-granularity`, `actor`, `target`,
  `reporter`.
- `attack-reference` on **tactics** (14) and **mitigations** (4): not
  mapped. A tactic bridge is possible (all 14 targets are enterprise
  tactics) but the card scopes `ADAPTED_FROM` to techniques; KGCS has no
  ATT&CK mitigation class, so the mitigation references have no target.
  Open question 3.
- `references[]` (bibliography), `uuid`, per-relationship `description`.

### D6 — Build metadata

`shapes/build.shacl.ttl` v1.2 adds `ATLAS` to the `sourceSnapshots`
vocabulary: `ATLAS=<collection.version>` (e.g. `ATLAS=2026.09`). The
loader reads the versioned file `dist/v6/ATLAS-<release>.yaml` (or the
release asset), not the `ATLAS-latest.yaml` symlink, so the value is
reproducible.

### Validation (`shapes/atlas.shacl.ttl`)

Six node shapes: `atlas:AtlasTacticShape`, `atlas:AtlasTechniqueShape`,
`atlas:AtlasSubTechniqueShape`, `atlas:AtlasMitigationShape` (closed; id
patterns, vocabularies, cardinalities; sub-technique id prefix = parent id
and tactic subset by SPARQL), `atlas:AdaptedFromStatementShape`
(provenance fields, target class, one statement per edge, edge exists) and
`atlas:AtlasBoundaryShape` (incoming-edge guard over the four classes).
Negative fixtures, at least one per shape, pinned in
`tests/fixtures/negative/manifest.json`.

## Alternatives considered

**A1 — ATLAS techniques as ATT&CK `Technique` nodes with `domains = ["atlas"]`.**
Reuses every ATT&CK template and shape. Rejected: breaks Rule 5 (`AML.*`
ids under `attackId`), pulls ATLAS into the chain (a CAPEC `IMPLEMENTS` or
D3FEND `MITIGATED_BY` edge to an ATLAS technique would become valid), and
`attck.shacl.ttl` closes `domains` to enterprise | mobile | ics.

**A2 — Extend the chain: `AttackPattern → AtlasTechnique` or `AtlasTechnique → D3FEND`.**
Rejected: no source declares either edge (CAPEC has no ATLAS mappings;
D3FEND has none), so each would be KGCS inference; and Hard Rule 2.

**A3 — `ADAPTED_FROM` as `owl:equivalentClass` / `skos:exactMatch` between
individuals.** Rejected: ATLAS says *adapted from*, not *identical to*; the
AI-specific scope differs; and an equivalence would let reasoners merge
ids across taxonomies (Rule 5).

**A4 — No ATT&CK link at all.** Simplest. Rejected: the source declares
44 adaptations; dropping a published cross-reference loses the only way an
agent can go from an AI-system technique to the enterprise defences
reachable from ATT&CK (read-only, through `ADAPTED_FROM`, never as a
chain hop).

**A5 — Separate edge names (`ACHIEVES`, `SPECIALIZES`) instead of reusing
`PART_OF` / `SUBTECHNIQUE_OF`.** Avoids any count collision with ATT&CK.
Not chosen because the session card fixes the names and the edges mean
the same thing inside a matrix; the collision risk is handled by label
scoping (D2) and the consequence below. Open question 1.

**A6 — STIX (`stix-atlas.json`) as the source of record.** Same counts, but
drops `maturity` and ATLAS's own relationship types. The YAML is chosen;
the STIX equivalents are listed in the mapping doc for cross-checking.

## Consequences

- **Spec:** new module, shape file, mapping doc; `build.shacl.ttl` v1.2
  gains `ATLAS`; namespace policy v1.2 gains `atlas:`; contract labels
  `AtlasTactic`, `AtlasTechnique`, `AtlasSubTechnique`, `AtlasMitigation`,
  edges `PART_OF` / `SUBTECHNIQUE_OF` (ATLAS-scoped), `MITIGATES`,
  `ADAPTED_FROM`; invariant 10. No frozen file is modified; ATT&CK shapes
  and Core are untouched.
- **Counts that change in the graph.** `PART_OF` (+225) and
  `SUBTECHNIQUE_OF` (+88) grow when ATLAS is loaded. Every count, export or
  post-load check of these two types **must qualify the labels**
  (`(:Technique)-[:PART_OF]->(:Tactic)`, `(:SubTechnique)-[:SUBTECHNIQUE_OF]->(:Technique)`).
  The existing checks do (`attck-to-owl-v1.0.md`, coverage matrix ETL
  priority 7); the snapshot v12 exports and the `extract_neo4j_stats.py`
  minimums in session Q18/Q19 must be checked for unqualified counts
  before the chain-equivalence gate.
- **Pipeline (session Q18, not done here):** downloader `mitre_atlas`
  (versioned YAML, pinned release); `load_atlas.py` after `load_attck.py`
  (ADAPTED_FROM needs the ATT&CK nodes); unique constraint on `atlasId`
  per label; expected counts 16 / 120 / 88 / 40 nodes, 225 `PART_OF`, 88
  `SUBTECHNIQUE_OF`, 361 `MITIGATES`, `ADAPTED_FROM` = 44 − unresolved (43
  against the `kgcs-v11` ATT&CK load); post-load checks in
  `mappings/atlas-to-owl-v1.0.md`. **Chain loaders must show an empty diff.**
- **Agents (`kgcs-server`):** ATLAS is a separate entry point (an AI-system
  technique), not a continuation of a CVE path. A template may go
  `AtlasTechnique -[:ADAPTED_FROM]-> Technique` and then use the ATT&CK
  defensive edges, and must say so in `provenance` (the hop is ATLAS's
  `attack-reference`, not KGCS inference).
- **Research:** the T1656 gap (ATT&CK technique cited by ATLAS but absent
  from the `kgcs-v11` ATT&CK load) is a data-quality finding for the ATT&CK
  loader, outside this ADR.

## Open questions — resolved on acceptance (2026-09-27)

HC accepted this ADR as written on 2026-09-27 (commit `1ace23a`). No separate
answer was recorded per question, so each one below resolves to the option the
*Decision* section implements (the one marked *proposed* when the question was
raised). Recorded by the session on 2026-09-27 from that acceptance. Reversing
any item is a CHANGELOG note on a v1.2.x, not a silent edit of this list.

1. **Edge names.** Reuse `PART_OF` / `SUBTECHNIQUE_OF` scoped by label
   (proposed, as the card specifies) or introduce `ACHIEVES` /
   `SPECIALIZES` (A5) so no ATT&CK count can ever include ATLAS edges?

   **Resolved:** Reuse `PART_OF` / `SUBTECHNIQUE_OF` scoped by label (D2), as the session card specifies. Consumers must qualify both endpoint labels in every count (see *Upgrade notes*).

2. **`PART_OF` on sub-techniques.** Write all 225 `achieves` entries
   (proposed; the source states them) or only the 131 on top-level
   techniques, mirroring the ATT&CK graph?

   **Resolved:** All 225 `achieves` entries, sub-techniques included: the source states them.

3. **Tactic `attack-reference`.** Add `ADAPTED_FROM` from `AtlasTactic` to
   enterprise `Tactic` (14 edges, all targets exist on `kgcs-v11`), or keep
   the bridge technique-only (proposed for v1.0)?

   **Resolved:** Bridge technique-only in v1.0. `AtlasTactic → Tactic` (14 edges) stays a v1.2.x candidate.

4. **Case studies.** Confirm out of v1.0 and whether an `AtlasCaseStudy`
   module (D5) is wanted for v1.3.

   **Resolved:** Case studies out of v1.0. An `AtlasCaseStudy` module (D5) is a candidate for the phase-C release (v1.3), decided there.

5. **`maturity` and `platforms`.** Stored verbatim with closed vocabularies
   (`Feasible | Demonstrated | Realized`; `Enterprise | Predictive AI |
   Generative AI | Agentic AI`): a new value in a future release fails
   validation until the shape is updated. Confirm the strictness
   (Violation), or downgrade to Warning.

   **Resolved:** Closed vocabularies for `maturity` and `platforms` at Violation: a new source value fails validation until the shape is updated, which is the intended signal.

6. **T1656.** Record the missing ATT&CK technique as a finding for the
   ATT&CK loader / bundle refresh (proposed), or block Q18 on it?

   **Resolved:** `T1656` recorded as a finding for the ATT&CK loader / bundle refresh (session Q18 report); Q18 is not blocked on it.
