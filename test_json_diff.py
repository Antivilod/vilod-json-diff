from decimal import Decimal
import tempfile
from pathlib import Path
import unittest
import json_diff as tool


class JsonDiffTests(unittest.TestCase):
    def test_object_order_and_numeric_equivalence(self):
        self.assertTrue(tool.compare({'a':1,'b':2}, {'b':2,'a':Decimal('1.0')})['equal'])

    def test_boolean_is_not_number(self):
        self.assertEqual(tool.compare(True, 1)['counts']['type_changed'], 1)

    def test_nested_add_remove_change(self):
        result = tool.compare({'a':{'x':1},'old':0}, {'a':{'x':2},'new':0})
        self.assertEqual(result['counts'], {'added':1,'removed':1,'type_changed':0,'value_changed':1})

    def test_arrays_are_ordered(self):
        self.assertEqual(tool.compare([1,2], [2,1,3])['recorded_changes'], 3)

    def test_paths_opt_in_and_pointer_escaping(self):
        result = tool.compare({'a/b~c':'old'}, {'a/b~c':'new'}, show_paths=True)
        self.assertEqual(result['changes'][0]['path'], '/a~1b~0c')
        self.assertNotIn('changes', tool.compare({'private-key':'old'}, {'private-key':'new'}))
        self.assertNotIn('new', str(result))

    def test_cap_is_explicit(self):
        result = tool.compare([1,2,3], [4,5,6], max_changes=2)
        self.assertTrue(result['truncated'])
        self.assertFalse(result['equal'])
        self.assertEqual(result['recorded_changes'], 2)
        self.assertFalse(tool.compare([1], [2], max_changes=1)['truncated'])

    def test_strict_input_and_bom(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'in.json'
            for content in ('{"a":1,"a":2}', 'NaN', 'Infinity', '{'):
                path.write_text(content, encoding='utf-8')
                with self.assertRaises(ValueError): tool.load(path)
            path.write_bytes(b'\xef\xbb\xbf{"a":1.5}')
            self.assertEqual(tool.load(path)['a'], Decimal('1.5'))

    def test_empty_objects_and_root_path(self):
        self.assertTrue(tool.compare({}, {})['equal'])
        self.assertEqual(tool.compare(None, [], True)['changes'][0]['path'], '')

    def test_invalid_limit(self):
        with self.assertRaises(ValueError): tool.compare(1, 2, max_changes=0)
