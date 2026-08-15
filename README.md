# github-workflows

Reusable GitHub Actions workflows for deg-labs repositories.

`gce-deploy.yml` authenticates with Workload Identity Federation, starts non-production GCE instances when necessary, waits for SSH readiness, uploads an application archive, and runs the caller-provided deployment command.

The called job selects the caller repository's GitHub Environment from the required `environment_name` input. Environment-specific deployment values are stored as repository or organization secrets with an environment prefix:

```text
DEV_GCE_INSTANCE_NAME / STG_GCE_INSTANCE_NAME / PRD_GCE_INSTANCE_NAME
DEV_GCE_ZONE          / STG_GCE_ZONE          / PRD_GCE_ZONE
DEV_GCP_SA_EMAIL      / STG_GCP_SA_EMAIL      / PRD_GCP_SA_EMAIL
DEV_GCP_WIF_PROVIDER  / STG_GCP_WIF_PROVIDER  / PRD_GCP_WIF_PROVIDER
DEV_APP_ENV            / STG_APP_ENV            / PRD_APP_ENV
DEV_DISCORD_WEBHOOK_URL / STG_DISCORD_WEBHOOK_URL / PRD_DISCORD_WEBHOOK_URL
DEV_ADDRESSES_TXT      / STG_ADDRESSES_TXT      / PRD_ADDRESSES_TXT
```

`ORG_GH_APP_ID` and `ORG_GH_APP_PRIVATE_KEY` remain repository or organization secrets. Callers only select the environment and provide application-specific deployment commands; they do not pass environment-specific secret names. Existing `PROD_*` names are accepted as a production compatibility fallback.

The `dev`, `stg`, and `prd` Environment is still used for deployment protection and status; it is not used to make the secret names common.
