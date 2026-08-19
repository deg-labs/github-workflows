# github-workflows

deg-labs リポジトリ向けの再利用可能な GitHub Actions ワークフローです。

`gce-deploy.yml` は Workload Identity Federation で認証し、必要に応じて非本番環境の GCE インスタンスを起動します。その後、SSH 接続の準備が整うまで待機し、アプリケーションのアーカイブをアップロードして、呼び出し元から渡されたデプロイコマンドを実行します。

呼び出されたジョブは、必須の `environment_name` 入力に基づいて、呼び出し元リポジトリの GitHub Environment を選択します。環境ごとのデプロイ値は、環境プレフィックスを付けたリポジトリまたは Organization Secret として保存します。

```text
DEV_GCE_INSTANCE_NAME / STG_GCE_INSTANCE_NAME / PRD_GCE_INSTANCE_NAME
DEV_GCE_ZONE          / STG_GCE_ZONE          / PRD_GCE_ZONE
DEV_GCP_SA_EMAIL      / STG_GCP_SA_EMAIL      / PRD_GCP_SA_EMAIL
DEV_GCP_WIF_PROVIDER  / STG_GCP_WIF_PROVIDER  / PRD_GCP_WIF_PROVIDER
```

`ORG_GH_APP_ID` と `ORG_GH_APP_PRIVATE_KEY` は、引き続きリポジトリまたは Organization Secret として使用します。呼び出し元は環境を選択し、アプリケーション固有のデプロイコマンドを渡します。環境ごとの GCP Secret 名を渡す必要はありません。既存の `PROD_*` 名は、本番環境向けの互換性フォールバックとして利用できます。

`dev`、`stg`、`prd` の Environment は、引き続きデプロイの保護とステータス管理に使用します。Secret 名を共通化するためのものではありません。

アプリケーション固有の値は、呼び出し元が管理します。呼び出し元の `prepare_command` で値が必要な場合は、`app_env_secret`、`discord_webhook_secret`、`addresses_secret` のいずれかの任意入力を使って、呼び出し元の Secret 名を渡します。共有ワークフローは選択された値を `prepare_command` に公開するだけで、アプリケーション固有の `DEV_*`、`STG_*`、`PRD_*` Secret 名は定義しません。
