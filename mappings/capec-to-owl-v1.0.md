# CAPEC to OWL Mapping v1.0

## Overview

CAPEC (Common Attack Pattern Expression and Enumeration) is the MITRE-maintained repository of common attack patterns used by adversaries. Each attack pattern describes a methodology for targeting specific weaknesses, covering attack prerequisites, execution flows, and typical severity outcomes. CAPEC patterns map to the core ontology's `kgcs:AttackPattern` class, providing detailed attack methodology semantics complementary to ATT&CK tactics and techniques. This mapping bridges CAPEC schema v3.5.0 XML structures into KGCS OWL representation for integrated threat modeling and attack surface analysis.

---

## Sources

- `data/schemas/CAPEC/ap_schema_latest.xsd` (CAPEC v3.5.0, October 2021)
- MITRE CAPEC Knowledge Base: <http://capec.mitre.org/>
- CAPEC namespace: `http://capec.mitre.org/capec-3`
- XML Schema defines root `Attack_Pattern_Catalog` with:
  - Attack_Patterns collection (unbounded)
  - Categories collection (groupings by effect/intent)
  - Views collection (perspective-based organization)
  - External_References collection (citations, resources)

---

## Target Ontology

- `ontology/standards/capec-ontology-v1.0.owl` (to be created)
- Core classes used: `kgcs:AttackPattern` (from core ontology)
- New CAPEC namespace: `capec: <http://www.motherhacker.me/kgcs/ontology/capec#>`
- Import: `owl:imports <http://www.motherhacker.me/kgcs/ontology/core#>`
- Inheritance: All CAPEC classes extend or relate to core cybersecurity semantics

---

## Entity Mapping

| Source Record Type | Target Class | Primary ID | ID Datatype | Key Name Field | Notes |
| --- | --- | --- | --- | --- | --- |
| `AttackPatternType` | `kgcs:AttackPattern` | `capec:capecId` | xsd:integer | `capec:name` | Primary entity; inherits from core; requires ID, Name, Abstraction, Status |
| `CategoryType` | `capec:Category` | `capec:categoryId` | xsd:integer | `capec:categoryName` | Grouping mechanism for patterns by effect/intent; optional organizational entity |
| `ViewType` | `capec:View` | `capec:viewId` | xsd:integer | `capec:viewName` | Perspective-based collection of patterns; three types: Graph, Explicit, Implicit |
| External Reference | handled via `capec:references` | (string) | xsd:string | Title | Not primary entity; linked from patterns/categories/views |

---

## Field Mapping: Attack Pattern (Primary Entity)

### Core Required Fields

| Source Field | XSD Type | Target OWL Property | Range | Cardinality | Notes |
| --- | --- | --- | --- | --- | --- |
| `@ID` | xs:integer | `capec:capecId` | xsd:integer | 1 | Unique globally static identifier; never reused even if deprecated |
| `@Name` | xs:string | `capec:name` | xsd:string | 1 | Capitalized descriptive title (except articles, prepositions) |
| `@Abstraction` | xs:enumeration | `capec:abstraction` | xsd:string | 1 | Enum: meta, standard, detailed (hierarchical abstraction levels) |
| `@Status` | xs:enumeration | `capec:status` | xsd:string | 1 | Enum: stable, usable, draft, incomplete, deprecated, obsolete |
| `Description` | StructuredTextType | `capec:description` | rdf:HTML or xsd:string | 1 | High-level 1-3 sentence overview including intent, technique, impact |
| `Extended_Description` | StructuredTextType | `capec:extendedDescription` | rdf:HTML or xsd:string | 0-1 | Additional context, rationale, interesting notes not in primary description |

### Optional Metadata Fields

| Source Field | XSD Type | Target OWL Property | Range | Cardinality | Notes |
| --- | --- | --- | --- | --- | --- |
| `Alternate_Terms` | AlternateTermsType | `capec:alternateTerms` | xsd:string* | 0+ | Synonymous names with context descriptions |
| `Typical_Severity` | SeverityEnumeration | `capec:typicalSeverity` | xsd:string | 0-1 | Average severity: veryHigh, high, medium, low, veryLow |
| `Likelihood_Of_Attack` | LikelihoodEnumeration | `capec:attackLikelihood` | xsd:string | 0-1 | Success probability: high, medium, low, unknown |

### Complex Type Aggregations

| Source Element | Target Property | Type | Cardinality | Mapping Strategy | Notes |
| --- | --- | --- | --- | --- | --- |
| `Related_Attack_Patterns` | `capec:relatedPatterns` | ObjectProperty (named) | 0+ | One property per relationship type (childOf, parentOf, etc.) | Hierarchical and sequential pattern relationships |
| `Execution_Flow` | `capec:executionSteps` | rdf:Seq (ordered) | 0+ | Sequence of steps with number, phase, description | Three phases: Explore (reconnaissance), Experiment (testing), Exploit (execution) |
| `Prerequisites` | `capec:prerequisites` | rdf:Bag (unordered) | 0+ | Text description bag | Conditions required for successful attack deployment |
| `Skills_Required` | `capec:skillsRequired` | rdf:Bag of SkillRequirement | 0+ | Skill objects with level + description | Attacker knowledge/capabilities needed (high, medium, low) |
| `Resources_Required` | `capec:resourcesRequired` | rdf:Bag (unordered) | 0+ | Text description bag | Tools, infrastructure, access, or special knowledge required |
| `Indicators` | `capec:indicators` | rdf:Bag (unordered) | 0+ | Text description bag | Observable behaviors, artifacts, network patterns indicating attack |
| `Consequences` | `capec:consequences` | rdf:Bag of Consequence | 0+ | Objects with scope + impact + likelihood | Security impacts: Confidentiality, Integrity, Availability, etc. |
| `Mitigations` | `capec:mitigations` | rdf:Bag (unordered) | 0+ | Text description bag | Design, implementation, operational strategies to prevent/detect |
| `Example_Instances` | `capec:exampleInstances` | rdf:Bag (unordered) | 0+ | Text description bag | Real-world attacks, specific incidents, CVE examples |
| `Related_Weaknesses` | `capec:exploitsCWE` | ObjectProperty | 1+ | Reference to CWE ontology individuals | **CRITICAL:** Links to weaknesses (CWE) that enable the attack |
| `Taxonomy_Mappings` | `capec:mappedTo` | ObjectProperty (with fit) | 0+ | Cross-taxonomy references with quality indicators | ATTACK, WASC, OWASP Attacks frameworks |

---

## Field Mapping: Category and View Entities

### Category Fields

| Source Field | Target Property | Range | Cardinality | Notes |
| --- | --- | --- | --- | --- |
| `@ID` | `capec:categoryId` | xsd:integer | 1 | Unique stable identifier |
| `@Name` | `capec:categoryName` | xsd:string | 1 | Descriptive title |
| `@Status` | `capec:categoryStatus` | xsd:string | 1 | Status enum same as patterns |
| `Summary` | `capec:categorySummary` | rdf:HTML or xsd:string | 1 | Short key-points defining category |
| `Relationships` | `capec:categoryConcerns` | ObjectProperty | 0+ | Pattern/Category/View membership |
| `References` | `capec:categoryReferences` | ObjectProperty | 0+ | External citation links |

### View Fields

| Source Field | Target Property | Range | Cardinality | Notes |
| --- | --- | --- | --- | --- |
| `@ID` | `capec:viewId` | xsd:integer | 1 | Unique stable identifier |
| `@Name` | `capec:viewName` | xsd:string | 1 | Descriptive title |
| `@Type` | `capec:viewType` | xsd:string | 1 | Enum: Graph, Explicit, Implicit |
| `@Status` | `capec:viewStatus` | xsd:string | 1 | Status enum |
| `Objective` | `capec:viewObjective` | rdf:HTML or xsd:string | 1 | Perspective/purpose of view |
| `Audience` | `capec:viewAudience` | xsd:string | 0-1 | Target stakeholders |
| `Members` | `capec:viewMembers` | ObjectProperty | 0+ | Pattern/Category membership in view |

---

## Relationship Mapping

### Attack Pattern Relationships (Critical)

Related patterns are organized by nature of relationship, reflecting attack methodology dependencies:

| Relationship Type | Target Property | Domain | Range | Direction | Inverse | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| ChildOf | `capec:childOf` | AttackPattern | AttackPattern | directed | `capec:parentOf` | Pattern at lower abstraction level (inherits from higher) |
| ParentOf | `capec:parentOf` | AttackPattern | AttackPattern | directed | `capec:childOf` | Pattern at higher abstraction level (generalizes lower) |
| CanPrecede | `capec:canPrecede` | AttackPattern | AttackPattern | directed | `capec:canFollow` | Can logically occur before in multi-stage attack |
| CanFollow | `capec:canFollow` | AttackPattern | AttackPattern | directed | `capec:canPrecede` | Can logically occur after in multi-stage attack |
| CanAlsoBe | `capec:canAlternateWith` | AttackPattern | AttackPattern | bidirectional | symmetric | Alternative characterization of same attack method |
| PeerOf | `capec:peerOf` | AttackPattern | AttackPattern | bidirectional | symmetric | Similar pattern without hierarchical or sequential relationship |

**Exclude_Related Logic:** Relationship can have exception contexts (e.g., "ChildOf X except in Y context") - preserved in Transformation Notes.

### Critical External Relationships

#### CWE Linkage (Weakness Exploitation - CRITICAL)

| Relationship | Domain | Range | Cardinality | Semantics | Notes |
| --- | --- | --- | --- | --- | --- |
| `capec:exploitsCWE` | AttackPattern | CWEWeakness | 1+ | "This attack pattern exploits one or more of these weaknesses" | **REQUIRED:** Minimum 1 CWE per pattern recommended for ETL validation |

**Logic:** Multiple CWEs = ANY one (or specific combination) may enable the attack. Does NOT imply all must be present for success.

**Implementation:** Create bidirectional reference enabling queries:

- Forward: "What CWEs does this CAPEC pattern exploit?"
- Reverse: "What CAPEC patterns exploit CWE-89?"

#### Category/View Organization

| Relationship | Source | Target | Cardinality | Semantics |
| --- | --- | --- | --- | --- |
| `capec:memberOf` | AttackPattern | Category | 0+ | Pattern belongs to category (grouping by effect/intent) |
| `capec:hasMember` | Category | AttackPattern | 0+ | Category contains pattern (inverse) |
| `capec:memberOf` | AttackPattern | View | 0+ | Pattern is perspective member of view |
| `capec:hasMember` | View | AttackPattern | 0+ | View includes pattern (inverse) |

#### Cross-Taxonomy Mapping

| Relationship | Domain | Range | Cardinality | Structure |
| --- | --- | --- | --- | --- |
| `capec:mappedTo` | AttackPattern | External Concept | 0+ | Contains mapping quality indicator (exact, more abstract, more specific, imprecise, perspective) |

**Supported Taxonomies:** ATT&CK, WASC, OWASP Attacks, others

---

## Transformation Notes

### CWE Integration Strategy (Critical for ETL)

**Semantic Binding:**

```text
CAPEC Pattern X exploitsCWE [CWE-Y, CWE-Z]
means: "Successful execution of Pattern X requires the presence of Weakness Y OR Z (or combination)"
```

**ETL Implementation:**

1. Parse `Related_Weakness` CDATA containing `<Related_Weakness CWE_ID="[integer]"/>`
2. Create `capec:exploitsCWE` ObjectProperty linking to external CWE instance URI
3. Format CWE URI: `http://www.motherhacker.me/kgcs/ontology/cwe#CWE_[ID]`
4. Example: CAPEC-18 (SQL Injection) → capec:exploitsCWE → CWE-89
5. **Validation:** Alert if pattern has zero CWE references (recommend minimum 1)

**Bidirectional Index Support:**
Enable queries such as:

```sparql
SELECT ?pattern WHERE {
  ?pattern capec:exploitsCWE cwe:CWE_89 .
}
```

### Attack Pattern Abstraction Levels (Hierarchy)

```text
Meta          [Generalized approach, technology-agnostic, parent patterns]
  ├─ Standard [Focused technique/methodology, general approach]
  │  └─ Detailed [Low-level specifics, technology/implementation-bound]
```

**Ontology Implementation Options:**

Option 1: Datatype Property (Recommended)

```turtle
capec:abstraction a owl:DatatypeProperty ;
    rdfs:domain kgcs:AttackPattern ;
    rdfs:range xsd:string ;
    rdfs:comment "Enum values with implicit hierarchy (client imposes ordering)" .
```

Option 2: Class Hierarchy

```turtle
capec:DetailedPattern rdfs:subClassOf capec:StandardPattern ;
  rdfs:subClassOf capec:MetaPattern .
```

**ETL Rule:** Enforce hierarchy: Meta-level patterns cannot have Detailed parents.

### Status Lifecycle & Interpretation

| Status | Production Ready? | Usage | Treatment |
| --- | --- | --- | --- |
| **Stable** | ✅ YES | Vetted, production deployment | Use as-is |
| **Usable** | ✅ YES | Ready for use, minor issues remain | Use with caution |
| **Draft** | ❌ NO | Under development, incomplete | Informational only; flag in ETL |
| **Incomplete** | ❌ NO | Needs additional work | Do not process; alert developers |
| **Deprecated** | ❌ NO | Superseded by newer patterns | Keep for historical traceability only |
| **Obsolete** | ❌ NO | No longer valid, replaced | Consider removal; keep lineage |

**ETL Implementation:** Filter based on status in ETL rules; provide status-aware query results for trust scoring.

### Complex Type Handling

#### 1. ExecutionFlow → Ordered Sequence

**XML Structure Example:**

```xml
<Execution_Flow>
  <Attack_Step Number="1" Phase="Explore">
    <Description>Attacker searches for target...</Description>
  </Attack_Step>
  <Attack_Step Number="2" Phase="Experiment">
    <Description>Attacker tests for vulnerability...</Description>
  </Attack_Step>
</Execution_Flow>
```

**OWL Representation (rdf:Seq for ordering):**

```turtle
[ rdf:type rdf:Seq ;
  rdf:_1 [ capec:stepNumber 1 ;
           capec:stepPhase "Explore" ;
           capec:stepDescription "Attacker searches for..." ] ;
  rdf:_2 [ capec:stepNumber 2 ;
           capec:stepPhase "Experiment" ;
           capec:stepDescription "Attacker tests for..." ]
]
```

**Phase Enumeration:** Explore (reconnaissance), Experiment (testing), Exploit (execution)

#### 2. Prerequisites → Unordered Bag

**Representation:** rdf:Bag of text descriptions (unordered, typically 1-5 items)

```turtle
capec:prerequisites [ rdf:type rdf:Bag ;
  rdf:_1 "Attacker has network access to target" ;
  rdf:_2 "Target system has unpublished vulnerability"
]
```

#### 3. SkillsRequired → Typed Objects with Levels

**OWL Class:**

```turtle
capec:SkillRequirement a owl:Class ;
  rdfs:subClassOf [
    owl:onProperty capec:skillName ;
    owl:hasValue "SQL Injection"
  ] .
```

**Instance Structure:**

```turtle
[ capec:skillName [ rdfs:label "SQL Injection" ] ;
  capec:skillLevel "Medium" ;
  capec:skillDescription "Understanding of SQL mechanics..."
]
```

**Skill Levels:** High (expert knowledge), Medium (intermediate training), Low (basic/widely available)

#### 4. Consequences → Typed Objects with Scope + Impact

**OWL Class:**

```turtle
capec:Consequence a owl:Class ;
  rdfs:domain kgcs:AttackPattern ;
  rdfs:properties (capec:scope capec:technicalImpact capec:likelihood)
```

**Instance Structure:**

```turtle
[ capec:scope "Integrity" ;
  capec:technicalImpact "Modify Data" ;
  capec:likelihood "Always"
]
```

**Scope Values:** Confidentiality, Integrity, Availability, Access Control, Accountability, Authentication, Authorization, Non-Repudiation, Other

**Technical Impacts:** Modify Data, Read Data, Unreliable Execution, Resource Consumption, Execute Unauthorized Commands, Gain Privileges, Bypass Protection, Hide Activities, Alter Logic, Other

#### 5. Mitigations/Indicators/Resources/Examples → Unordered Bags

```turtle
capec:mitigations [ rdf:type rdf:Bag ;
  rdf:_1 "Implement prepared statements" ;
  rdf:_2 "Apply input validation whitelist" ;
  rdf:_3 "Use web application firewall"
]
```

### Taxonomy Mapping Quality Indicators

**Cross-Framework Mapping:**

| Fit Indicator | Meaning | Example |
| --- | --- | --- |
| **Exact** | Precise 1:1 semantic correspondence | CAPEC-18 ↔ ATTACK T1190 (Exploit Public-Facing Application) |
| **CAPEC More Abstract** | CAPEC generalizes external concept | CAPEC-18 (SQL Injection patterns) generalizes WASC Web Services Attack |
| **CAPEC More Specific** | CAPEC specializes external concept | CAPEC-18 (SQL Injection) extends OWASP's "Injection" category |
| **Imprecise** | Loose correspondence, partial overlap | CAPEC-28 (Reflection Attack) loosely relates to ATTACK T1021 (RDP Hijacking) |
| **Perspective** | Different viewpoint, not direct mapping | CAPEC patterns (methodology) vs ATT&CK techniques (observable behavior) |

**ETL Mapping Structure:**

```turtle
[ capec:externalConceptId "ATTACK-T1190" ;
  capec:externalFramework "ATT&CK Enterprise" ;
  capec:mappingQuality "Exact" ;
  capec:mappingNotes "Technique describes exploitation; CAPEC describes methodology"
]
```

### Identifier Uniqueness Constraints

**Enforcement Rules:**

1. **capec:capecId** globally unique integer; NEVER reused (even if pattern deprecated)
2. **capec:categoryId** globally unique; same reuse prevention rule
3. **capec:viewId** globally unique; same reuse prevention rule
4. When deprecating: Keep placeholder entry with deprecated comment, do NOT reassign ID

**ETL Validation:**

```sparql
SELECT ?id (COUNT(?pattern) as ?count) WHERE {
  ?pattern capec:capecId ?id .
} GROUP BY ?id HAVING (?count > 1)
-- Should return empty result set
```

### Alternate Terms Handling

**XML Structure:**

```xml
<Alternate_Terms>
  <Alternate_Term>
    <Term>SQL Injection Attack</Term>
    <Description>Traditional reference in older literature</Description>
  </Alternate_Term>
</Alternate_Terms>
```

**OWL Representation:**

```turtle
[ capec:term "SQL Injection Attack" ;
  capec:termContext "Traditional reference in older literature"
]
```

### Content History & Provenance

**Tracking:** Author, submission date, modification dates with importance levels (Normal/Critical)

**OWL Class:**

```turtle
capec:ContentHistory a owl:Class ;
  properties: (capec:submitter capec:submissionDate capec:modifications)
```

**Modification Importance:** Indicate critical vs. normal changes for trust scoring.

### Relationship Exclude Logic

**Edge Case Handling:** Some relationships have exceptions (e.g., "ChildOf X, except when inherited from Y")

**ETL Handling:** Store Exclude_Related as annotation property describing conditions where relationship does NOT hold.

```turtle
capec:excludedCondition [ rdf:value "Does not apply in mobile context" ]
```

---

## ETL Test Priorities

1. **Identifier Uniqueness** - Validate capec:capecId, categoryId, viewId are globally unique with zero duplicates
2. **CWE Bindings** - Ensure every pattern has minimum 1 CWE reference; validate CWE existence in external ontology
3. **Abstraction Hierarchy** - Verify Pattern hierarchies respect Meta → Standard → Detailed ordering
4. **Status Filtering** - Implement ETL rules to handle Draft/Incomplete (do not load), Deprecated (audit trail), Stable/Usable (production)
5. **Cross-Taxonomy Consistency** - Validate mapping quality indicators align with actual concept correspondence
6. **Circular References** - Detect and prevent circular parent-child relationships in pattern hierarchy
