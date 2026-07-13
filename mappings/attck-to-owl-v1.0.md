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
| `x_mitre_domains` | `attack:domain` | Array of domains (`enterprise-attack`, `mobile-attack`, `ics-attack`) |
| `x_mitre_version` | `attack:attackVersion` | Version string |
| `x_mitre_modified_by_ref` | `attack:modifiedBy` | Reference to MITRE identity |
| `kill_chain_phases.phase_name` | `attack:shortname` | Link Technique → Tactic |
| `kill_chain_phases.kill_chain_name` | `attack:killChainName` | `mitre-attack`, `mitre-mobile-attack`, `mitre-ics-attack` |

## Relationship Mapping

| Source Structure | Ontology Edge |
| ---------------- | ------------- |
| `x_mitre_parent` (Technique → Tactic) | `attack:contains` (`Tactic` → `Technique`) |
| `subtechnique_of` (Technique → Technique) | `attack:subtechnique_of` |
| `uses` (Group/Software → Technique) | `attack:uses` |
| `detects` (DataComponent → Technique) | `attack:detects` |
| `targets` (Technique → Asset) | `attack:targets` |
| `references` (DataSource/Component → Analytic) | `attack:references` |
| `x_mitre_domain` (Technique → Domain) | `attack:belongsToDomain` |

## Transformation Notes

- All `x_mitre_id` values are preserved as literal strings via `attack:attackId`.
- Deprecated fields (`x_mitre_detection`) are still mapped for backward compatibility but will be removed in the next major release.
- The `kill_chain_phases` array is flattened: each element becomes a `attack:shortname` + `attack:killChainName` edge from the Technique to the corresponding Tactic.
- For sub‑techniques, the `x_mitre_is_subtechnique` flag is asserted via `attack:isSubtechnique`.
- The `created_by_ref` and `x_mitre_modified_by_ref` fields are linked to a `attack:Identity` node (not shown in this mapping, but available in the MITRE identity ontology).
- All timestamp fields (`created`, `modified`) are kept in ISO‑8601 UTC format.
