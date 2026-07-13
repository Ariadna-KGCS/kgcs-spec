# CAR to OWL Mapping v1.0

## Overview

CAR (Cyber Analytics Repository) is the MITRE-maintained knowledge base of detection analytics, data models, and sensor capabilities for identifying adversary behavior aligned with ATT&CK techniques. This mapping implements CAR as a three-entity schema linking detection analytics to ATT&CK offensive techniques and data model observables to sensor capabilities. CAR bridges the gap between attack tactics (ATT&CK) and defensive detection mechanisms (D3FEND), enabling organizations to map which analytics detect which techniques and how those analytics correlate to defensive countermeasures.

---

## Sources

- **MITRE CAR Program:** `http://car.mitre.org/`
- **Raw Data Location:** `data/raw/car/analytics/`, `data/raw/car/data_model/`, `data/raw/car/sensors/`
- **Format:** YAML
- **Scale:** 100+ analytics, 10 data model entities, 7 sensor definitions
- **Namespace:** `http://www.motherhacker.me/kgcs/ontology/car#`
- **External Framework Integrations:** ATT&CK (techniques, tactics), D3FEND (defensive techniques), Data Models (cyber observables)
- **Architecture:** Three-entity federation pattern (Analytic → ATT&CK technique; Sensor → DataModel)

### Entity Distribution

| Entity Type | Count | Purpose |
| ----------- | ----- | ------- |
| Analytics | 100+ | Detection rules indexed CAR-YYYY-MM-NNN |
| Data Models | 10 | Cyber observable entity types (Process, File, Flow, etc.) |
| Sensors | 7 | Data source capability definitions |

---

## Target Ontology

- **File:** `ontology/standards/car-ontology-v1.0.owl`
- **Core Classes Used:**
  - `kgcs:DetectionAnalytic` (base for CAR analytics)
  - `kgcs:CyberObservable` (base for data models)
  - `kgcs:DataSource` (base for sensors)
- **New CAR Namespace:** `car: <http://www.motherhacker.me/kgcs/ontology/car#>`
- **Core Import:** Explicit `owl:imports <http://www.motherhacker.me/kgcs/ontology/core#>`
- **Design Pattern:** Federation with bidirectional relationships to ATT&CK and D3FEND

---

## Entity Mapping

### Primary Entity Types

| CAR Source Entity | Target KGCS Class | Primary ID | ID Datatype | Notes |
| --- | --- | --- | --- | --- |
| Analytic | kgcs:DetectionAnalytic | car:analyticId | xsd:string | Detection rule indexed CAR-YYYY-MM-NNN, links to ATT&CK techniques and D3FEND defenses |
| DataModel | kgcs:CyberObservable | car:datamodelName | xsd:string | Entity type definition (Process, File, Flow, Registry, etc.) with actions and fields |
| Sensor | kgcs:DataSource | car:sensorName | xsd:string | Data source capability definition (Sysmon, osquery, auditd, etc.) with event mappings |

### Supporting Entity Types

| Entity | Target Class | Purpose |
| ------ | ------------ | ------- |
| DataModel Action | car:DataModelAction | Action on entity (create, terminate, load, etc.) |
| DataModel Field | car:DataModelField | Observable property (fqdn, pid, file_path, etc.) |
| Sensor Mapping | car:SensorMapping | Event-to-observable mapping (sensor event → data model entity/action) |
| Coverage Entry | car:CoverageBucket | ATT&CK technique/tactic coverage specification within analytic |

---

## Field Mapping: Analytic Entity

### Core Required Fields

| Source Field | Target OWL Property | Range | Cardinality | Notes |
| --- | --- | --- | --- | --- |
| `id` | `car:analyticId` | xsd:string | 1 | Unique CAR identifier CAR-YYYY-MM-NNN (e.g., CAR-2013-01-002) |
| `title` | `rdfs:label` | xsd:string | 1 | Human-readable analytic title |
| `submission_date` | `car:submissionDate` | xsd:string | 1 | Date in YYYY/MM/DD format |
| `information_domain` | `car:informationDomain` | xsd:string | 1 | Primary domain: Network, Host, File, Object, Launched Script, Process, User, Cloud |
| `description` | `rdfs:comment` | xsd:string | 1 | Detailed analytic description |

### Optional Array Fields

| Source Field | Target OWL Property | Range | Cardinality | Notes |
| --- | --- | --- | --- | --- |
| `platforms` | `car:applicablePlatforms` | xsd:string | 0+ | Platforms: Windows, Linux, macOS, etc.; or "N/A" |
| `subtypes` | `car:analyticSubtypes` | xsd:string | 0+ | Analytic subtype (PCAP, Process, Registry, etc.) |
| `analytic_types` | `car:analyticTypes` | xsd:string | 0+ | Type classification (Situational Awareness, Detection, etc.) |
| `contributors` | `car:contributors` | xsd:string | 1+ | Contributors who developed/maintained analytic |

### Complex Object Fields

| Source Field | Target Property | Type | Cardinality | Strategy | Notes |
| --- | --- | --- | --- | --- | --- |
| `coverage` | `car:coverage` | car:CoverageBucket | 1+ | Array of coverage objects | **CRITICAL:** Minimum 1 required; links to ATT&CK techniques and tactics |
| `implementations` | `car:hasImplementation` | car:Implementation | 0+ | Code/pseudocode implementations | SQL, Splunk SPL, EQL, pseudocode, etc. |
| `data_model_references` | `car:references_datamodel` | car:DataModel | 0+ | References to data model fields | e.g., "flow/message/dest_port" |
| `d3fend_mappings` | `car:has_d3fend_mapping` | d3fend:DefensiveTechnique | 0+ | Links to D3FEND defensive techniques | Bidirectional defensive-offensive alignment |

### Coverage Array Structure

| Field | Type | Cardinality | Semantics |
| ----- | ---- | ---- | --------- |
| `technique` | string (pattern T[0-9]{4}) | 1 | ATT&CK technique ID being detected (e.g., T1039) |
| `tactics` | array of strings (pattern TA[0-9]{4}) | 1+ | ATT&CK tactics for this technique (e.g., [TA0009]) |
| `subtechniques` | array of strings (pattern T[0-9]{4}\\.[0-9]{3}) | 0+ | Subtechnique IDs if applicable (e.g., T1021.002) |
| `coverage` | enum (Low, Moderate, High) | 0-1 | Coverage effectiveness level |

---

## Field Mapping: DataModel Entity

### Core Fields

| Source Field | Target OWL Property | Range | Cardinality | Notes |
| --- | --- | --- | --- | --- |
| `name` | `car:datamodelName` | xsd:string | 1 | Entity type name (Process, File, Flow, Registry, etc.) |
| `description` | `rdfs:comment` | xsd:string | 1 | Detailed entity description |

### Complex Fields

| Source Field | Target Property | Type | Cardinality | Notes |
| - | - | - | - | - |
| `actions` | `car:hasAction` | car:DataModelAction | 1+ | Actions performable on entity (create, terminate, modify, etc.) |
| `fields` | `car:hasField` | car:DataModelField | 1+ | Observable properties/attributes of entity |

### DataModelAction Properties

| Field | Type | Notes |
| ----- | ---- | ----- |
| `name` | xsd:string | Action name (create, terminate, access, load, modify, etc.) |
| `description` | xsd:string | Description of when/how action occurs |

### DataModelField Properties

| Field | Type | Notes |
| ----- | ---- | ----- |
| `name` | xsd:string | Field name (fqdn, pid, command_line, image_path, etc.) |
| `description` | xsd:string | Detailed field description |
| `example` | xsd:string (optional) | Example value for this field |

---

## Field Mapping: Sensor Entity

### Core Fields

| Source Field | Target OWL Property | Range | Cardinality | Notes |
| --- | --- | --- | --- | --- |
| `sensor_name` | `car:sensorName` | xsd:string | 1 | Data source name (Sysmon, osquery, auditd, etc.) |
| `sensor_version` | `car:sensorVersion` | xsd:string | 1 | Version string (e.g., 11.0, 4.6.0) |
| `sensor_developer` | `car:sensorDeveloper` | xsd:string | 1 | Organization (Microsoft, Osquery Foundation, etc.) |
| `sensor_url` | `car:sensorUrl` | xsd:anyURI | 1 | URL to official sensor documentation |
| `sensor_description` | `rdfs:comment` | xsd:string | 1 | Sensor purpose and capabilities description |

### Complex Field

| Source Field | Target Property | Type | Cardinality | Notes |
| - | - | - | - | - |
| `mappings` | `car:hasMapping` | car:SensorMapping | 1+ | Event-to-data-model mappings |

### SensorMapping Properties

| Field | Type | Notes |
| ----- | ---- | ----- |
| `object` | xsd:string | Data model entity (file, driver, flow, process, etc.) |
| `action` | xsd:string | Action on entity (create, load, start, etc.) |
| `notes` | xsd:string | Implementation notes (e.g., Sysmon Event ID reference) |
| `fields` | array of xsd:string | Data model fields captured by this sensor event |

---

## Relationship Mapping

### Critical: Analytic-to-ATT&CK Relationships

| Relationship | Domain | Range | Direction | Cardinality | Semantics | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `car:coverage_technique` | DetectionAnalytic | attack:Technique | directed | 1+ | "This analytic detects execution of this ATT&CK technique" | **REQUIRED:** Minimum 1 per analytic |
| `car:coverage_tactic` | DetectionAnalytic | attack:Tactic | directed | 0+ | "This analytic provides coverage for this ATT&CK tactic" | Derived from technique-tactic mappings |

**Validation Rule:** Every DetectionAnalytic MUST have at least one `car:coverage_technique` pointing to a valid attack:Technique. This is the core semantic assertion that links defensive analytics to offensive techniques.

### Cross-Standard: Analytic-to-D3FEND Relationships

| Relationship | Domain | Range | Cardinality | Semantics | Notes |
| - | - | - | - | - | - |
| `car:has_d3fend_mapping` | DetectionAnalytic | d3fend:DefensiveTechnique | 0+ | "This analytic detects/supports this defensive technique" | Optional but recommended; enables defensive-offensive alignment |

### Sensor-to-DataModel Relationships

| Relationship | Domain | Range | Direction | Cardinality | Semantics |
| - | - | - | - | - | - |
| `car:sensor_provides` | DataSource (Sensor) | CyberObservable (DataModel) | directed | 1+ | "This sensor captures data about this observable" |
| `car:model_collected_by` | CyberObservable (DataModel) | DataSource (Sensor) | directed (inverse) | 0+ | "This observable is collected by this sensor" |

### Analytic-to-Sensor Relationships

| Relationship | Domain | Range | Cardinality | Semantics |
| - | - | - | - | - |
| `car:uses_sensor` | DetectionAnalytic | DataSource (Sensor) | 0+ | "This analytic requires data from this sensor" |
| `car:sensor_used_by` | DataSource (Sensor) | DetectionAnalytic | 0+ | "This sensor is used by these analytics" |

### Analytic-to-DataModel Relationships

| Relationship | Domain | Range | Cardinality | Semantics |
| - | - | - | - | - |
| `car:analyzes_observable` | DetectionAnalytic | CyberObservable (DataModel) | 0+ | "This analytic analyzes data about this observable" |

---

## Transformation Notes

### ATT&CK Coverage Integration Strategy (CRITICAL)

**Semantic Binding:**

```text
CAR Analytic X --[car:coverage_technique]--> ATT&CK Technique Y
means: "This analytic can detect/identify organizations where ATT&CK Technique Y has been executed or is present"
```

**ETL Implementation:**

1. Parse `coverage` array in analytic YAML
2. For each coverage object:
   - Extract `technique` field (e.g., "T1039")
   - Extract `tactics` array (e.g., ["TA0009"])
   - Extract optional `subtechniques` array (e.g., ["T1021.002"])
   - Extract optional `coverage` level (Low, Moderate, High)
3. Create ObjectProperty assertions:
   - `car:coverage_technique` linking to `attack:Technique`
   - Derived `car:coverage_tactic` linking to `attack:Tactic`
4. Create CoverageBucket object capturing full coverage metadata

**Bidirectional Index Support:**

Enable queries such as:

```sparql
SELECT ?analytic ?coverage_level WHERE {
  ?analytic car:coverage_technique attack:T1059 ;
            car:coverage ?coverage_bucket .
  ?coverage_bucket car:coverageLevel ?coverage_level .
}
```

**Coverage Level Semantics:**

- `Low` - Minimal or occasional detection capability
- `Moderate` - Reasonable detection coverage, may have false positives or gaps
- `High` - Comprehensive detection capability with high confidence

### D3FEND Alignment (Optional but Recommended)

**Semantic Binding:**

```text
CAR Analytic X --[car:has_d3fend_mapping]--> D3FEND DefensiveTechnique Y
means: "This analytic detects or supports the implementation of this defensive technique"
```

**ETL Implementation:**

1. Parse optional `d3fend_mappings` array in analytic YAML
2. For each D3FEND mapping:
   - Extract `iri`, `id`, `label` fields
   - Create reference to corresponding d3fend defensive technique
3. Create ObjectProperty assertion linking to d3fend namespace

**Example:**

```turtle
car:CAR_2013_01_003 car:has_d3fend_mapping d3fend:IPCTrafficAnalysis .
```

This enables questions like: "What analytics support the IPC Traffic Analysis defensive technique?" and "What defenses does this analytic support?"

### Data Model Federation

**Semantic Binding:**

```text
CAR Sensor X --[car:sensor_provides]--> DataModel Y
CAR Analytic Z --[car:analyzes_observable]--> DataModel Y
means: "Sensor X collects Y-observable data that Analytic Z analyzes"
```

**ETL Implementation:**

1. Extract data model entity definitions (10 types: Process, File, Flow, etc.)
2. For each sensor, parse `mappings` array:
   - Link sensor to DataModel entities via `object` field
   - Link to DataModelActions via `action` field
   - Link to DataModelFields via `fields` array
3. For each analytic, parse `data_model_references`:
   - Link to hierarchical data model fields (e.g., "flow/message/dest_port")

### Cardinality and Validation Rules

**Critical Constraints:**

| Rule | Severity | Description | Enforcement |
| ---- | -------- | ----------- | ----------- |
| Coverage Minimum | ERROR | Every analytic must have ≥1 coverage entry | Reject analytic without coverage |
| Coverage Format | ERROR | Coverage must include technique and tactic fields | Validate regex patterns before ingestion |
| ID Uniqueness | ERROR | analyticId must be globally unique (CAR-YYYY-MM-NNN) | Enforce via database constraints |
| DataModel Uniqueness | ERROR | DataModel entity names must be unique | Enforce via functional property |

**Recommended Constraints:**

| Rule | Severity | Description | Enforcement |
| ---- | -------- | ----------- | ----------- |
| D3FEND Coverage | WARN | Analytics should have D3FEND mappings (helps with defense alignment) | Log warnings, don't reject |
| Sensor Mapping | WARN | Analytic should reference sensors used for data collection | Log warnings, informational |

### Sensor Abstraction Levels

Sensors vary in abstraction and vendor:

| Sensor Type | Examples | Abstraction | Scope |
| ----------- | -------- | ----------- | ----- |
| **Host-based** | Sysmon, osquery, auditd | Low-level process/file system events | Single endpoint |
| **Cloud-based** | AWS CloudTrail, Azure Monitor | High-level API/service events | Cloud tenant/subscription |
| **Network-based** | PCAP, NetFlow | Network flow event data | Network segment |
| **Log aggregation** | Splunk, ELK | Heterogeneous log data (host, app, service) | Organization-wide |

**ETL Handling:** Preserve sensor-specific event identifiers (e.g., Sysmon Event ID 11 for file creation) in mapping notes.

### Status and Lifecycle

**Analytic Status:**

All CAR analytics are considered stable and production-ready. If future CAR versions introduce status variations (Draft, Deprecated, etc.):

```turtle
car:status a owl:DatatypeProperty ;
    rdfs:range xsd:string ;
    rdfs:comment "Status: stable (default), beta, deprecated, obsolete" .
```

### Version Tracking and Pinning

**KGCS CAR Mapping Alignment:**

```text
KGCS car-ontology-v1.0.owl <-- aligned with --> CAR v1.0 (Latest)
```

If CAR versions change:

- Option 1: Create new `car-ontology-v2.0.owl` alongside v1.0
- Option 2: Add version-aware properties: `car:compatibleWithCARVersion xsd:string`

---

## ETL Implementation

### Data Ingestion Pipeline

#### **Stage 1: Load CAR Raw Files**

```text
Input: data/raw/car/analytics/*.yaml
       data/raw/car/data_model/*.yaml
       data/raw/car/sensors/*.yaml
Parse: YAML parser (PyYAML, SnakeYAML, etc.)
Extract: All analytic, data model, and sensor definitions
Filter: Exclude incomplete/draft entries
```

#### **Stage 2: Validate Against Schema**

```text
Validation:
  ✓ Every analytic has CAR-YYYY-MM-NNN format ID
  ✓ Coverage array has minimum 1 entry
  ✓ Technique IDs match T[0-9]{4} pattern
  ✓ Tactic IDs match TA[0-9]{4} pattern
  ✓ Information domain is in allowed enum
  ✓ Required fields present (title, submission_date, description)
```

#### **Stage 3: Link to ATT&CK Framework**

```text
For each coverage entry:
  Extract technique ID (e.g., "T1039")
  Resolve to attack:Technique URI: http://www.motherhacker.me/kgcs/ontology/attack#T1039
  Create car:coverage_technique relationship
  Create derived car:coverage_tactic from technique's attack:belongs_to
```

#### **Stage 4: Link to D3FEND Framework (Optional)**

```text
For each d3fend_mapping entry:
  Extract iri, id, label
  Resolve to d3fend defensive technique IRI
  Create car:has_d3fend_mapping relationship
```

#### **Stage 5: Index and Store**

```text
Create RDF triples for all entities and relationships
Store in KGCS knowledge graph
Build indices for fast queries:
  - Analytic by ID (CAR-YYYY-MM-NNN)
  - Techniques by analytic
  - Sensors by data model type
  - Analytics by platform support
```

### Query Examples

#### **Query 1: Find all analytics detecting a specific technique**

```sparql
PREFIX car: <http://www.motherhacker.me/kgcs/ontology/car#>
PREFIX attack: <http://www.motherhacker.me/kgcs/ontology/attack#>

SELECT ?analytic ?title ?coverage_level WHERE {
  ?analytic car:coverage_technique attack:T1059 ;
            rdfs:label ?title ;
            car:coverage ?coverage_bucket .
  ?coverage_bucket car:coverageLevel ?coverage_level .
}
ORDER BY DESC(?coverage_level)
```

#### **Query 2: Find analytics with D3FEND defensive coverage**

```sparql
SELECT ?analytic ?title ?d3fend_defense WHERE {
  ?analytic car:has_d3fend_mapping ?d3fend_defense ;
            rdfs:label ?title ;
            car:coverage_technique ?technique .
  ?technique attack:belongs_to attack:Reconnaissance .
}
```

#### **Query 3: Find which sensors support a specific data model**

```sparql
SELECT ?sensor ?sensor_version ?actions WHERE {
  ?sensor car:sensor_provides car:Process ;
          car:sensorName ?sensorname ;
          car:sensorVersion ?sensor_version ;
          car:hasMapping ?mapping .
  ?mapping car:action ?actions .
}
```

#### **Query 4: Find data model references used by a specific analytic**

```sparql
SELECT ?analytic ?datamodel ?fields WHERE {
  ?analytic car:analyticId "CAR-2013-01-003" ;
            car:references_datamodel ?datamodel .
  ?datamodel car:hasField ?fields .
}
```

---

## Summary

CAR integration into KGCS leverages a three-entity federation model: Detection Analytics link to ATT&CK offensive techniques, Sensors map to cyber observable DataModels, and optional D3FEND mappings enable unification of offensive-defensive-detection alignment. The 100+ CAR analytics, 10 data models, and 7 sensor definitions are ingested via deterministic schema validation, enabling organizations to query "What analytics detect technique X?" and "What defenses support detection of Y?" across the full defensive-offensive spectrum.
