# mecablr
MeCab

## index
- [requirements](#requirements)
- [usage](#usage)
- [with-docker-compose](#with-docker-compose)
- [[Appendix] Alpine Linux](#alpine-linux)

## requirements
- Docker

## usage
### setup
```shell
# リポジトリのダウンロード
$ git clone git@github.com:moriaki3193/mecablr.git
$ cd mecablr

# イメージのビルド
$ docker build -t mecablr .

# コンテナの起動
$ docker run -p 3193:5000 --name mecablr --rm -d mecablr

# コンテナの停止
$ docker stop mecablr

# コンテナへのログイン
$ docker exec -it mecablr sh  # /mecablr ディレクトリへ
```

### request
リクエストの方法は2通り存在します。
いずれもレスポンスの形式はJSONです。

```shell
# GETを利用する方法
$ curl "127.0.0.1:3193/?sentence=Pythonの勉強"

# POSTを利用する方法
# クエリパラメータとして渡すには長すぎる文章を解析したい場合に利用
$ curl "127.0.0.1:3193" \
    -H 'Content-Type:application/json' \
    -d '{"sentence": "Pythonの勉強"}'
```

### response
上記の例を利用して説明します。

```json
{
    "sentence": "Pythonの勉強",
    "result": [
        {"Surface": "Python", "PoS": "名詞", "PoS1": "固有名詞", "PoS2": "一般", "PoS3": "*", "VerbConjugation": "*", "Original": "*", "Reading": "Python", "Pronunciation": "パイソン"},
        {"Surface": "の", "PoS": "助詞", "PoS1": "連体化", "PoS2": "*", "PoS3": "*", "VerbConjugation": "*", "Original": "*", "Reading": "の", "Pronunciation": "ノ"},
        {"Surface": "勉強", "PoS": "名詞", "PoS1": "サ変接続", "PoS2": "*", "PoS3": "*", "VerbConjugation": "*", "Original": "*", "Reading": "勉強", "Pronunciation": "ベンキョウ"}
    ]
}
```

## with docker-compose
このイメージはstand-aloneで実行されるため、docker-composeを利用して他のサービスと簡単連携できます。
以下は、docker-composeを利用してサービスを組み合わせる場合の一例です。

### example
#### ディレクトリ構成
```
- proj-root
    + containers
        + mecablr         # step.1
        + yourapp         # step.2
        + proxy           # step.3
            + Dockerfile
            + nginx.conf
            + log
    + docker-compose.yml  # step.4
```

#### step.1
`proj-root/containers`で以下のコマンドを実行し、mecablrをクローンします。

```shell
$ git clone git@github.com:moriaki3193/mecablr.git
```

#### step.2
`proj-root/containers`にあなたの作成するWebアプリケーションを設置する。
ここにはアプリケーションそのものを置いても良いですし、イメージの定義のみをDockerfileで行い、他のプロジェクトディレクトリにおいてアプリケーションの中身を書いても良いです。
作成するアプリケーションの規模に応じて選択してください。

#### step.3
アプリケーションの利用者がmecablrとあなたのアプリケーションを意識しなくて済むように、リバースプロキシを設定します。
`Dockerfile`と`nginx.conf`をそれぞれ次のように設定してみましょう。

##### Dockerfile
```dockerfile
FROM nginx

CMD [ "nginx", "-g", "daemon off;", "-c", "/etc/nginx/nginx.conf" ]
```

##### nginx.conf
```conf
user nginx;
worker_processes auto;

error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" $request_time (ms)';

    access_log /var/log/nginx/access.log main;

    # Define the parameters to optimize the delivery of static content.
    sendfile on;
    # tcp_nopush on;
    # tcp_nodelay on;

    keepalive_timeout 65;

    # upstream context
    # ROLE
    #     バックエンドのアプリケーションサーバを示し
    #     serverディレクティブの記述をまとめたものに名前を付与する
    # FORMAT
    #     upstream <backend_server_name> {
    #         server <host_ip>:<port_number>;
    #     }
    upstream uwsgi {
        server yourapp:3031;
    }

    upstream mecablr {
        server mecablr:3032;
    }

    # server directive
    # ROLE
    #     外部からのアクセス方法を示す
    #     リバースプロキシを指定する場合はproxy_passディレクティブで
    #     転送先のupstreamの名前を指定する
    server {
        listen 80;
        charset utf-8;

        location / {
            include uwsgi_params;
            uwsgi_pass uwsgi;  # `uwsgi` upstream コンテキストを参照する
        }

        location /macablr {
            include uwsgi_params;
            uwsgi_pass mecablr;
        }

        location = /favicon.ico {
            empty_gif;
        }
    }
}
```

#### step.4
最後に複数のコンテナをまとめるための`docker-compose.yml`を作成すれば完成です。

```yaml
version: "3"

services:

  yourapp:
    container_name: yourapp
    build:
      context: .
      dockerfile: containers/yourapp/Dockerfile
    expose:
      - "3031"
    # !!! その他の設定はアプリケーションに応じて行なってください !!!

  mecab:
    container_name: mecablr
    build:
      context: ./containers/mecablr
    expose:
      - "3032"
    environment:
      TZ: "Asia/Tokyo"

  proxy:
    container_name: proxy
    build:
      context: .
      dockerfile: containers/proxy/Dockerfile
    volumes:
      - ./containers/proxy/nginx.conf:/etc/nginx/nginx.conf
      - ./containers/proxy/log/nginx:/var/log/nginx
    links:
      - yourapp
      - mecablr
    ports:
      - "3193:80"  # Host:Container
    environment:
      TZ: "Asia/Tokyo"
```

プロジェクトルートに移動し、`docker-compose up -d`などのコマンドを実行してサービスを起動してみましょう。

## Alpine Linux
今回作成するMeCabのサービスは、Alpine Linuxという名称の軽量化されたOSイメージの上に構築されます。
MeCabや関連するパッケージのサイズは大変大きいため、せめてOSのサイズだけでも小さくて済むようにという思いからこのOSを採用しました。
ここにAlpine Linuxを利用する上での簡単なチュートリアルをまとめます。

### apk
Alpine LinuxはRAM上で動作することを想定して作成されているため、パッケージ管理は次の2つの段階から成り立ちます。
- パッケージのインストール・アップグレード・削除をシステム上で行う
- 以前に設定された状態に基づいてシステムをリストアします。これまでにインストールされたパッケージやローカルで修正された設定ファイルが含まれます。

**apk**は実行されているシステムからソフトウェアをインストール・更新・削除するためのツールです。
また、**lbu**はコレまでに設定された状態へとシステムを復元する為に必要なデータを把握するためのツールです。

#### overview
**apk**は次のアプレットを持つツールです。

- add: 新しいパッケージを追加する
- del: パッケージを削除する
- fix: インストールされたパッケージを修復ないし更新しようとする
- update: 利用可能なパッケージのインデックスを更新する
- info: インストールされた・利用可能なパッケージの情報を表示する
- search: パッケージを検索する
- upgrade: 現在インストールされているパッケージを更新する
- cache: ローカルにキャッシュされたリポジトリの管理を行う
- version: インストールされているパッケージのバージョンと利用可能なものとの差分を比較する
- index: パッケージのリストからリポジトリのインデックスを作成する
- fetch: パッケージをダウンロードする（ただしインストールはしない）
- audit: パッケージの最初期の状態からのファイルシステムに対する変更を表示する
- verify: パッケージの署名を有効にする
- dot: `graphvis`グラフをパッケージについて作成する
- policy: パッケージを更新・追加するリポジトリについて表示する
- stats: インストールされた・利用可能なパッケージの総数やディレクトリ・ファイル数を含めた統計情報を表示する
- manifest: パッケージに含まれるファイルのチェックサムを表示する

### ash
Linux系OSではshellとしてbashが採用されているケースがほとんどですが、Alpine Linuxについては軽量化の為にベースイメージであるBusyBoxに含まれている**ash**をログインシェルとしています。
それに伴ってshebangが`#!/bin/sh`となったり、Dockerを対話的に起動する際には`sh`を指定しなければならないといった変更点が生まれます。
また、環境変数を設定するrcファイルは`.bash_profile`ではなく`~/.profile`となることにも注意が必要です。

#### memo
- **apk**は`a-pack`と呼ばれることもある
    - つまり「エイパック」となる

#### references
- [Alpine Linux Wiki](https://wiki.alpinelinux.org/wiki/Alpine_Linux_package_management)
- [Alpine Linux ash](https://unicorn.limited/jp/item/1035)