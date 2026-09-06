"""contracts/*.json are valid JSON Schema documents and their examples validate."""

import json

import pytest
from jsonschema import Draft7Validator, validators

from conftest import CONTRACTS_DIR

CONTRACT_FILES = sorted(CONTRACTS_DIR.glob("*.json"))


def _load(path):
    with path.open(encoding="utf-8") as fh:
        doc = json.load(fh)
    if not doc:
        pytest.fail(f"{path.name}: empty document")
    return doc


@pytest.mark.parametrize("path", CONTRACT_FILES, ids=lambda p: p.name)
def test_contract_is_valid_json_schema(path):
    doc = _load(path)
    assert doc.get("$schema", "").startswith("http://json-schema.org/draft-07/"), f"{path.name}: not Draft-07"
    cls = validators.validator_for(doc, default=Draft7Validator)
    cls.check_schema(doc)


@pytest.mark.parametrize("path", CONTRACT_FILES, ids=lambda p: p.name)
def test_contract_examples_validate(path):
    doc = _load(path)
    examples = doc.get("examples", [])
    cls = validators.validator_for(doc, default=Draft7Validator)
    validator = cls(doc)
    for i, example in enumerate(examples):
        errors = sorted(validator.iter_errors(example), key=lambda e: list(e.path))
        assert not errors, f"{path.name} examples[{i}]: " + "; ".join(e.message for e in errors)


def test_at_least_one_contract():
    assert CONTRACT_FILES
