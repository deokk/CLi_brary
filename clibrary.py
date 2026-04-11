# clibrary.py
import sys

# validator에서 validate_date 함수를 추가로 불러옵니다!
from src.validator import (
    check_environment,
    get_saved_system_time_str,
    save_system_time,
    validate_date,
    validate_date_not_past,
)
from src.auth import login, register
from src.book import search_book, rent_book, return_book, view_book
from src.admin import add_book, delete_book, edit_book, view_users

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
    saved_system_date = get_saved_system_time_str()
    while True:
        if saved_system_date:
            print(f"저장된 system_time 날짜: {saved_system_date}")

        date_input = input("현재 날짜를 입력하세요 (YYYY-MM-DD) : ").strip()

        if not validate_date(date_input):
            print("!!! 오류: 날짜 형식이 맞지 않거나 존재하지 않는 날짜입니다. (예: 2026-04-08)")
            continue

        if not validate_date_not_past(date_input):
            print("!!! 오류: 입력한 날짜는 저장된 system_time 날짜보다 이전일 수 없습니다.")
            continue

        if not save_system_time(date_input):
            print("!!! 오류: system_time.txt에 날짜를 저장하지 못했습니다. 다시 입력해주세요.")
            continue

        system_date = date_input
        print(f"시스템 날짜가 [{system_date}]로 설정되었습니다.")
        break
            
    # 2. 세션 관리 (여기에 system_date도 함께 관리해 주면 아주 좋습니다)
    current_user = {
        "is_logged_in": False,
        "user_id": None
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
            elif choice == "2":
                register()
            elif choice == "3":
                search_book()
            else:
                print("올바르지 않은 입력입니다.")

        # --------------------------------------------------
        # 상태 2: 일반 사용자 (학생) 메뉴
        # --------------------------------------------------
        elif current_user["user_id"] != "admin":
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
                rent_book(current_user["user_id"], system_date) 
            elif choice == "2":
                return_book(current_user["user_id"], system_date)
            elif choice == "3":
                search_book()
            elif choice == "4":
                view_book(current_user["user_id"])
            else:
                print("올바르지 않은 입력입니다.")

        # --------------------------------------------------
        # 상태 3: 관리자 (Admin) 메뉴
        # --------------------------------------------------
        elif current_user["user_id"] == "admin":
            print(f"  [관리자 모드] 접속 중 (현재: {system_date})")
            print("="*40)
            print("원하는 동작에 해당하는 숫자를 입력하세요.")
            print("1. 도서추가")
            print("2. 도서삭제")
            print("3. 도서수정")
            print("4. 사용자조회")
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
                edit_book()
            elif choice == "4":
                view_users()
            else:
                print("올바르지 않은 입력입니다.")

if __name__ == "__main__":
    main()
