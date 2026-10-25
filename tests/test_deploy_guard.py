import os
from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest


WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/gce-deploy.yml"


class DeployGuardTest(unittest.TestCase):
    def run_guard(self, actor, author, api_status=0):
        # Execute the workflow's actual shell block with a mocked GitHub API.
        guard = WORKFLOW.read_text().split("        id: deploy-guard\n", 1)[1]
        guard = guard.split("\n      - name:", 1)[0]
        script = textwrap.dedent(guard.split("        run: |\n", 1)[1])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gh = root / "gh"
            gh.write_text(
                '#!/bin/bash\n'
                'printf "%s\\n" "haturatu" "other-member"\n'
                'exit "$MOCK_API_STATUS"\n'
            )
            gh.chmod(0o755)
            output = root / "output"
            result = subprocess.run(
                ["bash", "-c", script],
                env={
                    **os.environ,
                    "PATH": f"{root}{os.pathsep}{os.environ['PATH']}",
                    "DEPLOY_ACTOR": actor,
                    "PR_AUTHOR": author,
                    "DEPLOY_TEAM_SLUG": "deg-develop",
                    "ORG_NAME": "deg-labs",
                    "GITHUB_OUTPUT": str(output),
                    "MOCK_API_STATUS": str(api_status),
                },
                capture_output=True,
                text=True,
            )
            allowed = output.read_text() if output.exists() else ""
        return result, allowed

    def test_allowed_members_and_dependabot_author(self):
        for author in ("haturatu", "other-member", "dependabot[bot]", ""):
            with self.subTest(author=author):
                result, output = self.run_guard("haturatu", author)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(output, "allowed=true\n")

    def test_unapproved_authors_are_blocked(self):
        for author in ("outsider", "dependabot", "dependabot[bot]-fake"):
            with self.subTest(author=author):
                result, output = self.run_guard("haturatu", author)
                self.assertEqual(result.returncode, 1)
                self.assertIn("PR author", result.stderr)
                self.assertEqual(output, "")

    def test_dependabot_author_does_not_bypass_actor_check(self):
        for actor in ("outsider", "dependabot[bot]"):
            with self.subTest(actor=actor):
                result, output = self.run_guard(actor, "dependabot[bot]")
                self.assertEqual(result.returncode, 1)
                self.assertIn("Actor", result.stderr)
                self.assertEqual(output, "")

    def test_membership_lookup_failure_blocks_deployment(self):
        result, output = self.run_guard("haturatu", "dependabot[bot]", api_status=1)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(output, "")


if __name__ == "__main__":
    unittest.main()
