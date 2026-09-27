# Mapping Coverage Matrix v1.2

Purpose: quick audit view of schema-to-OWL mapping coverage for ETL implementation and tests.

Supersedes `mapping-coverage-matrix-v1.1.md` (kept frozen). v1.2 adds the
decision extension (ADR-0003: CISA KEV, FIRST EPSS, CISA SSVC via NVD
`ssvcV203`), the two new build-metadata keys, and an explicit **Exclusions**
table naming what is deliberately not mapped. Every v1.1 row is carried
over unchanged unless marked *(v1.2)*; the loader status of the v1.1 rows
was re-read from the v1.1.0 release and the `kgcs-v11` load of 2026-09-27
where noted.

Status legend:

- implemented: mapped to a declared OWL term; the graph loader writes it
- partial: mapped but requires ETL rule logic or derived key generation
- planned: identified but intentionally deferred; no OWL term declared
- planned (loader): OWL term and shape exist; the loader does not write it yet
- excluded: deliberately out of scope for this release (see Exclusions)
- external: mapped to a vocabulary outside KGCS (`rdfs:`, `dct:`); not a KGCS term and not constrained by the shapes

## CPE + CPEMatch

Unchanged from v1.0 (18 rows, all implemented). Target module
`cpe-ontology-v1.0.owl`; identity keys `cpe:cpeUri`, `cpe:cpeNameId`,
`cpe:matchCriteriaId`; expansion edge `cpe:matchesPlatform` (`MATCHES_PLATFORM`).

## CVE

| Source Field | Required in Source | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| `cve.id` | yes | `cve:cveId` | implemented | Vulnerability stable ID |
| `cve.published` | yes | `cve:published` | implemented | `xsd:dateTime` (shape aligned in v1.1) |
| `cve.lastModified` | yes | `cve:lastModified` | implemented | |
| `cve.sourceIdentifier` | no | `cve:source` | implemented | |
| `cve.configurations[].nodes[].cpeMatch[]` | no | `cve:affects` | implemented (projection) | Compatibility projection over non-negated `vulnerable = true` leaves; the full expression is the applicability layer below |
| `cve.references[]` | yes | `cve:references` | partial | Reference node key strategy still implementation-defined (`cve-to-owl-v1.0.md`) |
| `cve.references[].url` | yes | `cve:referenceUrl` | implemented | Declared by `graph-labels-v1.0.owl` (v1.1) |
| `cve.metrics.ssvcV203[]` | no | see **SSVC** below | planned (loader) *(v1.2)* | Was silently ignored by `load_cvss.py` (reads `cvssMetric*` only); 38,126 ADP entries in the 2024 file alone |

## CVE applicability layer (`cve-applicability-v1.0.owl`, v1.1)

| Source Field | Required in Source | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| `configurations[i]` | no | `cve:VulnerabilityConfiguration`, `cve:has_configuration` | implemented | key `cve:vcId` = `<cveId>::CFG::<i>` |
| `configurations[i].operator` / `.negate` | no | `cve:operator`, `cve:negate` | implemented | verbatim; logic evaluated in ETL only |
| `configurations[i].nodes[j]` | no | `cve:VulnerabilityConfigurationNode`, `cve:has_node` | implemented | key `cve:vcnId` = `<vcId>::NODE::<j>`; exactly one parent |
| `nodes[j].operator` / `.negate` | no | `cve:operator`, `cve:negate` | implemented | |
| `nodes[j].cpeMatch[k].matchCriteriaId` | yes | `cve:matches_criteria` | implemented | graph `MATCHES_CRITERIA {vulnerable, matchIndex}` |
| `nodes[j].cpeMatch[k].vulnerable` | yes | `cve:matches_vulnerable_criteria` / `cve:matches_context_criteria` | implemented | RDF form of the edge flag (sub-properties) |
| `i`, `j` | derived | `cve:configIndex`, `cve:nodeIndex` | implemented | document order |

## CAUSED_BY provenance (`cve-weakness-provenance-v1.0.owl`, v1.1, ADR-0002)

| Source Field | Required in Source | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| `weaknesses[].description[].value` | yes | `kgcs:caused_by`; reified as `cve:CausedByStatement` | implemented (edge) / planned (statement) | graph `CAUSED_BY`, exactly one edge per (CVE, CWE) pair; 331,107 on `kgcs-v11` (2026-09-27), unchanged |
| `weaknesses[].source` | yes | `cve:weaknessSources` | implemented *(v1.2 status update)* | edge property `sources`, string list, verbatim; written by the Q5 `load_cwe.py` (`kgcs-v11`: 0 edges without provenance) |
| derived from `weaknesses[].source` | derived | `cve:weaknessSourceRoles` | implemented *(v1.2 status update)* | edge property `sourceRoles`: `nvd` / `adp` (`134c704f-9b21-4f2e-91b3-4a467353bcc0`, CISA ADP) / `cna`; 38,463 edges with role `adp` on `kgcs-v11` |
| `weaknesses[].type` | yes | `cve:weaknessTypes` | implemented *(v1.2 status update)* | edge property `types`: `Primary` / `Secondary`; the three lists are index-aligned, equal length |

## Decision extension (`decision-extension-v1.0.owl`, v1.2, ADR-0003)

Three leaf classes adhered to `kgcs:Vulnerability`; no row below creates an
edge to any class of the causal chain. Loader status: **planned (loader)**
throughout — session Q18 writes `load_kev.py`, `load_epss.py`,
`load_ssvc.py`. Field-level detail: `kev-to-owl-v1.0.md`,
`epss-to-owl-v1.0.md`, `ssvc-to-owl-v1.0.md`.

### KEV (CISA `known_exploited_vulnerabilities.json`, schema verified 2026-09-27)

| Source Field | Required in Source | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| `vulnerabilities[]` entry | — | `kev:KevEntry`, `kev:has_kev_entry` | planned (loader) | graph `KevEntry`, `HAS_KEV_ENTRY`; exactly one per CVE; refreshed in place |
| `cveID` | yes | `kev:cve_id` | planned (loader) | key (`cveId`, unique on the label); CISA pattern `^CVE-[0-9]{4}-[0-9]{4,19}$` |
| `vendorProject`, `product`, `vulnerabilityName`, `shortDescription`, `requiredAction` | yes | `kev:vendor_project`, `kev:product`, `kev:vulnerability_name`, `kev:short_description`, `kev:required_action` | planned (loader) | verbatim |
| `dateAdded`, `dueDate` | yes | `kev:date_added`, `kev:due_date` | planned (loader) | `xsd:date`; graph keeps `YYYY-MM-DD` strings |
| `knownRansomwareCampaignUse` | no | `kev:known_ransomware_campaign_use` | planned (loader) | `Known` / `Unknown`; absence is a Warning |
| `forensicTriage` | no | `kev:forensic_triage` | planned (loader) | `Yes` / `No` (BOD 26-04; 2026 field) |
| `notes` | no | `kev:notes` | planned (loader) | verbatim, unparsed |
| `cwes[]` | no | `kev:cwes` | planned (loader) | string list on the entry; **never `CAUSED_BY`** (ADR-0003 A4 rejected; Open question 2) |
| file `catalogVersion`, `dateReleased` | yes | `kev:catalog_version`, `kev:date_released` | planned (loader) | copied onto every entry; refresh provenance |
| file `title`, `count` | yes | — | excluded | `count` is a loader check only |

### EPSS (FIRST daily CSV, file of 2026-09-27 verified)

| Source Field | Required in Source | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| one CSV row | — | `epss:EpssScore`, `epss:has_epss` | planned (loader) | graph `EpssScore`, `HAS_EPSS`; one per CVE per score date; append-only |
| derived key | n/a | `epss:epss_id` | planned (loader) | `<cve>::EPSS::<scoreDate>` (`epssId`, unique) |
| column `cve` | yes | `epss:cve_id` | planned (loader) | verbatim |
| column `epss` | yes | `epss:score` | planned (loader) | decimal [0, 1], verbatim precision; a published datum, never derived from |
| column `percentile` | yes | `epss:percentile` | planned (loader) | decimal [0, 1] |
| header `score_date` | yes (since v2022.01.01) | `epss:score_date` (date part), `epss:score_timestamp` (verbatim) | planned (loader) | part of the key; files before 2022-02-04 have no header and are excluded |
| header `model_version` | yes | `epss:model_version` | planned (loader) | travels with every node; versions are not comparable |
| API fields `cve`, `epss`, `percentile`, `date` | — | same terms | excluded | the loader reads the CSV; the API is a check, not a source |

### SSVC (NVD `metrics.ssvcV203[]`, raw 2024 and 2026 files verified)

| Source Field | Required in Source | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| `ssvcV203[]` entry with `source` in the declared ADP list | — | `ssvc:SsvcDecision`, `ssvc:has_ssvc` | planned (loader) | graph `SsvcDecision`, `HAS_SSVC`; one per CVE per timestamp; exact duplicates collapse |
| derived key | n/a | `ssvc:ssvc_id` | planned (loader) | `<cveId>::SSVC::<timestamp>` (`ssvcId`, unique; timestamp verbatim) |
| `ssvcData.id` | no (always present on ADP entries) | `ssvc:cve_id` | planned (loader) | equals the owning CVE |
| `ssvcData.version` | yes | `ssvc:version` | planned (loader) | closed to `2.0.3` |
| `ssvcData.timestamp` | no (always present on ADP entries) | `ssvc:timestamp` | planned (loader) | `xsd:dateTime`, two lexical forms, verbatim |
| `ssvcData.options[].exploitation` / `.automatable` / `.technicalImpact` | yes | `ssvc:exploitation`, `ssvc:automatable`, `ssvc:technical_impact` | planned (loader) | `{none, poc, active}`, `{no, yes}`, `{partial, total}` |
| `ssvcData.role` | yes | `ssvc:role` | planned (loader) | verbatim (`CISA Coordinator`) |
| `source` | yes | `ssvc:source` | planned (loader) | verbatim NVD source identifier |
| derived from `source` | derived | `ssvc:source_role` | planned (loader) | ADR-0002 rule; v1.2 admits `adp` only |
| entries by non-ADP sources (`9119a7d8-…` CISA-as-CNA; CNA-role entries without timestamp) | — | — | excluded | dropped and counted per source (ADR-0003 Open question 1) |
| `ssvcData.computed`, `decisionTree`, `decisionTreeUrl`, `generator`, `$schema` | no | — | excluded | optional in the SSVC schema; absent from every NVD entry verified |

## CWE

| Source Field | Required in Source | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| CWE ID | yes | `cwe:cweId` | implemented | Weakness stable ID |
| `@Abstraction` | no | `cwe:abstraction` | implemented | Pillar/Class/Base/Variant/Compound |
| `Related_Attack_Patterns` | no | `kgcs:exploited_by` | implemented | graph `DEMONSTRATED_BY` (Weakness → AttackPattern), written by `load_capec.py` from CAPEC `Related_Weaknesses` |

### CWE enrichment (`cwe-enrichment-v1.0.owl`, v1.1)

Implemented by the Q6 `load_cwe.py` and present on `kgcs-v11` (14 Weakness
properties, `description` on every Weakness; 2026-09-27) *(v1.2 status
update; v1.1 listed these rows as planned (loader))*.

| Source Field | Required in Source | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| `Description` | yes | `cwe:description` | implemented | |
| `Extended_Description` | no | `cwe:extended_description` | implemented | StructuredText flattened |
| `Mapping_Notes/Usage` | yes | `cwe:mapping_usage` | implemented | enum (4) |
| `Mapping_Notes/Reasons/Reason/@Type` | no | `cwe:mapping_reasons` | implemented | enum (12), multi-valued |
| `@Structure` | yes | `cwe:structure` | implemented | enum (3) |
| `@Status` | yes | `cwe:status` | implemented | enum (6) |
| `Alternate_Terms/Alternate_Term/Term` | no | `cwe:alternate_terms` | implemented | terms only |
| `Likelihood_Of_Exploit` | no | `cwe:likelihood_of_exploit` | implemented | enum (4) |
| `Functional_Areas/Functional_Area` | no | `cwe:functional_areas` | implemented | enum (20) |
| `Affected_Resources/Affected_Resource` | no | `cwe:affected_resources` | implemented | enum (5) |
| `Modes_Of_Introduction/Introduction/Phase` | no | `cwe:modes_of_introduction` | implemented | enum (17), deduplicated |
| `Weakness_Ordinalities/Weakness_Ordinality/Ordinality` | no | `cwe:ordinalities` | implemented | enum (3) |

### CWE consequences (`cwe-consequences-v1.0.owl`, v1.1, ADR-0001)

Implemented by the Q6 loaders: 2,051 `Consequence` nodes on `kgcs-v11`
(CWE 1,237 + CAPEC 814) *(v1.2 status update)*.

| Source Field | Required in Source | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| `Common_Consequences/Consequence` | no | `cwe:Consequence`, `cwe:has_consequence` | implemented | one sub-node per record; key `cwe:consequence_id` = `<cweId>-C<ordinal>` |
| `Consequence/Scope` | yes | `cwe:scope` | implemented | 1..N inside the record |
| `Consequence/Impact` | yes | `cwe:technical_impact` | implemented | 1..N; 25-value CWE vocabulary, never merged with CAPEC |
| `Consequence/Likelihood` | no | `cwe:consequence_likelihood` | implemented | |
| `Consequence/Note` | no | `cwe:consequence_note` | implemented | flattened |

## CVSS

| Source Field | Required in Source | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| `metrics.cvssMetric*.cvssData.baseScore` | yes (per score entry) | `cvss:baseScore` | implemented | 0.0–10.0 |
| `cvssData.version` or metric discriminator | yes | `cvss:version` | implemented | enum 2.0 / 3.0 / 3.1 / 4.0, never merged |
| derived score key | n/a | `cvss:scoreId` | implemented | `<cveId>_<version>` (pattern enforced by `cvss.shacl.ttl`) |
| CVE-to-score linkage | n/a | `cvss:hasScore` | implemented | graph `HAS_SCORE`; one Score node per source score entry, no duplicate version per CVE (post-load check) |
| `metrics.cvssMetric*[].source` / `.type` | yes | — | planned | `load_cvss.py` prefers the `Primary` entry and discards CNA secondary scores: the one hop without the ADR-0002 double provenance (candidate ADR, phase C) |

## CAPEC

| Source Field | Required in Source | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| `@ID` | yes | `capec:capecId` | implemented | graph value `CAPEC-<n>` (patterned string); OWL v1.0 range `xsd:integer` is the recorded deviation |
| `@Name` | yes | `capec:name` | implemented | |
| `@Abstraction`, `@Status` | yes | `capec:abstraction`, `capec:status` | implemented | Q6 loader writes `abstraction`, `typicalSeverity`, `attackLikelihood` *(v1.2 status update)* |
| `Related_Weaknesses` | yes | `kgcs:exploited_by` (inverse direction) | implemented | graph `DEMONSTRATED_BY` from Weakness |
| `Related_Attack_Patterns` (ChildOf) | no | `capec:childOf` | implemented | graph `CHILD_OF` (AttackPattern → AttackPattern); 533 on `kgcs-v11` after the Q5 ordering fix |
| `Taxonomy_Mappings` (ATT&CK) | no | `kgcs:implemented_as` | implemented | graph `IMPLEMENTS` (AttackPattern → Technique), written by `load_attck.py`; v1.1 revoked/deprecated rule applied (244 edges on `kgcs-v11`) |
| `Consequences/Consequence` | no | `capec:Consequence`, `capec:hasConsequence`, `capec:scope`, `capec:technicalImpact`, `capec:consequenceLikelihood` (frozen) + `capec:consequence_id`, `capec:consequence_note` (`capec-consequences-v1.0.owl`) | implemented *(v1.2 status update)* | ADR-0001; Impact optional (CAPEC XSD `minOccurs=0`); 10-value CAPEC vocabulary; 814 nodes on `kgcs-v11` |
| Categories, Views, Execution_Flow, Skills, Resources, Indicators, Mitigations, Example_Instances | no | see audit below | planned | `capec-to-owl-v1.0.md` cites terms not declared by any OWL module |

## ATT&CK

Corrected against `attck-ontology-v1.0.owl`, `attck-core-alignment-v1.0.owl`
and `graph-labels-v1.0.owl`. The v1.0 rows that mapped to `rdfs:`/`dct:`
vocabulary or to undeclared `attack:` terms are marked accordingly.

| STIX Field | Required in Source | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| `x_mitre_id` | yes | `attack:attackId` | implemented | `T####`, `T####.###`, `TA####` |
| `name` | yes | `attack:name` | implemented | v1.1 (`graph-labels-v1.0.owl`); v1.0 cited `rdfs:label` |
| `kill_chain_phases.phase_name` | no | `attack:phaseName` (Tactic), `attack:contains_by` ≡ `kgcs:belongs_to` (Technique → Tactic) | implemented *(v1.2 status update; v1.1: partial)* | graph `PART_OF`; the Q5 loader resolves the tactic by `attackId` inside the same STIX bundle: 436 edges on `kgcs-v11`, 0 cross-domain (was 1,054 / 618) |
| `x_mitre_is_subtechnique` | no | `attack:isSubtechnique` | implemented (OWL) | graph keeps a separate `SubTechnique` label |
| `relationship_type = subtechnique-of` | no | `attack:subtechnique_of` ⊑ `kgcs:subtechnique_of` | implemented | graph `SUBTECHNIQUE_OF`, exactly one parent |
| `external_references` (CAPEC) | no | `kgcs:implemented_as` | implemented | graph `IMPLEMENTS`, parent techniques only |
| `x_mitre_platforms` | no | `attack:platform` | implemented (OWL) | loader coverage not re-verified |
| `x_mitre_domains` | no | `attack:domain` | implemented | graph `domains` string list on Technique, SubTechnique and Tactic, short form `enterprise` / `mobile` / `ics` (from the bundle file name); required since `attck.shacl.ttl` v1.1; SUBTECHNIQUE_OF domain coherence added |
| `relationship_type = revoked-by`, `x_mitre_deprecated` | no | none (loader behaviour) | implemented *(v1.2 status update)* | Q5 `load_attck.py` / `load_d3fend.py` remap revoked targets and drop deprecated ones (`IMPLEMENTS` 244, `MITIGATED_BY` 3,087 on `kgcs-v11`) |
| `x_mitre_version`, `revoked`, `confidence`, `created_by_ref`, `x_mitre_modified_by_ref`, `x_mitre_tactic_type` | no | `attack:attackVersion`, `attack:revoked`, `attack:confidence`, `attack:createdBy`, `attack:modifiedBy`, `attack:tacticType` | implemented (OWL) | loader coverage not re-verified |
| `kill_chain_phases.kill_chain_name` | no | `attack:killChainName` | implemented (OWL) | `mitre-attack`, `mitre-mobile-attack`, `mitre-ics-attack` |
| `description`, `created`, `modified`, `lang`, `labels` | yes/no | `dct:description`, `dct:created`, `dct:modified`, `dct:language`, `dct:subject` | external | not KGCS terms; unconstrained by shapes |
| `x_mitre_data_sources`, `x_mitre_data_components`, `x_mitre_detection`, `granular_markings`, `extensions` | no | `attack:dataSource`, `attack:dataComponent`, `attack:detection`, `attack:granularMarkings`, `attack:extensions` | planned | cited by v1.0 rows, declared by no OWL module (classes `attack:DataSource` / `attack:DataComponent` exist; the properties do not) |

## D3FEND

| Source Field | Required in Source | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| technique class IRI fragment | yes | `d3fend:d3fendId` | implemented | `D3-<LETTERS>`; loader fallback to URI fragment (Warning pattern) |
| `rdfs:label` | yes | `d3fend:name` | implemented | v1.1 (`graph-labels-v1.0.owl`) |
| offensive-technique mapping | no | `kgcs:mitigated_by` | implemented | graph `MITIGATED_BY` (Technique → DefensiveTechnique); the only edge `load_d3fend.py` writes; v1.1 revoked/deprecated rule applied (3,087 on `kgcs-v11`) |
| `d3fend:references_cwe`, `d3fend:counters_attack_pattern` (frozen OWL) | no | as declared | planned | declared in `d3fend-ontology-v1.0.owl`, never loaded; policy call pending (shapes/README.md, D3FEND v1.1 candidates) — the same call governs KEV `cwes` (ADR-0003 Open question 2) |
| DefensiveTactic, Procedure, Capability, PrerequisiteCondition | no | `d3fend:DefensiveTactic`, `d3fend:Procedure`, `d3fend:Capability`, `d3fend:PrerequisiteCondition` | implemented (OWL) | loader coverage not re-verified |

## CAR

| Source Field | Required in Source | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| `id` | yes | `car:analyticId` | implemented | `CAR-YYYY-MM-NNN` |
| `title` | yes | `car:title` | implemented | v1.1 (`graph-labels-v1.0.owl`); v1.0 cited `rdfs:label` |
| `coverage[].technique` | yes | `kgcs:detected_by` | implemented | graph `DETECTED_BY` (Technique → DetectionAnalytic) |
| `submission_date`, `information_domain`, `platforms`, `subtypes`, `analytic_types`, `contributors` | varies | `car:submissionDate`, `car:informationDomain`, `car:applicablePlatforms`, `car:analyticSubtypes`, `car:analyticTypes`, `car:contributors` | implemented (OWL) | loader coverage not re-verified |
| data models, sensors, implementations | no | see audit below | planned | `car-to-owl-v1.0.md` cites `kgcs:CyberObservable`, `kgcs:DataSource`, `car:hasImplementation` … undeclared |

## SHIELD

| Source Field | Required in Source | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| technique `id` | yes | `shield:techniqueId` | implemented | `DTE####`; graph label `DeceptionTechnique` (OWL `shield:DefensiveTechnique ⊑ kgcs:DefensiveTechnique` is the recorded deviation) |
| technique `name` | yes | `shield:name` | implemented | v1.1 (`graph-labels-v1.0.owl`); v1.0 cited `rdfs:label` |
| ATT&CK mapping | no | `kgcs:countered_by` | implemented | graph `COUNTERED_BY` (Technique → DeceptionTechnique) |
| tactics, opportunities, use cases, procedures | no | `shield:tacticId`, `shield:opportunityId`, `shield:useCaseId`, `shield:procedureId` + classes | implemented (OWL) | loader coverage not re-verified |
| ATT&CK mapping record fields | no | `shield:mapToAttack`, `shield:attackTechniqueId`, `shield:attackTacticId` | planned | cited by `shield-to-owl-v1.0.md`, undeclared |

## ENGAGE

| Source Field | Required in Source | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| activity / approach / goal `id` | yes | `engage:activityId`, `engage:approachId`, `engage:goalId` | implemented | `[ES]AC####`, `[ES]AP####`, `[ES]GO####` (patterns derived from loader source, not re-verified against raw data) |
| `name` | yes | `engage:name` | implemented | v1.1 (`graph-labels-v1.0.owl`); v1.0 cited `rdfs:label` |
| `attack_techniques[]` | no | `kgcs:disrupts` | implemented | graph `DISRUPTS` (EngagementConcept → Technique) |
| `goals[]`, references, EAVs | no | `engage:supports_goal`, `engage:Reference`, `engage:refId`, … | implemented (OWL) | loader coverage not re-verified; `engage:approach_enables` is cited but undeclared |

## Build metadata (`build-metadata-v1.0.owl`, v1.1; `build.shacl.ttl` v1.2)

Implemented by the Q6 postscript: one `BuildMetadata` node on `kgcs-v11`
with 10 `sourceSnapshots` and `pipelineCommit` (2026-09-27) *(v1.2 status
update)*.

| Source | Required | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| pipeline `SPEC_VERSION` | yes | `build:spec_version` | implemented | |
| load completion instant | yes | `build:build_timestamp` | implemented | |
| `git rev-parse HEAD` of kgcs-pipeline | yes | `build:pipeline_commit` | implemented | |
| per-source download snapshot | yes | `build:source_snapshot` | implemented | `<SOURCE>=<snapshot>`, at most one value per SOURCE (`build.shacl.ttl` v1.1) |
| KEV catalog version | yes (v1.2) | `build:source_snapshot` | planned (loader) *(v1.2)* | `KEV=<catalogVersion>`, e.g. `KEV=2026.09.25` |
| EPSS score date + model | yes (v1.2) | `build:source_snapshot` | planned (loader) *(v1.2)* | `EPSS=<scoreDate>;model:<modelVersion>`, e.g. `EPSS=2026-09-27;model:v2026.06.15`; SSVC has no key (covered by `CVE=`) |

Snapshot value per source: the exact release loaded, taken from the source
itself wherever the source states it. Otherwise it is the download instant
recorded by the downloader.

| SOURCE | Snapshot value | Example |
| --- | --- | --- |
| `CWE` | catalogue `Version` attribute | `CWE=4.20` |
| `CAPEC` | catalogue `Version` attribute | `CAPEC=3.9` |
| `D3FEND` | ontology `owl:versionInfo` | `D3FEND=1.3.0` |
| `ATTCK` | One key for the three bundles. If all three carry an `x-mitre-collection` with the same `x_mitre_version`: that release. Otherwise `download:<date>;modified-max:<max modified across the three bundles>`. Never the `x-mitre-matrix` `x_mitre_version` (object version, not the ATT&CK release). Per-domain keys remain a candidate | `ATTCK=18.1`; today `ATTCK=download:2026-09-06;modified-max:2026-08-04` |
| `CVE`, `CPE`, `CVSS` | NVD feed / API download instant (UTC) | `CVE=2026-09-01T03:00:00Z` |
| `CAR`, `SHIELD`, `ENGAGE` | release tag if any, else repository commit or download date | `ENGAGE=1.0` |
| `KEV` *(v1.2)* | file `catalogVersion` | `KEV=2026.09.25` |
| `EPSS` *(v1.2)* | header `score_date` (date part) and `model_version` | `EPSS=2026-09-27;model:v2026.06.15` |

The frozen OWL comment on `build:source_snapshot` enumerates the ten v1.0
sources; the `sh:pattern` in `build.shacl.ttl` v1.2 is the normative
vocabulary (comment fix = OWL v1.1 candidate, same register as
`capec:capecId`).

## Exclusions (v1.2) — deliberately not mapped

Everything in this table was considered for the decision layer and left
out on purpose. A row leaves this table only through an ADR.

| Item | Why excluded | Where it may come back |
| --- | --- | --- |
| VEX (OpenVEX / CSAF VEX), CSAF advisories | Vendor exploitability statements and advisories: a second decision layer with its own actors; not in the v1.2 perimeter (`kgcs-research` D-Q7) | Paper expectation 2.0; needs its own ADR |
| purl / SBOM (CycloneDX, SPDX) | The seam between inventory and CPE; an asset-side concern, not a decision input | Experiment E6 (after the seam spec) |
| OCSF, Sigma | Telemetry and detection formats; neither a standard of the chain nor a decision input | Paper expectation 2.0 |
| KEV `cwes[]` as `CAUSED_BY` edges | Would let a decision source write the chain and change the `CAUSED_BY` count (ADR-0003 A4) | ADR-0003 Open question 2, with the D3FEND `references_cwe` policy call |
| KEV file `title`, `count` | File metadata; `count` is a loader check | — |
| KEV CSV twin (`known_exploited_vulnerabilities.csv`) | Same content as the JSON | — |
| EPSS API (`api.first.org/data/v1/epss`) | Same values at 9 decimals; the CSV is the source of record with the model header | Loader check only |
| EPSS files before 2022-02-04 (EPSS v1) | No header line, so no `model_version` / `score_date`; not loadable by this mapping | — |
| EPSS daily history back-fill | A load parameter (how many files), not a mapping change | ADR-0003 Open question 3 (Q18/Q20) |
| SSVC entries by non-ADP sources | CISA-as-CNA (`9119a7d8-…`) is timestamped but is a CNA; CNA-role entries have no timestamp and no id, so no key | ADR-0003 Open question 1 |
| SSVC optional fields `computed`, `decisionTree`, `decisionTreeUrl`, `generator`, `$schema` | Absent from every NVD entry verified (85,454 entries) | If NVD starts publishing them |
| SSVC decision-tree outcome (Track / Track\* / Attend / Act) | Not published by NVD; deriving it would be inference in KGCS | Never in Core; a consumer may compute it from the three stored points |
| Any derived exploitability / priority score | Would introduce probabilistic or decision semantics into Core | Never (ADR-0003 D2) |

## Audit — terms cited by mapping docs but declared by no OWL module

Scripted 2026-09-27 over every `` `prefix:term` `` in the new v1.2 docs
(`kev-to-owl-v1.0.md` 19 terms, `epss-to-owl-v1.0.md` 13, `ssvc-to-owl-v1.0.md`
15, `docs/adr/ADR-0003-decision-extension.md` 13,
`contracts/agent-consumable-schema.md` 10) against the union of
`ontology/**/*.owl` (19 modules after v1.2): **0 undeclared**. The v1.1 rows
below are unchanged (design intent in the v1.0 mapping docs that never
reached an OWL module; each is "planned" until a versioned module declares
it).

| Mapping doc | Cited | Undeclared |
| --- | --- | --- |
| `attck-to-owl-v1.0.md` | 36 | `attack:Identity`, `attack:dataComponent`, `attack:dataSource`, `attack:detection`, `attack:extensions`, `attack:granularMarkings` |
| `capec-to-owl-v1.0.md` | 45 | `capec:categoryConcerns`, `capec:categoryReferences`, `capec:consequences`, `capec:executionSteps`, `capec:hasMember`, `capec:memberOf`, `capec:references`, `capec:relatedPatterns`, `capec:skillsRequired`, `capec:viewAudience`, `capec:viewMembers` |
| `car-to-owl-v1.0.md` | 31 | `car:hasImplementation`, `car:model_collected_by`, `car:references_datamodel`, `kgcs:CyberObservable`, `kgcs:DataSource` |
| `d3fend-to-owl-v1.0.md` | 22 | `d3fend:AppliedWhitelisting`, `d3fend:DefensiveTechnique`, `d3fend:OffensiveTactic`, `d3fend:OffensiveTechnique` |
| `engage-to-owl-v1.0.md` | 19 | `engage:approach_enables` |
| `shield-to-owl-v1.0.md` | 17 | `shield:attackTacticId`, `shield:attackTechniqueId`, `shield:mapToAttack` |
| `mapping-coverage-matrix-v1.0.md` | 48 | `attack:dataComponent`, `attack:dataSource`, `attack:detection`, `attack:extensions`, `attack:granularMarkings` |
| `kev-to-owl-v1.0.md`, `epss-to-owl-v1.0.md`, `ssvc-to-owl-v1.0.md` *(v1.2)* | 19 / 13 / 15 | none |
| all other mapping docs | — | none |

## ETL Test Priorities

1. Validate deterministic IDs (`matchCriteriaId`, `cveId`, `cweId`, `scoreId`, `vcId`, `vcnId`, `consequenceId`, and *(v1.2)* `epssId`, `ssvcId`, `KevEntry.cveId`).
2. Validate CPEMatch expansion (`cpe:matchesPlatform`) against `matches[]` arrays.
3. Validate CVE configuration boolean handling (`operator`, `negate`, `vulnerable`) before `cve:affects` edge emission — expressible as `shapes/cve.shacl.ttl` v1.1 on an RDF export.
4. Validate CVSS multi-version coexistence (do not overwrite prior score nodes).
5. Re-run `shapes/cwe.shacl.ttl` v1.2 and `shapes/capec.shacl.ttl` v1.1 against exported data after each CWE/CAPEC reload; the enrichment `sh:minCount 1` constraints must pass.
6. Exactly one `BuildMetadata` node per graph (Cypher), `shapes/build.shacl.ttl` v1.2 on export.
7. Zero `PART_OF` edges crossing domains (Cypher in `attck-to-owl-v1.0.md`, v1.1); 436 on the 2026-09-06 bundles.
8. `CAUSED_BY` count unchanged on the same raw data (331,107), and `size(sources) = size(sourceRoles) = size(types)` on every edge.
9. Per-bridge counts (remapped / dropped deprecated / unresolved) reported by the loader and recorded with the snapshot.
10. *(v1.2)* After `load_kev.py` / `load_epss.py` / `load_ssvc.py`: every decision node has exactly one incoming edge and it is the has_\* edge from the Vulnerability with the same `cveId`; no edge leaves a decision node (`shapes/decision.shacl.ttl` on export, or the Cypher equivalents in the three mapping docs); `count(EpssScore)` never decreases; dropped-and-counted totals per source recorded with the snapshot.
11. *(v1.2)* **Chain equivalence:** every chain export (nodes and edges of `CPE → CVE/CVSS → CWE → CAPEC → ATT&CK → defences`, `CAUSED_BY` with provenance, `BuildMetadata` minus the two new keys) is hash-identical between `kgcs-v11` and `kgcs-v12` on the same raw data (session Q19 gate). The decision extension adds nodes and edges; it must change nothing else.
