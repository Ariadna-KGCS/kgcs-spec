# CVSS to OWL Mapping v1.0

## Sources

- `data/schemas/CVE/cve_api_json_2.0.schema` -> `metrics.cvssMetricV2|V30|V31|V40`
- CVSS schemas under `data/schemas/CVE/` (`cvss-v2.0.json`, `cvss-v3.0.json`, `cvss-v3.1.json`, `cvss-v4.0.json`)

## Target Ontology

- `ontology/standards/cvss-ontology-v1.0.owl`
- Core class: `kgcs:VulnerabilityScore` (alias class `cvss:Score`)

## Entity Mapping

| Source Record | Target Class | Primary ID |
| --- | --- | --- |
| each metric entry in CVE `metrics` arrays | `kgcs:VulnerabilityScore` | `cvss:scoreId` |

## Field Mapping

| Source Field | Ontology Property |
| --- | --- |
| derived stable score key (e.g., CVE + version + vector hash) | `cvss:scoreId` |
| `cvssData.version` (or metric version discriminator) | `cvss:version` |
| `cvssData.baseScore` | `cvss:baseScore` |

## Relationship Mapping

| Source Structure | Ontology Edge |
| --- | --- |
| CVE metric entry linked to owning CVE | `cvss:hasScore` (`Vulnerability` -> `VulnerabilityScore`) |
| inverse edge | `cvss:scoreOfVulnerability` |

## Transformation Notes

- Do not overwrite older CVSS versions; emit one score node per versioned score entry.
- Preserve multiple score nodes per CVE where provided by NVD.
- Use deterministic `scoreId` generation to keep idempotent loads.
