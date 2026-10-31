import os
from pathlib import Path
import subprocess
import textwrap
import unittest

WORKFLOW = Path(__file__).resolve().parents[1] / '.github/workflows/gce-deploy.yml'


class DeployModesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text()
        step = cls.workflow.split('      - name: Validate deployment mode\n', 1)[1]
        cls.script = textwrap.dedent(step.split('        run: |\n', 1)[1].split('\n      - name:', 1)[0])

    def validate(self, mode, name='new-app', label='dev', environment='dev'):
        env = dict(os.environ, DEPLOY_MODE=mode, CALLER_NAME=name,
                   EVENT_NAME='pull_request', EVENT_LABEL=label, DEPLOY_ENV=environment)
        return subprocess.run(['bash', '-c', self.script], env=env, capture_output=True, text=True)

    def test_generic_modes_and_new_repository(self):
        for mode in ('compose', 'package-update'):
            with self.subTest(mode=mode):
                self.assertEqual(self.validate(mode).returncode, 0)

    def test_rejects_legacy_unknown_and_unsafe_name(self):
        for mode, name in [('legacy', 'new-app'), ('', 'new-app'), ('compose', '../unsafe')]:
            with self.subTest(mode=mode, name=name):
                self.assertNotEqual(self.validate(mode, name).returncode, 0)

    def test_rejects_mismatched_label(self):
        self.assertNotEqual(self.validate('compose', label='prd').returncode, 0)

    def test_artifact_id_downloads_use_flat_layout(self):
        expected = "artifact-ids: ${{ inputs.artifact_id }}\n          path: artifact\n          merge-multiple: true"
        self.assertEqual(self.workflow.count(expected), 2)

    def test_no_arbitrary_commands(self):
        for name in ('prepare_command', 'remote_deploy_command', 'additional_upload_files'):
            self.assertNotIn(f'      {name}:', self.workflow)


if __name__ == '__main__':
    unittest.main()
