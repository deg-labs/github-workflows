import os
from pathlib import Path
import subprocess
import textwrap
import unittest


WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/gce-deploy.yml"


class DeployModesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text()
        step = cls.workflow.split("      - name: Validate deployment mode\n", 1)[1]
        cls.script = textwrap.dedent(step.split("        run: |\n", 1)[1].split("\n      - name:", 1)[0])

    def validate(self, mode, repository, *, label="dev", environment="dev"):
        env = dict(os.environ, DEPLOY_MODE=mode, CALLER_REPOSITORY=repository,
                   EVENT_NAME="pull_request", EVENT_LABEL=label, DEPLOY_ENV=environment)
        return subprocess.run(["bash", "-c", self.script], env=env, capture_output=True, text=True)

    def test_allowed_modes(self):
        for mode, repository in [
            ("compose", "deg-labs/hdm"),
            ("compose", "deg-labs/volatility-monorepo"),
            ("compose", "deg-labs/stock-theme-ranking-bot"),
            ("scheduled-container", "deg-labs/jsf-taisyaku"),
            ("package-update", "deg-labs/gce-package-maintenance"),
        ]:
            with self.subTest(mode=mode, repository=repository):
                result = self.validate(mode, repository)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_legacy_unknown_or_wrong_repository(self):
        for mode, repository in [
            ("legacy", "deg-labs/hdm"),
            ("", "deg-labs/hdm"),
            ("unknown", "deg-labs/hdm"),
            ("compose", "deg-labs/gce-package-maintenance"),
            ("package-update", "deg-labs/hdm"),
        ]:
            with self.subTest(mode=mode, repository=repository):
                self.assertNotEqual(self.validate(mode, repository).returncode, 0)

    def test_rejects_mismatched_label(self):
        self.assertNotEqual(self.validate("compose", "deg-labs/hdm", label="prd").returncode, 0)

    def test_arbitrary_command_inputs_are_absent(self):
        inputs = self.workflow.split("    inputs:\n", 1)[1].split("\njobs:\n", 1)[0]
        for name in ("prepare_command", "remote_deploy_command", "additional_upload_files", "artifact_excludes"):
            with self.subTest(name=name):
                self.assertNotIn(f"      {name}:", inputs)
        self.assertIn("      deploy_mode:\n", inputs)
        mode = inputs.split("      deploy_mode:\n", 1)[1].split("      checkout_submodules:", 1)[0]
        self.assertIn("required: true", mode)


if __name__ == "__main__":
    unittest.main()
