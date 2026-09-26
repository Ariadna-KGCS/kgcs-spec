# Mapping Coverage Matrix v1.1

Purpose: quick audit view of schema-to-OWL mapping coverage for ETL implementation and tests.

Supersedes `mapping-coverage-matrix-v1.0.md` (kept frozen). v1.1 completes the
matrix for all ten standards and the versioned modules added after v1.0.0
(CWE enrichment, CWE/CAPEC consequences, CVE applicability, CAUSED_BY
provenance, graph labels, ATT&CK-core alignment, build metadata), corrects
the ATT&CK rows that cited terms no OWL module declares, and adds a scripted
audit of every `prefix:term` cited by the mapping docs. The v1.1.0 release
also folds in the 2026-09-26 graph-quality review: PART_OF domain coherence,
CAUSED_BY provenance, the revoked/deprecated ATT&CK bridge rule and exact
per-source build snapshots.

Status legend:

- implemented: mapped to a declared OWL term; the graph loader writes it
- partial: mapped but requires ETL rule logic or derived key generation
- planned: identified but intentionally deferred; no OWL term declared
- external: mapped to a vocabulary outside KGCS (`rdfs:`, `dct:`); not a KGCS term and not constrained by the shapes

"Loader writes it" is taken from the pipeline loader sources and the
pipeline post-load checks as of 2026-09-06 and was not re-verified against a
live graph in this environment.

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
| `weaknesses[].description[].value` | yes | `kgcs:caused_by`; reified as `cve:CausedByStatement` | implemented (edge) / planned (statement) | graph `CAUSED_BY`, exactly one edge per (CVE, CWE) pair; count unchanged (331,107 on the 2026-09-26 raw data) |
| `weaknesses[].source` | yes | `cve:weaknessSources` | planned (loader) | edge property `sources`, string list, verbatim |
| derived from `weaknesses[].source` | derived | `cve:weaknessSourceRoles` | planned (loader) | edge property `sourceRoles`: `nvd` for `nvd@nist.gov`, `adp` for a declared ADP identifier (`134c704f-9b21-4f2e-91b3-4a467353bcc0`, CISA ADP), else `cna` |
| `weaknesses[].type` | yes | `cve:weaknessTypes` | planned (loader) | edge property `types`: `Primary` / `Secondary`; the three lists are index-aligned, equal length |

## CWE

| Source Field | Required in Source | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| CWE ID | yes | `cwe:cweId` | implemented | Weakness stable ID |
| `@Abstraction` | no | `cwe:abstraction` | implemented | Pillar/Class/Base/Variant/Compound |
| `Related_Attack_Patterns` | no | `kgcs:exploited_by` | implemented | graph `DEMONSTRATED_BY` (Weakness → AttackPattern), written by `load_capec.py` from CAPEC `Related_Weaknesses` |

### CWE enrichment (`cwe-enrichment-v1.0.owl`, v1.1) — requires the enrichment-aware `load_cwe.py`

| Source Field | Required in Source | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| `Description` | yes | `cwe:description` | planned (loader) | OWL + shape ready; `load_cwe.py` writes `cweId`/`abstraction` only as of 2026-09-06 |
| `Extended_Description` | no | `cwe:extended_description` | planned (loader) | StructuredText flattened |
| `Mapping_Notes/Usage` | yes | `cwe:mapping_usage` | planned (loader) | enum (4) |
| `Mapping_Notes/Reasons/Reason/@Type` | no | `cwe:mapping_reasons` | planned (loader) | enum (12), multi-valued |
| `@Structure` | yes | `cwe:structure` | planned (loader) | enum (3) |
| `@Status` | yes | `cwe:status` | planned (loader) | enum (6) |
| `Alternate_Terms/Alternate_Term/Term` | no | `cwe:alternate_terms` | planned (loader) | terms only |
| `Likelihood_Of_Exploit` | no | `cwe:likelihood_of_exploit` | planned (loader) | enum (4) |
| `Functional_Areas/Functional_Area` | no | `cwe:functional_areas` | planned (loader) | enum (20) |
| `Affected_Resources/Affected_Resource` | no | `cwe:affected_resources` | planned (loader) | enum (5) |
| `Modes_Of_Introduction/Introduction/Phase` | no | `cwe:modes_of_introduction` | planned (loader) | enum (17), deduplicated |
| `Weakness_Ordinalities/Weakness_Ordinality/Ordinality` | no | `cwe:ordinalities` | planned (loader) | enum (3) |

### CWE consequences (`cwe-consequences-v1.0.owl`, v1.1, ADR-0001) — requires the consequence-aware loader

| Source Field | Required in Source | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| `Common_Consequences/Consequence` | no | `cwe:Consequence`, `cwe:has_consequence` | planned (loader) | one sub-node per record; key `cwe:consequence_id` = `<cweId>-C<ordinal>` |
| `Consequence/Scope` | yes | `cwe:scope` | planned (loader) | 1..N inside the record |
| `Consequence/Impact` | yes | `cwe:technical_impact` | planned (loader) | 1..N; 25-value CWE vocabulary, never merged with CAPEC |
| `Consequence/Likelihood` | no | `cwe:consequence_likelihood` | planned (loader) | |
| `Consequence/Note` | no | `cwe:consequence_note` | planned (loader) | flattened |

## CVSS

| Source Field | Required in Source | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| `metrics.cvssMetric*.cvssData.baseScore` | yes (per score entry) | `cvss:baseScore` | implemented | 0.0–10.0 |
| `cvssData.version` or metric discriminator | yes | `cvss:version` | implemented | enum 2.0 / 3.0 / 3.1 / 4.0, never merged |
| derived score key | n/a | `cvss:scoreId` | implemented | `<cveId>_<version>` (pattern enforced by `cvss.shacl.ttl`) |
| CVE-to-score linkage | n/a | `cvss:hasScore` | implemented | graph `HAS_SCORE`; one Score node per source score entry, no duplicate version per CVE (post-load check) |

## CAPEC

| Source Field | Required in Source | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| `@ID` | yes | `capec:capecId` | implemented | graph value `CAPEC-<n>` (patterned string); OWL v1.0 range `xsd:integer` is the recorded deviation |
| `@Name` | yes | `capec:name` | implemented | |
| `@Abstraction`, `@Status` | yes | `capec:abstraction`, `capec:status` | implemented (OWL) | loader coverage not re-verified |
| `Related_Weaknesses` | yes | `kgcs:exploited_by` (inverse direction) | implemented | graph `DEMONSTRATED_BY` from Weakness |
| `Related_Attack_Patterns` (ChildOf) | no | `capec:childOf` | implemented | graph `CHILD_OF` (AttackPattern → AttackPattern) |
| `Taxonomy_Mappings` (ATT&CK) | no | `kgcs:implemented_as` | implemented | graph `IMPLEMENTS` (AttackPattern → Technique), written by `load_attck.py`; v1.1 revoked/deprecated rule applies (15 of 272 CAPEC 3.9 rows cite revoked techniques) |
| `Consequences/Consequence` | no | `capec:Consequence`, `capec:hasConsequence`, `capec:scope`, `capec:technicalImpact`, `capec:consequenceLikelihood` (frozen) + `capec:consequence_id`, `capec:consequence_note` (`capec-consequences-v1.0.owl`) | planned (loader) | ADR-0001; Impact optional (CAPEC XSD `minOccurs=0`); 10-value CAPEC vocabulary |
| Categories, Views, Execution_Flow, Skills, Resources, Indicators, Mitigations, Example_Instances | no | see audit below | planned | `capec-to-owl-v1.0.md` cites terms not declared by any OWL module |

## ATT&CK

Corrected against `attck-ontology-v1.0.owl`, `attck-core-alignment-v1.0.owl`
and `graph-labels-v1.0.owl`. The v1.0 rows that mapped to `rdfs:`/`dct:`
vocabulary or to undeclared `attack:` terms are marked accordingly.

| STIX Field | Required in Source | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| `x_mitre_id` | yes | `attack:attackId` | implemented | `T####`, `T####.###`, `TA####` |
| `name` | yes | `attack:name` | implemented | v1.1 (`graph-labels-v1.0.owl`); v1.0 cited `rdfs:label` |
| `kill_chain_phases.phase_name` | no | `attack:phaseName` (Tactic), `attack:contains_by` ≡ `kgcs:belongs_to` (Technique → Tactic) | partial | graph `PART_OF`; `attack:shortname` is the v1.0 Tactic term for the same value. v1.1: the tactic is resolved by `attackId` inside the same STIX bundle, never by `phaseName` alone (`attck-to-owl-v1.0.md`). The loader as of 2026-09-26 still matches on `phaseName`: 618 of 1,054 edges cross domains, which `attack:PartOfDomainCoherenceShape` detects |
| `x_mitre_is_subtechnique` | no | `attack:isSubtechnique` | implemented (OWL) | graph keeps a separate `SubTechnique` label |
| `relationship_type = subtechnique-of` | no | `attack:subtechnique_of` ⊑ `kgcs:subtechnique_of` | implemented | graph `SUBTECHNIQUE_OF`, exactly one parent |
| `external_references` (CAPEC) | no | `kgcs:implemented_as` | implemented | graph `IMPLEMENTS`, parent techniques only |
| `x_mitre_platforms` | no | `attack:platform` | implemented (OWL) | loader coverage not re-verified |
| `x_mitre_domains` | no | `attack:domain` | implemented | graph `domains` string list on Technique, SubTechnique and Tactic, short form `enterprise` / `mobile` / `ics` (from the bundle file name); required since `attck.shacl.ttl` v1.1; SUBTECHNIQUE_OF domain coherence added |
| `relationship_type = revoked-by`, `x_mitre_deprecated` | no | none (loader behaviour) | planned (loader) | bridges into ATT&CK (`IMPLEMENTS`, `MITIGATED_BY`): revoked targets are remapped to the live successor, deprecated targets are dropped and counted (`attck-to-owl-v1.0.md`, v1.1) |
| `x_mitre_version`, `revoked`, `confidence`, `created_by_ref`, `x_mitre_modified_by_ref`, `x_mitre_tactic_type` | no | `attack:attackVersion`, `attack:revoked`, `attack:confidence`, `attack:createdBy`, `attack:modifiedBy`, `attack:tacticType` | implemented (OWL) | loader coverage not re-verified |
| `kill_chain_phases.kill_chain_name` | no | `attack:killChainName` | implemented (OWL) | `mitre-attack`, `mitre-mobile-attack`, `mitre-ics-attack` |
| `description`, `created`, `modified`, `lang`, `labels` | yes/no | `dct:description`, `dct:created`, `dct:modified`, `dct:language`, `dct:subject` | external | not KGCS terms; unconstrained by shapes |
| `x_mitre_data_sources`, `x_mitre_data_components`, `x_mitre_detection`, `granular_markings`, `extensions` | no | `attack:dataSource`, `attack:dataComponent`, `attack:detection`, `attack:granularMarkings`, `attack:extensions` | planned | cited by v1.0 rows, declared by no OWL module (classes `attack:DataSource` / `attack:DataComponent` exist; the properties do not) |

## D3FEND

| Source Field | Required in Source | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| technique class IRI fragment | yes | `d3fend:d3fendId` | implemented | `D3-<LETTERS>`; loader fallback to URI fragment (Warning pattern) |
| `rdfs:label` | yes | `d3fend:name` | implemented | v1.1 (`graph-labels-v1.0.owl`) |
| offensive-technique mapping | no | `kgcs:mitigated_by` | implemented | graph `MITIGATED_BY` (Technique → DefensiveTechnique); the only edge `load_d3fend.py` writes; v1.1 revoked/deprecated rule applies (≤ 12 revoked, 1 deprecated IDs in D3FEND 1.3.0 mappings) |
| `d3fend:references_cwe`, `d3fend:counters_attack_pattern` (frozen OWL) | no | as declared | planned | declared in `d3fend-ontology-v1.0.owl`, never loaded; policy call pending (shapes/README.md, D3FEND v1.1 candidates) |
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

## Build metadata (`build-metadata-v1.0.owl`, v1.1)

| Source | Required | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| pipeline `SPEC_VERSION` | yes | `build:spec_version` | planned (loader) | loader postscript, M0 scope |
| load completion instant | yes | `build:build_timestamp` | planned (loader) | |
| `git rev-parse HEAD` of kgcs-pipeline | yes | `build:pipeline_commit` | planned (loader) | |
| per-source download snapshot | yes | `build:source_snapshot` | planned (loader) | `<SOURCE>=<snapshot>`, at most one value per SOURCE (`build.shacl.ttl` v1.1) |

Snapshot value per source: the exact release loaded, taken from the source
itself wherever the source states it. Otherwise it is the download instant
recorded by the downloader.

| SOURCE | Snapshot value | Example |
| --- | --- | --- |
| `CWE` | catalogue `Version` attribute | `CWE=4.20` |
| `CAPEC` | catalogue `Version` attribute | `CAPEC=3.9` |
| `D3FEND` | ontology `owl:versionInfo` | `D3FEND=1.3.0` |
| `ATTCK` | One key for the three bundles. If all three carry an `x-mitre-collection` with the same `x_mitre_version`: that release. Otherwise `download:<date>;modified-max:<max modified across the three bundles>`. Never the `x-mitre-matrix` `x_mitre_version` (object version, not the ATT&CK release). Per-domain keys are a v1.2 candidate | `ATTCK=18.1`; today `ATTCK=download:2026-09-06;modified-max:2026-08-04` |
| `CVE`, `CPE`, `CVSS` | NVD feed / API download instant (UTC) | `CVE=2026-09-01T03:00:00Z` |
| `CAR`, `SHIELD`, `ENGAGE` | release tag if any, else repository commit or download date | `ENGAGE=1.0` |

## Audit — terms cited by mapping docs but declared by no OWL module

Scripted 2026-09-06 over every `` `prefix:term` `` in `mappings/*.md` against
the union of `ontology/**/*.owl` (17 modules after v1.1; the v1.1.0 release adds
`cve-weakness-provenance-v1.0.owl`, 18, whose terms are all cited correctly). Rows are design
intent in the mapping docs that never reached an OWL module; each is
"planned" until a versioned module declares it.

| Mapping doc | Cited | Undeclared |
| --- | --- | --- |
| `attck-to-owl-v1.0.md` | 36 | `attack:Identity`, `attack:dataComponent`, `attack:dataSource`, `attack:detection`, `attack:extensions`, `attack:granularMarkings` |
| `capec-to-owl-v1.0.md` | 45 | `capec:categoryConcerns`, `capec:categoryReferences`, `capec:consequences`, `capec:executionSteps`, `capec:hasMember`, `capec:memberOf`, `capec:references`, `capec:relatedPatterns`, `capec:skillsRequired`, `capec:viewAudience`, `capec:viewMembers` |
| `car-to-owl-v1.0.md` | 31 | `car:hasImplementation`, `car:model_collected_by`, `car:references_datamodel`, `kgcs:CyberObservable`, `kgcs:DataSource` |
| `d3fend-to-owl-v1.0.md` | 22 | `d3fend:AppliedWhitelisting`, `d3fend:DefensiveTechnique`, `d3fend:OffensiveTactic`, `d3fend:OffensiveTechnique` |
| `engage-to-owl-v1.0.md` | 19 | `engage:approach_enables` |
| `shield-to-owl-v1.0.md` | 17 | `shield:attackTacticId`, `shield:attackTechniqueId`, `shield:mapToAttack` |
| `mapping-coverage-matrix-v1.0.md` | 48 | `attack:dataComponent`, `attack:dataSource`, `attack:detection`, `attack:extensions`, `attack:granularMarkings` |
| all other mapping docs | — | none |

## ETL Test Priorities

1. Validate deterministic IDs (`matchCriteriaId`, `cveId`, `cweId`, `scoreId`, `vcId`, `vcnId`, `consequenceId`).
2. Validate CPEMatch expansion (`cpe:matchesPlatform`) against `matches[]` arrays.
3. Validate CVE configuration boolean handling (`operator`, `negate`, `vulnerable`) before `cve:affects` edge emission — now expressible as `shapes/cve.shacl.ttl` v1.1 on an RDF export.
4. Validate CVSS multi-version coexistence (do not overwrite prior score nodes).
5. After the enrichment loaders land: re-run `shapes/cwe.shacl.ttl` v1.2 and `shapes/capec.shacl.ttl` v1.1 against exported data; the enrichment `sh:minCount 1` constraints must pass.
6. After the build-metadata postscript lands: exactly one `BuildMetadata` node per graph (Cypher), `shapes/build.shacl.ttl` on export.
7. After the `PART_OF` loader fix: zero `PART_OF` edges crossing domains (Cypher in `attck-to-owl-v1.0.md`, v1.1). The `PART_OF` count drops (436 expected on the 2026-09-06 bundles); a new snapshot is required.
8. After the provenance-aware `load_cwe.py` (the `CAUSED_BY` writer): the `CAUSED_BY` count is unchanged on the same raw data, and `size(sources) = size(sourceRoles) = size(types)` holds on every edge.
9. After the revoked-by remap: the per-bridge counts (remapped / dropped deprecated / unresolved) are reported by the loader and recorded with the snapshot.
