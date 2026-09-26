# KGCS Glossary & Standard Definitions

**Purpose:** Central reference for security standards, ontology concepts, and their relationships.

---

## Standards Overview

| Standard | Scope | Source | Latest Version |
| --- | --- | --- | --- |
| **CPE** | Platform identifiers | NVD | 2.3 |
| **CVE** | Vulnerabilities | NVD | 2020 format |
| **CVSS** | Vulnerability severity | NVD/FIRST | v2.0, v3.1, v4.0 |
| **CWE** | Software weaknesses | MITRE | 4.14 |
| **CAPEC** | Attack patterns | MITRE | 3.14 |
| **ATT&CK** | Adversary tactics & techniques | MITRE | STIX 2.1 |
| **D3FEND** | Defense techniques | MITRE | 1.3 |
| **CAR** | Detection analytics | MITRE | Latest |
| **SHIELD** | Deception techniques | MITRE | Latest |
| **ENGAGE** | Engagement concepts | MITRE | Latest |

---

## Core Ontology Concepts

### Harmonized Terms (Multi-Agent)

- **Risk**: Subjective assessment and decision layer (ACCEPT, MITIGATE, TRANSFER, AVOID); lives in the Risk Extension; never overwrites CVSS.
- **Exposure**: Applicability at the PlatformConfiguration level (version bounds, update state), not the abstract Platform.
- **Threat**: Potential adversarial capability or intent expressed through ATT&CK Techniques or ThreatActor claims (extension); never a direct edge to CVE/CWE.
- **Coverage**: The set of mapped mitigations, detections, and deceptions for a Technique; not a probability.
- **Confidence**: Explicit certainty indicator with basis and provenance; required for attribution and agent responses.
- **Attack Path**: Authoritative causal chain CPE → CVE → CWE → CAPEC → ATT&CK; no skipped hops.
- **Mitigation**: DefensiveTechnique or Control mapped to a Technique via `mitigated_by`; does not alter core semantics.

### Platform (CPE)

- **Definition:** Atomic identifier for a software/hardware component
- **Syntax:** `cpe:2.3:part:vendor:product:version:...`
- **Key property:** `cpeUri` (immutable)
- **Example:** `cpe:2.3:a:apache:log4j:2.14.1:*:*:*:*:java:*:*`
- **Invariant:** Never changes (represents a specific product version combination)
- **Related:** PlatformConfiguration (contains versioning specifics)

### PlatformConfiguration

- **Definition:** Deployment-specific details (updates, status, application bounds)
- **Key properties:**
  - `cpeUri` (the platform identifier)
  - `configStatus` (VULNERABLE, FIXED, UNKNOWN)
  - `lowerBound`, `upperBound` (version bounds)
  - `excludingBounds` (versions to exclude)
  - `versionStartExcluding`, `versionEndExcluding`
  - `releaseDate`, `updateDate`
  - `matches` (array of affected CVEs)
- **Use case:** Track which versions are vulnerable to CVE-2025-1234
- **Invariant:** Different configurations of same CPE create separate nodes

### Vulnerability (CVE)

- **Definition:** Named vulnerability with unique ID
- **Key property:** `cveId` (e.g., CVE-2025-1234)
- **CVSS versions coexist:** v2.0, v3.1, v4.0 are separate nodes (never merged)
- **Relationships:**
  - `affects` → PlatformConfiguration
  - `caused_by` → CWE (root cause weakness)
  - `has_score` → Score (CVSS)
- **Source:** NVD (authoritative for CVE, platform mapping)

### VulnerabilityConfiguration

- **Definition:** One entry of the NVD `cve.configurations[]` array — a complete applicability statement for a CVE, grouping one or more boolean clauses
- **Key properties:** `operator` (AND/OR across its nodes), `negate` (boolean; inverts the whole statement)
- **Relationships:** `has_node` → VulnerabilityConfigurationNode
- **Provenance:** Direct mirror of NVD CVE API 2.0 JSON structure; the layer exists so operator/negate semantics survive into the graph instead of being flattened away
- **Source:** NVD

### VulnerabilityConfigurationNode

- **Definition:** One entry of the NVD `configurations[].nodes[]` array — a boolean clause (AND/OR + `negate`) over a set of CPE match criteria. The "Node" suffix is NVD's own vocabulary for these clause objects, not a generic graph term
- **Key properties:** `operator` (AND/OR across its criteria), `negate` (boolean; inverts the clause)
- **Relationships:** `matches_criteria` → PlatformConfiguration (with `vulnerable` flag on the edge)
- **Why it matters:** `AFFECTS` edges are only valid when backed by a non-negated, vulnerable leaf through this chain — the post-load integrity check `affects_backed_by_applicability` enforces exactly that. Without this layer, negated or non-vulnerable criteria (e.g. "running ON this OS but not vulnerable IN it") would produce false `AFFECTS` edges
- **Chain:** `(Vulnerability)-[:HAS_CONFIGURATION]->(VulnerabilityConfiguration)-[:HAS_NODE]->(VulnerabilityConfigurationNode)-[:MATCHES_CRITERIA]->(PlatformConfiguration)`
- **Source:** NVD

### Weakness (CWE)

- **Definition:** Type/category of weakness in code/design
- **Key property:** `cweId` (e.g., CWE-79 Cross-site Scripting)
- **Categories:**
  - **Pillar** (highest level, e.g., Improper Neutralization)
  - **Class** (middle, e.g., Improper Neutralization of Input During Web Page Generation)
  - **Base** (specific, e.g., Improper Neutralization of Input During Web Page Generation: 'Cross-site Scripting')
- **Relationships:**
  - `child_of`, `parent_of`, `peer_of` (CWE hierarchy)
  - `demonstrated_by` → CAPEC (attack pattern)
  - `mitigated_by` → D3FEND (defense technique)
- **Source:** MITRE (CWE list)

### AttackPattern (CAPEC)

- **Definition:** Generalized method for attacking a system
- **Key property:** `capecId` (e.g., CAPEC-4 XSS)
- **Relationships:**
  - `exploits` → CWE (uses specific weakness)
  - `enables` → Technique (maps to ATT&CK)
- **Source:** MITRE (CAPEC database)

### Technique (ATT&CK)

- **Definition:** Specific method adversaries use to achieve goals
- **Key property:** `attackId` (e.g., T1021 Remote Service Session Initiation)
- **Hierarchy:**
  - **Tactic** (e.g., Initial Access, Execution, Persistence)
  - **Technique** (e.g., T1204 User Execution)
  - **Sub-Technique** (e.g., T1204.001 Malicious Link)
- **Relationships:**
  - `parent_of` → SubTechnique
  - `detected_by` → DataComponent (from Data Sources)
  - `mitigated_by` → DefenseTechnique (D3FEND, CAR, SHIELD)
- **Source:** MITRE (ATT&CK database)

### DefenseTechnique (D3FEND)

- **Definition:** Method to detect, deny, disrupt threats
- **Key property:** `d3fendId` (e.g., D3-PA Physical Access Prevention)
- **Subcategories:**
  - Detection (identify attacks)
  - Denial (prevent attacks)
  - Disruption (slow attacks)
- **Relationships:**
  - `counters` → Technique (ATT&CK)
  - `related_to` → CAR, SHIELD, ENGAGE
- **Source:** MITRE (D3FEND)

### DetectionAnalytic (CAR)

- **Definition:** Method to detect specific adversary tactics
- **Key property:** `analyticId` (e.g., CAR-2020-04-001)
- **Relationships:**
  - `detects` → Technique
- **Source:** MITRE (CAR database)

### DeceptionTechnique (SHIELD)

- **Definition:** Active deception tactic to detect/slow adversaries
- **Key properties:** `techniqueId` (SHIELD techniques), `tacticId` (SHIELD tactics), `opportunityId`, `useCaseId`, `procedureId`
- **Relationships:**
  - `counters` → Technique
- **Source:** MITRE (SHIELD)

### EngagementConcept (ENGAGE)

- **Definition:** Engagement framework for adversary interaction
- **Key properties:** `activityId`, `approachId`, `goalId` (plus `refId`, `eav_id` for ENGAGE-specific entities)
- **Relationships:**
  - `engages_against` → Technique
- **Source:** MITRE (ENGAGE)

### Score (CVSS)

- **Definition:** Severity score for a vulnerability
- **Versions:** v2.0, v3.1, v4.0 (separate nodes, never merged)
- **v2.0 metrics:** AccessVector, AccessComplexity, Authentication, ConfImpact, IntegImpact, AvailImpact
- **v3.1 metrics:** AttackVector, AttackComplexity, PrivilegesRequired, UserInteraction, Scope, ConfidentialityImpact, IntegrityImpact, AvailabilityImpact
- **v4.0 metrics:** New risk-based approach, attack complexity factors
- **Key property:** `baseScore` (0–10 or 0–100 in v4.0)
- **Source:** NVD + vulnerability-specific assessments

---

## Causal Chain (Critical Invariant)

```text
CPE (Platform)
    ↓ has vulnerability
CVE (Vulnerability)
    ↓ caused by
CWE (Weakness)
    ↓ demonstrated by
CAPEC (Attack Pattern)
    ↓ enables
Technique (ATT&CK Tactic/Technique)
    ↓ can be
    ├── detected_by → CAR (Detection)
    ├── countered_by → D3FEND (Defense)
    ├── engaged_against → SHIELD (Deception)
    └── engaged_with → ENGAGE (Engagement)
```

**Rule:** Never skip steps. Never link CPE → CWE directly. Always follow: CPE → CVE → CWE → CAPEC → Technique.

---

## Extension Concepts (Phase 4+)

### Incident (Contextual)

- **Definition:** Observed attack event with timeline
- **Key properties:**
  - `incidentId`
  - `timeline` (when observed)
  - `location` (where observed)
  - `techniques_used` (links to ATT&CK)
- **Invariant:** Never asserts ground truth (always qualifies with "observed")
- **Relationship:** Only references core (CVE, Technique, etc.), never modifies

### RiskAssessment (Subjective)

- **Definition:** Decision on handling a vulnerability/threat
- **Key properties:**
  - `riskId`
  - `decision` (ACCEPT, MITIGATE, TRANSFER, AVOID)
  - `rationale` (business/technical reason)
  - `owner` (accountable person)
- **Invariant:** Only layer where subjectivity is allowed
- **Relationship:** References CVE, Platform, Threat Actor (subjective)

### ThreatActor (Attribution)

- **Definition:** Claim about who might exploit a vulnerability
- **Key properties:**
  - `actorId`
  - `confidenceLevel` (HIGH, MEDIUM, LOW)
  - `capabilities` (known techniques, tools)
- **Invariant:** Always includes confidence; never asserts ground truth
- **Relationship:** References Technique, Campaign, Infrastructure

---

## Relationships (Edges)

### Authoritative (Core)

| From | To | Edge | Semantics |
| --- | --- | --- | --- |
| CVE | Platform | `affects` | This vulnerability impacts this platform |
| CVE | CWE | `caused_by` | This CVE stems from this weakness |
| CVE | Score | `has_score` | This CVE has this CVSS assessment |
| CWE | CWE | `child_of`, `parent_of`, `peer_of` | CWE hierarchy |
| CWE | CAPEC | `demonstrated_by` | This weakness can be exploited via this attack pattern |
| CAPEC | Technique | `enables` | This attack pattern corresponds to this ATT&CK technique |
| Technique | DataComponent | `detected_by` | This technique can be detected via this data component |
| Technique | DefenseTechnique | `mitigated_by` | This technique can be mitigated by this defense |

### Contextual (Extensions)

| From | To | Edge | Semantics |
| --- | --- | --- | --- |
| Incident | Technique | `uses` | This incident observed this technique |
| RiskAssessment | CVE | `evaluates` | This risk assessment concerns this CVE |
| ThreatActor | Technique | `employs` | This actor uses this technique |
| ThreatActor | Campaign | `conducts` | This actor conducts this campaign |

---

## Example: CVE-2021-44228 (Log4Shell)

```text
CPE: cpe:2.3:a:apache:log4j:2.0.0:*:*:*:*:java:*:*
  ↓ (in range 2.0.0 – 2.16.0)
CVE: CVE-2021-44228
  ├─ has_score → CVSS v3.1 (Base: 10.0 CRITICAL)
  └─ caused_by → CWE-917 (Expression Language Injection)
      └─ demonstrated_by → CAPEC-242 (Accessing Data Through a Blind SQL Injection)
          └─ enables → Technique T1190 (Exploit Public-Facing Application)
              ├─ detected_by → CAR-2020-04-001 (Suspicious Log4j Config)
              ├─ mitigated_by → D3FEND-SA (Supply Chain Attack Prevention)
              └─ countered_by → SHIELD-A (Deception: Honeypot)

Incident: "Log4Shell detected in prod environment"
  └─ uses → T1190 (observed technique)

RiskAssessment: "Log4j 2.15.0 in dev; decision: MITIGATE (upgrade to 2.17.0)"
  └─ evaluates → CVE-2021-44228

ThreatActor: "APT-X (HIGH confidence)"
  └─ employs → T1190
```

---

## Data Quality Principles

### Immutability

- Core ontology concepts (CPE, CVE, CWE, etc.) are immutable post-release
- Changes require versioning + deprecation (never override)

### Traceability

- Every statement includes `source` field (cveId, attackId, analyticId, etc.)
- Extensions include `confidence` or `rationale`

### No Fabrication

- Never invent edges to "complete the graph"
- If a standard doesn't define a relationship, it doesn't exist in core
- Extensions can propose relationships (with caveats)

### Version Coexistence

- CVSS versions (v2.0, v3.1, v4.0) exist as separate nodes
- New standards coexist with old; never replace

---

## References

- `architecture.md` (in `kgcs-server`) — 5-phase roadmap
- `governance.md` (in `kgcs-server`) — Data policies
- Approved Cypher query templates — `agents/*/cypher_templates.py` (in `kgcs-server`)
- NVD: <https://nvd.nist.gov/>
- MITRE ATT&CK: <https://attack.mitre.org/>
- MITRE CWE: <https://cwe.mitre.org/>
- MITRE CAPEC: <https://capec.mitre.org/>
- MITRE D3FEND: <https://d3fend.mitre.org/>
- MITRE CAR: <https://car.mitre.org/>
- MITRE SHIELD: <https://shield.mitre.org/>
- MITRE ENGAGE: <https://engage.mitre.org/>
