# 🏢 Asset Extension Ontology v1.0

**Status:** Extension Layer
**Depends on:** Core Ontology v1.0
**Scope:** Organizational asset modeling and exposure context
**Design Goal:** Connect real-world assets to Core security knowledge without contaminating Core semantics
**Version Baseline:** Frozen OWL artifacts at v1.0

---

## 1. Extension Purpose

The Asset Extension provides a structured model for representing:

* Organizational systems
* Infrastructure components
* Software deployments
* Platform configurations in context

It enables exposure reasoning while preserving the integrity of Core Ontology v1.0.

---

## 2. Hard Boundary

This extension:

* MUST NOT redefine Core classes
* MUST NOT modify Core relationships
* MUST NOT introduce probabilistic semantics
* MUST NOT introduce incident-level semantics
* MUST NOT alter Core invariants

The extension operates strictly on top of Core.

---

## 3. Core Dependency

This extension depends on the following Core classes:

* `Platform`
* `PlatformConfiguration`
* `Vulnerability`
* `Weakness`
* `AttackPattern`
* `Technique`

Core relationships such as:

```text
PlatformConfiguration ── affected_by ──▶ Vulnerability
```

remain authoritative and untouched.

---

## 4. Extension Classes

## 4.1 Asset

| Class   | Description                                                      |
| ------- | ---------------------------------------------------------------- |
| `Asset` | Organizational system, device, workload, or environment instance |

### Definition

An `Asset` represents a real-world deployment or system instance within an organization.

It is:

* Contextual
* Organization-specific
* Not part of Core Ontology

Examples:

* Production Web Server
* Customer Database Cluster
* Endpoint Device
* SaaS Tenant

---

### 4.2 AssetConfiguration

| Class                | Description                                 |
| -------------------- | ------------------------------------------- |
| `AssetConfiguration` | Concrete configuration instance of an Asset |

This class links organizational systems to Core exposure logic.

It is a contextualized wrapper over Core `PlatformConfiguration`.

---

## 5. Structural Relationships (Extension-Level)

These relationships are structural and non-authoritative.

---

### 5.1 Asset Composition

```text
Asset ── hasConfiguration ──▶ AssetConfiguration
```

Each Asset may have one or more configurations.

---

### 5.2 Configuration Mapping

```text
AssetConfiguration ── maps_to ──▶ PlatformConfiguration
```

This connects the organization-specific configuration to the Core configuration logic.

---

### 5.3 Optional Direct Platform Association

```text
Asset ── runsPlatform ──▶ Platform
```

This shortcut may exist for convenience but does not replace configuration-based reasoning.

---

## 6. Derived Relationships (Non-Core)

Derived relationships are computed using deterministic rules.

They MUST NOT be defined inside Core Ontology.

---

### 6.1 Derived Exposure

```text
Asset ── affected_by ──▶ Vulnerability
```

This relationship is computed if:

```text
Asset.hasConfiguration = AC
AND
AC.maps_to = PC
AND
PC.affected_by = V
THEN
Asset affected_by V
```

Characteristics:

* Deterministic
* Recomputable
* Materializable
* Not authoritative
* Not stored in Core

---

### 6.2 Derived Weakness

```text
Asset ── exposed_to ──▶ Weakness
```

Derived via:

```text
Asset → Vulnerability → caused_by → Weakness
```

---

### 6.3 Derived Attack Surface

```text
Asset ── exploitable_by ──▶ Technique
```

Derived via causal backbone:

```text
Asset
 └─ affected_by → Vulnerability
     └─ caused_by → Weakness
         └─ exploited_by → AttackPattern
             └─ implemented_as → Technique
```

---

## 7. Rule Engine Layer (Deterministic Computation)

The following logic belongs outside OWL:

* CPE matching evaluation
* Version range comparison
* Boolean configuration logic
* Matching criteria resolution

Core invariant respected:

> Vulnerabilities affect configurations, not platforms.

The Asset layer only inherits exposure via configuration mapping.

---

## 8. Materialized Graph Projection

In graph databases (e.g., Neo4j), the following relations may be materialized for performance:

```text
Asset ── directly_affected_by ──▶ Vulnerability
Asset ── directly_exploitable_by ──▶ Technique
Asset ── directly_exposed_to ──▶ Weakness
```

These relations must:

* Be tagged as derived
* Be recomputable
* Never replace authoritative Core relations

---

## 9. Extension Invariants

1. Asset is not part of Core Ontology.
2. Asset never bypasses PlatformConfiguration.
3. No direct Vulnerability → Platform relation is introduced.
4. No probabilistic semantics exist in this layer.
5. No incident semantics exist in this layer.
6. All derived edges must be computable from authoritative Core relations.

---

## 10. Canonical Traversal (Asset Context)

Question:

> “Is this asset exposed to known exploitation techniques?”

Traversal:

```text
Asset
 └─ hasConfiguration ──▶ AssetConfiguration
     └─ maps_to ──▶ PlatformConfiguration
         └─ affected_by ──▶ Vulnerability
             └─ caused_by ──▶ Weakness
                 └─ exploited_by ──▶ AttackPattern
                     └─ implemented_as ──▶ Technique
```

Optional materialized shortcut:

```text
Asset ── directly_exploitable_by ──▶ Technique
```

---

## 11. Separation of Concerns

| Layer              | Responsibility                     |
| ------------------ | ---------------------------------- |
| Core Ontology      | Authoritative standards knowledge  |
| Asset Extension    | Organizational system modeling     |
| Rule Engine        | Deterministic exposure computation |
| Graph Projection   | Performance optimization           |
| Risk Extension     | Probabilistic scoring              |
| Incident Extension | Temporal observations              |

---

## 12. What This Extension Enables

* Asset exposure modeling
* Multi-agent reasoning over real systems
* Deterministic vulnerability impact mapping
* Clean separation between semantic knowledge and operational state
* Safe integration with risk modeling

---

## 13. Versioning Policy

* Asset Extension v1.0 depends on Core v1.0
* Core is frozen in this workspace; any core change requires a new versioned core artifact
* Derived logic may evolve in extension/rule layers without changing Core

---

## 14. Systems-Agent Compatibility Projection

To support a stable, read-only systems-agent contract while preserving Core immutability, compatibility aliases and key field declarations are defined in standards modules under `ontology/standards/`, not in the asset extension.

### 14.1 Compatibility Predicates

```text
Vulnerability ── cve:affects ──▶ PlatformConfiguration   (inverse of Core `kgcs:affected_by`)
Vulnerability ── cvss:hasScore ──▶ VulnerabilityScore    (aligned with Core `kgcs:scored_by`)
Vulnerability ── cve:references ──▶ Reference            (aligned with Core `kgcs:references`)
```

These predicates are standards-level compatibility terms for agent/graph ergonomics and do not alter Core semantics.

### 14.2 Systems Key Fields (Datatype Declarations)

Declared in standards namespaces for schema-level consistency across loaders and agent views:

* `cpe:cpeUri`, `cpe:cpeNameId`
* `cpe:matchCriteriaId`, `cpe:configStatus`
* `cve:cveId`, `cve:published`, `cve:lastModified`, `cve:source`
* `cwe:cweId`, `cwe:abstraction`
* `cvss:scoreId`, `cvss:version`, `cvss:baseScore`

All values remain sourced from authoritative standards metadata (NVD/MITRE) and must preserve provenance in agent responses.
