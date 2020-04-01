__all__ = [
    'AlwaysSucceeds',
    'CreateTextFile',
    'CreateDir',
    'Command'
]

import os
import io
import contextlib
from pathlib import Path
from abc import abstractmethod
from collections import OrderedDict


class Command:
    """Base class implementing the Command pattern
    supports undo and subcommands

    override only __init__, __do__ and __undo__"""
    def __init__(self, *args, **kwargs):
        self._subcommands = OrderedDict()
        self._do_exception = None
        self._undo_exception = None
        self._done = False
        self._undone = False

    @contextlib.contextmanager
    def _exec_do_cmd(self, raise_exception):
        try:
            self._do_exception = None
            self._undo_exception = None
            self._done = False
            self._undone = False

            yield self
            # command succeeded
        except Exception as e:
            # command failed
            self._do_exception = e
        finally:
            self._done = True
            self._undone = False
            if raise_exception and self.failed_doing:
                raise self.done_failure

    @contextlib.contextmanager
    def _exec_undo_cmd(self, raise_exception):
        try:
            self._undo_exception = None
            self._undone = False

            yield self
            # command succeeded
        except Exception as e:
            # command failed
            self._undo_exception = e
        finally:
            self._undone = True
            if raise_exception and self.failed_undoing:
                raise self.undone_failure

    def do(self, reraise=False):
        """executes the command.
        Set reraise to True for a subcommand"""
        assert self._done == self._undone, \
            "Undo before doing and do it once at first"
        with self._exec_do_cmd(reraise):
            self.__do__()
            for _, cmd in self._subcommands.items():
                cmd.do(reraise=True)

    @abstractmethod
    def __do__(self):
        raise NotImplementedError  # pragma: no cover

    @property
    def done(self):
        return self._done

    @property
    def failed(self):
        return bool(self.failure)

    @property
    def failed_doing(self):
        return bool(self.done_failure)

    @property
    def failed_undoing(self):
        return bool(self.undone_failure)

    @property
    def failure(self):
        return self._do_exception or self._undo_exception

    @property
    def done_failure(self):
        return self._do_exception

    @property
    def undone_failure(self):
        return self._undo_exception

    @property
    def succeeded(self):
        return not self.failed

    @property
    def succeeded_doing(self):
        return not self.failed_doing

    @property
    def succeeded_undoing(self):
        return not self.failed_undoing

    def undo(self, reraise=False):
        """reverts the result of Command.do.
        Set reraise to True for a subcommand
        """
        assert self._done and not self._undone, \
            "Do before undoing or undo once"

        with self._exec_undo_cmd(reraise):
            for _, cmd in reversed(self._subcommands.items()):
                cmd.undo(reraise=True)
            self.__undo__()

    @abstractmethod
    def __undo__(self):
        raise NotImplementedError  # pragma: no cover

    @property
    def undone(self):
        return self._undone

    def visit(self, callback, prefix=True):
        if prefix:
            callback(self)
        for _, cmd in self._subcommands.items():
            cmd.visit(callback, prefix=prefix)
        if not prefix:
            callback(self)

    def add_subcommand(self, cls, *args, name=None, **kwargs):
        cmd = cls(*args, **kwargs)
        cmd.name = self._make_name(name)
        self._subcommands[cmd.name] = cmd
        return cmd

    def _make_name(self, name):
        if name and name not in self._subcommands:
            # provided name appears to be valid
            pass
        else:
            name = f"cmd{len(self._subcommands)}"
            name = f'cmd#{hex(hash(name))}'
        return name

    def __contains__(self, item):
        return self._subcommands.__contains__(item)

    def __getitem__(self, item):
        return self._subcommands.__getitem__(item)

    def __len__(self):
        return len(self._subcommands)


class AlwaysSucceeds(Command):
    """Dummy Command class for testing purposes"""
    def __do__(self):
        pass

    def __undo__(self):
        pass


class CreateDir(Command):
    """Command that creates a new directory"""
    def __init__(self, path, *args, **kwargs):
        self.path = Path(path)
        super().__init__(*args, **kwargs)

    def __do__(self):
        os.mkdir(self.path)

    def __undo__(self):
        os.rmdir(self.path)


class CreateTextFile(Command):
    """Command that creates a new text file with optional content"""
    def __init__(self, filename, path, *args, content=None, **kwargs):
        self.path = Path(path).joinpath(filename)
        self.filename = filename
        self.content = content
        super().__init__(*args, **kwargs)

    def __do__(self):
        with io.open(self.path, mode='w') as f:
            f.writelines(self.content if self.content else '')

    def __undo__(self):
        os.remove(self.path)
