"""SHACL well-formedness, OWL<->SHACL alignment and ABox fixture validation."""

from __future__ import annotations

from collections import Counter

import pytest
from pyshacl import validate
from rdflib import OWL, RDF, RDFS, Graph, URIRef

from conftest import (
    INFERENCE_MODE,
    NEGATIVE_DIR,
    ROOT,
    SH,
    materialise,
    negative_fixture_files,
    parse_turtle,
    qname,
)

# Documented, intentional deviations between sh:datatype and rdfs:range.
# shapes/README.md, "v1.1 Candidates - OWL label properties".
DATATYPE_DEVIATIONS = {
    "capec#capecId": "KGCS IDs are patterned strings; frozen OWL v1.0 range is xsd:integer",
}


def _severity_counts(results_graph: Graph) -> Counter:
    return Counter(
        qname(results_graph.value(r, SH.resultSeverity))
        for r in results_graph.subjects(RDF.type, SH.ValidationResult)
    )


def _path_str(g: Graph, node):
    """Render a SHACL path (IRI, inverse or sequence) deterministically."""
    if node is None or isinstance(node, URIRef):
        return qname(node)
    inv = g.value(node, SH.inversePath)
    if inv is not None:
        return "^" + _path_str(g, inv)
    alt = g.value(node, SH.alternativePath)
    if alt is not None:
        return "(" + "|".join(_path_str(g, m) for m in g.items(alt)) + ")"
    if (node, RDF.first, None) in g:
        return "/".join(_path_str(g, m) for m in g.items(node))
    return "<bnode-path>"


def _results(results_graph: Graph) -> list[dict]:
    out = []
    for r in results_graph.subjects(RDF.type, SH.ValidationResult):
        out.append(
            {
                "focus": qname(results_graph.value(r, SH.focusNode)),
                "path": _path_str(results_graph, results_graph.value(r, SH.resultPath)),
                "severity": qname(results_graph.value(r, SH.resultSeverity)),
                "constraint": qname(results_graph.value(r, SH.sourceConstraintComponent)),
                "shape": qname(results_graph.value(r, SH.sourceShape)),
                "message": str(results_graph.value(r, SH.resultMessage) or ""),
            }
        )
    return sorted(out, key=lambda d: (d["focus"], d["path"], d["constraint"]))


def test_inference_mode_is_fixed():
    assert INFERENCE_MODE == "alignment-owlrl"


def test_shapes_are_valid_shacl(shapes):
    conforms, _, text = validate(shapes, shacl_graph=None, meta_shacl=True, inference="none")
    assert conforms, f"shapes graph is not valid SHACL:\n{text}"


def test_every_shape_reference_resolves_to_declared_owl_term(shapes, declared_terms):
    unresolved = set()
    for pred in (SH.path, SH["class"], SH.targetClass, SH.targetSubjectsOf, SH.targetObjectsOf):
        for _, o in shapes.subject_objects(pred):
            if isinstance(o, URIRef) and o not in declared_terms:
                unresolved.add(f"{qname(pred)} -> {qname(o)}")
    # Sequence / inverse paths are blank nodes; resolve their members too.
    for _, path in shapes.subject_objects(SH.path):
        if isinstance(path, URIRef):
            continue
        members = list(shapes.items(path)) if (path, RDF.first, None) in shapes else []
        inv = shapes.value(path, SH.inversePath)
        if inv is not None:
            members.append(inv)
        for m in members:
            if isinstance(m, URIRef) and m not in declared_terms:
                unresolved.add(f"sh:path member -> {qname(m)}")
    assert not unresolved, "shape references not declared in any OWL module:\n  " + "\n  ".join(sorted(unresolved))


def test_shape_datatypes_match_owl_ranges(shapes, tbox):
    mismatches = []
    for ps in shapes.subjects(SH.path, None):
        p = shapes.value(ps, SH.path)
        dt = shapes.value(ps, SH.datatype)
        if not isinstance(p, URIRef) or dt is None:
            continue
        ranges = set(tbox.objects(p, RDFS.range))
        if ranges and dt not in ranges and qname(p) not in DATATYPE_DEVIATIONS:
            mismatches.append(f"{qname(p)}: shape {qname(dt)} vs OWL {[qname(r) for r in ranges]}")
    assert not mismatches, "\n".join(mismatches)


def test_documented_datatype_deviations_still_exist(shapes, tbox):
    """If a deviation is fixed in a successor module, drop it from the allowlist."""
    for term in DATATYPE_DEVIATIONS:
        p = URIRef("http://www.motherhacker.me/kgcs/ontology/" + term)
        assert (p, RDFS.range, None) in tbox, f"{term} no longer declared"


def test_tbox_as_data_has_no_violations(tbox, shapes):
    """Legacy TBox-only run: OWL modules validated as data (mostly vacuous).

    The frozen Engage and SHIELD modules embed example individuals; one of
    them (engage:EAC0001) lacks engage:name and yields a pre-existing Warning.
    Violations are never tolerated.
    """
    conforms, rg, text = validate(tbox, shacl_graph=shapes, inference="none")
    counts = _severity_counts(rg)
    assert counts.get("sh:Violation", 0) == 0, text
    assert counts.get("sh:Warning", 0) <= 1, text


# ---------------------------------------------------------------------------
# ABox fixtures - the part that makes minCount / sh:class / sh:pattern real
# ---------------------------------------------------------------------------


def _focus_nodes(shape: URIRef, shapes: Graph, data: Graph) -> set:
    nodes = set()
    for cls in shapes.objects(shape, SH.targetClass):
        nodes |= set(data.subjects(RDF.type, cls))
    for prop in shapes.objects(shape, SH.targetSubjectsOf):
        nodes |= set(data.subjects(prop, None))
    for prop in shapes.objects(shape, SH.targetObjectsOf):
        nodes |= set(data.objects(None, prop))
    return nodes


def test_every_node_shape_has_a_focus_node_in_fixture(shapes, positive_fixture, alignment):
    """No shape may be vacuous against the fixture."""
    data = materialise(positive_fixture, alignment)
    empty, untargeted = [], []
    for shape in shapes.subjects(RDF.type, SH.NodeShape):
        has_target = any(
            (shape, t, None) in shapes
            for t in (SH.targetClass, SH.targetSubjectsOf, SH.targetObjectsOf, SH.targetNode)
        )
        if not has_target:
            # Anonymous shapes are reached through sh:node; a named shape
            # without a target is dead and must not exist.
            if isinstance(shape, URIRef):
                untargeted.append(qname(shape))
            continue
        if not _focus_nodes(shape, shapes, data):
            empty.append(qname(shape))
    assert not untargeted, "named node shapes without any target: " + ", ".join(sorted(untargeted))
    assert not empty, "node shapes with no focus node in tests/fixtures/*.ttl:\n  " + "\n  ".join(sorted(empty))


def test_positive_fixture_conforms(shapes, positive_fixture, alignment):
    assert len(positive_fixture) > 0
    data = materialise(positive_fixture, alignment)
    conforms, rg, text = validate(data, shacl_graph=shapes, inference="none")
    assert conforms, text


def test_negative_manifest_covers_every_negative_fixture(negative_manifest):
    files = {p.name for p in negative_fixture_files()}
    listed = set(negative_manifest)
    assert files, f"no negative fixtures in {NEGATIVE_DIR.relative_to(ROOT)}"
    assert files == listed, f"manifest/file mismatch: files-only={files - listed} manifest-only={listed - files}"


@pytest.mark.parametrize("path", negative_fixture_files(), ids=lambda p: p.name)
def test_negative_fixture_produces_expected_results(path, shapes, positive_fixture, alignment, negative_manifest):
    """Each negative fixture is the positive fixture plus one mutation file.

    The manifest lists, per file, the expected results as
    ``{"focus", "path", "constraint", "severity"}`` and the run must produce
    exactly that set - no more, no less.
    """
    expected = negative_manifest[path.name]["expected"]
    assert expected, f"{path.name}: manifest lists no expected results"
    mutation = parse_turtle(path)
    data = Graph()
    data += positive_fixture
    data += mutation
    data = materialise(data, alignment)
    conforms, rg, text = validate(data, shacl_graph=shapes, inference="none")
    assert not conforms, f"{path.name}: expected violations, got conforms=True"
    got = [
        {k: r[k] for k in ("focus", "path", "constraint", "severity")}
        for r in _results(rg)
    ]
    exp = sorted(expected, key=lambda d: (d["focus"], d["path"], d["constraint"]))
    assert got == exp, f"{path.name}\nexpected: {exp}\ngot:      {got}\n{text}"
