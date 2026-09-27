# 🌐 Namespace Policy v1.2

Supersedes `namespace-policy-v1.1.md` additively: every v1.0 and v1.1
namespace and rule is unchanged; v1.2 registers the namespaces of the
decision extension (ADR-0003) and of the MITRE ATLAS module (ADR-0004).
v1.1 stays frozen and remains the reference for every v1.1 artifact.

## 1. Core Namespace

```text
http://www.motherhacker.me/kgcs/ontology/core#
Prefix: kgcs:
```

All authoritative Core classes and properties live here. No module may
declare a term here, and no module places its `owl:Ontology` header here.

## 2. Standard Namespaces

Unchanged from v1.0 (`cpe:`, `cve:`, `cvss:`, `cwe:`, `capec:`, `attack:`,
`d3fend:`, `car:`, `shield:`, `engage:`). Versioned modules scoped to one
standard declare their terms in that standard's namespace.

v1.2 adds three standard namespaces for the published decision inputs
adhered to Vulnerability. Each belongs to one publisher's standard, so
source-specific identifiers never mix (Hard Rule 5):

| Standard | Publisher | Namespace | Prefix | Since |
| --- | --- | --- | --- | --- |
| KEV (Known Exploited Vulnerabilities catalog) | CISA | `http://www.motherhacker.me/kgcs/ontology/kev#` | `kev:` | v1.2 |
| EPSS (Exploit Prediction Scoring System) | FIRST | `http://www.motherhacker.me/kgcs/ontology/epss#` | `epss:` | v1.2 |
| SSVC (Stakeholder-Specific Vulnerability Categorization, v2.0.3 as published in NVD `ssvcV203`) | CISA (ADP) via NVD | `http://www.motherhacker.me/kgcs/ontology/ssvc#` | `ssvc:` | v1.2 |

The three are declared by one module, `ontology/extensions/decision-extension-v1.0.owl`,
because they share one design decision (ADR-0003) and one shape file; the
module lives in `extensions/` because it is cross-publisher. A future
successor of any of the three may be split into its own file without
changing a term.

v1.2 also adds the namespace of MITRE ATLAS, a parallel matrix beside
ATT&CK for AI-enabled systems (ADR-0004). It is **not** `attack:`: ATLAS
identifiers (`AML.*`) never share a property with ATT&CK identifiers
(Hard Rule 5), and the ATLAS module declares no term in `attack:` or
`kgcs:`.

| Standard | Publisher | Namespace | Prefix | Since |
| --- | --- | --- | --- | --- |
| ATLAS (Adversarial Threat Landscape for AI Systems) | MITRE | `http://www.motherhacker.me/kgcs/ontology/atlas#` | `atlas:` | v1.2 |

Declared by the standard-scoped module `ontology/standards/atlas-ontology-v1.0.owl`
(ontology IRI `atlas:AtlasOntology`); the shape-graph prefix node
`atlas:ATLASShapesPrefixes` lives in the same namespace, as
`attack:ATTCKShapesPrefixes` does in `attack:`.

## 3. Extension Namespaces

| Extension | Namespace | Prefix | Since |
| --- | --- | --- | --- |
| Asset | `http://www.motherhacker.me/kgcs/ontology/asset#` | `asset:` | v1.0 |
| Build metadata | `http://www.motherhacker.me/kgcs/ontology/build#` | `build:` | v1.1 |
| Graph labels | `http://www.motherhacker.me/kgcs/ontology/graph-labels#` | `labels:` | v1.1 (ontology IRI only; its properties stay in the standards' namespaces) |
| ATT&CK–core alignment | `http://www.motherhacker.me/kgcs/ontology/attck-core-alignment#` | `align:` | v1.1 (ontology IRI only; declares no term) |
| Decision extension | `http://www.motherhacker.me/kgcs/ontology/decision#` | `decision:` | v1.2 (ontology IRI and shape-graph nodes only — the SPARQL prefix declaration and the cross-source `decision:VulnerabilityDecisionEdgesShape`; declares no OWL term; terms live in `kev:`, `epss:`, `ssvc:`) |

No extension may reuse the `kgcs:` prefix for its terms. Rule: cross-cutting
extension modules declare their own ontology IRI under
`http://www.motherhacker.me/kgcs/ontology/<module>#`; standard-scoped modules
use their standard's namespace; no module ever places its header in a frozen
namespace it does not own.

## 4. Rule Engine Namespace (Non-OWL)

Unchanged from v1.0 (`http://kgcs.motherhacker.me/rules#`, prefix `rule:`).

---

Namespace policy v1.2 is frozen once spec v1.2.0 is tagged. The ATLAS
namespace (session Q17, ADR-0004) is the last v1.2 addition.
