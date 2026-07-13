# Mapping Coverage Matrix v1.0

Purpose: quick audit view of schema‑to‑OWL mapping coverage for ETL implementation and tests.

Status legend:

- implemented: mapped to current OWL term(s)
- partial: mapped but requires ETL rule logic or derived key generation
- planned: identified but intentionally deferred

## CPE + CPEMatch

| Source Field | Required in Source | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| `cpe.cpeName` | yes | `cpe:cpeUri` | implemented | Platform canonical URI |
| `cpe.cpeNameId` | yes | `cpe:cpeNameId` | implemented | Platform stable ID |
| CPE parsed `part` | implied | `cpe:part` | implemented | From CPE URI decomposition |
| CPE parsed `vendor` | implied | `cpe:vendor` | implemented | From CPE URI decomposition |
| CPE parsed `product` | implied | `cpe:product` | implemented | From CPE URI decomposition |
| CPE parsed `version` | implied | `cpe:version` | implemented | From CPE URI decomposition |
| `matchString.criteria` | yes | `cpe:criteria` | implemented | PlatformConfiguration base expression |
| `matchString.matchCriteriaId` | yes | `cpe:matchCriteriaId` | implemented | PlatformConfiguration stable ID |
| `matchString.status` | yes | `cpe:configStatus` | implemented | Lifecycle/status field |
| `matchString.created` | yes | `cpe:created` | implemented | CPEMatch metadata timestamp |
| `matchString.lastModified` | yes | `cpe:lastModified` | implemented | CPEMatch metadata timestamp |
| `matchString.cpeLastModified` | no | `cpe:cpeLastModified` | implemented | Optional metadata timestamp |
| CVE `cpeMatch.vulnerable` | yes (in cpeMatch object) | `cpe:vulnerable` | implemented | Comes from CVE configurations, not cpematch API |
| `versionStartIncluding` | no | `cpe:versionStartIncluding` | implemented | Lower inclusive bound |
| `versionStartExcluding` | no | `cpe:versionStartExcluding` | implemented | Lower exclusive bound |
| `versionEndIncluding` | no | `cpe:versionEndIncluding` | implemented | Upper inclusive bound |
| `versionEndExcluding` | no | `cpe:versionEndExcluding` | implemented | Upper exclusive bound |
| `matchString.matches[].cpeNameId` | no | `cpe:matchesPlatform` | implemented | Structural expansion edge |

## CVE

| Source Field | Required in Source | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| `cve.id` | yes | `cve:cveId` | implemented | Vulnerability stable ID |
| `cve.published` | yes | `cve:published` | implemented | CVE publish timestamp |
| `cve.lastModified` | yes | `cve:lastModified` | implemented | CVE update timestamp |
| `cve.sourceIdentifier` | no | `cve:source` | implemented | Source authority string |
| `cve.configurations[].nodes[].cpeMatch[]` | no | `cve:affects` | partial | Requires boolean config evaluation + matchCriteria join |
| `cve.references[]` | yes | `cve:references` | partial | Needs stable Reference node key strategy |

## CWE

| Source Field | Required in Source | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| CWE ID | yes | `cwe:cweId` | implemented | Weakness stable ID |
| CWE abstraction level | no | `cwe:abstraction` | implemented | Pillar/Class/Base/Variant etc. |

## CVSS

| Source Field | Required in Source | Target OWL Term(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| `metrics.cvssMetric*.cvssData.baseScore` | yes (per score entry) | `cvss:baseScore` | implemented | Numeric severity |
| `cvssData.version` or metric discriminator | yes | `cvss:version` | implemented | Score version label |
| derived score key | n/a | `cvss:scoreId` | partial | Requires deterministic key algorithm |
| CVE-to-score linkage | n/a | `cvss:hasScore` | partial | Emit one score node per source score entry |

## ATT&CK

| STIX Field | Required in Source | Target OWL Term(s) | Status | Notes |
| ---------- | ------------------ | ------------------ | ------ | ----- |
| `x_mitre_id` | yes | `attack:attackId` | implemented | Primary identifier |
| `name` | yes | `rdfs:label` | implemented | |
| `description` | yes | `dct:description` | implemented | |
| `x_mitre_tactic_type` | no (mobile only) | `attack:tacticType` | partial | Mobile domain only |
| `x_mitre_is_subtechnique` | no | `attack:isSubtechnique` | implemented | Boolean |
| `x_mitre_platforms` | no | `attack:platform` | implemented | Array of strings |
| `x_mitre_data_sources` | no | `attack:dataSource` | implemented | Array of references |
| `x_mitre_data_components` | no | `attack:dataComponent` | implemented | Array of references |
| `x_mitre_detection` | no (deprecated) | `attack:detection` | partial | Deprecated v3.3.0 |
| `created` | yes | `dct:created` | implemented | Timestamp |
| `modified` | yes | `dct:modified` | implemented | Timestamp |
| `created_by_ref` | no | `attack:createdBy` | implemented | Reference to MITRE identity |
| `confidence` | no | `attack:confidence` | implemented | Integer 1–99 |
| `lang` | no | `dct:language` | implemented | Language code |
| `revoked` | no | `attack:revoked` | implemented | Boolean |
| `labels` | no | `dct:subject` | implemented | Array of tags |
| `external_references` | no | `attack:references` | implemented | Array of Reference nodes |
| `granular_markings` | no | `attack:granularMarkings` | implemented | Array of Marking objects |
| `extensions` | no | `attack:extensions` | implemented | Dictionary of extensions |
| `x_mitre_domains` | no | `attack:domain` | implemented | Array of domains |
| `x_mitre_version` | no | `attack:attackVersion` | implemented | Version string |
| `x_mitre_modified_by_ref` | no | `attack:modifiedBy` | implemented | Reference to MITRE identity |
| `kill_chain_phases.phase_name` | no | `attack:shortname` | implemented | Link Technique → Tactic |
| `kill_chain_phases.kill_chain_name` | no | `attack:killChainName` | implemented | `mitre-attack`, `mitre-mobile-attack`, `mitre-ics-attack` |

## ETL Test Priorities

1. Validate deterministic IDs (`matchCriteriaId`, `cveId`, `cweId`, `scoreId`).
2. Validate CPEMatch expansion (`cpe:matchesPlatform`) against `matches[]` arrays.
3. Validate CVE configuration boolean handling (`operator`, `negate`, `vulnerable`) before `cve:affects` edge emission.
4. Validate CVSS multi-version coexistence (do not overwrite prior score nodes).
