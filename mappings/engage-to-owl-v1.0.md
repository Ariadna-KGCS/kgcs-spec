# ENGAGE to OWL Mapping v1.0

## Overview

ENGAGE (Defender Adversary Engagement) is the MITRE framework for defensive engagement operations combining deception, denial, and detection activities to learn about and disrupt adversary operations. This mapping implements ENGAGE as a hierarchical goal-approach-activity architecture with integrated Engagement Adversarial Vulnerabilities (EAVs) that describe specific adversary behavioral weaknesses activities can exploit.

ENGAGE integrates with the ATT&CK offensive framework to provide defensive alignment: engagement activities map to ATT&CK techniques they engage with or detect, enabling defenders to understand how engagement strategies address offensive capabilities. The ENGAGE framework complements offensive-defensive alignment by focusing on active engagement tactics that go beyond static defense (like D3FEND mitigation) to include deception, dynamic interaction, and adversary learning.

**Key Concepts:**
- **Hierarchical Structure:** Strategic Goals decompose to Approaches, which organize Activities
- **Engagement Adversarial Vulnerabilities:** Behavioral weaknesses that activities can exploit
- **Bidirectional ATT&CK Alignment:** Activities link to offensive techniques for defensive-offensive analysis
- **Reference Knowledge:** Academic papers and documentation ground engagement tactics in research

---

## Sources

- **MITRE ENGAGE Framework:** Official framework for defender adversary engagement operations
- **Raw Data Location:** `data/raw/engage/` (12 JSON files)
- **Format:** JSON
- **Scale:** 20+ engagement activities (EACxxxx), 9 approaches (7 EAPxxxx + 2 SAPxxxx), 5 goals (3 EGOxxxx + 2 SGOxxxx), 30+ references (REFxxxx)
- **Namespace:** `http://www.motherhacker.me/kgcs/ontology/engage#`
- **External Framework Integrations:** ATT&CK (techniques and tactics), Engagement Adversarial Vulnerabilities (EAV framework)

---

## Target Ontology

- **File:** `ontology/standards/engage-ontology-v1.0.owl` (to be implemented)
- **Core Classes Used:**
  - `kgcs:EngagementConcept` - Base class for engagement concepts
  - `kgcs:DeceptionTechnique` - For deception/lure activities
  - `kgcs:DefensiveTechnique` - For defensive/prevention approaches
  - `kgcs:Reference` - For documentation references
- **New ENGAGE Namespace:** `engage: <http://www.motherhacker.me/kgcs/ontology/engage#>`
- **Core Import:** Explicit `owl:imports <http://www.motherhacker.me/kgcs/ontology/core#>`
- **Design Pattern:** Hierarchical federation with goal→approach→activity decomposition and EAV exploitation semantics

---

## Entity Mapping

### Primary Entity Types

| ENGAGE Source Entity | Target KGCS Class | Primary ID | ID Datatype | Notes |
| --- | --- | --- | --- | --- |
| Activity (EACxxxx) | engage:EngagementActivity | engage:activityId | xsd:string | Engagement activity (20+ instances); links to Goals, EAVs, ATT&CK techniques |
| Approach (EAP/SAPxxxx) | engage:EngagementApproach | engage:approachId | xsd:string | Strategic or tactical approach (9 total: 7 EAP + 2 SAP); organizes activities, achieves goals |
| Goal (EGO/SGOxxxx) | engage:EngagementGoal | engage:goalId | xsd:string | Engagement or strategic goal (5 total: 3 EGO + 2 SGO); decomposes to approaches |
| Reference (REFxxxx) | engage:Reference | engage:refId | xsd:string | Academic/technical reference (30+ instances); supports specific activity |

---

## Field Mapping: Engagement Activity Entity

### Core Required Fields

| Source Field | Target OWL Property | Range | Cardinality | Notes |
| --- | --- | --- | --- | --- |
| `id` | `engage:activityId` | xsd:string | 1 | Unique activity identifier; pattern: EAC[0-9]{4} (e.g., EAC0001) |
| `name` | `rdfs:label` | xsd:string | 1 | Human-readable activity name (e.g., "API Monitoring") |
| `description` | `rdfs:comment` | xsd:string | 1 | Short description (1-2 sentences) summarizing activity purpose |
| `long_description` | `engage:longDescription` | xsd:string | 1 | Detailed description with examples, use cases, and contextual information |
| `type` | `engage:activityType` | xsd:string | 1 | Activity classification: Enum = { "Engagement", "Strategic" }; required, exactly 1 |

### Optional Array Fields

| Source Field | Target OWL Property | Range | Cardinality | Notes |
| --- | --- | --- | --- | --- |
| `goals` | `engage:supports_goal` | xsd:string | 0+ | Goal IDs this activity supports (EGOxxxx or SGOxxxx); 0 to many |

### Complex Object Fields

| Source Field | Target Property | Type | Cardinality | Strategy | Notes |
| --- | --- | --- | --- | --- | --- |
| `vulnerabilities` | `engage:exploits_vulnerability` | engage:EAV | 0+ | Array of EAV objects | **CRITICAL:** Each EAV has two fields: `id` (EAVxxxx pattern) and `eav` (description text); 0 or more vulnerabilities per activity |
| `attack_techniques` | `engage:engages_technique` | attack:Technique | 0+ | Array of technique objects | Each object includes: `id` (T[0-9]{4} pattern), `name` (technique name), `attack_tactics` (array of tactic names) |

---

## Field Mapping: Engagement Approach Entity

### Core Required Fields

| Source Field | Target OWL Property | Range | Cardinality | Notes |
| --- | --- | --- | --- | --- |
| `id` | `engage:approachId` | xsd:string | 1 | Unique approach identifier; pattern: (EAP\|SAP)[0-9]{4} (e.g., EAP0001, SAP0001) |
| `name` | `rdfs:label` | xsd:string | 1 | Approach name (e.g., "Collect", "Detect", "Plan", "Analysis") |
| `description` | `rdfs:comment` | xsd:string | 1 | Short description of approach purpose and scope |
| `long_description` | `engage:longDescription` | xsd:string | 1 | Strategic context describing how approach supports goals; includes rationale and application context |

---

## Field Mapping: Engagement Goal Entity

### Core Required Fields

| Source Field | Target OWL Property | Range | Cardinality | Notes |
| --- | --- | --- | --- | --- |
| `id` | `engage:goalId` | xsd:string | 1 | Unique goal identifier; pattern: (EGO\|SGO)[0-9]{4} (e.g., EGO0001, SGO0001) |
| `name` | `rdfs:label` | xsd:string | 1 | Goal name (e.g., "Expose", "Affect", "Elicit", "Prepare", "Understand") |
| `description` | `rdfs:comment` | xsd:string | 1 | Short description of goal objective |
| `long_description` | `engage:longDescription` | xsd:string | 1 | Detailed strategic context; describes sub-goals, rationale, and operational implications |

### Optional Fields

| Source Field | Target OWL Property | Range | Cardinality | Notes |
| --- | --- | --- | --- | --- |
| `goal_type` | `engage:goalType` | xsd:string | 0-1 | Goal classification: Enum = { "Engagement", "Strategic" }; optional, 0 or 1 value |

---

## Field Mapping: Reference Entity

### Core Required Fields

| Source Field | Target OWL Property | Range | Cardinality | Notes |
| --- | --- | --- | --- | --- |
| `id` | `engage:refId` | xsd:string | 1 | Unique reference identifier; pattern: REF[0-9]{4} (e.g., REF0001) |
| `title` | `rdfs:label` | xsd:string | 1 | Title of reference (academic paper, article, documentation, etc.) |
| `url` | `engage:url` | xsd:anyURI | 1 | Valid URI to reference material (DOI, arxiv, documentation link); must be HTTP/HTTPS |
| `activity_id` | `engage:documents_activity` | engage:EngagementActivity | 1 | Links to specific activity (EACxxxx); **1-to-1 relationship** (one reference per activity, binds reference to activity) |

---

## Relationship Mapping

### Critical: Activity-to-Goal Relationships

| Relationship | Domain | Range | Cardinality | Semantics |
| --- | --- | --- | --- | --- |
| `engage:supports_goal` | EngagementActivity | EngagementGoal | 0+ | **CRITICAL:** This activity helps achieve this goal; enables queries: "What activities support EGO0001 (Expose)?" |

### Critical: Activity-to-EAV Relationships

| Relationship | Domain | Range | Cardinality | Semantics |
| --- | --- | --- | --- | --- |
| `engage:exploits_vulnerability` | EngagementActivity | EAV | 0+ | **CRITICAL:** This activity can exploit this adversary behavioral vulnerability; enables "What vulnerabilities does API Monitoring target?" queries |

### Critical: Activity-to-ATT&CK Relationships

| Relationship | Domain | Range | Cardinality | Semantics |
| --- | --- | --- | --- | --- |
| `engage:engages_technique` | EngagementActivity | attack:Technique | 0+ | This activity engages with or detects this ATT&CK offensive technique; enables defensive-offensive alignment |
| `engage:engages_tactic` | EngagementActivity | attack:Tactic | 0+ | Derived from technique-to-tactic mappings in ATT&CK; implicit relationship |

### Hierarchical Relationships (Ontology Structure)

| Relationship | Domain | Range | Semantics |
| --- | --- | --- | --- |
| `engage:approach_enables` | EngagementApproach | EngagementActivity | Approach organizes and enables related activities |
| `engage:goal_has_approach` | EngagementGoal | EngagementApproach | Goal decomposes into approaches; goal→approach→activity hierarchy |

### Reference Relationship

| Relationship | Domain | Range | Cardinality | Semantics |
| --- | --- | --- | --- | --- |
| `engage:documents_activity` | Reference | EngagementActivity | 1 | Reference provides academic/technical support for this activity; **1-to-1 relationship** |

---

## Transformation Notes

### Engagement Adversarial Vulnerability (EAV) Exploitation Semantics

**Semantic Binding:**

```
EngagementActivity --[engage:exploits_vulnerability]--> EAV
Semantics: "This activity can exploit this adversary vulnerability when executed"
```

EAVs define specific behavioral vulnerabilities that adversaries exhibit when operating in engagement environments. Unlike generic network vulnerabilities (CVE), EAVs capture how adversary behavior becomes exploitable through defender interaction.

**Examples from ENGAGE:**

- **EAC0001 (API Monitoring)** exploits:
  - **EAV0001:** "When adversaries interact with environment/personas, vulnerable to revealing behaviors"
  - **EAV0010:** "When adversaries interact with resources, vulnerable to triggering tripwires/detection"

- **EAC0005 (Lures)** exploits:
  - **EAV0001:** Behavioral disclosure when adversary interacts with deceptive content
  - **EAV0002:** Observable interaction patterns during social engineering

- **EAC0021 (Change Default Credentials)** exploits:
  - **EAV0003:** Adversary vulnerability when using/detecting modified credentials
  - **EAV0010:** Tripwire triggering when accessing credential-protected resources

**ETL Implementation:** Extract EAV objects (id + description) from activity vulnerabilities arrays; create engage:exploits_vulnerability relationships with full EAV metadata.

---

### Goal-Approach-Activity Hierarchy

**Structure:**

```
Strategic Goals (SGO0001-SGO0002)
├── SGO0001 "Prepare" → Approach SAP0001 "Plan"
│   └── Activities: Program design, operation planning, personnel assignment
└── SGO0002 "Understand" → Approach SAP0002 "Analysis"
    └── Activities: Intelligence analysis, behavior analysis, capability assessment

Engagement Goals (EGO0001-EGO0003)
├── EGO0001 "Expose" → Approaches
│   ├── EAP0001 "Collect" → Activities: API Monitoring, Lures, Decoys
│   └── EAP0002 "Detect" → Activities: Behavior profiling, anomaly detection
├── EGO0002 "Affect" → Approaches
│   ├── EAP0003 "Prevent" → Activities: Blocking, restriction
│   ├── EAP0004 "Direct" → Activities: Redirection, guidance
│   └── EAP0005 "Disrupt" → Activities: Disruption, denial
└── EGO0003 "Elicit" → Approaches
    ├── EAP0006 "Reassure" → Activities: Message reassurance, authenticity
    └── EAP0007 "Motivate" → Activities: Motivation, incentivization
```

**Semantic Pattern:**
- Goals are strategic/tactical objectives
- Approaches are categories organizing related activities
- Activities are specific implementation actions
- **Ontology Implication:** Goals and Approaches are distinct concepts from Activities (not subclasses); Activities are leaf implementations

**Cardinality:**
- Goal-to-Approach: 1-to-many (one goal has multiple approaches)
- Approach-to-Activity: many-to-many (activities can support multiple approaches; approaches organize activities)

---

### ATT&CK Alignment Pattern

**Semantic Binding:**

```
EngagementActivity --[engage:engages_technique]--> ATT&CK Technique
EngagementActivity --[engage:engages_tactic]--> ATT&CK Tactic (derived)
Semantics: "This activity engages with/detects this offensive technique"
```

Each activity's `attack_techniques` array contains objects with:
- `id`: ATT&CK technique ID (T[0-9]{4} pattern, e.g., "T1007")
- `name`: Technique name
- `attack_tactics`: Array of associated tactic names

**ETL Implementation:**
1. Parse activity's `attack_techniques` array
2. For each technique, extract ID and resolve to attack:Technique URI
3. Create `engage:engages_technique` relationship
4. Derive `engage:engages_tactic` from ATT&CK technique-to-tactic mappings

**Query Capability:**
- "Find all ENGAGE activities that engage with technique T1007 (System Service Discovery)"
- "What ATT&CK tactics do our engagement activities address?"
- "Which engagement approaches detect techniques in the Reconnaissance tactic?"

**Defensive-Offensive Alignment:** Activities → Techniques links enable full defensive analysis: ENGAGE Activities → ATT&CK Techniques → D3FEND Defenses

---

### Activity Type: Engagement vs Strategic

**Semantic Distinction:**

- **"Engagement" Type:** Active engagement operations during active defense
  - Examples: Collection (API Monitoring, Lures), Detection (profiling), Prevention (restrictions), Direction (redirection), Disruption (blocking), Reassurance (authenticity adding), Motivation (incentive)
  - Operational focus: Direct adversary interaction

- **"Strategic" Type:** Strategic planning and intelligence analysis
  - Examples: Program preparation, personnel planning, intelligence analysis, threat assessment
  - Operational focus: Preparation and learning, not direct engagement

**Constraint:** Activity type must be exactly 1, required, non-null. Every activity must be classified as either Engagement or Strategic.

---

### Cardinality Rules

**Critical Constraints:**

| Rule | Severity | Description | Enforcement |
| --- | --- | --- | --- |
| Activity Type Required | ERROR | Every activity must have exactly 1 type field (Engagement OR Strategic) | Reject activity without type |
| Activity ID Unique | ERROR | activityId must be globally unique and follow EAC[0-9]{4} pattern | Enforce via ontology functional property |
| Reference to Activity | ERROR | Every reference must link to exactly 1 activity via activity_id field | 1-to-1 relationship; reject orphan references |
| Goal/Approach ID Pattern | ERROR | All ID patterns must match (EGO\|SGO\|EAP\|SAP)[0-9]{4} | Validate regex before ingestion |

**Recommended Constraints:**

| Rule | Severity | Description | Enforcement |
| --- | --- | --- | --- |
| Activity Goal Support | WARN | Activity should support ≥1 goal (behavioral anchoring) | Log warnings but accept 0 goals |
| Engagement Activity-Technique Link | WARN | Engagement-type activities should engage with ≥1 ATT&CK technique | Log warnings; aids defensive-offensive alignment |
| Goal-Approach Mapping | WARN | Approaches should be explicitly mapped to goals in ontology | Log warnings; aids traceability |

**Identifier Uniqueness Rules:**

- **Activity IDs (EACxxxx):** Globally unique, never reused (static for lifetime)
- **Approach IDs (EAPxxxx/SAPxxxx):** Globally unique, never reused
- **Goal IDs (EGOxxxx/SGOxxxx):** Globally unique, never reused
- **Reference IDs (REFxxxx):** Globally unique, never reused
- **EAV IDs (EAVxxxx):** Globally unique, externally maintained by MITRE ENGAGE program

---

## ETL Implementation

### Stage 1: Load ENGAGE JSON Files

```
Input: data/raw/engage/*.json
  - activities.json (activity definitions)
  - approaches.json (approach definitions)
  - goals.json (goal definitions)
  - references.json (reference definitions)
  - activity_details.json (complex activity metadata)
  - attack_mapping.json (ATT&CK technique linkages)
  - goal_approach_mappings.json (hierarchical relationships)

Parser: JSON parser (standard libraries)
Extract: All Activity, Approach, Goal, Reference entity definitions
Filter: Exclude incomplete entries (status = draft)
Output: In-memory entity store with complete metadata
```

### Stage 2: Validate Against Schema

```
Validation Rules:
✓ Every activity has EAC[0-9]{4} format ID (pattern matching)
✓ Every activity has exactly 1 type field; value ∈ { "Engagement", "Strategic" }
✓ Every goal/approach has (EGO|SGO|EAP|SAP)[0-9]{4} format ID
✓ Every reference has REF[0-9]{4} format ID
✓ All ATT&CK technique IDs match T[0-9]{4} or T[0-9]{4}\.[0-9]{3} pattern (supports subtechniques)
✓ All tactic names are valid ATT&CK tactic identifiers (discovery, execution, persistence, etc.)
✓ Required fields present for each entity (id, name, description, long_description)
✓ Goal references in activities (goals array) point to valid goal IDs
✓ No circular dependencies in hierarchy (Goal→Approach→Activity)
```

### Stage 3: Link to ATT&CK Framework

```
For each activity's attack_techniques array:
  1. Extract technique ID (e.g., "T1007")
  2. Validate format: T[0-9]{4} or T[0-9]{4}\.[0-9]{3}
  3. Resolve to attack:Technique URI:
     http://www.motherhacker.me/kgcs/ontology/attack#T1007
  4. Create engage:engages_technique relationship
  5. Lookup technique-to-tactic mappings in ATT&CK ontology
  6. Create engage:engages_tactic relationships (derived)
  7. Store coverage metadata (if present)

Example:
  Activity EAC0001 has attack_techniques = [
    { id: "T1007", name: "System Service Discovery", attack_tactics: ["discovery"] },
    { id: "T1016", name: "System Network Configuration Discovery", attack_tactics: ["discovery"] }
  ]
  Result: EAC0001 engages with T1007 and T1016; EAC0001 engages with discovery tactic
```

### Stage 4: Link to EAV Framework

```
For each activity's vulnerabilities array:
  1. Extract EAV object: { id: "EAVxxxx", eav: "description text" }
  2. Validate EAV ID matches EAV[0-9]{4} pattern
  3. Validate EAV description is non-empty
  4. Create engage:exploits_vulnerability relationship
  5. Preserve vulnerability description as triple comment/metadata

Example:
  Activity EAC0001 has vulnerabilities = [
    { id: "EAV0001", eav: "When adversaries interact with environment/personas, vulnerable to revealing behaviors" },
    { id: "EAV0010", eav: "When adversaries interact with resources, vulnerable to triggering tripwires/detection" }
  ]
  Result: EAC0001 exploits EAV0001 and EAV0010
```

### Stage 5: Index and Store

```
Create RDF Triples:
  1. All entity instances (Activity, Approach, Goal, Reference)
  2. All relationships (supports_goal, exploits_vulnerability, engages_technique, documents_activity)
  3. All metadata (rdfs:label, rdfs:comment, custom properties)

Build Query Indices:
  - Activity ID → Activity instance (EAC[0-9]{4})
  - Goal ID → Goal instance (EGO/SGO xxxx)
  - Activity → Goals (inverse query: what activities support this goal)
  - Activity → EAVs (vulnerability exploitation index)
  - Activity → Techniques (offensive alignment)
  - Activity → References (reference lookup)
  - Approach → Activities (approach-activity membership)

Store: Persist triples to KGCS knowledge graph (RDF store)

Result: Fully federated ENGAGE knowledge graph ready for SPARQL queries
```

---

## Example SPARQL Queries

### Query 1: Find activities supporting a specific goal

```sparql
PREFIX engage: <http://www.motherhacker.me/kgcs/ontology/engage#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?activity ?name ?description WHERE {
  ?activity engage:supports_goal engage:EGO0001 ;
            rdfs:label ?name ;
            rdfs:comment ?description .
}
```

*Result:* All activities supporting EGO0001 (Expose goal)

### Query 2: Find activities exploiting a specific vulnerability

```sparql
PREFIX engage: <http://www.motherhacker.me/kgcs/ontology/engage#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?activity ?name WHERE {
  ?activity engage:exploits_vulnerability ?eav ;
            rdfs:label ?name .
  ?eav rdf:value "EAV0001" .
}
```

*Result:* All activities that exploit adversary behavioral vulnerability EAV0001

### Query 3: Find activities engaging with ATT&CK techniques in a specific tactic

```sparql
PREFIX engage: <http://www.motherhacker.me/kgcs/ontology/engage#>
PREFIX attack: <http://www.motherhacker.me/kgcs/ontology/attack#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?activity ?name ?technique WHERE {
  ?activity engage:engages_technique ?technique ;
            rdfs:label ?name .
  ?technique attack:belongs_to attack:Reconnaissance .
}
```

*Result:* All ENGAGE activities that engage with techniques in ATT&CK's Reconnaissance tactic

### Query 4: Find approaches supporting a goal

```sparql
PREFIX engage: <http://www.motherhacker.me/kgcs/ontology/engage#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?approach ?approach_name WHERE {
  ?goal engage:goal_has_approach ?approach .
  ?goal rdf:value engage:EGO0001 .
  ?approach rdfs:label ?approach_name .
}
```

*Result:* All approaches that support EGO0001 (should be EAP0001, EAP0002)

### Query 5: Find references for a specific activity

```sparql
PREFIX engage: <http://www.motherhacker.me/kgcs/ontology/engage#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?ref ?title ?url WHERE {
  ?ref engage:documents_activity engage:EAC0001 ;
       rdfs:label ?title ;
       engage:url ?url .
}
```

*Result:* Academic papers and documentation supporting EAC0001 (API Monitoring)

---

## Summary

ENGAGE mapping to KGCS OWL provides a complete hierarchical representation of the defender adversary engagement framework. The mapping:

- **Preserves ENGAGE Hierarchy:** Goals decompose to Approaches, which organize Activities
- **Exploits EAV Framework:** Activities explicitly link to behavioral vulnerabilities they target
- **Enables Defensive-Offensive Alignment:** Activities→ATT&CK Techniques→D3FEND Defenses chain
- **Supports Federation:** 4 entity types (Activity, Approach, Goal, Reference) with clear cardinality rules
- **Provides Query Capability:** SPARQL enables offensive-defensive analysis, vulnerability targeting, and reference grounding

The ontology implementation will define engage:* properties and classes following this specification, enabling KGCS users to reason about engagement strategies, adversary vulnerabilities, and defensive-offensive alignment in a unified cybersecurity knowledge graph.

