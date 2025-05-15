# JWT
AppleアカウントのJWT生成手順と、関連してAppStoreConnectAPIで色々やるスクリプト。


### ローカルで実行するためのコピペ用

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python CreateJTW.py
deactivate
```

## Credentials.pyの存在
重要な情報はCredentials.pyで定義しコミット対象から外す運用をする。
そのため、CreateJWT.pyだけではISSUER_IDなどが未定義のためエラーが出る。
Credentials.pyを作成し自信で取得したISSUER＿IDやAPI_KEYを定義して運用すること。


## JWT生成
CreateJTW.py を実行してprintされたハッシュ文字列を取得する。
expireの期限を発行から5分後に設定しないと動作しない。

### apiKey と issuer と秘密鍵の取得

|**項目**|**用途**|**取得場所**|
|---|---|---|
|API キーID（apiKey）|キー識別子（例：2M3W47ABC1）|App Store Connect|
|Issuer ID（apiIssuer）|組織固有の ID（例：57246542-96fe-1a63-e053-0824d011072a）|App Store Connect|
|秘密鍵ファイル（AuthKey_XXXX.p8）|認証用の秘密鍵|ダウンロードしてローカル保存|

1. Apple Developer アカウントにログイン
	•	https://appstoreconnect.apple.com/
	•	アカウント権限：Admin または App Manager 以上が必要
2. サイドメニュー「ユーザとアクセス」をクリック（英語の場合は “Users and Access”）
3. 「API キー（API Keys）」タブを開く
4. 「＋キーを生成」をクリック
	•	キー名：任意（例：UploadCIKey）
	•	アクセス範囲：基本的には App Manager または Developer
5. キーを作成後、以下を取得・保存

|**項目**|**保存先**|
|---|---|
|API キーID（Key ID）|メモ帳などに控える（例：2M3W47ABC1）|
|Issuer ID（発行者 ID）|表示されるのでメモしておく|
|秘密鍵（.p8 ファイル）|**一度だけ DL 可能**。~/.appstoreconnect/private_keys/ に保存推奨|

※ .p8 はデフォルトパス（~/.appstoreconnect/private_keys/）に置いておけば自動的に読み込まれる。ファイル名を変更すると読み込まれないかもしれないので注意。ファイル名 = APIキー名。


## AddTester
AppStoreConnect経由で手動でやらなければならなかったテスターの追加を自動で行う。

必要なデータは下記2点で詳細は後述
- bundle_ids.txt
- emails.txt

### bundle_ids.txt

bundleIDを下記のように1行1つで列記する。

```txt
jp.jigax.workingmem
jp.jigax.anyappName
com.apple.myapp
```

### emails.txt
追加したいテスターのメールアドレスを列記する。

```txt
slownin9232@gmail.com
k-sasakawa@dxg.jp
```


