# Azure OpenAI RAG pattern dev template

## Function App へ Deploy 時に事前にやっておくべきこと

### 環境変数 (local.settings.json) の upload

コマンドパレットから実行可能: Function: Upload Local Settings...

![image](https://github.com/user-attachments/assets/cb17bb51-79b5-4bcf-87e9-b325a4f5203d)




### 環境変数のセット

- `SCM_DO_BUILD_DURING_DEPLOYMENT: true`
- `ENABLE_ORYX_BUILD: true`
- `PYTHON_ISOLATE_WORKER_DEPENDENCIES: 1`



## Prep

以下の `Deploy to Azure` のボタンを `CTRL` キー (Mac の場合 `CMD`) を押しながらクリックすることで、別タブで Azure portal に遷移してカスタムデプロイの画面が開き、以下のリソースの一括作成ができます。

- Cosmos DB for NoSQL (`Vector Search for NoSQL API (preview)` の有効化)
- Azure Functions (Consumption Plan/Python)


<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fstyokosandbox.blob.core.windows.net%2Farm-templates%2Faoai-workshop-cosmos-template.json" target="_blank" rel="noopener noreferrer"><img src="https://aka.ms/deploytoazurebutton" alt="Deploy to Azure"></a>

