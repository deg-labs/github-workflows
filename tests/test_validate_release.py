import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import validate_release as validator


class ReleaseTest(unittest.TestCase):
    def archive(self, name, kind=tarfile.REGTYPE):
        temp = tempfile.NamedTemporaryFile(suffix='.tgz')
        with tarfile.open(temp.name, 'w:gz') as tar:
            member = tarfile.TarInfo(name)
            member.type = kind
            if kind == tarfile.REGTYPE:
                member.size = 4
                tar.addfile(member, io.BytesIO(b'test'))
            else:
                member.linkname = '/etc/passwd'
                tar.addfile(member)
        self.addCleanup(temp.close)
        return temp.name

    def test_rejects_traversal_symlink_and_env(self):
        for name, kind in [('../escape', tarfile.REGTYPE), ('link', tarfile.SYMTYPE), ('.env', tarfile.REGTYPE)]:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as dest:
                with self.assertRaises(ValueError):
                    validator.validate_archive(self.archive(name, kind), dest)

    def test_rejects_privileged_service(self):
        with tempfile.TemporaryDirectory() as dest:
            root = Path(dest)
            (root / 'compose.yaml').write_text('services: {}')
            result = mock.Mock(returncode=0, stdout=json.dumps({'services': {'x': {'privileged': True}}}))
            with mock.patch.object(validator.subprocess, 'run', return_value=result):
                with self.assertRaises(ValueError):
                    validator.validate_compose(root)

    def test_rejects_unsafe_bind(self):
        with tempfile.TemporaryDirectory() as dest:
            root = Path(dest)
            (root / 'compose.yaml').write_text('services: {}')
            result = mock.Mock(returncode=0, stdout=json.dumps({'services': {'x': {'volumes': [{'type': 'bind', 'source': '/etc'}]}}}))
            with mock.patch.object(validator.subprocess, 'run', return_value=result):
                with self.assertRaises(ValueError):
                    validator.validate_compose(root)


if __name__ == '__main__':
    unittest.main()
