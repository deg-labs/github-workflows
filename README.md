# github-workflows

deg-labs リポジトリ向けの再利用可能な GitHub Actions ワークフローです。

`gce-deploy.yml` は `compose` または `package-update` を実行します。Compose の呼び出し元は、Secret と Git の管理ファイルを除外した `deploy.tar.gz` を同じワークフロー実行内で成果物としてアップロードし、その成果物 ID を渡します。`.env` 系の名前を持つファイルは作成時に除外し、アップロード前にも確認します。名前の検査だけでは、別名のファイルやソースコード中に含まれる Secret を検出できないため、呼び出し元で成果物の内容を管理してください。準備ジョブに GCP 認証情報や本番 Secret を渡さないでください。

共有ワークフローは、権限を限定した検証ジョブでアーカイブと Compose の設定を検査します。絶対パス、親ディレクトリへの移動、リンク、特殊ファイル、`.env` と `.git`、特権コンテナ、ホスト名前空間、危険なバインドマウントなどを拒否します。成果物に記録された対象コミットを照合し、アーカイブの SHA-256 を配置前に再確認します。コミット情報は作成ジョブの自己申告であり、成果物内容の署名や安全性を保証しません。アプリ固有の除外対象は、呼び出し元が `.gce-deployignore` で指定します。

実行時設定は `runtime_env_secret` で dotenv の Secret 名を指定します。Secret が単一値の場合は `runtime_env_key` に環境変数名を指定します。必要に応じて `runtime_file_secret` と `runtime_file_name` で設定ファイルを１個渡せます。これらの値は成果物に含めず、デプロイ時に送信します。`DEPLOY_ENV` は自動設定します。

環境別の GCE 接続情報は `DEV_*`、`STG_*`、`PRD_*` の `GCE_INSTANCE_NAME`、`GCE_ZONE`、`GCP_SA_EMAIL`、`GCP_WIF_PROVIDER` Secret を使用します。`ORG_GH_APP_ID` と `ORG_GH_APP_PRIVATE_KEY` はデプロイチームの認可に使用します。

`package-update` は APT 更新後に再起動を予約します。任意のコマンドは受け付けません。Compose 設定の検査はすべての危険を排除するものではありません。アプリとイメージのレビュー、GCP 側の権限分離と WIF の制限も必要です。
