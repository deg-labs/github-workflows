#!/usr/bin/env python3
"""Validate a deployment archive and its resolved Compose configuration."""
import json
import os
import pathlib
import re
import subprocess
import sys
import tarfile
import tempfile


def fail(message):
    raise ValueError(message)


def relative(path):
    if not isinstance(path, str) or not path or "\\" in path or "$" in path:
        return False
    p = pathlib.PurePosixPath(path)
    return not p.is_absolute() and ".." not in p.parts


def validate_archive(archive, directory):
    total = 0
    seen = set()
    with tarfile.open(archive, "r:gz") as tar:
        for member in tar.getmembers():
            path = pathlib.PurePosixPath(member.name)
            if member.name in (".", "./"):
                continue
            if not relative(member.name) or not (member.isfile() or member.isdir()):
                fail(f"Unsafe archive member: {member.name}")
            normalized = str(path)
            if normalized in seen:
                fail(f"Duplicate archive member: {member.name}")
            seen.add(normalized)
            if any(part == ".git" or part == ".env" or part.startswith(".env.") for part in path.parts):
                fail(f"Forbidden archive member: {member.name}")
            total += member.size
            if total > 512 * 1024 * 1024:
                fail("Archive exceeds uncompressed size limit")
        tar.extractall(directory, filter="data")


def validate_compose(root):
    files = [root / n for n in ("compose.yaml", "compose.yml", "docker-compose.yaml", "docker-compose.yml") if (root / n).is_file()]
    if len(files) != 1:
        fail("Exactly one root Compose file is required")
    text = files[0].read_text()
    if re.search(r"(?m)^\s*(include|extends|provider)\s*:", text):
        fail("Compose include, extends and provider are not supported")
    proc = subprocess.run(["docker", "compose", "-f", str(files[0]), "config", "--no-interpolate", "--no-env-resolution", "--no-path-resolution", "--format", "json"], cwd=root, capture_output=True, text=True)
    if proc.returncode:
        fail("Invalid Compose configuration")
    config = json.loads(proc.stdout)
    for name, service in config.get("services", {}).items():
        if service.get("privileged") or service.get("cap_add") or service.get("devices") or service.get("security_opt") or service.get("provider"):
            fail(f"Service {name} requests restricted privileges")
        for field in ("network_mode", "pid", "ipc", "uts", "userns_mode"):
            if service.get(field, "").startswith(("host", "container:", "service:")):
                fail(f"Service {name} has restricted {field}")
        build = service.get("build", {})
        if build and (not relative(build.get("context", ".")) or not relative(build.get("dockerfile", "Dockerfile")) or build.get("additional_contexts") or build.get("privileged")):
            fail(f"Service {name} has an unsafe build context")
        for env in service.get("env_file", []):
            if env.get("path", "") not in (".env", "./.env"):
                fail(f"Service {name} has an unsupported env_file")
        for volume in service.get("volumes", []):
            if volume.get("type") == "bind" and not relative(volume.get("source", "")):
                fail(f"Service {name} has an unsafe bind mount")
    for volume in config.get("volumes", {}).values():
        if volume and volume.get("driver_opts"):
            fail("Custom volume driver options are not allowed")
    if config.get("secrets") or config.get("configs"):
        fail("Compose file-backed secrets and configs are not supported")
    return files[0].name


def main():
    try:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            validate_archive(sys.argv[1], root)
            if len(sys.argv) > 2:
                if not re.fullmatch(r"[0-9a-f]{40}", sys.argv[2]):
                    fail("Invalid expected source commit")
                if (root / ".gce-deploy-source").read_text().strip() != sys.argv[2]:
                    fail("Artifact source commit does not match the workflow commit")
            compose_file = validate_compose(root)
            if os.environ.get("GITHUB_OUTPUT"):
                with open(os.environ["GITHUB_OUTPUT"], "a") as output:
                    output.write(f"compose_file={compose_file}\n")
    except (ValueError, OSError, tarfile.TarError, json.JSONDecodeError) as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1
    print("Deployment archive and Compose configuration validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
