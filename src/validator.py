# clibrary.py
import sys

# validator에서 validate_date 함수를 추가로 불러옵니다!
from src.validator import check_environment, validate_date
from src.auth import login, register
from src.book import search_book, rent_book, return_book, view_book
from src.admin import add_book, delete_book, modify_book

def main():
    # 1. 환경 검사
    check_environment()
    
    # --------------------------------------------------
    # ★ 시스템 가상 날짜 설정 로직 추가
    # --------------------------------------------------
    print("\n" + "="*40)
    print("  시스템 가상 시간 설정")
    print("="*40)
    
    system_date = None
    while True:
        date_input = input("현재 날짜를 입력하세요 (YYYY-MM-DD) : ").strip()
        
        # 검증 모듈에 날짜 던져서 확인받기
        if validate_date(date_input):
            system_date = date_input
            print(f"✅ 시스템 날짜가 [{system_date}]로 설정되었습니다.")
            break # 통과하면 무한 루프 탈출
        else:
            print("!!! 오류: 날짜 형식이 맞지 않거나 존재하지 않는 날짜입니다. (예: 2026-04-08)")
            
    # 2. 세션 관리 (여기에 system_date도 함께 관리해 주면 아주 좋습니다)
    current_user = {
        "is_logged_in": False,
        "user_id": None,
        "role": None 
    }
    
    # 3. 메인 무한 루프
    while True:
        print("\n" + "="*40)
        
        # --------------------------------------------------
        # 상태 1: 로그인 전 (비회원 메뉴)
        # --------------------------------------------------
        if not current_user["is_logged_in"]:
            # 헤더에 설정된 날짜도 같이 보여주면 UX가 훨씬 좋아집니다.
            print(f"  CLi_brary 도서관 시스템 (현재: {system_date})") 
            print("="*40)
            print("원하는 동작에 해당하는 숫자를 입력하세요.")
            print("1. 로그인")
            print("2. 회원가입")
            print("3. 도서검색")
            print("0. 종료")
            
            choice = input("\n한 자리 숫자를 입력하세요: ").strip()
            
            if choice == "0":
                print("프로그램을 종료합니다.")
                sys.exit(0)
            elif choice == "1":
                login_result = login() 
                if login_result:
                    current_user["is_logged_in"] = True
                    current_user["user_id"] = login_result["id"]
                    current_user["role"] = login_result["role"]
            elif choice == "2":
                register()
            elif choice == "3":
                search_book()
            else:
                print("올바르지 않은 입력입니다.")

        # --------------------------------------------------
        # 상태 2: 일반 사용자 (학생) 메뉴
        # --------------------------------------------------
        elif current_user["role"] == '0':
            print(f"  [{current_user['user_id']}] 님 접속 중 (현재: {system_date})")
            print("="*40)
            print("원하는 동작에 해당하는 숫자를 입력하세요.")
            print("1. 도서대출")
            print("2. 도서반납")
            print("3. 도서검색")
            print("4. 대출현황")
            print("0. 종료")
            
            choice = input(f"\n[{current_user['user_id']}] 한 자리 숫자를 입력하세요: ").strip()
            
            if choice == "0":
                print("로그아웃 후 프로그램을 종료합니다.")
                sys.exit(0)
            elif choice == "1":
                # 나중에 대출 기능 구현할 때 현재 날짜를 같이 넘겨줘야 합니다.
                rent_book() 
            elif choice == "2":
                return_book()
            elif choice == "3":
                search_book()
            elif choice == "4":
                view_book()
            else:
                print("올바르지 않은 입력입니다.")

        # --------------------------------------------------
        # 상태 3: 관리자 (Admin) 메뉴
        # --------------------------------------------------
        elif current_user["role"] == '1':
            print(f"  [관리자 모드] 접속 중 (현재: {system_date})")
            print("="*40)
            print("원하는 동작에 해당하는 숫자를 입력하세요.")
            print("1. 도서추가")
            print("2. 도서삭제")
            print("3. 사용자조회")
            print("4. 대출현황조회")
            print("0. 종료")
            
            choice = input("\n[ADMIN] 한 자리 숫자를 입력하세요: ").strip()
            
            if choice == "0":
                print("로그아웃 후 프로그램을 종료합니다.")
                sys.exit(0)
            elif choice == "1":
                add_book()
            elif choice == "2":
                delete_book()
            elif choice == "3":
                print("🛠️ [시스템] '사용자조회' 기능은 현재 구현 중입니다.")
            elif choice == "4":
                print("🛠️ [시스템] '전체 대출현황조회' 기능은 현재 구현 중입니다.")
            else:
                print("올바르지 않은 입력입니다.")

if __name__ == "__main__":
    main()