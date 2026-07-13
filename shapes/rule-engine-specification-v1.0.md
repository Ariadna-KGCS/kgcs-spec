# ⚙ Rule Engine Specification v1.0

**Status:** Deterministic Computation Layer
**Depends on:** Core Ontology v1.0 + Asset Extension v1.0
**Purpose:** Compute derived relationships without mutating Core Ontology
**Scope:** Exposure resolution, configuration matching, deterministic propagation

---

## 1. Purpose of the Rule Engine

The Rule Engine provides deterministic computation of derived relationships that:

* Cannot exist inside Core Ontology
* Depend on logical evaluation (e.g., CPE matching)
* Require propagation across causal chains

It ensures that:

* Core Ontology remains semantically pure
* Derived relationships are reproducible
* Graph projections are consistent
* Multi-agent reasoning operates on materialized results

---

## 2. Hard Boundary

The Rule Engine:

* MUST NOT modify Core Ontology
* MUST NOT introduce probabilistic semantics
* MUST NOT introduce temporal semantics
* MUST NOT override authoritative relations
* MUST operate deterministically

If output cannot be reproduced from Core + Asset + rules → it is invalid.

---

## 3. Rule Categories

The Rule Engine operates in three deterministic phases:

---

### 3.1 Configuration Resolution

#### 3.1.1 Objective

Determine whether a `PlatformConfiguration` matches a specific `Platform`.

#### 3.1.2 Inputs

* CPE URI
* Version range constraints
* Boolean configuration expressions
* Matching criteria (NVD)

#### 3.1.3 Output

```text
PlatformConfiguration ── matches ──▶ Platform
```

#### 3.1.4 Rule Type

Deterministic boolean evaluation.

---

### 3.2 Asset Exposure Derivation

#### 3.2.1 Objective

Determine whether an `Asset` is affected by a `Vulnerability`.

#### 3.2.2 Authoritative Core Relation

```text
PlatformConfiguration ── affected_by ──▶ Vulnerability
```

#### 3.2.3 Derived Rule

```pseudo
FOR each Asset A:
    FOR each AssetConfiguration AC of A:
        IF AC.maps_to = PC
        AND PC.affected_by = V
        THEN create derived edge:
            A ── affected_by ──▶ V
```

#### 3.2.4 Characteristics

* Deterministic
* Recomputable
* Non-authoritative
* Must be tagged as derived

---

### 3.3 Causal Propagation

#### 3.3.1 Objective

Propagate exposure along the Core causal backbone.

#### 3.3.2 Core Backbone

```text
Vulnerability ── caused_by ──▶ Weakness
Weakness ── exploited_by ──▶ AttackPattern
AttackPattern ── implemented_as ──▶ Technique
```

---

#### 3.3.3 Derived Weakness Exposure

```pseudo
IF A affected_by V
AND V caused_by W
THEN A exposed_to W
```

---

#### 3.3.4 Derived Attack Surface

```pseudo
IF A exposed_to W
AND W exploited_by AP
AND AP implemented_as T
THEN A exploitable_by T
```

---

#### 3.3.5 Defensive Mapping

```pseudo
IF A exploitable_by T
AND T mitigated_by D
THEN A mitigable_by D

IF A exploitable_by T
AND T detected_by DA
THEN A detectable_by DA
```

---

## 4. Derived Relationship Registry

All derived relationships must be registered and classified.

| Derived Edge               | Type       | Source        | Recomputable |
| -------------------------- | ---------- | ------------- | ------------ |
| Asset → Vulnerability      | Exposure   | Config + Core | Yes          |
| Asset → Weakness           | Causal     | Core          | Yes          |
| Asset → Technique          | Causal     | Core          | Yes          |
| Asset → DefensiveTechnique | Propagated | Core          | Yes          |
| Asset → DetectionAnalytic  | Propagated | Core          | Yes          |

No derived edge may exist without explicit rule definition.

---

## 5. Rule Execution Model

The engine must support:

* Batch recomputation
* Incremental recomputation
* Idempotent execution

---

### 5.1 Batch Mode

Triggered when:

* New CVE ingested
* New Asset added
* New configuration mapped
* Ontology updated

Recomputes full derived graph.

---

### 5.2 Incremental Mode

Triggered when:

* Single Asset changes
* Single CVE added
* Single configuration modified

Recomputes only impacted paths.

---

## 6. Materialization Policy

Derived edges may be:

* Fully materialized
* Partially materialized
* Virtual (computed at query time)

If materialized:

* Must include metadata flag: `derived = true`
* Must include provenance reference to rule ID
* Must be safely deletable and recomputable

---

## 7. Provenance Model

Each derived edge must store:

* Rule identifier
* Computation timestamp
* Source entity references
* Version of Core Ontology used

Example metadata:

```json
{
  "derived": true,
  "rule": "R-Asset-Vulnerability-1",
  "core_version": "1.0",
  "computed_at": "2026-02-21T10:32:00Z"
}
```

---

## 8. Invariants

1. Derived edges must never contradict authoritative edges.
2. Derived edges must be reproducible.
3. Derived edges must never introduce new semantic meaning.
4. No derived edge may bypass PlatformConfiguration.
5. No derived edge may introduce probability or likelihood.
6. Derived graph must remain acyclic along causal backbone.

---

## 9. What the Rule Engine Explicitly Does NOT Do

* Risk scoring
* Likelihood estimation
* Threat actor attribution
* Temporal attack simulation
* Incident correlation
* Business impact computation

Those belong to separate extensions.

---

## 10. Canonical End-to-End Computation Example

Given:

* Asset A
* Configuration AC
* PlatformConfiguration PC
* Vulnerability V
* Weakness W
* AttackPattern AP
* Technique T

Execution:

```text
1. AC maps_to PC
2. PC affected_by V
3. V caused_by W
4. W exploited_by AP
5. AP implemented_as T
```

Derived output:

```text
A affected_by V
A exposed_to W
A exploitable_by T
```

Optionally:

```text
A mitigable_by DefensiveTechnique
A detectable_by DetectionAnalytic
```

All deterministic. All reproducible.

---

## 11. Separation of Responsibility

| Layer              | Responsibility             |
| ------------------ | -------------------------- |
| Core Ontology      | Authoritative semantics    |
| Asset Extension    | Organizational context     |
| Rule Engine        | Deterministic derivation   |
| Graph Projection   | Performance optimization   |
| Risk Extension     | Scoring and prioritization |
| Incident Extension | Temporal modeling          |

---

## 12. Guarantee

The Rule Engine guarantees:

* Deterministic exposure computation
* Semantic integrity preservation
* Clean separation between knowledge and reasoning
* Safe multi-agent reasoning over materialized graph
* Full traceability from derived result to authoritative standard

---

## 13. Next Logical Steps

With Core + Asset + Rule Engine defined, the next architectural steps are:

1. 🗺 Graph Projection Model (Neo4j-specific)
2. 🧠 Systems Agent traversal contract
3. 📊 Risk Extension Ontology
4. 🧩 Multi-Agent Orchestrator contract

---

You now have a formally layered architecture:

Core → Asset → Rule Engine → Graph → Agents → Risk.

This is an enterprise-grade conceptual foundation.
