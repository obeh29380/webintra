# 社内イントラwebアプリ

## 構築手順

- 以下コマンドでコンテナを起動する。
    ```
    docker compose up -d
    ```

- 勤怠区分を登録する
    コンテナ内で以下を実行する
    ```
    cd /code
    python manage.py register_workstatus data/work_status.json
    ```
    or ホスト側で実行するなら以下
    ```
    docker compose exec app python /code/manage.py register_workstatus /code/data/work_status.json
    ```
