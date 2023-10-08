# 社内イントラwebアプリ

## 構築手順

1. DB作成
    コンテナ内に入り、以下実行

    ```
    python manage.py makemigrations
    python manage.py migrate
    ```

2. 初期必須データ登録
    ```
    python manage.py register_workstatus data/work_status.json
    ```
