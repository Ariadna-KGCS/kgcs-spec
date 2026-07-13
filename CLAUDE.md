# kgcs-spec — Agent Instructions

This repo is the **KGCS standard**: the single source of truth for semantics and contracts in the Ariadna project. Treat it with release discipline.

## Hard Rules

1. **Frozen artifacts.** Every `*-v1.0.owl` under `ontology/` is sealed. Never edit one. New or changed semantics land as a new versioned file (e.g., `-v1.1.owl`) or a new extension module under `ontology/extensions/`. If a task appears to require changing frozen semantics, stop and confirm the versioning approach with the user.
2. **Causal chain.** `CPE → CVE/CVSS → CWE → CAPEC → ATT&CK → {D3FEND, CAR, SHIELD, ENGAGE}` is part of the standard. No shortcut edges may be introduced in any ontology, shape, contract, or doc.
3. **Contracts are canonical.** `contracts/*.json` defines the graph schema and request/response envelopes. Downstream repos (`kgcs-pipeline`, `kgcs-server`) generate/validate against these — never the other way around. Schema changes here first, consumers after.
4. **Namespaces.** Only canonical namespaces from `docs/namespace-policy-v1.0.md`. No placeholder prefixes.
5. **Provenance separation.** Source-specific identifiers never mix across taxonomies; CVSS versions stay separate.

## Release Discipline

- Every substantive change gets a `CHANGELOG.md` entry and ships as an annotated git tag (`vX.Y.Z`).
- Breaking contract changes bump the major version.
- Verification before release: SHACL shapes parse (`riot --validate` or equivalent), JSON Schemas are valid Draft-07, internal doc links resolve.

## Repo Neighbors

Part of the Ariadna umbrella (`../README.md`). Never read from or write to sibling repos by relative path.
