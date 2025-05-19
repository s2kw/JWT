import requests
import jwt
import datetime
import os
from CreateJWT import create_jwt

# 1. JWT取得
token = create_jwt()

api_headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

GROUP_NAME = "管理部"

# 2. アシスタント関数

def get_app_id(bundle_id):
    url = f"https://api.appstoreconnect.apple.com/v1/apps?filter[bundleId]={bundle_id}"
    print(f"[DEBUG] Requesting: {url}")
    r = requests.get(url, headers=api_headers)
    print(f"[DEBUG] Response: {r.status_code}")
    print(f"[DEBUG] Body: {r.text}")
    r.raise_for_status()
    data = r.json().get("data", [])
    return data[0]["id"] if data else None

def get_beta_group_id(app_id):
    r = requests.get(f"https://api.appstoreconnect.apple.com/v1/apps/{app_id}/betaGroups", headers=api_headers)
    r.raise_for_status()
    data = r.json().get("data", [])
    return data[0]["id"] if data else None

def get_or_create_beta_tester(email):
    # 存在チェック
    r = requests.get(f"https://api.appstoreconnect.apple.com/v1/betaTesters?filter[email]={email}", headers=api_headers)
    r.raise_for_status()
    data = r.json().get("data", [])
    if data:
        return data[0]["id"]
    # 存在しなければ作成（注意：成功するにはApple IDに紐づいたアカウントである必要がある）
    print(f"[Info] Creating beta tester for {email}")
    r = requests.post(
        "https://api.appstoreconnect.apple.com/v1/betaTesters",
        headers=api_headers,
        json={
            "data": {
                "type": "betaTesters",
                "attributes": {
                    "email": email
                }
            }
        }
    )
    r.raise_for_status()
    return r.json()["data"]["id"]

def get_or_create_beta_group_id(app_id):
    # Step 1: Get existing groups
    r = requests.get(f"https://api.appstoreconnect.apple.com/v1/apps/{app_id}/betaGroups", headers=api_headers)
    r.raise_for_status()
    groups = r.json().get("data", [])
    
    for group in groups:
        if group["attributes"]["name"] == GROUP_NAME:
            return group["id"]
    
    # Step 2: Create named group
    print(f"[INFO] Creating beta group '{GROUP_NAME}' for app {app_id}")
    r = requests.post("https://api.appstoreconnect.apple.com/v1/betaGroups",
        headers=api_headers,
        json={
            "data": {
                "type": "betaGroups",
                "attributes": {
                    "name": GROUP_NAME,
                    "isInternalGroup": True
                },
                "relationships": {
                    "app": {
                        "data": {
                            "type": "apps",
                            "id": app_id
                        }
                    }
                }
            }
        }
    )
    r.raise_for_status()
    return r.json()["data"]["id"]

def add_tester_to_group(beta_tester_id, beta_group_id):
    url = f"https://api.appstoreconnect.apple.com/v1/betaGroups/{beta_group_id}/relationships/betaTesters"
    r = requests.post(
        url,
        headers=api_headers,
        json={
            "data": [
                {
                    "type": "betaTesters",
                    "id": beta_tester_id
                }
            ]
        }
    )
    if r.status_code == 409:
        print("[Skip] Already in group")
    else:
        r.raise_for_status()

# 3. メイン処理

with open("emails.txt") as ef:
    emails = [line.strip() for line in ef if line.strip()]

with open("bundle_ids.txt") as bf:
    bundle_ids = [line.strip() for line in bf if line.strip()]

for bundle_id in bundle_ids:
    # スキップ文字列を含む場合は次へ
    if '#'in bundle_id:
        continue
    print(f"--- Processing app: {bundle_id} ---")
    app_id = get_app_id(bundle_id)
    if not app_id:
        print(f"[Error] App not found for bundle ID {bundle_id}")
        continue
    beta_group_id = get_or_create_beta_group_id(app_id)
    if not beta_group_id:
        print(f"[Error] No beta group found for app {bundle_id}")
        continue

    for email in emails:
        try:
            print(f"→ Adding {email} to app {bundle_id}")
            beta_tester_id = get_or_create_beta_tester(email)
            add_tester_to_group(beta_tester_id, beta_group_id)
            print("✓ Done")
        except Exception as e:
            print(f"[Error] Failed to add {email}: {e}")