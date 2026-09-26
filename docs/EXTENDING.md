# Extending KGCS: Adding New Standards

**Purpose:** Guide for adding new security standards to KGCS.

---

## When to Add to Core vs. Extension

### Add to Core If

- Standard is authoritative (e.g., NVD, MITRE)
- Provides 1:1 mapping to official schema
- Fits into causal chain (CPE → CVE → ... → Defense)
- Will be used by multiple applications
- Rarely changes (frozen after Phase 1)

**Examples:** CPE, CVE, CWE, CAPEC, ATT&CK, D3FEND, CAR, SHIELD, ENGAGE

### Add to Extension If

- Data is contextual, temporal, or subjective
- Organization-specific or assessment-based
- Requires frequent updates
- References core concepts

**Examples:** Incident, Risk, ThreatActor, RiskAssessment

---

## Module location convention (v1.1)

- A **versioned module scoped to one standard** (enrichment, consequences, applicability, a future `-v1.1.owl` successor) lives in `ontology/standards/<std>-<module>-vX.Y.owl` and declares its terms in that standard's namespace (`docs/namespace-policy-v1.1.md`).
- A **cross-cutting module** (alignment axioms, graph labels, build metadata, an organisational extension such as `asset`) lives in `ontology/extensions/`.
- Frozen files are never edited or moved. A module that changes the meaning of an existing term is a successor file, not an addition.
- Every module ships with: a shape update (new `shapes/<std>.shacl.ttl` version or a new shape file), a mapping doc (`mappings/<std>-<module>-to-owl-vX.Y.md`), a `CHANGELOG.md` entry, one focus node per new shape in `tests/fixtures/kgcs-abox.ttl` and at least one negative case in `tests/fixtures/negative/` with its `manifest.json` entry.

---

## Adding a Core Standard

The `.owl` files are **Turtle syntax** despite the suffix (every existing module is; the harness parses them with `format="turtle"`).

### Step 1: Define the Ontology

Create `ontology/standards/<standard>-ontology-v1.0.owl`:

```turtle
@prefix std:  <http://www.motherhacker.me/kgcs/ontology/<standard>#> .
@prefix kgcs: <http://www.motherhacker.me/kgcs/ontology/core#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

std:<Standard>Ontology a owl:Ontology ;
    rdfs:label "KGCS <Standard> Ontology v1.0" ;
    owl:imports <http://www.motherhacker.me/kgcs/ontology/core#> .

std:YourEntity a owl:Class ;
    rdfs:label "Your Entity" ;
    rdfs:comment "Definition and purpose." .

std:your_property a owl:DatatypeProperty ;
    rdfs:domain std:YourEntity ;
    rdfs:range xsd:string ;
    rdfs:comment "OWL properties are snake_case; the graph property is camelCase (yourProperty)." .

std:relates_to a owl:ObjectProperty ;
    rdfs:domain std:YourEntity ;
    rdfs:range std:OtherEntity ;
    rdfs:comment "Graph relationship: RELATES_TO. Must not skip a hop of the causal chain." .
```

The namespace must be listed in the current `docs/namespace-policy-vX.Y.md`; a new standard needs a policy successor that adds it.

### Step 2: Write the Mapping Doc

Create `mappings/<standard>-to-owl-v1.0.md`: source schema, entity mapping, field mapping (source field → OWL property → graph property → cardinality → vocabulary), transformation rules, provenance notes. Every `prefix:term` cited must exist in an OWL module — `mappings/mapping-coverage-matrix-v1.1.md` audits this.

### Step 3: Create SHACL Shapes

Create `shapes/<standard>.shacl.ttl` (existing naming: `attck.shacl.ttl`, `d3fend.shacl.ttl`, …):

```turtle
@prefix sh:  <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix std: <http://www.motherhacker.me/kgcs/ontology/<standard>#> .

std:YourEntityShape
    a sh:NodeShape ;
    sh:targetClass std:YourEntity ;
    sh:property [
        sh:path std:your_property ;
        sh:datatype xsd:string ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:message "YourEntity must have exactly one yourProperty." ;
        sh:severity sh:Violation ;
    ] .
```

`sh:path` always uses the OWL name, never the graph name. Loader-derived ID patterns are `sh:Warning`; XSD-required fields are `sh:Violation`.

### Step 4: Add Fixtures

- `tests/fixtures/kgcs-abox.ttl` — one valid individual per new node shape (the harness fails if a shape has no focus node).
- `tests/fixtures/negative/<case>.ttl` + entry in `manifest.json` — the exact results the mutation must produce.

### Step 5: Run the Harness

```bash
python -m pytest
```

### Step 6: Downstream (other repos, after a spec release)

- `kgcs-pipeline`: downloader + `etl/load_<standard>.py` + post-load Cypher checks; bump `SPEC_VERSION` and run `sync_spec.py`.
- `kgcs-server`: Cypher templates and response schemas.
- Never by relative path: consumers pin a released tag of this repo.

### Step 7: Update Documentation

1. Add to [GLOSSARY.md](GLOSSARY.md) — standard definition + classes + relationships.
2. Add the standard to `contracts/agent-consumable-schema.md` (labels, key properties, relationship types).
3. `CHANGELOG.md` entry under `[Unreleased]`.

---

## Adding an Extension

### Step 1: Define the Extension Ontology

Create `ontology/extensions/<extension>-extension-v1.0.owl` (Turtle):

```turtle
@prefix ext:  <http://www.motherhacker.me/kgcs/ontology/<extension>#> .
@prefix kgcs: <http://www.motherhacker.me/kgcs/ontology/core#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ext:<Extension>ExtensionOntology a owl:Ontology ;
    owl:imports <http://www.motherhacker.me/kgcs/ontology/core#> .   # core only, one-way

ext:YourContextualEntity a owl:Class ;
    rdfs:comment "References core, adds context/subjectivity." .

ext:assesses a owl:ObjectProperty ;
    rdfs:domain ext:YourContextualEntity ;
    rdfs:range kgcs:Vulnerability .   # reference core classes, never redefine them
```

The extension namespace must be added by a namespace-policy successor (`docs/namespace-policy-v1.1.md` is the current one; `asset:` and `build:` are the registered extension namespaces).

### Step 2: Create SHACL Shapes

`shapes/<extension>.shacl.ttl`, plus fixtures as in Step 4 above.

### Step 3: Create Extension Spec

`docs/<extension>-extension-ontology-v1.0.md` (see `docs/asset-extension-ontology-v1.0.md`).

### Step 4: **Never Modify Core**

- Extension classes reference core, not vice versa
- Never add properties to core classes
- Never remove from core
- Never alter core relationships

---

## Versioning Policy

### Core Standards

- Versions frozen after Phase 1 release
- Changes require new version (v2.0, v3.0)
- Old versions remain available (no overwrites)
- Deprecation period: announce changes 1–3 months before cutover

### CVSS Special Case

- v2.0, v3.1, v4.0 exist as separate entities (never merged)
- Each CVE may have multiple CVSS versions
- New versions added incrementally

### Extensions

- Can change more frequently (Phase 4+)
- Current workspace baseline is v1.0; future changes require explicit new versioned artifacts
- Backward-compatible updates preferred

---

## Checklist for Adding a Standard

- [ ] OWL module defined (Turtle; `ontology/standards/` or `ontology/extensions/` per the location convention; namespace registered in the current namespace policy)
- [ ] Mapping doc written (`mappings/*-to-owl-vX.Y.md`) and coverage matrix updated
- [ ] SHACL shapes created or versioned (`shapes/<std>.shacl.ttl`)
- [ ] Fixture focus node + negative case + manifest entry (`tests/fixtures/`)
- [ ] `python -m pytest` green (CI: `.github/workflows/validate.yml`)
- [ ] Documentation updated (GLOSSARY, `contracts/agent-consumable-schema.md`, CHANGELOG)
- [ ] Downstream work filed against the consumers (`kgcs-pipeline` loader + post-load checks, `kgcs-server` templates/schemas) for after the release
- [ ] PR reviewed for:
  - No circular imports
  - Causal chain maintained
  - Explicit provenance (all edges traceable)
  - 1:1 standards alignment verified

---

## Extending the AI Layer

The `ai/` and `orchestrator/` packages described here live in `kgcs-server`; this section is kept in the spec because the invariants below are part of the standard.

The `ai/` package is intentionally narrow and deterministic. All extensions must stay within these boundaries: no LLM inference, no dynamic Cypher, no graph writes.

### Adding a New Intent

1. Add the new intent string to `VALID_INTENTS` in `orchestrator/constants.py`.
2. Add payload field expectations to `INTENT_PAYLOAD_FIELDS` in the same file.
3. Implement the orchestration path in `orchestrator/executor.py`.
4. Add classification logic to `ai/intent_classifier.py`:
   - Add domain-specific keyword pattern lists (follow `_VULN_PATTERNS`, `_ATTACK_PATTERNS`).
   - Add resolution logic in `classify()` after the existing entity-first and domain-score checks.
   - Do not modify existing resolution paths; add new else-branches only.
5. Add an intent-specific renderer method to `ai/response_renderer.py` following the `_render_vuln_lookup` signature.
6. Add tests in `ai/tests/` covering at minimum: correct routing, entity extraction, safety pass-through, and rendered output shape.

Classification must remain deterministic. Do not introduce LLM calls or probabilistic scoring.

### Extending Entity Extraction

Entity patterns live in `ai/entity_extractor.py` as module-level regex constants.

- Add a new regex constant following the `_CVE_RE`, `_CWE_RE` naming convention.
- Add a private helper method `_extract_<type>` that returns a single match or raises `MultipleEntitiesError` on multiple matches.
- Add the new type to the intent-priority routing table in `extract()`.
- Update `INTENT_PAYLOAD_FIELDS` in `orchestrator/constants.py` to declare the new field.

The `MultipleEntitiesError` contract is intentional — do not silently drop duplicates. If a prompt contains multiple IDs of the same type, the error surfaces so callers know the input was ambiguous.

### Modifying the Response Renderer

The renderer in `ai/response_renderer.py` must preserve these invariants:

1. **Provenance always present:** `_render_provenance()` must be called for every non-error response.
2. **Confidence always present:** `_render_confidence()` must be called for every non-error response.
3. **Low-confidence warning:** When `confidence.value < 0.25`, a warning is prepended. Do not change this threshold without updating tests.
4. **No inference:** The renderer formats data from the `ResponseEnvelope`. It must not add claims, summaries, or interpretations absent from the envelope.

When adding a new intent renderer, follow the `_render_vuln_lookup` / `_render_attack_path` pattern: extract data from the envelope, format it as a string, and return. The `render()` dispatcher appends `_render_provenance()` and `_render_confidence()` as shared postfix steps.

### Where NOT to Introduce LLM Logic

| Location | Reason |
| --- | --- |
| `ai/intent_classifier.py` | Classification must be deterministic and auditable. |
| `ai/entity_extractor.py` | Entity IDs must match authoritative regex patterns exactly. |
| `ai/safety.py` | Safety checks must not be bypassable by model reasoning. |
| `orchestrator/` | Orchestrator and agents are graph-read-only and schema-driven. |
| Any Cypher template | Cypher is never generated; templates are static and parameterized. |

If future work adds an LLM for richer natural-language understanding, it must sit strictly between the user input and the `classify` step — never between `safety` and `execute`, and never touching Cypher or graph data directly.

---

## References

- [GLOSSARY.md](GLOSSARY.md) — Existing standards + relationships
- [namespace-policy-v1.1.md](namespace-policy-v1.1.md) — Registered namespaces
- [adr/ADR-0001-consequence-subnodes.md](adr/ADR-0001-consequence-subnodes.md) — Worked example of a versioned module decision
- `../shapes/README.md` — Shape conventions, alignment modules, inference mode
- Example loaders: `etl/load_cpe.py`, `etl/load_cve.py` (in `kgcs-pipeline`)
