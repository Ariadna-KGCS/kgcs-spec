# CPE + CPEMatch to OWL Mapping v1.0

## Sources

- `data/schemas/CPE/cpe_api_json_2.0.schema`
- `data/schemas/CPE/cpematch_api_json_2.0.schema`

## Target Ontology

- `ontology/standards/cpe-ontology-v1.0.owl`
- Core classes: `kgcs:Platform`, `kgcs:PlatformConfiguration`

## Entity Mapping

| Source Record | Target Class | Primary ID |
| --- | --- | --- |
| CPE API `products[].cpe` | `kgcs:Platform` | `cpe:cpeNameId` (+ `cpe:cpeUri`) |
| CPE Match API `matchStrings[].matchString` | `kgcs:PlatformConfiguration` | `cpe:matchCriteriaId` |

## Field Mapping: Platform (CPE)

| Source Field | Ontology Property |
| --- | --- |
| `cpeName` | `cpe:cpeUri` |
| `cpeNameId` | `cpe:cpeNameId` |
| parsed CPE part segment | `cpe:part` |
| parsed CPE vendor segment | `cpe:vendor` |
| parsed CPE product segment | `cpe:product` |
| parsed CPE version segment | `cpe:version` |

## Field Mapping: PlatformConfiguration (CPEMatch/CVE config)

| Source Field | Ontology Property |
| --- | --- |
| `criteria` | `cpe:criteria` |
| `matchCriteriaId` | `cpe:matchCriteriaId` |
| `status` | `cpe:configStatus` |
| `created` | `cpe:created` |
| `lastModified` | `cpe:lastModified` |
| `cpeLastModified` | `cpe:cpeLastModified` |
| `versionStartIncluding` | `cpe:versionStartIncluding` |
| `versionStartExcluding` | `cpe:versionStartExcluding` |
| `versionEndIncluding` | `cpe:versionEndIncluding` |
| `versionEndExcluding` | `cpe:versionEndExcluding` |
| CVE config `vulnerable` | `cpe:vulnerable` |
| propagated base criteria URI | `cpe:cpeUri` |

## Relationship Mapping

| Source Structure | Ontology Edge |
| --- | --- |
| `matchString.matches[].cpeNameId` join to Platform | `cpe:matchesPlatform` (`PlatformConfiguration` -> `Platform`) |
| inverse projection | `cpe:isMatchedByConfiguration` |

## Transformation Notes

- Keep `cpe:cpeUri` on both `kgcs:Platform` and `kgcs:PlatformConfiguration` for join/debug support.
- `cpe:matchesPlatform` is structural/materialized from CPE Match expansion, not an authoritative vulnerability edge.
- `cpe:vulnerable` is taken from CVE `configurations.nodes[].cpeMatch[]`, not from CPE Match API.
