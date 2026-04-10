# clibrary.py
import sys

from src.validator import (
    check_environment,
    validate_date,
    validate_date_format_only,
    validate_date_not_past,
    get_saved_system_time_str,
    save_system_time,
    has_violations,
)
from src.auth import login, register
from src.book import search_book, rent_book, return_book, view_book
from src.admin import add_book, delete_book, modify_book


def main():
    # 1. 환경 검사
    check_environment()

    # --------------------------------------------------
    # 날짜 입력 프롬프트 (기획서 6.1)
    # 이미 저장된 날짜가 있으면: 현재 날짜를 입력하시오(마지막 기록일:YYYY-MM-DD):
    # 없으면: 현재 날짜를 입력하세요(YYYY-MM-DD):
    # --------------------------------------------------
    system_date = None
    while True:
        saved = get_saved_system_time_str()
        if saved:
            date_input = input(f"현재 날짜를 입력하시오(마지막 기록일:{saved}): ").strip()
        else:
            date_input = input("현재 날짜를 입력하세요(YYYY-MM-DD): ").strip()

        # 형식 검사
        if not validate_date_format_only(date_input):
            print("날짜 형식이 올바르지 않습니다. 다시 입력해주세요.")
            continue

        # 존재하는 날짜인지 검사
        if not validate_date(date_input):
            print("존재하지 않는 날짜입니다. 다시 입력해주세요.")
            continue

        # 비가역성 검사 (기획서 5.4.2)
        if not validate_date_not_past(date_input):
            print("날짜 형식이 올바르지 않습니다. 마지막 기록일 이후의 날짜를 입력하세요:")
            continue

        # 날짜 저장
        save_system_time(date_input)
        system_date = date_input
        break

    # 2. 세션 관리
    current_user = {
        "is_logged_in": False,
        "user_id": None,
        "role": None
    }

    # 3. 메인 무한 루프
    while True:

        # --------------------------------------------------
        # 로그인 전 메뉴 (기획서 6.2 / image18)
        # --------------------------------------------------
        if not current_user["is_logged_in"]:
            print("원하는 동작에 해당하는 숫자를 입력하세요.")
            print("1.로그인")
            print("2.회원가입")
            print("3.도서검색")
            print("0.종료")

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
        # 일반 사용자 메뉴 (기획서 image29)
        # --------------------------------------------------
        elif current_user["role"] == '0':
            # 위반 항목 있으면 프롬프트 위에 안내 출력
            if has_violations():
                print("문법 위배 항목이 발견되었습니다.")

            print("원하는 동작에 해당하는 숫자를 입력하세요.")
            print("1.도서대출")
            print("2.도서반납")
            print("3.도서검색")
            print("4.대출현황")
            print("0.종료")

            choice = input(f"\n[{current_user['user_id']}]한 자리 숫자를 입력하세요: ").strip()

            if choice == "0":
                print("프로그램을 종료합니다.")
                sys.exit(0)
            elif choice == "1":
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
        # 관리자 메뉴 (기획서 image23)
        # --------------------------------------------------
        elif current_user["role"] == '1':
            # 위반 항목 있으면 프롬프트 위에 안내 출력
            if has_violations():
                print("문법 위배 항목이 발견되었습니다.")

            print("원하는 동작에 해당하는 숫자를 입력하세요.")
            print("1.도서추가")
            print("2.도서삭제")
            print("3.사용자조회")
            print("4.대출현황조회")
            print("0.종료")

            choice = input("\n[ADMIN]한 자리 숫자를 입력하세요: ").strip()

            if choice == "0":
                print("프로그램을 종료합니다.")
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
