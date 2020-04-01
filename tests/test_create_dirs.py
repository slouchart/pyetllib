from unittest import TestCase
from unittest import main as run_tests

from unittest.mock import Mock, patch


from src.pyetllib.etlskel.operations import create_skeleton


class TestCreateDirs(TestCase):
    def test_create_dirs(self):
        """Test the structure created by create_skeleton"""
        paths_created = []

        def mock_mkdir(path):
            paths_created.append(path)

        def no_op():
            pass

        with patch('src.pyetllib.etllib.commands.os.mkdir',
                   new=Mock(wraps=mock_mkdir)):
            with patch('src.pyetllib.etlskel.operations.CreateTextFile.__do__',
                       new=Mock(wraps=no_op)):
                with self.subTest("Default project"):
                    paths_created = []

                    cmd, _ = create_skeleton('foo')
                    cmd.do()
                    self.assertGreater(len(paths_created), 0)
                    self.assertEqual(len(paths_created), 4)

                with self.subTest("Default project - no templates"):
                    paths_created = []

                    cmd, _ = create_skeleton('foo', create_template_dir=False)

                    cmd.do()
                    self.assertGreater(len(paths_created), 0)
                    self.assertEqual(len(paths_created), 3)

                with self.subTest("Package project - no templates"):
                    paths_created = []

                    cmd, _ = create_skeleton('foo', main_package_name='bar',
                                             create_template_dir=False)
                    cmd.do()
                    self.assertGreater(len(paths_created), 0)
                    self.assertEqual(len(paths_created), 3)
                    self.assertIn('bar', str(paths_created[1]))

                with self.subTest("Full project with source dir"):
                    paths_created = []
                    cmd, _ = create_skeleton('foo', main_package_name='bar',
                                             create_source_dir=True)
                    cmd.do()
                    self.assertGreater(len(paths_created), 0)
                    self.assertEqual(len(paths_created), 5)
                    self.assertIn('src', str(paths_created[1]))


if __name__ == '__main__':
    run_tests()
