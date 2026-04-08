# src/auth.py

# src/auth.py

def login() -> dict | bool:
    """
    [1차 구현용 로그인] 
    - 텍스트 파일 연동 없이 아이디(ID)의 형태로만 권한을 구분합니다.
    - 'admin' 입력 시 -> 관리자(1)
    - 9자리 숫자 입력 시 -> 학생(0)
    """
    print("\n--------------------------------------------------")
    print("[시스템] 로그인 메뉴로 진입했습니다.")
    print("--------------------------------------------------")
    
    user_id = input("학번(또는 admin)을 입력하세요: ").strip()
    password = input("비밀번호를 입력하세요: ").strip()
    
    # 1. 관리자 구분 로직
    if user_id == "admin":
        if password == "admin": # 임시 비밀번호
            print("👑 관리자 계정으로 로그인 성공!")
            return {"id": user_id, "role": "1"}
        else:
            print("!!! 오류: 비밀번호가 일치하지 않습니다.")
            return False
            
    # 2. 일반 학생 구분 로직 (9자리 숫자)
    elif len(user_id) == 9 and user_id.isdigit():
        # 1차 테스트이므로 9자리 숫자를 치면 무조건 해당 학번으로 로그인 성공 처리
        print(f"👤 {user_id} 학생으로 로그인 성공!")
        return {"id": user_id, "role": "0"}
        
    # 3. 규격에 맞지 않는 아이디를 친 경우
    else:
        print("!!! 오류: 아이디 형식이 올바르지 않습니다. (학번 9자리 또는 admin)")
        return False


def register() -> bool:
    """회원가입 정보 입력 및 users.txt에 새 레코드 생성"""
    print("\n--------------------------------------------------")
    print("🛠️ [시스템] '회원가입' 기능은 현재 구현 중입니다.")
    print("--------------------------------------------------")
    return True



def register() -> bool:
    """회원가입 정보 입력 및 users.txt에 새 레코드 생성"""
    print("\n--------------------------------------------------")
    print("🛠️ [시스템] '회원가입(users.txt에 생성)' 기능은 현재 구현 중입니다.")
    print("--------------------------------------------------")
    return True