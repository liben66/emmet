"""Regression checks for JSON-like fields using a Pydantic wrap handler."""

import json
import unittest

from pydantic import BaseModel

from emmet.core.tasks import TaskDoc
from emmet.core.types.typing import JsonDictType, JsonListType


class JsonPayload(BaseModel):
    mapping: JsonDictType = None
    sequence: JsonListType = None


class JsonSerializationTests(unittest.TestCase):
    def test_empty_json_like_fields(self):
        self.assertEqual(
            JsonPayload().model_dump(), {"mapping": None, "sequence": None}
        )
        self.assertIsNone(TaskDoc().model_dump()["custodian"])

    def test_python_and_json_round_trips(self):
        value = JsonPayload(mapping={"energy": -1.2}, sequence=[{"step": 1}])
        expected = {"mapping": {"energy": -1.2}, "sequence": [{"step": 1}]}
        self.assertEqual(value.model_dump(), expected)
        self.assertEqual(json.loads(value.model_dump_json()), expected)
        self.assertEqual(
            JsonPayload.model_validate(value.model_dump()).model_dump(), expected
        )

    def test_arrow_format_round_trip(self):
        value = JsonPayload(mapping={"energy": -1.2}, sequence=[{"step": 1}])
        result = value.model_dump(context={"format": "arrow"})
        self.assertIsInstance(result["mapping"], str)
        self.assertIsInstance(result["sequence"], str)
        self.assertEqual(
            JsonPayload.model_validate(result).model_dump(), value.model_dump()
        )

    def test_task_document_custodian_round_trip(self):
        document = TaskDoc(custodian=[{"job": {"command": "vasp_ncl"}}], calcs_reversed=[])
        restored = TaskDoc.model_validate(document.model_dump())
        self.assertEqual(restored.custodian[0].job, {"command": "vasp_ncl"})


if __name__ == "__main__":
    unittest.main()
