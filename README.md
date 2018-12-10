# mecablr
MeCab

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