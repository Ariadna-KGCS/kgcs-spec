# KGCS Schema-to-OWL Mappings

## Overview

This directory contains deterministic field‑by‑field contracts that translate authoritative source schemas into KGCS OWL terms. Each mapping file follows the same structure:

1. **Sources** – The source schemas or data feeds.
2. **Target Ontology** – The OWL file that receives the mapping.
3. **Entity Mapping** – Primary ID and class for each source record.
4. **Field Mapping** – One‑to‑one mapping of source fields to OWL properties.
5. **Relationship Mapping** – How source structures become graph edges.
6. **Transformation Notes** – Any special handling, deprecation, or edge cases.

All mappings preserve source identifiers, timestamps, and relationships. The core ontology (`core-ontology-v1.0.owl`) remains immutable; new classes and properties for each standard live in a dedicated ontology that imports the core.

## Mapping Files

- [cpe-cpematch-to-owl-v1.0.md](cpe-cpematch-to-owl-v1.0.md)
- [cve-to-owl-v1.0.md](cve-to-owl-v1.0.md)
- [cwe-to-owl-v1.0.md](cwe-to-owl-v1.0.md)
- [cvss-to-owl-v1.0.md](cvss-to-owl-v1.0.md)
- [attck-to-owl-v1.0.md](attck-to-owl-v1.0.md)
- [capec-to-owl-v1.0.md](capec-to-owl-v1.0.md)
- [d3fend-to-owl-v1.0.md](d3fend-to-owl-v1.0.md)
- [car-to-owl-v1.0.md](car-to-owl-v1.0.md)
- [engage-to-owl-v1.0.md](engage-to-owl-v1.0.md)
- [shield-to-owl-v1.0.md](shield-to-owl-v1.0.md)
- [kev-to-owl-v1.0.md](kev-to-owl-v1.0.md) (v1.2, decision extension)
- [epss-to-owl-v1.0.md](epss-to-owl-v1.0.md) (v1.2, decision extension)
- [ssvc-to-owl-v1.0.md](ssvc-to-owl-v1.0.md) (v1.2, decision extension)
- [mapping-coverage-matrix-v1.0.md](mapping-coverage-matrix-v1.0.md) (frozen) · [mapping-coverage-matrix-v1.1.md](mapping-coverage-matrix-v1.1.md) (frozen) · [mapping-coverage-matrix-v1.2.md](mapping-coverage-matrix-v1.2.md) (current)

---

## **Implementation Status**

| Standard | Mapping File | Ontology File | Status | Details |
| --- | --- | --- | --- | --- |
| CPE | `cpe-cpematch-to-owl-v1.0.md` | `ontology/standards/cpe-ontology-v1.0.owl` | ✅ Complete | 2 object properties, 15 datatype properties |
| CVE | `cve-to-owl-v1.0.md` | `ontology/standards/cve-ontology-v1.0.owl` | ✅ Complete | 3 object properties, 4 datatype properties |
| CWE | `cwe-to-owl-v1.0.md` | `ontology/standards/cwe-ontology-v1.0.owl` | ✅ Complete | Minimal: 2 datatype properties (cweId, abstraction) |
| CVSS | `cvss-to-owl-v1.0.md` | `ontology/standards/cvss-ontology-v1.0.owl` | ✅ Complete | Class alias, 2 object properties, 3 datatype properties |
| ATT&CK | `attck-to-owl-v1.0.md` | `ontology/standards/attck-ontology-v1.0.owl` | ✅ Complete | 11 classes, 13 object properties, 12 datatype properties (247 lines) |
| CAPEC | `capec-to-owl-v1.0.md` | `ontology/standards/capec-ontology-v1.0.owl` | ✅ Complete | 5 classes, 16 object properties, 36 datatype properties (434 lines) |
| D3FEND | `d3fend-to-owl-v1.0.md` | `ontology/standards/d3fend-ontology-v1.0.owl` | ✅ Complete | 4 classes, 16 object properties, 10 datatype properties (350 lines); passthrough architecture |
| CAR | `car-to-owl-v1.0.md` | `ontology/standards/car-ontology-v1.0.owl` | ✅ Complete | 7 classes, 16 object properties, 23 datatype properties (352 lines); three-entity federation |
| ENGAGE | `engage-to-owl-v1.0.md` | `ontology/standards/engage-ontology-v1.0.owl` | ✅ Complete | 4 entity types (Activity, Approach, Goal, Reference), hierarchical goal-approach-activity federation with EAV exploitation semantics; 5 classes, 12 object properties, 10 datatype properties (272 lines) |
| KEV / EPSS / SSVC (v1.2) | `kev-to-owl-v1.0.md`, `epss-to-owl-v1.0.md`, `ssvc-to-owl-v1.0.md` | `ontology/extensions/decision-extension-v1.0.owl` | ✅ Mapping complete; loaders pending (Q18) | 3 classes, 3 object properties, 32 datatype properties; leaf nodes adhered to Vulnerability (ADR-0003) |
| SHIELD | `shield-to-owl-v1.0.md` | `ontology/standards/shield-ontology-v1.0.owl` | ✅ Mapping Complete | 6 entity types (Tactic, Technique, Opportunity, UseCase, Procedure, ATT&CK Mapping), hierarchical tactic-technique-opportunity-usecase federation with critical Opportunity→UseCase minimum cardinality (1); 11 object properties, 9 datatype properties (494 lines) |

---

## **Validation Summary**

All KGCS standards ontologies have been implemented with consistent namespace architecture:

- **Namespace Consistency**: All 8 ontologies properly declare standard prefixes (owl, rdfs, rdf, xsd)
- **Core Import Chain**: All standards correctly import core ontology with no circular dependencies
- **Semantic Alignment**: Object properties use bidirectional `owl:inverseOf` declarations
- **Cardinality Constraints**: All primary IDs have exactly-1 cardinality restrictions (Functional Properties); critical relationships enforce minimum cardinality
- **Documentation**: All properties have rdfs:label and rdfs:comment annotations
- **Passthrough Architecture**: D3FEND implements knowledge graph federation pattern (4,279 official classes referenced, not re-implemented)
- **Three-Entity Federation**: CAR implements detection analytics → ATT&CK techniques, sensors → data models, analytics → D3FEND defenses

---

## **Ontology Completeness Metrics**

- **Classes**: 13 (core) + 11 (ATT&CK) + 5 (CAPEC) + 4 (D3FEND) + 7 (CAR) + 5 (ENGAGE) + 2 (CVSS) = 47 total (plus 4,279 D3FEND federated)
- **Properties**: 170+ properties across all ontologies
- **Object Properties**: 105+ (6 core + 13 ATT&CK + 16 CAPEC + 16 D3FEND + 16 CAR + 12 ENGAGE + 2 CVSS + others)
- **Datatype Properties**: 95+ (10 core + 12 ATT&CK + 36 CAPEC + 10 D3FEND + 23 CAR + 10 ENGAGE + 3 CVSS + others)
- **Disjointness Constraints**: Logical contradiction prevention across incompatible types (3 constraints in ENGAGE, 7 in CAR)
- **Cardinality Constraints**: Critical relationships enforce minimum cardinality (minimum 1 coverage_technique per CAR analytic, minimum 1 action/field per data model, minimum 1 sensor per mapping, minimum 1 ATT&CK technique per ENGAGE activity, minimum 1 type per ENGAGE activity, etc.)
- **Cross-Standard Relationships**: CWE linkage from CAPEC, platform alignment from CPE, scoring from CVSS, defensive-offensive mitigation from D3FEND, detection coverage from CAR, EAV exploitation from ENGAGE
- **Bidirectional Relationships**: All relationships support inverse queries via owl:inverseOf
