import jwt
import datetime
import os

import Credentials

def create_jwt():
    # 設定値 DXG
    API_KEY_ID=Credentials.API_KEY_ID
    ISSUER_ID=Credentials.ISSUER_ID

    # `~` 以下にあるものは明けてくれない
    PRIVATE_KEY_PATH = os.path.expanduser(f'~/.appstoreconnect/private_keys/AuthKey_{API_KEY_ID}.p8')
    # 鍵の読み込み
    with open(PRIVATE_KEY_PATH, 'r') as f:
        private_key = f.read()

    # JWTの生成
    issued_at = datetime.datetime.now(datetime.timezone.utc)
    expiration_time = issued_at + datetime.timedelta(minutes=5)  # 5分以内に設定

    headers = {
        "alg": "ES256",
        "kid": API_KEY_ID,
        "typ": "JWT"
    }

    payload = {
        "iss": ISSUER_ID,
        "iat": int(issued_at.timestamp()),
        "exp": int(expiration_time.timestamp()),
        "aud": "appstoreconnect-v1"
    }

    # Debug出力
    print("=== JWT DEBUG INFO ===")
    print("iss:", payload["iss"])
    print("kid:", headers["kid"])
    print("iat:", payload["iat"])
    print("exp:", payload["exp"])
    print("aud:", payload["aud"])
    print("======================")

    # ES256アルゴリズムで署名
    token = jwt.encode(payload, private_key, algorithm="ES256", headers=headers)
    
    # 出力
    print(token)
    
    return token

create_jwt()