"""Every OWL module and SHACL shape file parses as Turtle with > 0 triples."""

import pytest
from rdflib import OWL, RDF

from conftest import owl_files, parse_turtle, shape_files


@pytest.mark.parametrize("path", owl_files(), ids=lambda p: p.name)
def test_owl_parses(path):
    g = parse_turtle(path)
    ontologies = list(g.subjects(RDF.type, OWL.Ontology))
    assert len(ontologies) == 1, f"{path.name}: expected exactly one owl:Ontology header"


@pytest.mark.parametrize("path", shape_files(), ids=lambda p: p.name)
def test_shape_parses(path):
    parse_turtle(path)
