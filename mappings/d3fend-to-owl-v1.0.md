# D3FEND to OWL Mapping v1.0

## Overview

D3FEND (Detection, Defeasibility, Deception, and Defensive techniques) is the MITRE-maintained knowledge base that encodes defensive countermeasures as a "mirror" to ATT&CK's offensive framework. While ATT&CK describes attack patterns and how adversaries operate, D3FEND catalogs defensive and evasive countermeasures, detection strategies, and deception techniques to counter those attacks. This mapping implements D3FEND as a "knowledge graph passthrough" in KGCS: the official D3FEND OWL remains authoritative, while KGCS provides a thin integration layer that aligns D3FEND defensive concepts with core cybersecurity semantics and establishes bidirectional relationships between defensive and offensive techniques (attack:Technique and attack:Tactic). The 7 D3FEND defensive tactics (Deceive, Detect, Evict, Harden, Isolate, Model, Restore) form the strategic backbone for categorizing defensive techniques.

---

## Sources

- **Official OWL Knowledge Graph:** `data/schemas/D3FEND/d3fend.owl` (d3fend.mitre.org)
- **Version:** D3FEND v1.3.0 (Release: 2025-12-16)
- **Format:** Web Ontology Language (OWL) 2.0
- **Scale:** 4,279 classes, 4,658 individuals
- **Namespace:** `http://d3fend.mitre.org/ontologies/d3fend.owl#`
- **External Framework Integrations:** ATT&CK (enterprise, mobile, ICS), CAPEC (attack patterns), ATLAS (AI/ML attacks)
- **Architecture:** Standalone OWL with rdfs:isDefinedBy references to external taxonomies (no owl:imports)

**Key D3FEND Entity Classes (from official OWL):**

- `d3fend:DefensiveTechnique` - Defensive countermeasures (e.g., "Application Whitelisting")
- `d3fend:DefensiveTactic` - Strategic categories (7 types: Deceive, Detect, Evict, Harden, Isolate, Model, Restore)
- `d3fend:Procedure` - Concrete implementation steps for techniques
- `d3fend:OffensiveTechnique` - References to ATT&CK attack techniques
- `d3fend:OffensiveTactic` - References to ATT&CK attack tactics

---

## Target Ontology

- **File:** `ontology/standards/d3fend-ontology-v1.0.owl` (to be created)
- **Core Classes Used:**
  - `kgcs:DefensiveTechnique` (base for defensive implementations)
  - `kgcs:DetectionAnalytic` (detection-focused defenses)
  - `kgcs:DeceptionTechnique` (deception-based defenses)
  - `kgcs:EngagementConcept` (engagement/counter-deception strategies)
  - `kgcs:Tactic` (for defensive tactical grouping, if needed)
- **New KGCS Namespace:** `d3fend: <http://www.motherhacker.me/kgcs/ontology/d3fend#>`
- **Core Import:** Explicit `owl:imports <http://www.motherhacker.me/kgcs/ontology/core#>`
- **Design Pattern:** Thin integration layer (passthrough) that aligns official D3FEND OWL with KGCS schema without re-implementing 4,279 classes

---

## Entity Mapping

### Primary Entity Types

| D3FEND Source Entity | Target KGCS Class | Primary ID | ID Datatype | Notes |
| --- | --- | --- | --- | --- |
| DefensiveTechnique | kgcs:DefensiveTechnique (with d3fend: overlay) | d3fend:d3fendId | xsd:string | Core defensive countermeasure; example: D3FEND-AP001 (Application Whitelisting) |
| DefensiveTactic (7 types) | d3fend:DefensiveTactic (categorization) | d3fend:tacticId | xsd:string | Strategic defensive goal: Deceive, Detect, Evict, Harden, Isolate, Model, Restore |
| Procedure | d3fend:Procedure | d3fend:procedureId | xsd:string | Implementation steps/playbook for a DefensiveTechnique |
| OffensiveTechnique (ref) | attack:Technique (from ATT&CK import) | attack:attackId | xsd:string | Reference to ATT&CK technique that is countered/mitigated |
| OffensiveTactic (ref) | attack:Tactic (from ATT&CK import) | attack:attackId | xsd:string | Reference to ATT&CK tactic for defensive categorization |
| Capability | d3fend:Capability | d3fend:capabilityId | xsd:string | Required organizational capability for technique deployment |
| PrerequisiteCondition | d3fend:PrerequisiteCondition | d3fend:conditionId | xsd:string | Contextual condition required for technique effectiveness |

**Integration Philosophy:** Official D3FEND OWL is authoritative. KGCS creates compatibility predicates and named properties to align D3FEND offensive/defensive relationships with core KGCS semantics. D3FEND individuals (specific techniques, procedures, etc.) are federated into KGCS via property relationships, not class duplication.

---

## Integration Mapping

### Defensive-Offensive Alignment

**Bidirectional Relationship Pattern:**

```text
D3FEND Defensive Technique X --[d3fend:mitigates]--> ATT&CK Offensive Technique Y
     ↓
ATT&CK Technique Y --[kgcs:mitigated_by]--> D3FEND Defensive Technique X
```

**Example:** D3FEND "Application Whitelisting" counters ATT&CK "T1190: Exploit Public-Facing Application"

### 7 D3FEND Defensive Tactics Mapping

| D3FEND Tactic | Strategic Intent | Example Techniques | Maps to KGCS |
| --- | --- | --- | --- |
| **Detect** | Identify attack execution or compromise | Behavior Analysis, Network Monitoring, Log Analysis | kgcs:DetectionAnalytic |
| **Deceive** | Create false or misleading information | Decoy Systems, Honeypots, Deception Tokens | kgcs:DeceptionTechnique |
| **Harden** | Strengthen systems to resist exploitation | Patching, Segmentation, Encryption, Least Privilege | kgcs:DefensiveTechnique |
| **Evict** | Remove attacker from compromised system | Incident Response, Malware Removal, Access Revocation | kgcs:DefensiveTechnique |
| **Isolate** | Compartmentalize assets and limit exposure | Air-gapping, Network Segmentation, Microsegmentation | kgcs:DefensiveTechnique |
| **Model** | Understand attack surface and threat landscape | Threat Modeling, Red Teaming, Adversary Emulation | kgcs:DefensiveTechnique |
| **Restore** | Return systems to known-good state | Recovery Procedures, Backup Restoration, Disaster Recovery | kgcs:DefensiveTechnique |

### Instance-Level Mapping Example

**D3FEND Individual:** `d3fend:AppliedWhitelisting` (specific application whitelisting deployment)

```turtle
d3fend:AppliedWhitelisting
  rdf:type d3fend:DefensiveTechnique
  d3fend:belongs_to_tactic d3fend:Harden
  d3fend:mitigates attack:T1190     # Mitigates "Exploit Public-Facing Application"
  d3fend:mitigates attack:T1071     # Mitigates "Application Layer Protocol"
  d3fend:implemented_by [d3fend:Procedure with steps...]
  d3fend:requires_capability "HIGH"  # Requires high organizational capability
```

### Bidirectional Query Capability

**Forward Query:** "What D3FEND defenses counter technique T1059 (Command and Scripting Interpreter)?"

```sparql
SELECT ?defense WHERE {
  ?defense d3fend:mitigates attack:T1059 .
}
```

**Reverse Query:** "What ATT&CK techniques are mitigated by this D3FEND defensive tactic?"

```sparql
SELECT ?technique WHERE {
  ?defense rdf:type d3fend:DefensiveTechnique ;
           d3fend:belongs_to_tactic d3fend:Detect ;
           d3fend:mitigates ?technique .
}
```

---

## Relationship Mapping

### Defensive-to-Offensive Mitigation Relationships

| Relationship | Domain | Range | Direction | Cardinality | Semantics | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `d3fend:mitigates_technique` | DefensiveTechnique | attack:Technique | directed | 1+ | Defensive technique mitigates/counters ATT&CK offensive technique | CRITICAL: minimum 1 per defensive technique |
| `d3fend:mitigates_tactic` | DefensiveTechnique | attack:Tactic | directed | 0+ | Defensive technique helps counter ATT&CK tactic | Optional; indicates coverage of multiple techniques in same tactic |
| `d3fend:counters_attack_pattern` | DefensiveTechnique | kgcs:AttackPattern | directed | 0+ | Defensive technique counters CAPEC attack pattern | Links to CAPEC for methodology-level defense |

### Tactical Organization Relationships

| Relationship | Domain | Range | Direction | Cardinality | Semantics |
| --- | --- | --- | --- | --- | --- |
| `d3fend:belongs_to_tactic` | DefensiveTechnique | DefensiveTactic | directed | 1 | Technique belongs to exactly 1 of 7 strategic tactics (Functional Property) |
| `d3fend:tactic_has_member` | DefensiveTactic | DefensiveTechnique | directed (inverse) | 1+ | Tactic groups multiple defensive techniques |

### Implementation Relationships

| Relationship | Domain | Range | Direction | Cardinality | Semantics |
| --- | --- | --- | --- | --- | --- |
| `d3fend:implemented_by` | DefensiveTechnique | Procedure | directed | 0+ | Technique is executed via concrete procedures/playbooks |
| `d3fend:implements` | Procedure | DefensiveTechnique | directed (inverse) | 1 | Procedure implements exactly 1 defensive technique |

### Capability and Prerequisite Relationships

| Relationship | Domain | Range | Cardinality | Semantics |
| --- | --- | --- | --- | --- |
| `d3fend:requires_capability` | DefensiveTechnique | Capability | 0+ | Technique requires specific organizational capability (people, tools, process maturity) |
| `d3fend:requires_condition` | DefensiveTechnique | PrerequisiteCondition | 0+ | Technique only effective under specific contextual conditions |

### Cross-Reference Relationships (Optional)

| Relationship | Domain | Range | Notes |
| --- | --- | --- | --- |
| `d3fend:references_cwe` | DefensiveTechnique | cwe:CWEWeakness | Link to CWE weaknesses that technique addresses |
| `d3fend:references_capec` | DefensiveTechnique | capec:AttackPattern | Link to CAPEC attack patterns that technique mitigates |

---

## Transformation Notes

### Knowledge Graph Passthrough Architecture

**Core Principle:** D3FEND OWL is a complete, authoritative, read-only knowledge graph at its own namespace (`http://d3fend.mitre.org/ontologies/d3fend.owl#`). KGCS does NOT re-implement D3FEND's 4,279 classes. Instead, KGCS creates a **thin integration layer** that:

1. Defines KGCS-compatible properties for alignment (e.g., `d3fend:mitigates_technique`)
2. Creates bidirectional relationships to ATT&CK offensive entities via `owl:inverseOf`
3. Categorizes D3FEND techniques into 7 defensive tactics for strategic organization
4. Enables federation of D3FEND individuals into KGCS knowledge graphs

**ETL Model:**

```text
ETL Process:
  1. Load official d3fend.owl (5.8MB, 4,279 classes)
  2. Extract D3FEND individuals (DefensiveTechnique, Procedure, OffensiveTechnique references)
  3. Map to KGCS properties via d3fend: ontology
  4. Link to attack:Technique (via d3fend:mitigates_technique)
  5. Store as federated RDF triples in KGCS
```

### Defensive Tactic Enumeration (7 Strategic Categories)

**Tactic Definitions:**

1. **Detect** - Defensive techniques for identifying attacks, breaches, and adversary presence
   - Examples: Network Traffic Analysis, Endpoint Detection, Log Monitoring
   - KGCS Alignment: `kgcs:DetectionAnalytic`

2. **Deceive** - Deception-based countermeasures that mislead attackers
   - Examples: Honeypots, Decoy Systems, False Data, Deception Networks
   - KGCS Alignment: `kgcs:DeceptionTechnique`

3. **Harden** - Strengthening systems to reduce attack surface and likelihood of successful exploitation
   - Examples: Patching, Configuration Hardening, Least Privilege, Defense-in-Depth
   - KGCS Alignment: `kgcs:DefensiveTechnique`

4. **Evict** - Removing attackers and malware from compromised systems
   - Examples: Malware Removal, Access Revocation, Incident Response, Forensic Techniques
   - KGCS Alignment: `kgcs:DefensiveTechnique`

5. **Isolate** - Compartmentalization and containment of assets and systems
   - Examples: Network Segmentation, Microsegmentation, Air-gapping, Sandboxing
   - KGCS Alignment: `kgcs:DefensiveTechnique`

6. **Model** - Understanding attack surface, adversary capabilities, and threat landscape
   - Examples: Threat Modeling, Red Teaming, Adversary Emulation, Penetration Testing
   - KGCS Alignment: `kgcs:DefensiveTechnique`

7. **Restore** - Recovery and continuity procedures for compromised or damaged systems
   - Examples: Disaster Recovery, System Restoration, Backup Procedures, Business Continuity
   - KGCS Alignment: `kgcs:DefensiveTechnique`

### Status and Maturity Handling

**D3FEND v1.3.0 Status:** All techniques in official v1.3.0 are considered "stable" production-ready entries. If future D3FEND versions introduce status variations (Draft, Deprecated, etc.), use:

```turtle
d3fend:status a owl:DatatypeProperty ;
    rdfs:range xsd:string ;
    rdfs:comment "Status: stable, beta, deprecated, obsolete" .
```

### Version Tracking and Pinning

**KGCS D3FEND Mapping Alignment:**

```text
KGCS d3fend-ontology-v1.0.owl <-- aligned with --> D3FEND v1.3.0 (2025-12-16)
```

If D3FEND major versions change (e.g., v2.0):

- Option 1: Create new `d3fend-ontology-v2.0.owl` alongside v1.0
- Option 2: Add version-aware properties: `d3fend:compatibleWithD3FENDVersion xsd:string`
- Versioning preserves historical alignment for reproducibility

### Procedure Implementation Pattern

**XML/JSON-to-OWL Transformation:**

D3FEND Procedures in official OWL:

```xml
<Procedure id="AP-1-P-1">
  <TechniqueName>Application Whitelisting</TechniqueName>
  <Step number="1">Install whitelisting software on all endpoints</Step>
  <Step number="2">Create allowlist of approved applications</Step>
  <Step number="3">Enable enforcement mode with alerts</Step>
</Procedure>
```

KGCS OWL Representation:

```turtle
d3fend:AP_1_P_1 a d3fend:Procedure ;
    d3fend:implements d3fend:ApplicationWhitelisting ;
    d3fend:procedureSteps """
    1. Install whitelisting software on all endpoints
    2. Create allowlist of approved applications
    3. Enable enforcement mode with alerts
    """ ;
    d3fend:procedureId "AP-1-P-1" .
```

### Capability Level Semantics

**Organizational Capability Assessment:**

| Level | Definition | Example Requirements |
| --- | --- | --- |
| **Low** | Minimal organizational investment; widely available tools/skills | Firewall configuration, basic patching |
| **Medium** | Moderate investment; standard security tools/staff; requires process | EDR deployment, log aggregation, change management |
| **High** | Significant investment; specialized expertise; mature security program | Threat intelligence platform, full SIEM, specialized incident response team |

Example:

```turtle
d3fend:ApplicationWhitelisting d3fend:requires_capability "MEDIUM" .
d3fend:AdvancedThreatHunting d3fend:requires_capability "HIGH" .
```

### Prerequisite Condition Handling

**Contextual Requirements for Technique Effectiveness:**

```turtle
d3fend:NetworkSegmentation d3fend:requires_condition [
    rdfs:label "Network monitoring/alerting must be in place" ;
    d3fend:conditionDescription "Segmentation alone prevents direct attacks; must couple with detection of lateral movement attempts"
] .
```

### ATT&CK Cross-Reference Quality

**Relationship Cardinality and Semantics:**

- **1-to-1 Mapping:** Defensive technique directly counters single ATT&CK technique
  - Example: "Disable Script Execution" directly mitigates T1086 (PowerShell)
- **Many-to-1 Mapping:** Multiple defensive techniques counter single ATT&CK technique
  - Example: T1059 (Command/Scripting) countered by: Whitelisting, Script Disabling, Network Segmentation, etc.
- **1-to-Many Mapping:** Single defensive technique counters multiple ATT&CK techniques
  - Example: "Network Segmentation" reduces impact of many lateral movement techniques

---

## ETL Implementation

### Data Ingestion Pipeline

#### **Stage 1: Load D3FEND OWL**

```text
Input: data/schemas/D3FEND/d3fend.owl (official)
Parse: RDF/OWL parser (Jena, RDFLib, or similar)
Extract: All d3fend:DefensiveTechnique individuals
Filter: Exclude purely informational classes (keep executable techniques only)
```

#### **Stage 2: Link Offensive References**

```text
For each DefensiveTechnique:
  Extract countered ATT&CK techniques (via official d3fend:counters relationships)
  Resolve to attack:Technique URIs: http://www.motherhacker.me/kgcs/ontology/attack#T[ATTACK_ID]
  Create d3fend:mitigates_technique relationships
```

#### **Stage 3: Categorize Defensive Tactics**

```text
Map DefensiveTechnique to 7 D3FEND tactics (Detect, Deceive, etc.)
Assign d3fend:belongs_to_tactic property
Ensure every technique maps to exactly 1 tactic
```

#### **Stage 4: Validate and Index**

```text
Validation rules:
  ✓ Every DefensiveTechnique has d3fend:d3fendId (unique)
  ✓ Every DefensiveTechnique belongs to exactly 1 tactic
  ✓ Every DefensiveTechnique mitigates >= 1 ATT&CK technique (RECOMMENDED)
  ✓ No orphaned procedures (all Procedures implement a Technique)

Index: Build bidirectional indices for fast defensiveness queries
```

### Query Examples

#### **Query 1: Find all defensive techniques targeting a specific attack tactic**

```sparql
PREFIX d3fend: <http://www.motherhacker.me/kgcs/ontology/d3fend#>
PREFIX attack: <http://www.motherhacker.me/kgcs/ontology/attack#>

SELECT DISTINCT ?defensiveTechnique ?defenseLabel WHERE {
  ?defensiveTechnique d3fend:mitigates_technique ?technique .
  ?technique attack:belongs_to attack:InitialAccess .
  ?defensiveTechnique rdfs:label ?defenseLabel .
}
```

#### **Query 2: What are all the detection techniques that counter reconnaissance?**

```sparql
SELECT ?detection WHERE {
  ?detection d3fend:belongs_to_tactic d3fend:Detect ;
             d3fend:mitigates_technique ?technique .
  ?technique attack:belongs_to attack:Reconnaissance .
}
```

#### **Query 3: Which defensive techniques implement AppWhitelisting procedures?**

```sparql
SELECT ?technique ?procedure WHERE {
  ?technique d3fend:implemented_by ?procedure .
  ?technique rdfs:label "Application Whitelisting" .
  ?procedure rdfs:label ?procLabel .
}
```

### Validation Rules (Critical for ETL)

| Rule | Severity | Description | Action |
| --- | --- | --- | --- |
| Tactic Completeness | WARN | DefensiveTechnique must belong to 1 of 7 tactics | Flag if missing or > 1 |
| Offensive Linkage | WARN | Every DefensiveTechnique should mitigate >= 1 ATT&CK technique | Log if none found |
| Procedure Validity | ERROR | Procedure must implement exactly 1 DefensiveTechnique | Reject orphaned procedures |
| ID Uniqueness | ERROR | d3fendId must be globally unique | Fail on duplicates |
| Circular References | ERROR | No circular mitigation relationships (A→B→A forbidden) | Detect and log |

---

## Summary

D3FEND integration into KGCS follows a **knowledge graph passthrough** model: official D3FEND OWL (4,279 classes) remains authoritative and read-only. KGCS provides a thin, standards-compliant integration ontology that aligns D3FEND defensive concepts with core cybersecurity semantics, establishes bidirectional offensive-defensive relationships, and enables federation of D3FEND individuals into KGCS threat/defense correlations. The 7-tactic model (Detect, Deceive, Harden, Evict, Isolate, Model, Restore) provides strategic organization for categorizing defensive coverage.

## v1.1 — `MITIGATED_BY` sources that are revoked or deprecated in ATT&CK

The D3FEND mappings file (`d3fend-full-mappings.json`, D3FEND 1.3.0) cites
ATT&CK IDs as the offensive side of each row. The 2026-09-26 graph-quality
review counted 347 distinct IDs, of which at most 12 are revoked and 1 is
deprecated in the loaded ATT&CK (regex count, so an upper bound). The
loader's `OPTIONAL MATCH … WHERE t IS NOT NULL` drops those rows without
reporting them.

Rule (loader behaviour, no new term; defined once in
`attck-to-owl-v1.0.md`, "v1.1 — Revoked and deprecated ATT&CK targets"):
**bridge targets that are revoked are remapped via STIX `revoked-by` to the
live successor; deprecated targets are dropped and counted.** The remapped
edge is an ordinary `MITIGATED_BY` from the successor `Technique` /
`SubTechnique`. The drop count is reported, never silent. The D3FEND
release loaded is recorded as `D3FEND=<owl:versionInfo>` (e.g.
`D3FEND=1.3.0`) in `BuildMetadata.sourceSnapshots`.
