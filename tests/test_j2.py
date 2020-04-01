# -*- coding:utf-8 -*-

from unittest import TestCase
from unittest import main as run_tests

from pathlib import Path
from jinja2 import Template, TemplateError

from src.pyetllib.etllib.utils.j2 import load_template, get_templates_path
from src.pyetllib.etllib.utils.j2 import load_template_from_pkg
from src.pyetllib.etllib.utils.j2 import load_template_from_path
from src.pyetllib.etllib.tools.j2 import render_template


class TestJ2Render(TestCase):

    def test_get_template_dir(self):
        """Test etllib.j2render.get_templates_path"""
        template_path = get_templates_path(path_parts=('etlskel',))
        self.assertTrue(Path(template_path).exists())

    def test_load_template(self):
        """Test etllib.j2render.load_template"""
        template_path = get_templates_path(path_parts=('etlskel',))
        template = load_template(template_path, 'setuppy.j2')
        self.assertIsNotNone(template)

    def test_load_template_from_path(self):
        """Test etllib.j2render.load_template_from_path"""
        module_path = Path(get_templates_path(path_parts=('etlskel',)))\
            .parent
        template = load_template_from_path(module_path, 'setuppy.j2')
        self.assertIsNotNone(template)

    def test_load_template_from_path_errors(self):
        """Tests exception handling in
        etllib.j2render.load_template_from_path"""

        with self.subTest("Non existing package path"):
            module_path = Path("foo")
            with self.assertRaises(TemplateError) as cm:
                _ = load_template_from_path(module_path, 'setuppy.j2')
            self.assertEqual(f"Template path '"
                             f"{Path(module_path, 'templates')}' "
                             f"does not exist",
                             str(cm.exception))

        with self.subTest("Non existing template file"):
            module_path = Path(get_templates_path(
                path_parts=('etlskel',)
            )).parent
            with self.assertRaises(TemplateError) as cm:
                _ = load_template_from_path(module_path, 'foo.j2')
            self.assertEqual("Template not found 'foo.j2'",
                             str(cm.exception))

    def test_load_template_from_pkg(self):
        """Test etllib.j2render.load_template_from_pkg"""
        template = load_template_from_pkg('src.pyetllib.etlskel', 'setuppy.j2')
        self.assertIsNotNone(template)

    def test_load_template_from_pkg_error(self):
        """Test exception handling
        in etllib.j2render.load_template_from_pkg"""
        with self.subTest("Module not found"):
            with self.assertRaises(TemplateError) as cm:
                _ = load_template_from_pkg('foo.bar', 'spam.j2')
            self.assertEqual("No module named 'foo'", str(cm.exception))

        with self.subTest("Templates module not found"):
            with self.assertRaises(TemplateError) as cm:
                _ = load_template_from_pkg('tests', 'spam.j2')
            self.assertEqual("Template not found 'spam.j2'", str(cm.exception))

    def test_render_template_to_string(self):
        template = Template('{{ value }}')
        s = render_template(template, value='to_string')
        self.assertEqual(s, 'to_string')

    def test_render_template_tp_stream(self):
        template = Template('{% for value in data %}{{ value }}{% endfor %}')
        s = render_template(template, streaming=True, data=tuple(range(3)))
        self.assertListEqual(list(s), list(str(i) for i in range(3)))


if __name__ == '__main__':
    run_tests()
