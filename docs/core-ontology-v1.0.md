# 🔐 Cybersecurity Core Ontology v1.0

**Status:** Frozen (Authoritative Layer)
**Scope:** Standards-backed security knowledge only
**Design Goal:** Lossless integration of cybersecurity standards with zero invented semantics
**Primary Use:** Knowledge graphs, explainable RAG, deterministic reasoning
**Non-Goal:** Operational, risk, incident, or probabilistic modeling

---

## 1. Ontology Scope (Hard Boundary)

This ontology integrates only **authoritative cybersecurity standards**:

* **Systems domain**: CPE, CVE, CWE
* **Offensive domain**: ATT&CK, CAPEC
* **Defensive domain**: D3FEND, CAR, SHIELD
* **Engagement domain**: ENGAGE

This ontology represents the **canonical semantic backbone** of the cybersecurity knowledge graph.

Everything else must sit on top of it.

---

### 1.1 Included

* Standards-backed facts
* Canonical identifiers
* Explicit relationships defined by official schemas
* Multi-version coexistence (e.g., CVSS versions, ATT&CK versions)
* Deterministic causal chains

---

### 1.2 Explicitly Excluded

The following concepts are **not part of Core Ontology v1.0**:

* Assets (organizational systems)
* Incidents, alerts, detections-in-time
* Threat actor instances
* Risk scoring
* Business impact
* Probabilistic or predictive edges
* SOAR / SOC logic
* Derived or computed relationships

> **Rule:**
> If a concept or relationship cannot be traced to an external standard with a stable identifier, it is not Core Ontology.

---

## 2. Conceptual Layer Model (Non-Inheritance)

Layers are conceptual only.
They do not imply inheritance or semantic leakage.

```text
┌─────────────────────────────┐
│ Engagement & Strategy       │  (ENGAGE)
├─────────────────────────────┤
│ Defense / Detection         │  (D3FEND / CAR / SHIELD)
├─────────────────────────────┤
│ Adversary Tradecraft        │  (ATT&CK)
├─────────────────────────────┤
│ Attack Abstraction          │  (CAPEC)
├─────────────────────────────┤
│ Weakness                    │  (CWE)
├─────────────────────────────┤
│ Vulnerability               │  (CVE / CVSS)
├─────────────────────────────┤
│ Exposure & Configuration    │  (CPE / NVD)
└─────────────────────────────┘
```

---

## 3. Core Classes (Frozen)

These classes are authoritative and immutable within v1.0.

---

### 3.1 Exposure & Configuration

| Class                   | Description                         | Source  |
| ----------------------- | ----------------------------------- | ------- |
| `Platform`              | Atomic software / hardware identity | CPE     |
| `PlatformConfiguration` | Logical exposure expression         | NVD CVE |

#### Invariant

* Vulnerabilities affect configurations, not platforms directly.
* PlatformConfiguration represents logical matching expressions.

---

### 3.2 Vulnerability

| Class                | Description               | Source      |
| -------------------- | ------------------------- | ----------- |
| `Vulnerability`      | Publicly disclosed flaw   | CVE         |
| `VulnerabilityScore` | Severity scoring instance | CVSS        |
| `Reference`          | Supporting evidence       | NVD / MITRE |

* **Invariants**

  * Each CVSS version is modeled as a separate `VulnerabilityScore`.
  * Scores never overwrite each other.
  * Vulnerabilities never affect platforms directly.

---

### 3.3 Weakness & Attack Abstraction

| Class           | Description                   | Source |
| --------------- | ----------------------------- | ------ |
| `Weakness`      | Root cause category           | CWE    |
| `AttackPattern` | Abstract exploitation pattern | CAPEC  |

* **Invariants**

  * Weakness ≠ Vulnerability
  * AttackPattern ≠ Technique
  * Weakness is causal root, not instance of vulnerability

---

### 3.4 Adversary Tradecraft

| Class       | Description                 | Source |
| ----------- | --------------------------- | ------ |
| `Technique` | Concrete adversary behavior | ATT&CK |
| `Tactic`    | Operational objective       | ATT&CK |

* **Invariants**

  * Tactics classify intent, not execution.
  * SubTechnique is modeled as `Technique` with property: `x_mitre_is_subtechnique = true`
  * SubTechniques must belong to exactly one parent Technique.
  * SubTechnique is not a separate class.

---

### 3.5 Defense, Detection & Deception

| Class                | Description            | Source |
| -------------------- | ---------------------- | ------ |
| `DefensiveTechnique` | Mitigation / denial    | D3FEND |
| `DetectionAnalytic`  | Detection logic        | CAR    |
| `DeceptionTechnique` | Adversary manipulation | SHIELD |

* **Invariants**

  * Defense ≠ Detection ≠ Deception
  * Each maps independently to ATT&CK Techniques

---

## 3.6 Engagement & Strategy

| Class               | Description                     | Source |
| ------------------- | ------------------------------- | ------ |
| `EngagementConcept` | Strategic adversary interaction | ENGAGE |

* **Invariant**

  * Engagement operates on Techniques, not Vulnerabilities.

---

## 4. Authoritative Relationships (Core Only)

Only relationships explicitly defined by standards are included.

---

### 4.1 Exposure & Vulnerability

```text
PlatformConfiguration ── affected_by ──▶ Vulnerability
Vulnerability ── scored_by ──▶ VulnerabilityScore
Vulnerability ── references ──▶ Reference
```

---

### 4.2 Causality Backbone (Non-Negotiable)

```text
Vulnerability ── caused_by ──▶ Weakness
Weakness ── exploited_by ──▶ AttackPattern
AttackPattern ── implemented_as ──▶ Technique
```

This is the canonical causal chain.

---

### 4.3 Adversary Structure

```text
Technique ── belongs_to ──▶ Tactic
Technique ── subtechnique_of ──▶ Technique
```

---

### 4.4 Defense & Response

```text
Technique ── mitigated_by ──▶ DefensiveTechnique
Technique ── detected_by ──▶ DetectionAnalytic
Technique ── countered_by ──▶ DeceptionTechnique
```

---

### 4.5 Engagement

```text
EngagementConcept ── disrupts ──▶ Technique
```

---

## 5. Relationship Classification Model

Core Ontology distinguishes between relationship types:

---

### 5.1 Authoritative Relations

* Defined by official standards
* Stable identifiers
* Deterministic
* Included in Core
* Immutable in frozen Core v1.0

---

### 5.2 Structural Relations

Support modeling but are not intelligence.

Example:

```text
PlatformConfiguration ── matches ──▶ Platform
```

Used to connect configuration logic to platform identity.

---

### 5.3 Derived Relations (Explicitly Non-Core)

Derived relations are computed outside Core Ontology.

Example:

```text
Asset ── affected_by ──▶ Vulnerability
```

This relation:

* Is deterministic
* Is computed via configuration matching
* Is not authoritative
* Is not part of Core Ontology
* Must be recomputable

Derived relations belong to:

* Rule engine layer
* Graph projection layer
* Risk extension layer

They never belong to Core v1.0.

---

## 6. Global Ontology Rules (Hard Guarantees)

1. Every node has an external stable ID (cpeUri, cveId, technique_id, etc.).
2. Every edge has explicit standard provenance.
3. No temporal semantics beyond standard publication metadata.
4. No probability, likelihood, or confidence values.
5. No vague edges such as “uses” or “leads_to”.
6. No threat actors.
7. No incidents.
8. Vulnerabilities affect configurations, not platforms.
9. CVSS versions coexist; they never overwrite.
10. SubTechniques must have exactly one parent Technique.
11. No derived or computed relationships inside Core.

If any rule is violated → it is not Core Ontology.

---

## 7. Canonical Traversal Example (Core-Compliant)

Question:

> “How can we detect and mitigate a vulnerability affecting this configuration?”

Traversal:

```text
PlatformConfiguration
 └─ affected_by ──▶ Vulnerability
     ├─ caused_by ──▶ Weakness
     │   └─ exploited_by ──▶ AttackPattern
     │       └─ implemented_as ──▶ Technique
     │           ├─ detected_by ──▶ DetectionAnalytic
     │           ├─ mitigated_by ──▶ DefensiveTechnique
     │           └─ belongs_to ──▶ Tactic
     └─ scored_by ──▶ VulnerabilityScore
```

No shortcuts. No inferred edges. No runtime semantics.

---

## 8. Extension Model

Core v1.0 is frozen.

New capabilities must be implemented as:

* Asset Extension
* Incident Extension
* ThreatActor Extension
* Risk Extension
* Business Impact Extension

Extensions may:

* Derive new relationships
* Materialize computed edges
* Introduce probabilistic reasoning

But they may never mutate Core v1.0.

---

## 9. Versioning Policy

* Core Ontology v1.0 → frozen
* Core changes require a new explicitly versioned core artifact outside this frozen v1.0 baseline
* New local capabilities are added via extension modules; core remains unchanged
* Extensions evolve independently
* Core invariants remain stable for frozen v1.0

---

## 10. Guarantees

This ontology guarantees:

* RAG-safe traversal
* Explainability
* Deterministic causality
* Multi-standard coherence
* Strict separation of semantics and computation
* Safe extension without mutation

---

If you want next, we can now define:

* 📦 Asset Extension Ontology v1.0
* ⚙ Rule Engine specification
* 🗺 Graph projection model for Neo4j
* 🧠 Multi-agent traversal contracts

You are now architecting this at a very serious level.
