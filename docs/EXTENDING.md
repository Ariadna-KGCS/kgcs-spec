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

## Adding a Core Standard

### Step 1: Define the Ontology

Create `ontology/standards/<standard>-ontology-v1.0.owl`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:owl="http://www.w3.org/2002/07/owl#"
    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
    xmlns:std="http://www.motherhacker.me/kgcs/ontology/<standard>#">
    
    <!-- Import core namespace -->
    <owl:imports rdf:resource="http://www.motherhacker.me/kgcs/ontology/core#"/>
    
    <!-- Define classes -->
    <owl:Class rdf:about="http://www.motherhacker.me/kgcs/ontology/<standard>#YourEntity">
        <rdfs:label>Your Entity</rdfs:label>
        <rdfs:comment>Definition and purpose</rdfs:comment>
    </owl:Class>
    
    <!-- Define properties -->
    <owl:DatatypeProperty rdf:about="http://www.motherhacker.me/kgcs/ontology/<standard>#yourProperty">
        <rdfs:domain rdf:resource="http://www.motherhacker.me/kgcs/ontology/<standard>#YourEntity"/>
        <rdfs:range rdf:resource="http://www.w3.org/2001/XMLSchema#string"/>
    </owl:DatatypeProperty>
    
    <!-- Define relationships -->
    <owl:ObjectProperty rdf:about="http://www.motherhacker.me/kgcs/ontology/<standard>#relatesTo">
        <rdfs:domain rdf:resource="http://www.motherhacker.me/kgcs/ontology/<standard>#YourEntity"/>
        <rdfs:range rdf:resource="http://www.motherhacker.me/kgcs/ontology/<standard>#OtherEntity"/>
    </owl:ObjectProperty>
    
</rdf:RDF>
```

### Step 2: Write Human-Readable Spec

Create `docs/docs/<standard>-ontology-v1.0.md`:

```markdown
# [Standard] Ontology v1.0

## Overview
- **Source:** [Official spec URL]
- **Version:** v1.0 (frozen in KGCS)
- **Last Updated:** [Date]

## Core Entities
- **Class:** [Entity] ([Definition])
  - **Properties:** [property1], [property2], ...
  - **Example:** [ID: description]

## Relationships
- **Class A** --[edge]--> **Class B**
  - **Semantics:** [What this relationship means]

## Examples
[Real-world instances]
```

### Step 3: Create SHACL Shapes

Create `shapes/<standard>-shapes-v1.0.ttl`:

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#>.
@prefix std: <http://www.motherhacker.me/kgcs/ontology/<standard>#>.

# Shape for YourEntity
std:YourEntityShape
    a sh:NodeShape;
    sh:targetClass std:YourEntity;
    sh:property [
        sh:path std:yourProperty;
        sh:minCount 1;
        sh:maxCount 1;
        sh:datatype xsd:string;
    ].
```

### Step 4: Create Test Samples

Create positive and negative examples:

- `data/shacl-samples/<standard>-good.ttl` — Valid RDF
- `data/shacl-samples/<standard>-bad.ttl` — Invalid RDF (missing required properties, wrong types)

### Step 5: Create ETL Transformer

Create `src/etl/etl_<standard>.py`:

```python
from rdflib import Graph, Namespace, URIRef, Literal

class XyztoRDFTransformer:
    def __init__(self):
        self.graph = Graph()
        self.ns = Namespace("http://www.motherhacker.me/kgcs/ontology/<standard>#")
    
    def transform(self, json_data: dict) -> Graph:
        """
        Transform [Standard] JSON to RDF.
        
        Input: JSON from official source (API/download)
        Output: RDF Graph conforming to [standard]-shapes.ttl
        """
        for item in json_data.get("items", []):
            self._add_entity(item)
        return self.graph
    
    def _add_entity(self, item: dict):
        """Add an entity and its properties to graph."""
        entity_id = item.get("id")
        subj = self.ns[entity_id]
        
        # Type
        self.graph.add((subj, RDF.type, self.ns.YourEntity))
        
        # Properties
        self.graph.add((subj, self.ns.yourProperty, Literal(item.get("name"))))
        
        # Relationships
        for related_id in item.get("related", []):
            self.graph.add((subj, self.ns.relatesTo, self.ns[related_id]))

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", required=True)
    parser.add_argument("--output", "-o", required=True)
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    
    # Load JSON
    import json
    with open(args.input, 'r') as f:
        data = json.load(f)
    
    # Transform
    transformer = XyztoRDFTransformer()
    graph = transformer.transform(data)
    
    # Validate
    if args.validate:
        from src.core.validation import run_validator, load_graph
        shapes = load_graph("shapes/<standard>-shapes-v1.0.ttl")
        conforms, _, _ = run_validator(args.output, shapes, "artifacts")
        print("✓ PASS" if conforms else "✗ FAIL")
    
    # Save
    graph.serialize(destination=args.output, format="turtle")
    print(f"Saved {args.output}")

if __name__ == "__main__":
    main()
```

### Step 6: Create Unit Tests

Create `tests/test_<standard>_integration.py`:

```python
import json
import pytest
from src.etl.etl_<standard> import XyztoRDFTransformer
from src.core.validation import run_validator, load_graph

def test_<standard>_etl():
    """Test [Standard] ETL transformer."""
    # Load sample
    with open("data/<standard>/samples/sample_<standard>.json", "r") as f:
        data = json.load(f)
    
    # Transform
    transformer = XyztoRDFTransformer()
    graph = transformer.transform(data)
    
    # Assertions
    assert len(graph) > 0
    assert graph.query("SELECT ?s WHERE { ?s a ?YourEntity }")
```

### Step 7: Update CI/CD

Add to `.github/workflows/shacl-validation.yml`:

```yaml
- name: Validate [Standard]
  run: |
    python scripts/validate_shacl_stream.py \
      --data data/<standard>/samples/sample_<standard>.json \
    --shapes shapes/<standard>-shapes-v1.0.ttl
```

### Step 8: Update Documentation

1. Add to [GLOSSARY.md](GLOSSARY.md) — Standard definition + classes + relationships
2. Add to `architecture.md` (in `kgcs-server`) — Which phase, dependencies
3. Update `governance.md` (in `kgcs-server`) — Versioning policy, rollback procedure

---

## Adding an Extension

### Step 1: Define the Extension Ontology

Create `extensions/<extension>-extension-v1.0.owl`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:owl="http://www.w3.org/2002/07/owl#"
         xmlns:asset="http://www.motherhacker.me/kgcs/ontology/<extension>#"
         xmlns:kgcs="http://www.motherhacker.me/kgcs/ontology/core#">
    
    <!-- Import core ONLY (one-way) -->
    <owl:imports rdf:resource="http://www.motherhacker.me/kgcs/ontology/core#"/>
    
    <!-- Define extension classes -->
    <owl:Class rdf:about="http://www.motherhacker.me/kgcs/ontology/<extension>#YourContextualEntity">
        <rdfs:label>Contextual Entity</rdfs:label>
        <rdfs:comment>References core, adds context/subjectivity</rdfs:comment>
    </owl:Class>
    
    <!-- Reference core classes (don't redefine) -->
    <owl:ObjectProperty rdf:about="http://www.motherhacker.me/kgcs/ontology/<extension>#assesses">
        <rdfs:domain rdf:resource="http://www.motherhacker.me/kgcs/ontology/<extension>#YourContextualEntity"/>
        <rdfs:range rdf:resource="http://www.motherhacker.me/kgcs/ontology/core#Vulnerability"/>
    </owl:ObjectProperty>
    
</rdf:RDF>
```

### Step 2: Create SHACL Shapes

`shapes/<extension>-extension-shapes-v1.0.ttl`

### Step 3: Create Extension Spec

`docs/docs/<extension>-extension-ontology-v1.0.md`

### Step 4: Implement Python Module

`src/extensions/<extension>.py` — Load extension data independently

### Step 5: **Never Modify Core**

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

- [ ] OWL ontology defined (`ontology/core/`, `ontology/standards/`, or `ontology/extensions/` with `*-v1.0.owl` naming)
- [ ] Human-readable spec written (`docs/docs/*-ontology-v1.0.md`)
- [ ] SHACL shapes created (`shapes/*-v1.0.ttl`)
- [ ] Positive + negative test samples provided
- [ ] ETL transformer implemented (`src/etl/etl_*.py`)
- [ ] Unit tests written (`tests/test_*_integration.py`)
- [ ] CI/CD updated (`.github/workflows/`)
- [ ] Documentation updated (GLOSSARY, ARCHITECTURE, GOVERNANCE)
- [ ] PR reviewed for:
  - No circular imports
  - Causal chain maintained
  - Explicit provenance (all edges traceable)
  - 1:1 standards alignment verified

---

## Extending the AI Layer

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

- `architecture.md` (in `kgcs-server`) — Phases and dependencies
- [GLOSSARY.md](GLOSSARY.md) — Existing standards + relationships
- copilot-instructions.md — Development rules
- Example transformers: `src/etl/etl_cpe.py`, `src/etl/etl_cve.py`
