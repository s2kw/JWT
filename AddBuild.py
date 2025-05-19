
import requests
from CreateJWT import create_jwt  # 事前に用意したJWT作成関数を使う

# ----------------------
# 設定
# ----------------------
GROUP_NAME = "管理部"                    # ← 割り当てたいBeta Group名

# ----------------------
# JWT生成
# ----------------------
token = create_jwt()
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# ----------------------
# ヘルパー関数
# ----------------------
def get_app_id(bundle_id):
    r = requests.get(
        f"https://api.appstoreconnect.apple.com/v1/apps?filter[bundleId]={bundle_id}",
        headers=headers
    )
    r.raise_for_status()
    return r.json()["data"][0]["id"]

def get_beta_group_id(app_id, group_name):
    r = requests.get(
        f"https://api.appstoreconnect.apple.com/v1/apps/{app_id}/betaGroups",
        headers=headers
    )
    r.raise_for_status()
    for g in r.json()["data"]:
        if g["attributes"]["name"] == group_name:
            return g["id"]
    raise Exception(f"Beta group '{group_name}' not found")

def get_latest_build_id(app_id):
    r = requests.get(
        f"https://api.appstoreconnect.apple.com/v1/builds?filter[app]={app_id}&sort=-uploadedDate&limit=1",
        headers=headers
    )
    r.raise_for_status()
    builds = r.json().get("data", [])
    if not builds:
        raise Exception("No builds found for app")
    return builds[0]["id"]

def assign_build_to_group(build_id, group_id):
    r = requests.post(
        f"https://api.appstoreconnect.apple.com/v1/betaGroups/{group_id}/relationships/builds",
        headers=headers,
        json={
            "data": [
                {
                    "type": "builds",
                    "id": build_id
                }
            ]
        }
    )
    if r.status_code == 204:
        print("✅ Build assigned successfully.")
    elif r.status_code == 409:
        print("⚠️ Build is already assigned to this group.")
    else:
        print(f"❌ Error assigning build: {r.status_code}")
        print(r.text)
        r.raise_for_status()

# ----------------------
# 実行処理
# ----------------------
if __name__ == "__main__":
    with open("bundle_ids.txt") as bf:
        bundle_ids = [line.strip() for line in bf if line.strip()]

    for bundle_id in bundle_ids:
        print(f"\n--- Processing Bundle ID: {bundle_id} ---")
        try:
            app_id = get_app_id(bundle_id)
            group_id = get_beta_group_id(app_id, GROUP_NAME)
            build_id = get_latest_build_id(app_id)

            print(f"App ID    : {app_id}")
            print(f"Group ID  : {group_id}")
            print(f"Build ID  : {build_id}")

            print("🚀 Assigning build to group...")
            assign_build_to_group(build_id, group_id)
        except Exception as e:
            print(f"❌ Error processing {bundle_id}: {e}")