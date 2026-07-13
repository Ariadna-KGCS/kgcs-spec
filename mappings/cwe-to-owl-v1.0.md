# CWE to OWL Mapping v1.0

## Source

- CWE feed/XSD (`data/schemas/CWE/cwe_schema_latest.xsd`)
- CVE API weakness references (`data/schemas/CVE/cve_api_json_2.0.schema` -> `weaknesses[]`)

## Target Ontology

- `ontology/standards/cwe-ontology-v1.0.owl`
- Core class: `kgcs:Weakness`

## Entity Mapping

| Source Record | Target Class | Primary ID |
| --- | --- | --- |
| CWE weakness entry | `kgcs:Weakness` | `cwe:cweId` |

## Field Mapping

| Source Field | Ontology Property |
| --- | --- |
| CWE ID (`CWE-xxx`) | `cwe:cweId` |
| CWE abstraction/category level | `cwe:abstraction` |

## Relationship Notes

- CVE->CWE causality uses core `kgcs:caused_by` and is out-of-scope for `cwe:` module property definitions.
- `cwe:` module supplies weakness identity fields used by systems/offensive/defensive views.
