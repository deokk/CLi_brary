import sys

from src.admin import add_book, delete_book, edit_book, view_users
from src.auth import login, register
from src.book import rent_book, return_book, search_book, sync_overdue_bans, view_book
from src.validator import (
    check_environment,
    get_saved_system_time_str,
    save_system_time,
    validate_date,
    validate_date_not_past,
)


def prompt_system_date() -> str:
    print("\n" + "=" * 40)
    print("  시스템 날짜 설정")
    print("=" * 40)

    saved_system_date = get_saved_system_time_str()

    while True:
        if saved_system_date:
            print(f"저장된 system_time 날짜: {saved_system_date}")

        date_input = input("현재 날짜를 입력하세요 (YYYY-MM-DD): ").strip()
        if not validate_date(date_input):
            print("오류: 올바른 날짜 형식이 아니거나 존재하지 않는 날짜입니다. 예) 2026-03-01")
            continue

        if not validate_date_not_past(date_input):
            print("오류: 입력한 날짜는 저장된 system_time 날짜보다 과거일 수 없습니다.")
            continue

        if not save_system_time(date_input):
            print("오류: system_time.txt에 날짜를 저장하지 못했습니다. 다시 입력해 주세요.")
            continue

        print(f"시스템 날짜가 [{date_input}]로 설정되었습니다.")
        return date_input


def show_guest_menu(system_date: str) -> str:
    print(f"  CLi_brary 도서관 시스템 (현재: {system_date})")
    print("=" * 40)
    print("원하는 동작의 번호를 입력하세요.")
    print("1. 로그인")
    print("2. 회원가입")
    print("3. 도서 검색")
    print("0. 종료")
    return input("\n한자리 숫자를 입력하세요: ").strip()


def show_user_menu(user_id: str, system_date: str) -> str:
    print(f"  [{user_id}] 사용자 모드 (현재: {system_date})")
    print("=" * 40)
    print("원하는 동작의 번호를 입력하세요.")
    print("1. 도서 대출")
    print("2. 도서 반납")
    print("3. 도서 검색")
    print("4. 대출 현황")
    print("0. 종료")
    return input(f"\n[{user_id}] 한자리 숫자를 입력하세요: ").strip()


def show_admin_menu(system_date: str) -> str:
    print(f"  [관리자 모드] (현재: {system_date})")
    print("=" * 40)
    print("원하는 동작의 번호를 입력하세요.")
    print("1. 도서 추가")
    print("2. 도서 삭제")
    print("3. 도서 수정")
    print("4. 사용자 조회")
    print("5. 도서 검색")
    print("0. 종료")
    return input("\n[ADMIN] 한자리 숫자를 입력하세요: ").strip()


def main() -> None:
    check_environment()
    system_date = prompt_system_date()
    sync_overdue_bans(system_date)

    current_user = {
        "is_logged_in": False,
        "user_id": None,
    }

    while True:
        print("\n" + "=" * 40)

        if not current_user["is_logged_in"]:
            choice = show_guest_menu(system_date)

            if choice == "0":
                print("프로그램을 종료합니다.")
                sys.exit(0)
            if choice == "1":
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
            continue

        if current_user["user_id"] == "admin":
            choice = show_admin_menu(system_date)

            if choice == "0":
                print("프로그램을 종료합니다.")
                sys.exit(0)
            if choice == "1":
                add_book()
            elif choice == "2":
                delete_book()
            elif choice == "3":
                edit_book()
            elif choice == "4":
                view_users()
            elif choice == "5":
                search_book()
            else:
                print("올바르지 않은 입력입니다.")
            continue

        choice = show_user_menu(current_user["user_id"], system_date)

        if choice == "0":
            print("프로그램을 종료합니다.")
            sys.exit(0)
        if choice == "1":
            rent_book(current_user["user_id"], system_date)
        elif choice == "2":
            return_book(current_user["user_id"], system_date)
        elif choice == "3":
            search_book()
        elif choice == "4":
            view_book(current_user["user_id"])
        else:
            print("올바르지 않은 입력입니다.")


if __name__ == "__main__":
    main()
