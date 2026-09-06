# 🌐 Namespace Policy v1.1

Supersedes `namespace-policy-v1.0.md` additively: every v1.0 namespace and
rule is unchanged; v1.1 adds one cross-cutting module namespace. v1.0 stays
frozen and remains the reference for every v1.0 artifact.

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
standard (`<std>-enrichment`, `<std>-consequences`, `<std>-applicability`)
declare their terms in that standard's namespace.

## 3. Extension Namespaces

| Extension | Namespace | Prefix | Since |
| --- | --- | --- | --- |
| Asset | `http://www.motherhacker.me/kgcs/ontology/asset#` | `asset:` | v1.0 |
| Build metadata | `http://www.motherhacker.me/kgcs/ontology/build#` | `build:` | v1.1 |
| Graph labels | `http://www.motherhacker.me/kgcs/ontology/graph-labels#` | `labels:` | v1.1 (ontology IRI only; its properties stay in the standards' namespaces) |
| ATT&CK–core alignment | `http://www.motherhacker.me/kgcs/ontology/attck-core-alignment#` | `align:` | v1.1 (ontology IRI only; declares no term) |

No extension may reuse the `kgcs:` prefix for its terms. Rule: cross-cutting
extension modules declare their own ontology IRI under
`http://www.motherhacker.me/kgcs/ontology/<module>#`; standard-scoped modules
use their standard's namespace; no module ever places its header in a frozen
namespace it does not own.

## 4. Rule Engine Namespace (Non-OWL)

Unchanged from v1.0 (`http://kgcs.motherhacker.me/rules#`, prefix `rule:`).

---

Namespace policy v1.1 is frozen once spec v1.1.0 is tagged.
