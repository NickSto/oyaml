import sys
from collections import OrderedDict
from types import GeneratorType

import pytest

import oyaml as yaml


data = OrderedDict([('x', 1), ('z', 3), ('y', 2)])


# this release was pulled from index, but still might be seen in the wild
pyyaml_41 = yaml.pyyaml.__version__ == '4.1'


def test_dump():
    assert yaml.dump(data) == '{x: 1, z: 3, y: 2}\n'


def test_safe_dump():
    assert yaml.safe_dump(data) == '{x: 1, z: 3, y: 2}\n'


@pytest.mark.skipif(not pyyaml_41, reason="requires PyYAML version == 4.1")
def test_danger_dump():
    assert yaml.danger_dump(data) == '{x: 1, z: 3, y: 2}\n'


def test_dump_all():
    assert yaml.dump_all(documents=[data, {}]) == '{x: 1, z: 3, y: 2}\n--- {}\n'


@pytest.mark.skipif(pyyaml_41, reason="requires PyYAML version != 4.1")
def test_dump_and_safe_dump_match():
    mydict = {'x': 1, 'z': 2, 'y': 3}
    # don't know if mydict is ordered in the implementation or not (but don't care)
    assert yaml.dump(mydict) == yaml.safe_dump(mydict)


@pytest.mark.skipif(not pyyaml_41, reason="requires PyYAML version == 4.1")
def test_danger_dump_and_safe_dump_match():
    mydict = {'x': 1, 'z': 2, 'y': 3}
    assert yaml.danger_dump(mydict) == yaml.safe_dump(mydict)


def test_safe_dump_all():
    assert yaml.safe_dump_all(documents=[data, {}]) == '{x: 1, z: 3, y: 2}\n--- {}\n'


def test_load():
    loaded = yaml.load('{x: 1, z: 3, y: 2}')
    assert loaded == {'x': 1, 'z': 3, 'y': 2}


def test_safe_load():
    loaded = yaml.safe_load('{x: 1, z: 3, y: 2}')
    assert loaded == {'x': 1, 'z': 3, 'y': 2}


def test_load_all():
    gen = yaml.load_all('{x: 1, z: 3, y: 2}\n--- {}\n')
    assert isinstance(gen, GeneratorType)
    ordered_data, empty_dict = gen
    assert empty_dict == {}
    assert ordered_data == data


@pytest.mark.skipif(sys.version_info >= (3, 7), reason="requires python3.6-")
def test_loads_to_ordered_dict():
    loaded = yaml.load('{x: 1, z: 3, y: 2}')
    assert isinstance(loaded, OrderedDict)


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires python3.7+")
def test_loads_to_std_dict():
    loaded = yaml.load('{x: 1, z: 3, y: 2}')
    assert not isinstance(loaded, OrderedDict)
    assert isinstance(loaded, dict)


@pytest.mark.skipif(sys.version_info >= (3, 7), reason="requires python3.6-")
def test_safe_loads_to_ordered_dict():
    loaded = yaml.safe_load('{x: 1, z: 3, y: 2}')
    assert isinstance(loaded, OrderedDict)


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires python3.7+")
def test_safe_loads_to_std_dict():
    loaded = yaml.safe_load('{x: 1, z: 3, y: 2}')
    assert not isinstance(loaded, OrderedDict)
    assert isinstance(loaded, dict)


class MyOrderedDict(OrderedDict):
    pass


@pytest.mark.skipif(pyyaml_41, reason="requires PyYAML version != 4.1")
def test_subclass_dump_pyyaml3():
    data = MyOrderedDict([('x', 1), ('y', 2)])
    assert '!!python/object/apply:test_oyaml.MyOrderedDict' in yaml.dump(data)
    with pytest.raises(yaml.pyyaml.representer.RepresenterError, match='cannot represent an object') as cm:
        yaml.safe_dump(data)


@pytest.mark.skipif(not pyyaml_41, reason="requires PyYAML version == 4.1")
def test_subclass_dump_pyyaml4():
    data = MyOrderedDict([('x', 1), ('y', 2)])
    assert '!!python/object/apply:test_oyaml.MyOrderedDict' in yaml.danger_dump(data)
    with pytest.raises(yaml.pyyaml.representer.RepresenterError, match='cannot represent an object') as cm:
        yaml.dump(data)


def test_anchors_and_references():
    text = '''
        defaults:
          all: &all
            product: foo
          development: &development
            <<: *all
            profile: bar

        development:
          platform:
            <<: *development
            host: baz
    '''
    expected_load = {
        'defaults': {
            'all': {
                'product': 'foo',
            },
            'development': {
                'product': 'foo',
                'profile': 'bar',
            },
        },
        'development': {
            'platform': {
                'host': 'baz',
                'product': 'foo',
                'profile': 'bar',
            },
        },
    }
    assert yaml.load(text) == expected_load


def test_omap():
    text = '''
        Bestiary: !!omap
          - aardvark: African pig-like ant eater. Ugly.
          - anteater: South-American ant eater. Two species.
          - anaconda: South-American constrictor snake. Scaly.
    '''
    expected_load = {
        'Bestiary': ([
            ('aardvark', 'African pig-like ant eater. Ugly.'),
            ('anteater', 'South-American ant eater. Two species.'),
            ('anaconda', 'South-American constrictor snake. Scaly.'),
        ])
    }
    assert yaml.load(text) == expected_load


def test_omap_flow_style():
    text = 'Numbers: !!omap [ one: 1, two: 2, three : 3 ]'
    expected_load = {'Numbers': ([('one', 1), ('two', 2), ('three', 3)])}
    assert yaml.load(text) == expected_load
