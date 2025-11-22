"""
사용자 생성 테스트 스크립트
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_create_user():
    """사용자 생성 테스트"""
    print("=" * 60)
    print("🧪 사용자 생성 테스트")
    print("=" * 60)
    
    user_data = {
        "email": "jiankimr@example.com",
        "name": "jian",
        "password": "jian"
    }
    
    print(f"\n📤 요청 데이터:")
    print(json.dumps(user_data, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/users/",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📥 응답 상태: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ 성공!")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        elif response.status_code == 400:
            print("⚠️ 이미 존재하는 이메일")
            print(response.json())
        else:
            print(f"❌ 에러 발생 ({response.status_code})")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 요청 실패: {e}")

def test_get_users():
    """사용자 목록 조회"""
    print("\n" + "=" * 60)
    print("📋 사용자 목록 조회")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/users/")
        print(f"응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ 사용자 {len(users)}명 조회 성공")
            for user in users:
                print(f"  - {user['name']} ({user['email']})")
        else:
            print(f"❌ 에러: {response.text}")
            
    except Exception as e:
        print(f"❌ 요청 실패: {e}")

def test_health():
    """헬스 체크"""
    print("\n" + "=" * 60)
    print("🏥 헬스 체크")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"응답: {response.json()}")
        
        if response.json().get("status") == "healthy":
            print("✅ 서버 정상")
        else:
            print("⚠️ 서버 문제 있음")
            
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")

if __name__ == "__main__":
    # 순서대로 테스트
    test_health()
    test_create_user()
    test_get_users()
    
    print("\n" + "=" * 60)
    print("✅ 모든 테스트 완료!")
    print("=" * 60)

