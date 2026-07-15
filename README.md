# github-workflows

Reusable GitHub Actions workflows for deg-labs repositories.

`gce-deploy.yml` authenticates with Workload Identity Federation, starts non-production GCE instances when necessary, waits for SSH readiness, uploads an application archive, and runs the caller-provided deployment command.
