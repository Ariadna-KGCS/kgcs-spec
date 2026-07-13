# 🌐 Namespace Policy v1.0

## 1. Core Namespace

```text
http://www.motherhacker.me/kgcs/ontology/core#
Prefix: kgcs:
```

All authoritative Core classes and properties live here.

---

## 2. Standard Namespaces

These namespaces preserve source identity.

| Standard | Namespace                                                                                    | Prefix  |
| -------- | -------------------------------------------------------------------------------------------- | ------- |
| CPE      | [http://www.motherhacker.me/kgcs/ontology/cpe#](http://www.motherhacker.me/kgcs/ontology/cpe#)       | cpe:    |
| CVE      | [http://www.motherhacker.me/kgcs/ontology/cve#](http://www.motherhacker.me/kgcs/ontology/cve#)       | cve:    |
| CVSS     | [http://www.motherhacker.me/kgcs/ontology/cvss#](http://www.motherhacker.me/kgcs/ontology/cvss#)     | cvss:   |
| CWE      | [http://www.motherhacker.me/kgcs/ontology/cwe#](http://www.motherhacker.me/kgcs/ontology/cwe#)       | cwe:    |
| CAPEC    | [http://www.motherhacker.me/kgcs/ontology/capec#](http://www.motherhacker.me/kgcs/ontology/capec#)   | capec:  |
| ATT&CK   | [http://www.motherhacker.me/kgcs/ontology/attack#](http://www.motherhacker.me/kgcs/ontology/attack#) | attack: |
| D3FEND   | [http://www.motherhacker.me/kgcs/ontology/d3fend#](http://www.motherhacker.me/kgcs/ontology/d3fend#) | d3fend: |
| CAR      | [http://www.motherhacker.me/kgcs/ontology/car#](http://www.motherhacker.me/kgcs/ontology/car#)       | car:    |
| SHIELD   | [http://www.motherhacker.me/kgcs/ontology/shield#](http://www.motherhacker.me/kgcs/ontology/shield#) | shield: |
| ENGAGE   | [http://www.motherhacker.me/kgcs/ontology/engage#](http://www.motherhacker.me/kgcs/ontology/engage#) | engage: |

---

## 3. Extension Namespace

```text
http://www.motherhacker.me/kgcs/ontology/asset#
Prefix: asset:
```

No extension may reuse `kgcs:` prefix.

---

## 4. Rule Engine Namespace (Non-OWL)

```text
http://kgcs.motherhacker.me/rules#
Prefix: rule:
```

Used only for derived edge metadata.

---

Namespace policy is frozen for v1.0.

---
