from unittest import TestCase
from unittest import main as run_tests
from unittest.mock import patch

from pathlib import Path

from src.pyetllib.etllib.commands import Command, AlwaysSucceeds
from src.pyetllib.etllib.commands import CreateTextFile, CreateDir


class AlwaysFails(Command):
    def __do__(self):
        raise RuntimeError("I suck at doing things")

    def __undo__(self):
        raise RuntimeError("I suck at undoing things too!")


class FailsOnUndo(Command):
    def __do__(self):
        pass

    def __undo__(self):
        raise RuntimeError("Cannot be undone :(")


class AppendTo(Command):
    def __init__(self, ref_to_list, *args, **kwargs):
        self.ref_to_list = ref_to_list
        super().__init__(*args, **kwargs)

    def __do__(self):
        self.ref_to_list.append(1)

    def __undo__(self):
        self.ref_to_list.pop()


class TestCommand(TestCase):
    """Testing the Command class"""
    def test_simple_command(self):
        """Testing the do/undo flags in a nominal case"""
        cmd = AlwaysSucceeds()
        cmd.do()
        self.assertTrue(cmd.done)
        self.assertFalse(cmd.undone)
        self.assertTrue(cmd.succeeded)
        self.assertFalse(cmd.failed)

        cmd.undo()
        self.assertTrue(cmd.done)
        self.assertTrue(cmd.undone)
        self.assertTrue(cmd.succeeded)
        self.assertFalse(cmd.failed)

    def test_failing_command(self):
        """Testing the do/undo flags in a non-nominal case"""
        cmd = AlwaysFails()
        cmd.do()
        self.assertTrue(cmd.failed)
        self.assertFalse(cmd.succeeded)
        self.assertTrue(cmd.done)

        cmd.undo()
        self.assertTrue(cmd.failed_undoing)
        self.assertFalse(cmd.succeeded_undoing)
        self.assertTrue(cmd.undone)

        with self.assertRaises(RuntimeError):
            cmd.do(reraise=True)

        with self.assertRaises(RuntimeError):
            cmd.undo(reraise=True)

    def test_failing_undo(self):
        """Testing failure on undo"""
        cmd = FailsOnUndo()
        cmd.do()
        self.assertTrue(cmd.succeeded_doing)

        cmd.undo()
        self.assertTrue(cmd.failed_undoing)

    def test_undo_without_do(self):
        """Sanity check of undo without a do"""
        cmd = AlwaysSucceeds()
        with self.assertRaises(AssertionError):
            cmd.undo()
        self.assertFalse(cmd.done)
        self.assertFalse(cmd.undone)

    def test_subcommands(self):
        """Testing subcommands in a nominal case"""
        s = list()
        root = AppendTo(s)
        for i in range(4):
            root.add_subcommand(AppendTo, s, name=str(i))
            self.assertIn(str(i), root)

        self.assertEqual(len(root), 4)
        root.do()
        self.assertListEqual(s, [1] * 5)

    def test_subcommands_failure(self):
        """Testing subcommands in a non-nominal case (a subcommand fails)"""
        s = list()
        root = AlwaysSucceeds(s)
        root.add_subcommand(AppendTo, s, name="first")
        root.add_subcommand(AlwaysFails, name="fails")
        root.add_subcommand(AppendTo, s, name="never executed")
        root.do()
        self.assertTrue(root.failed)
        self.assertTrue(root['fails'].failed)
        self.assertFalse(root['first'].failed)
        self.assertFalse(root['never executed'].done)

        self.assertListEqual(s, [1])

    def test_subcommands_root_failure(self):
        """Testing subcommands in the case of a root failure"""
        root = AlwaysFails()
        root.add_subcommand(AlwaysSucceeds, name='never executed')
        root.do()
        self.assertTrue(root.failed)
        self.assertFalse(root['never executed'].done)

    def test_subcommands_undo_failure(self):
        s = list()
        root = AlwaysSucceeds(s)
        root.add_subcommand(AppendTo, s, name="first")
        root.add_subcommand(AlwaysFails, name="fails")
        root.add_subcommand(AppendTo, s, name="never executed")
        root.do()

        root.undo()
        self.assertTrue(root.failed)
        self.assertTrue(root.undone)
        self.assertFalse(root.succeeded_undoing)


class TestCommandCreateTextFile(TestCase):

    @patch('src.pyetllib.etllib.commands.io.open')
    @patch('src.pyetllib.etllib.commands.os.remove')
    def test_create_text_file(self, os_remove, io_open):
        cmd = CreateTextFile('file.txt', 'path/to')
        self.assertEqual(cmd.path, Path('path/to/file.txt'))
        cmd.do()
        io_open.assert_called_once_with(cmd.path, mode='w')

        cmd.undo()
        os_remove.assert_called_once_with(cmd.path)


class TestCreateDir(TestCase):

    @patch('src.pyetllib.etllib.commands.os.mkdir')
    @patch('src.pyetllib.etllib.commands.os.rmdir')
    def test_create_dir(self, os_rmdir, os_mkdir):
        cmd = CreateDir('my_dir')
        self.assertEqual(cmd.path, Path('my_dir'))
        cmd.do()
        os_mkdir.assert_called_once_with(cmd.path)

        cmd.undo()
        os_rmdir.assert_called_once_with(cmd.path)


class TestVisit(TestCase):
    def setUp(self):
        root = AlwaysSucceeds()
        root.add_subcommand(AlwaysSucceeds, name="first")
        root.add_subcommand(AlwaysSucceeds, name="second")
        root.add_subcommand(AlwaysSucceeds, name="third")
        self.root = root
        self.visited = []

    def visitor(self, arg):
        if hasattr(arg, 'name'):
            self.visited.append(arg.name)
        else:
            self.visited.append('root')

    def test_suffix_visitor(self):

        self.root.visit(self.visitor, prefix=False)
        self.assertListEqual(self.visited,
                             ['first', 'second', 'third', 'root'])

    def test_prefix_visitor(self):

        self.root.visit(self.visitor, prefix=True)
        self.assertListEqual(self.visited,
                             ['root', 'first', 'second', 'third'])

    def tearDown(self) -> None:
        self.visited = []


if __name__ == '__main__':
    run_tests()
