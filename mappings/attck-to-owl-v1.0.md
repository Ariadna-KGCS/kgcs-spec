# ATT&CK to OWL Mapping v1.0

## Sources

- MITRE ATT&CK STIX v2.1 repository (enterprise, mobile, ics, pre‑ATT&CK) – see `data/attack/schemas/` and `data/attack/raw/`
- ATT&CK STIX 2.1 JSON schema (`data/schemas/ATTCK-STIX/`)

## Target Ontology

- `ontology/standards/attck-ontology-v1.0.owl` – will be created in the standards layer
- Core classes: `attack:Tactic`, `attack:Technique`, `attack:SubTechnique`, `attack:Group`, `attack:Software`, `attack:DataSource`, `attack:DataComponent`, `attack:Asset`, `attack:DetectionStrategy`, `attack:Analytic`, `attack:LogSource`

## Entity Mapping

| Source Record | Target Class | Primary ID |
| ------------- | ------------ | ---------- |
| ATT&CK `x_mitre_tactic` | `attack:Tactic` | `x_mitre_id` (`TAxxxx`) |
| ATT&CK `x_mitre_attack_pattern` | `attack:Technique` | `x_mitre_id` (`Txxxx` or `Txxxx.yyy` for sub‑techniques) |
| ATT&CK `intrusion-set` | `attack:Group` | `x_mitre_id` (`Gxxxx`) |
| ATT&CK `malware` / `tool` | `attack:Software` | `x_mitre_id` (`Sxxxx` / `Mxxxx`) |
| ATT&CK `data-source` | `attack:DataSource` | `x_mitre_id` (`DSxxxx`) |
| ATT&CK `data-component` | `attack:DataComponent` | `x_mitre_id` (`DCxxxx`) |
| ATT&CK `asset` | `attack:Asset` | `x_mitre_id` (`Axxxx`) |
| ATT&CK `detection_strategy` | `attack:DetectionStrategy` | `x_mitre_id` (`DETxxxx`) |
| ATT&CK `analytic` | `attack:Analytic` | `x_mitre_id` (`ANxxxx`) |
| ATT&CK `log_source` | `attack:LogSource` | `x_mitre_id` (`LSxxxx`) |

## Field Mapping

| STIX Field | Ontology Property | Notes |
| ---------- | ----------------- | ----- |
| `x_mitre_id` | `attack:attackId` | Primary identifier |
| `name` | `rdfs:label` | Human‑readable name |
| `description` | `dct:description` | Long description |
| `x_mitre_tactic_type` | `attack:tacticType` | Mobile domain only |
| `x_mitre_is_subtechnique` | `attack:isSubtechnique` | Boolean |
| `x_mitre_platforms` | `attack:platform` | Array of platform strings |
| `x_mitre_data_sources` | `attack:dataSource` | Array of DataSource references |
| `x_mitre_data_components` | `attack:dataComponent` | Array of DataComponent references |
| `x_mitre_detection` | `attack:detection` | Deprecated (v3.3.0) |
| `created` | `dct:created` | Timestamp |
| `modified` | `dct:modified` | Timestamp |
| `created_by_ref` | `attack:createdBy` | Reference to MITRE identity |
| `confidence` | `attack:confidence` | Integer 1–99 |
| `lang` | `dct:language` | Language code |
| `revoked` | `attack:revoked` | Boolean |
| `labels` | `dct:subject` | Array of tags |
| `external_references` | `attack:references` | Array of Reference nodes |
| `granular_markings` | `attack:granularMarkings` | Array of Marking objects |
| `extensions` | `attack:extensions` | Dictionary of extensions |
| `x_mitre_domains` | `attack:domain` | Array of domains (`enterprise-attack`, `mobile-attack`, `ics-attack`); graph layer uses the short form `enterprise` / `mobile` / `ics` (v1.1 section below) |
| `x_mitre_version` | `attack:attackVersion` | Version string |
| `x_mitre_modified_by_ref` | `attack:modifiedBy` | Reference to MITRE identity |
| `kill_chain_phases.phase_name` | `attack:shortname` | Link Technique → Tactic |
| `kill_chain_phases.kill_chain_name` | `attack:killChainName` | `mitre-attack`, `mitre-mobile-attack`, `mitre-ics-attack` |

## Relationship Mapping

| Source Structure | Ontology Edge |
| ---------------- | ------------- |
| `kill_chain_phases[]` (Technique → Tactic, resolved per v1.1 rule below) | `attack:contains_by` (`Technique` → `Tactic`, graph `PART_OF`); inverse `attack:contains` |
| `subtechnique_of` (Technique → Technique) | `attack:subtechnique_of` |
| `uses` (Group/Software → Technique) | `attack:uses` |
| `detects` (DataComponent → Technique) | `attack:detects` |
| `targets` (Technique → Asset) | `attack:targets` |
| `references` (DataSource/Component → Analytic) | `attack:references` |
| `x_mitre_domain` (Technique → Domain) | `attack:belongsToDomain` |

## Transformation Notes

- All `x_mitre_id` values are preserved as literal strings via `attack:attackId`.
- Deprecated fields (`x_mitre_detection`) are still mapped for backward compatibility but will be removed in the next major release.
- The `kill_chain_phases` array is flattened: each element becomes a `attack:shortname` + `attack:killChainName` edge from the Technique to the corresponding Tactic, resolved inside the same STIX bundle (v1.1 rule below — never by `phase_name` alone).
- For sub‑techniques, the `x_mitre_is_subtechnique` flag is asserted via `attack:isSubtechnique`.
- The `created_by_ref` and `x_mitre_modified_by_ref` fields are linked to a `attack:Identity` node (not shown in this mapping, but available in the MITRE identity ontology).
- All timestamp fields (`created`, `modified`) are kept in ISO‑8601 UTC format.

## v1.1 — Technique → Tactic resolution and domains

Added in kgcs-spec v1.1.0 after the 2026-09-26 graph-quality review. On that
snapshot, 618 of 1,054 `PART_OF` edges (59%) linked a technique to a tactic
of another matrix. The loader had matched `Tactic {phaseName}`, and eleven
phase names (`execution`, `persistence`, `discovery`, …) exist in more than
one matrix under different tactic IDs (enterprise `TA0002`, mobile `TA0041`,
ICS `TA0104` are all `execution`).

**Resolution rule (normative).** For each `kill_chain_phases[]` entry of an
`attack-pattern`, resolve the tactic **inside the same STIX bundle**: take
the `x-mitre-tactic` of that bundle whose `x_mitre_shortname` equals
`phase_name` (and whose matrix matches `kill_chain_name`). Take its
`x_mitre_id` (`TA####`) and write `PART_OF` to the Tactic with that
`attackId`. A `Tactic` node must never be matched by `phaseName` alone:
`phaseName` is a label, not a key.

**Domains.** `x_mitre_domains` maps to the frozen `attack:domain`
(`xsd:string`, one RDF value per list member). The graph property is
`domains` (string list) on `Technique`, `SubTechnique` and `Tactic`. No new
OWL term is needed.

The graph layer uses a **short form** of the STIX values. `load_attck.py`
derives it from the bundle file name, not from `x_mitre_domains`:

| STIX `x_mitre_domains` | Graph `domains` / `attack:domain` value |
| --- | --- |
| `enterprise-attack` | `enterprise` |
| `mobile-attack` | `mobile` |
| `ics-attack` | `ics` |

`attck.shacl.ttl` v1.1 requires at least one value from `enterprise`,
`mobile`, `ics` and rejects the long form. On kgcs-demo (2026-09-26) every
Tactic (39), Technique (378) and SubTechnique (540) has exactly one value.
The divergence is recorded in `shapes/README.md` with the other graph-layer
divergences.

**Invariant.** `attack:PartOfDomainCoherenceShape` (`attck.shacl.ttl` v1.1)
checks that every domain of a Tactic a Technique is `PART_OF` is one of that
Technique's domains. The pipeline post-load equivalent is:

```cypher
MATCH (t)-[:PART_OF]->(ta:Tactic)
WHERE any(d IN ta.domains WHERE NOT d IN t.domains)
RETURN count(*)   // must be 0
```

SH-CORE-06 (`minCount 1`) is unchanged and does not cover this case.
Graphs loaded by `kgcs-pipeline` pinned to spec 1.0.0 fail this shape by
design (618 edges on kgcs-demo); the `load_attck.py` change of session Q5
fixes it.

**SUBTECHNIQUE_OF.** `attack:SubtechniqueOfDomainCoherenceShape` requires
that a SubTechnique share at least one domain with its parent. It passes on
kgcs-demo (540 edges, 0 cross-domain) and guards against regressions. The
`attackId` prefix check (`T####.###` → parent `T####`) is not implemented
(v1.2 candidate).

## v1.1 — Revoked and deprecated ATT&CK targets (loader behaviour)

This rule is shared by every bridge that points into ATT&CK: CAPEC
`IMPLEMENTS` (`capec-to-owl-v1.0.md`) and D3FEND `MITIGATED_BY`
(`d3fend-to-owl-v1.0.md`). Future bridges (e.g. CTID mappings) follow it
too.

- **Revoked targets are remapped.** Build one remap table from the loaded
  bundles' `relationship` objects with `relationship_type = revoked-by`
  (source = revoked object, target = successor). Follow it transitively to
  a live object and write the bridge edge to the successor's `attackId`.
  Remap the cited ID *before* rolling a sub-technique up to its parent:
  CAPEC's `T1562.001` goes to `T1685`, and not to the revoked `T1562`.
- **Deprecated targets are dropped and counted.** If the target, or the
  end of its `revoked-by` chain, is `x_mitre_deprecated = true`, write no
  edge. The loader reports how many edges were remapped, how many were
  dropped as deprecated, and how many were unresolved (ID not present in
  any bundle), per bridge.
- Revoked and deprecated objects themselves are still not loaded as
  nodes (`attck.shacl.ttl` header). Remapping can make two source rows hit
  the same successor; the `MERGE` collapses them into one edge.
- No new OWL term: `attack:revoked` (frozen) already names the STIX flag.
  The remap is ETL behaviour, and the resulting edge is an ordinary
  `IMPLEMENTS` / `MITIGATED_BY` edge.
- The ATT&CK release loaded is recorded in `BuildMetadata.sourceSnapshots`
  as a single `ATTCK` key with a deterministic value: if all three bundles (enterprise, mobile, ics) carry an `x-mitre-collection` object with the same `x_mitre_version`, that release (`ATTCK=18.1`); otherwise `ATTCK=download:<date>;modified-max:<max modified across the three bundles>`. The `x-mitre-matrix` `x_mitre_version` (2.0 / 1.0) is that object's own version, not the ATT&CK release, and is never used. Today's STIX 2.0 bundles carry no `x-mitre-collection`, so the value is `ATTCK=download:2026-09-06;modified-max:2026-08-04` (`mapping-coverage-matrix-v1.1.md`, "Build metadata";
  `shapes/build.shacl.ttl` header).
