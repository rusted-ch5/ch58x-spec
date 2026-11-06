"""Reject ambiguous command layouts and malformed conformance inputs."""
import copy
import json
import unittest

from jsonschema.exceptions import ValidationError

from validate_ble import ROOT, contract_check, vectors_check


class ContractValidation(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads((ROOT / 'protocol/ch585-ble-hci.json').read_text())
        self.vectors = json.loads((ROOT / 'conformance/ble-v1.json').read_text())

    def test_duplicate_opcode(self):
        self.contract['commands'].append(copy.deepcopy(self.contract['commands'][0]))
        with self.assertRaisesRegex(ValueError, 'duplicate opcode'):
            contract_check(self.contract)

    def test_overlapping_fields(self):
        self.contract['commands'][0]['fields'][1]['offset'] = 0
        with self.assertRaisesRegex(ValueError, 'overlapping'):
            contract_check(self.contract)

    def test_missing_parameter_octet(self):
        self.contract['commands'][0]['parameter_length'] += 1
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            contract_check(self.contract)

    def test_wrong_scalar_width(self):
        self.contract['commands'][0]['fields'][0]['width'] = 1
        with self.assertRaisesRegex(ValueError, 'scalar field width'):
            contract_check(self.contract)

    def test_duplicate_vector_id(self):
        self.vectors['cases'].append(copy.deepcopy(self.vectors['cases'][0]))
        with self.assertRaisesRegex(ValueError, 'duplicate vector ID'):
            vectors_check(self.vectors)

    def test_non_octet(self):
        self.vectors['cases'][0]['input']['bytes'][0] = 256
        with self.assertRaises((ValueError, ValidationError)):
            vectors_check(self.vectors)

    def test_oversized_mask(self):
        case = next(c for c in self.vectors['cases'] if c['operation'] == 'event-mask')
        case['input']['mask'] = 1 << 64
        with self.assertRaises((ValueError, ValidationError)):
            vectors_check(self.vectors)


if __name__ == '__main__':
    unittest.main()
