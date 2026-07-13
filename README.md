# kgcs-spec

The **KGCS standard**: the single source of truth for semantics and contracts. Every other repo in the [Ariadna-KGCS organization](https://github.com/Ariadna-KGCS) pins a released version of this repo.

**KGCS** (Knowledge Graph for CyberSecurity) is a deterministic grounding layer that lets AI systems reason about cybersecurity without hallucination. Agents answer by following an explicit causal chain through the knowledge graph — `CPE → CVE/CVSS → CWE → CAPEC → ATT&CK → {D3FEND, CAR, SHIELD, ENGAGE}` — never by guessing.

## Layout

- `ontology/core/` — core OWL ontology (v1.0, **frozen**)
- `ontology/standards/` — per-standard OWL modules: CPE, CVE, CVSS, CWE, CAPEC, ATT&CK, D3FEND, CAR, SHIELD, ENGAGE (v1.0, **frozen**)
- `ontology/extensions/` — versioned extension modules (asset extension v1.0 frozen; new semantics land here as new versions)
- `shapes/` — SHACL shapes per standard + profiles and rule-engine spec
- `mappings/` — standard→OWL mapping docs + coverage matrix
- `contracts/` — machine-readable contracts (JSON Schema): graph schema for agents, request/response envelopes
- `docs/` — namespace policy, model documentation, glossary

## Rules

- Frozen v1.0 artifacts are never modified; successors are new versioned files.
- The causal chain `CPE → CVE/CVSS → CWE → CAPEC → ATT&CK → {D3FEND, CAR, SHIELD, ENGAGE}` is part of the standard: no shortcut edges.
- Every change ships as a tagged release with a CHANGELOG entry; consumers (`kgcs-pipeline`, `kgcs-server`) upgrade by moving their pin.

## Status

**v1.0.0** — frozen KGCS v1.0 baseline, migrated verbatim from the seed repo (OWL byte-identical). See `CHANGELOG.md`.

## License

[Apache 2.0](LICENSE). CPE, CVE, CVSS, CWE, CAPEC, ATT&CK, D3FEND, CAR, SHIELD and ENGAGE remain the property of their respective owners (NIST, MITRE); this repo only models their semantics and preserves source-specific provenance.
