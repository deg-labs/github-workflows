# github-workflows

Reusable GitHub Actions workflows for deg-labs repositories.

`gce-deploy.yml` authenticates with Workload Identity Federation, starts non-production GCE instances when necessary, waits for SSH readiness, uploads an application archive, and runs the caller-provided deployment command.

The called job selects the caller repository's GitHub Environment from the required `environment_name` input. Each deployment repository should define `dev`, `stg`, and `prd` Environments as applicable, using the same secret names in each Environment:

```text
GCE_INSTANCE_NAME
GCE_ZONE
GCP_SA_EMAIL
GCP_WIF_PROVIDER
APP_ENV                 # applications that need it
DISCORD_WEBHOOK_URL     # applications that need it
ADDRESSES_TXT           # applications that need it
```

`ORG_GH_APP_ID` and `ORG_GH_APP_PRIVATE_KEY` remain repository or organization secrets. Callers only select the environment and provide application-specific deployment commands; they do not pass environment-specific secret names.

The values are environment-specific even though the new secret names are identical. For example, `dev/GCP_WIF_PROVIDER`, `stg/GCP_WIF_PROVIDER`, and `prd/GCP_WIF_PROVIDER` may all contain different providers. During migration, the workflow falls back to the legacy `DEV_*`, `STG_*`, `PRD_*`, and `PROD_*` repository secrets when the corresponding Environment secret is not present.
