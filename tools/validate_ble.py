#!/usr/bin/env python3
"""Check the CH585-first protocol contract, profiles and executable vectors."""
import json
from pathlib import Path

from jsonschema.validators import validator_for

ROOT = Path(__file__).resolve().parents[1]


def require(value, message):
    if not value:
        raise ValueError(message)


def schema_check(document, schema_name):
    schema = json.loads((ROOT / 'schema' / schema_name).read_text())
    validator = validator_for(schema)
    validator.check_schema(schema)
    validator(schema).validate(document)


def contract_check(contract):
    schema_check(contract, 'ble-hci.schema.json')
    opcodes = [command['opcode'] for command in contract['commands']]
    require(len(opcodes) == len(set(opcodes)), 'duplicate opcode')
    ids = [requirement['id'] for requirement in contract['requirements']]
    require(len(ids) == len(set(ids)), 'duplicate requirement ID')
    for command in contract['commands']:
        occupied = set()
        names = set()
        for field in command['fields']:
            require(field['name'] not in names, 'duplicate field name')
            names.add(field['name'])
            span = set(range(field['offset'], field['offset'] + field['width']))
            require(not occupied & span, 'overlapping HCI fields')
            occupied |= span
            width = {'u8': 1, 'u16le': 2, 'u64le': 8}.get(field['encoding'])
            require(width is None or width == field['width'], 'wrong scalar field width')
        require(occupied == set(range(command['parameter_length'])),
                f"{command['opcode']}: incomplete/oversized parameter layout")
    return len(opcodes)


def vectors_check(vectors):
    schema_check(vectors, 'ble-vectors.schema.json')
    ids = [case['id'] for case in vectors['cases']]
    require(len(ids) == len(set(ids)), 'duplicate vector ID')
    for case in vectors['cases']:
        data = case['input']
        for key in ('bytes', 'params'):
            if key in data:
                require(isinstance(data[key], list) and
                        all(type(v) is int and 0 <= v <= 255 for v in data[key]),
                        'invalid octet vector')
        if case['operation'] == 'event-mask':
            require(all(type(data[k]) is int and 0 <= data[k] < 2**64
                        for k in ('mask', 'le_mask')), 'invalid u64 mask')
        if case['operation'] == 'connection-parameters':
            require(len(data['values']) == 4 and
                    all(type(v) is int and 0 <= v <= 65535 for v in data['values']),
                    'invalid connection tuple')
    return len(ids)


def profiles_check():
    paths = sorted((ROOT / 'profiles').rglob('*.json'))
    names = set()
    for path in paths:
        profile = json.loads(path.read_text())
        require(profile['kind'] == 'ble-profile' and profile['schema_version'] == '1.0',
                'invalid profile kind/version')
        require(profile['name'] not in names, 'duplicate profile')
        names.add(profile['name'])
        if profile['chip'] == 'CH582':
            require(profile['experimental'] is True and 'experimental' in path.parts,
                    'CH582 must remain independently experimental')
            require(profile['sram_bytes'] == 32768, 'wrong CH582 SRAM budget')
        else:
            require(profile['chip'] == 'CH585' and profile['experimental'] is False,
                    'CH585 must be primary')
            require(profile['sram_bytes'] == 131072, 'wrong CH585 SRAM budget')
        ids = [feature['id'] for feature in profile['features']]
        require(len(ids) == len(set(ids)), 'duplicate feature')
        require(profile['status'] == 'not-yet-conformant',
                'acceptance transition requires a reviewed evidence schema')
    require(names == {'ch585-full', 'ch582-experimental-peripheral'}, 'missing profile')
    return len(paths)


def main():
    commands = contract_check(json.loads((ROOT / 'protocol/ch585-ble-hci.json').read_text()))
    vectors = vectors_check(json.loads((ROOT / 'conformance/ble-v1.json').read_text()))
    profiles = profiles_check()
    print(f'validated {commands} HCI command layouts, {vectors} vectors, {profiles} profiles')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
