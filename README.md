# github-workflows

Reusable GitHub Actions workflows for deg-labs repositories.

`gce-deploy.yml` authenticates with Workload Identity Federation, starts non-production GCE instances when necessary, waits for SSH readiness, uploads an application archive, and runs the caller-provided deployment command.

## 呼び出し時の参照(SHA 固定)

再利用ワークフローは `@main` / `@master` のような未ピン参照で呼び出さないでください。
共有リポジトリが侵害された場合に波及するため、必ずコミット SHA で参照を固定します。

```yaml
jobs:
  deploy:
    uses: deg-labs/github-workflows/.github/workflows/gce-deploy.yml@f18c392dc03da19be1f7005dd4ce295d8e4a8fc6
    secrets: inherit
    with:
      ...
```

セキュリティ修正を取り込むときは、修正を含むコミットの SHA に参照を更新してください。

### 注意: dependabot-auto-merge.yml は削除済み

以前は `dependabot-auto-merge.yml`(Dependabot 自動マージ用の再利用ワークフロー)を公開していましたが、
`f18c392` で削除済みです。呼び出し元リポジトリの
`deg-labs/github-workflows/.github/workflows/dependabot-auto-merge.yml@...` 参照は削除してください。
