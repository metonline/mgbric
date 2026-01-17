#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Secrets'ına Fly.io token'ı ekle
"""

import subprocess

GITHUB_REPO = "metonline/hosgoru-pwa"
GITHUB_ACTIONS_SECRET_NAME = "FLY_API_TOKEN"

# Token - bunu parametreden al
fly_token = "FlyV1 fm2_lJPECAAAAAAAENxVxBBlLtxIDIc0v/OSiaCL4ky/wrVodHRwczovL2FwaS5mbHkuaW8vdjGWAJLOABXWIx8Lk7lodHRwczovL2FwaS5mbHkuaW8vYWFhL3YxxDzTNWYVtHqeRnVrPXyOZnPIRzytpeH3aFacGo+jGAqi71j7e3HaasfgXGGjYafr7XbbxkHvIMalelqjouXETt8QKhv4UPXMT8dK9WCwc3FIuLPYTf/5wfizUMQBHPU9zH7y9ahx+aUBMISK0VIiebmnsRqmdIYsluMNAJR4qfQ9SzAL0eR2OrrNhX+Lnw2SlAORgc4AxMsRHwWRgqdidWlsZGVyH6J3Zx8BxCC3JdmCWkw0jqgPvtzSbiP3N8L1P5uMRUuY1c9LU05v1Q==,fm2_lJPETt8QKhv4UPXMT8dK9WCwc3FIuLPYTf/5wfizUMQBHPU9zH7y9ahx+aUBMISK0VIiebmnsRqmdIYsluMNAJR4qfQ9SzAL0eR2OrrNhX+Ln8QQ6WXbmgp8ptA9bqE65F3YtcO5aHR0cHM6Ly9hcGkuZmx5LmlvL2FhYS92MZgEks5panubzmtLrzkXzgAU9zcKkc4AFPc3DMQQffEXBOpy8dSFLn2Gan0ZRsQgZdFDVgkEhRwvEP8vkHTNLWc5V1Pv3s43Bl9jis+dQyw="

print("="*70)
print("📝 GITHUB SECRETS'A FLY.IO TOKEN EKLEME")
print("="*70 + "\n")

print(f"🔐 Token: {fly_token[:50]}...")
print(f"📦 Repo: {GITHUB_REPO}")
print(f"🔑 Secret name: {GITHUB_ACTIONS_SECRET_NAME}\n")

# GitHub CLI ile secret ekle
try:
    print("📤 GitHub'a gönderiliyor...")
    result = subprocess.run(
        [
            'gh', 'secret', 'set', GITHUB_ACTIONS_SECRET_NAME,
            '-b', fly_token,
            '-R', GITHUB_REPO
        ],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode == 0:
        print("✅ GitHub Secrets'a eklendi!")
        print("\n" + "="*70)
        print("✅ KURULUM BAŞARILI!")
        print("="*70)
        print("\n✅ Artık GitHub Actions otomatik olarak Fly.io'ya deploy edebilir")
        print("✅ Token 1 yıl boyunca geçerli\n")
    else:
        print(f"❌ Hata: {result.stderr}")
        print("\n⚠️  Manüel olarak GitHub'a ekle:")
        print(f"   1. https://github.com/{GITHUB_REPO}/settings/secrets/actions")
        print(f"   2. New repository secret")
        print(f"   3. Name: {GITHUB_ACTIONS_SECRET_NAME}")
        print(f"   4. Value: {fly_token[:50]}...")
        
except Exception as e:
    print(f"❌ Hata: {e}")
    print("\n⚠️  Manüel olarak GitHub'a ekle:")
    print(f"   1. https://github.com/{GITHUB_REPO}/settings/secrets/actions")
    print(f"   2. New repository secret")
    print(f"   3. Name: {GITHUB_ACTIONS_SECRET_NAME}")
    print(f"   4. Value: {fly_token}")
