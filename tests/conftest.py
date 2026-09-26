"""Shared fixtures for the kgcs-spec validation harness.

The harness validates the specification itself, not a graph instance:

* every ``ontology/**/*.owl`` (Turtle syntax) and ``shapes/*.ttl`` parses;
* the shapes graph is well-formed SHACL (meta-SHACL);
* every shape reference (``sh:path``, ``sh:class``, ``sh:targetClass`` ...)
  resolves to a term declared in some OWL module;
* ``contracts/*.json`` are valid JSON Schema documents;
* an ABox fixture (``tests/fixtures/*.ttl``) with at least one individual per
  node shape conforms to ``shapes/``, and each negative fixture in
  ``tests/fixtures/negative/`` produces exactly the violations listed in
  ``tests/fixtures/negative/manifest.json``.

Inference mode (fixed, see ``INFERENCE_MODE``)
----------------------------------------------
Shapes such as ``sh:class attack:Tactic`` on a node typed ``kgcs:Tactic`` only
hold if the alignment axioms in ``ontology/extensions/*-alignment-v*.owl``
(``owl:equivalentClass``, ``rdfs:subClassOf``, ``owl:equivalentProperty``,
``rdfs:subPropertyOf``, ``owl:inverseOf``) are materialised. The harness
computes an OWL-RL deductive closure over *fixture + alignment modules only*
and validates with pySHACL ``inference="none"``.

The closure is deliberately NOT computed over the full TBox: the frozen v1.0
standard modules carry multi-class ``rdfs:domain`` axioms (for example
``attack:attackId`` has eleven domain classes), so full RDFS/OWL-RL inference
would type every subject of ``attack:attackId`` as a Technique, a Tactic, a
Group ... and every ``TechniqueShape`` constraint would fire on Tactics.
Consumers that validate exported graph data must reproduce this mode.

Zero-triple guard
-----------------
Any parse that yields zero triples fails the test session immediately. A
vacuously green run (empty shapes, empty fixture) is treated as a failure,
never as a pass.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from rdflib import OWL, RDF, RDFS, Graph, Namespace, URIRef

ROOT = Path(__file__).resolve().parent.parent
ONTOLOGY_DIR = ROOT / "ontology"
SHAPES_DIR = ROOT / "shapes"
CONTRACTS_DIR = ROOT / "contracts"
FIXTURES_DIR = ROOT / "tests" / "fixtures"
NEGATIVE_DIR = FIXTURES_DIR / "negative"

SH = Namespace("http://www.w3.org/ns/shacl#")
KGCS_BASE = "http://www.motherhacker.me/kgcs/ontology/"

#: Fixed inference mode of the harness. ``alignment-owlrl`` = OWL-RL closure
#: over data + ``ontology/extensions/*-alignment-v*.owl`` only, then pySHACL
#: with ``inference="none"``. Changing this changes what the shapes mean.
INFERENCE_MODE = "alignment-owlrl"
ALIGNMENT_GLOB = "extensions/*-alignment-v*.owl"

DECLARATION_TYPES = (
    OWL.Class,
    OWL.ObjectProperty,
    OWL.DatatypeProperty,
    OWL.AnnotationProperty,
    RDFS.Class,
    RDF.Property,
)


def owl_files() -> list[Path]:
    files = sorted(ONTOLOGY_DIR.rglob("*.owl"))
    if not files:
        pytest.fail(f"No .owl files found under {ONTOLOGY_DIR}")
    return files


def shape_files() -> list[Path]:
    files = sorted(SHAPES_DIR.glob("*.ttl"))
    if not files:
        pytest.fail(f"No .ttl shape files found under {SHAPES_DIR}")
    return files


def alignment_files() -> list[Path]:
    return sorted(ONTOLOGY_DIR.glob(ALIGNMENT_GLOB))


def positive_fixture_files() -> list[Path]:
    files = sorted(FIXTURES_DIR.glob("*.ttl"))
    if not files:
        pytest.fail(f"No ABox fixtures found under {FIXTURES_DIR}")
    return files


def negative_fixture_files() -> list[Path]:
    return sorted(NEGATIVE_DIR.glob("*.ttl"))


def parse_turtle(path: Path) -> Graph:
    """Parse a Turtle file; fail hard on parse error or zero triples."""
    g = Graph()
    try:
        g.parse(str(path), format="turtle")
    except Exception as exc:  # noqa: BLE001 - report any parser failure
        pytest.fail(f"{path.relative_to(ROOT)}: parse error: {exc}")
    if len(g) == 0:
        pytest.fail(f"{path.relative_to(ROOT)}: parsed to zero triples")
    return g


def union(paths: list[Path]) -> Graph:
    g = Graph()
    for p in paths:
        g += parse_turtle(p)
    if len(g) == 0:
        pytest.fail(f"Union of {len(paths)} files has zero triples")
    return g


def qname(term):
    if term is None:
        return None
    return (
        str(term)
        .replace(KGCS_BASE, "")
        .replace("http://www.w3.org/2001/XMLSchema#", "xsd:")
        .replace("http://www.w3.org/ns/shacl#", "sh:")
        .replace("http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdf:")
    )


def materialise(data: Graph, alignment: Graph) -> Graph:
    """OWL-RL closure over data + alignment axioms (INFERENCE_MODE)."""
    from owlrl import DeductiveClosure, OWLRL_Semantics

    g = Graph()
    g += data
    g += alignment
    DeductiveClosure(
        OWLRL_Semantics, axiomatic_triples=False, datatype_axioms=False
    ).expand(g)
    return g


@pytest.fixture(scope="session")
def tbox() -> Graph:
    return union(owl_files())


@pytest.fixture(scope="session")
def shapes() -> Graph:
    return union(shape_files())


@pytest.fixture(scope="session")
def alignment() -> Graph:
    files = alignment_files()
    return union(files) if files else Graph()


@pytest.fixture(scope="session")
def declared_terms(tbox: Graph) -> set[URIRef]:
    terms: set[URIRef] = set()
    for t in DECLARATION_TYPES:
        terms |= set(tbox.subjects(RDF.type, t))
    if not terms:
        pytest.fail("No OWL term declarations found in the TBox")
    return terms


@pytest.fixture(scope="session")
def positive_fixture() -> Graph:
    return union(positive_fixture_files())


@pytest.fixture(scope="session")
def negative_manifest() -> dict:
    path = NEGATIVE_DIR / "manifest.json"
    if not path.exists():
        pytest.fail(f"Missing {path.relative_to(ROOT)}")
    with path.open(encoding="utf-8") as fh:
        manifest = json.load(fh)
    if not manifest:
        pytest.fail("negative manifest is empty")
    return manifest
