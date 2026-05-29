# src/book.py
import os
import re
import unicodedata
from datetime import datetime, timedelta


_ROOT_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR     = os.path.join(_ROOT_DIR, "data")
_BOOKS_FILE   = os.path.join(_DATA_DIR, "books.txt")
_USERS_FILE   = os.path.join(_DATA_DIR, "users.txt")
_RENTALS_FILE = os.path.join(_DATA_DIR, "rentals.txt")

def load_books():
    with open(_BOOKS_FILE, "a+", encoding="utf-8") as fbooks:
        fbooks.seek(0)
        return [line for line in fbooks.read().splitlines() if line.strip()]

def load_rentals():
    with open(_RENTALS_FILE, "a+", encoding="utf-8") as frentals:
        frentals.seek(0)
        return [line for line in frentals.read().splitlines() if line.strip()]

def load_users():
    with open(_USERS_FILE, "a+", encoding="utf-8") as fusers:
        fusers.seek(0)
        return [line for line in fusers.read().splitlines() if line.strip()]

def display_width(text):
    width = 0
    for ch in text:
        if unicodedata.east_asian_width(ch) in ("F", "W"):
            width += 2
        else:
            width += 1
    return width

def fit_display(text, width):
    text_width = display_width(text)

    if text_width <= width:
        return text + (" " * (width - text_width))

    trimmed = ""
    current_width = 0
    ellipsis = "..."

    for ch in text:
        ch_width = 2 if unicodedata.east_asian_width(ch) in ("F", "W") else 1
        if current_width + ch_width + len(ellipsis) > width:
            break
        trimmed += ch
        current_width += ch_width

    return trimmed + ellipsis + (" " * (width - current_width - len(ellipsis)))

def sync_overdue_bans(date):
    rentals_lines = load_rentals()
    users_lines = load_users()

    current_date = datetime.strptime(date, "%Y-%m-%d")
    user_max_bans = {}

    for line in rentals_lines:
        parts = line.split("/")
        if len(parts) != 6:
            continue

        _, rental_user, _, _, rental_date_end, rental_date_return = parts

        if rental_date_return != "NONE":
            continue

        due_date = datetime.strptime(rental_date_end, "%Y-%m-%d")
        if current_date <= due_date:
            continue

        late_days = (current_date - due_date).days
        ban_date = current_date + timedelta(days=late_days)

        saved_ban = user_max_bans.get(rental_user)
        if saved_ban is None or ban_date > saved_ban:
            user_max_bans[rental_user] = ban_date

    updated_users = []

    for line in users_lines:
        parts = line.split("/")
        if len(parts) != 3:
            continue

        user_id, user_pw, user_ban = parts

        if user_id in user_max_bans:
            user_ban = user_max_bans[user_id].strftime("%Y-%m-%d")
        elif user_ban != "NONE":
            saved_ban_date = datetime.strptime(user_ban, "%Y-%m-%d")
            if current_date > saved_ban_date:
                user_ban = "NONE"

        updated_users.append(f"{user_id}/{user_pw}/{user_ban}")

    with open(_USERS_FILE, "w", encoding="utf-8") as fusers:
        fusers.write("\n".join(updated_users) + "\n")


def update_overdue_ban(id, date):
    rentals_lines = load_rentals()
    users_lines = load_users()

    current_date = datetime.strptime(date, "%Y-%m-%d")
    max_ban_date = None

    for line in rentals_lines:
        parts = line.split("/")
        if len(parts) != 6:
            continue

        rental_num, rental_user, rental_book_id, rental_date_start, rental_date_end, rental_date_return = parts

        if rental_user == id and rental_date_return == "NONE":
            due_date = datetime.strptime(rental_date_end, "%Y-%m-%d")

            # 반납예정일이 지난 경우
            if current_date > due_date:
                late_days = (current_date - due_date).days
                ban_date = current_date + timedelta(days=late_days)

                if max_ban_date is None or ban_date > max_ban_date:
                    max_ban_date = ban_date

    if max_ban_date is None:
        return

    ban_date_str = max_ban_date.strftime("%Y-%m-%d")

    updated_users = []

    for line in users_lines:
        parts = line.split("/")
        if len(parts) != 3:
            continue

        user_id, user_pw, user_ban = parts

        if user_id == id:
            if user_ban == "NONE":
                user_ban = ban_date_str
            else:
                old_ban_date = datetime.strptime(user_ban, "%Y-%m-%d")
                if max_ban_date > old_ban_date:
                    user_ban = ban_date_str

        updated_users.append(f"{user_id}/{user_pw}/{user_ban}")

    with open(_USERS_FILE, "w", encoding="utf-8") as fusers:
        fusers.write("\n".join(updated_users) + "\n")

def rent_book(id, date):
    """도서 대여"""

    update_overdue_ban(id,date)

    while True:
        print("\n--------------------------------------------------")
        book = input("대출할 도서의 도서번호를 입력하세요: ").strip()

        pattern = re.compile(r"^[FSHTAPLG][0-9]{3}-[0-9]{2}$")
        if not pattern.fullmatch(book):
            print("옳지 않은 입력입니다.")
            return

        books_lines = load_books()
        rentals_lines = load_rentals()
        users_lines = load_users()

        invalid = False
        book_is_found = False

        for line in books_lines:
            book_id, book_category, book_title, book_author, book_status = line.split("/")
            if book == book_id:
                book_is_found = True
                if book_status == "RENTED":
                    print("현재 대출중인 도서번호입니다. 다시 입력해주세요.")
                    invalid = True

        if not book_is_found:
            print("존재하지 않는 도서번호입니다. 다시 입력해주세요.")
            invalid = True

        rentaled_book = 0
        for line in rentals_lines:
            parts = line.split("/")
            if len(parts) != 6:
                continue
            rental_num, rental_user, rental_book_id, rental_date_start, rental_date_end, rental_date_return = parts
            if rental_user == id and rental_date_return == "NONE":
                rentaled_book += 1

        if rentaled_book > 2:
            print("대여중인 수량이 최대(3권)입니다. 반납 후 시도해주세요.")
            invalid = True

        for line in users_lines:
            parts = line.split("/")
            if len(parts) != 3:
                continue
            user_id, user_pw, user_ban = parts
            if user_id == id and user_ban != "NONE":
                ban_date = datetime.strptime(user_ban, "%Y-%m-%d")
                current_date = datetime.strptime(date, "%Y-%m-%d")
                if current_date <= ban_date:
                    print("현재 대출 정지 중입니다. 대출정지 종료일 이후에 시도해주세요.")
                    invalid = True
                else:
                    updated_users = []
                    for uline in users_lines:
                        u_parts = uline.split("/")
                        if len(u_parts) != 3:
                            continue
                        u_id, u_pw, u_ban = u_parts
                        if u_id == id:
                            u_ban = "NONE"
                        updated_users.append(f"{u_id}/{u_pw}/{u_ban}")

                    with open(_USERS_FILE,"w", encoding="utf-8") as fusers2:
                        fusers2.write("\n".join(updated_users) + "\n")


        if invalid:
            print("옳지 않은 입력입니다. 다시 입력해주세요.")
            return

        updated_books = []
        for line in books_lines:
            book_id, category, title, author, status = line.split("/")
            if book_id == book:
                status = "RENTED"
            updated_books.append(f"{book_id}/{category}/{title}/{author}/{status}")

        with open(_BOOKS_FILE,"w", encoding="utf-8") as fbooks2:
            fbooks2.write("\n".join(updated_books) + "\n")

        max_num = 0
        for line in rentals_lines:
            rental_num = line.split("/")[0]
            if rental_num.startswith("R") and rental_num[1:].isdigit():
                num = int(rental_num[1:])
                max_num = max(max_num, num)

        new_rental_num = f"R{max_num + 1:04d}"
        start_date = datetime.strptime(date, "%Y-%m-%d")
        end_date = start_date + timedelta(days=14)
        end_date_str = end_date.strftime("%Y-%m-%d")
        new_line = f"{new_rental_num}/{id}/{book}/{date}/{end_date_str}/NONE"

        with open(_RENTALS_FILE,"a", encoding="utf-8") as frentals2:
            if rentals_lines:
                frentals2.write("\n")
            frentals2.write(new_line)

        print(f"[도서번호] {book}")
        print("도서 대여가 완료되었습니다.")
        print("--------------------------------------------------")
        return


def return_book(id, date):
    """도서 반납"""
    while True:
        print("\n--------------------------------------------------")
        book = input("반납할 도서의 도서번호를 입력하세요: ").strip()

        pattern = re.compile(r"^[FSHTAPLG][0-9]{3}-[0-9]{2}$")
        if not pattern.fullmatch(book):
            print("옳지 않은 입력입니다.")
            break

        books_lines = load_books()
        rentals_lines = load_rentals()

        book_is_found = False
        book_is_available = False

        for line in books_lines:
            book_id, book_category, book_title, book_author, book_status = line.split("/")
            if book == book_id:
                book_is_found = True
                if book_status == "AVAILABLE":
                    book_is_available = True

        if not book_is_found:
            print("존재하지 않는 도서번호입니다.")
            break

        if book_is_available:
            print("대출중인 도서가 아닙니다.")
            break

        rented_by_other = False
        rented_by_me = False
        for line in rentals_lines:
            parts = line.split("/")
            if len(parts) != 6:
                continue
            rental_num, rental_user, rental_book_id, rental_date_start, rental_date_end, rental_date_return = parts
            if rental_book_id == book and rental_user == id and rental_date_return == "NONE":
                rented_by_me = True
            if rental_book_id == book and rental_user != id and rental_date_return == "NONE":
                rented_by_other = True

        if rented_by_other and not rented_by_me:
            print("회원님이 대출중인 도서가 아닙니다. ")
            break

        if not rented_by_me:
            print("대출 기록을 찾을 수 없습니다.")
            break

        updated_books = []
        for line in books_lines:
            book_id, category, title, author, status = line.split("/")
            if book_id == book:
                status = "AVAILABLE"
            updated_books.append(f"{book_id}/{category}/{title}/{author}/{status}")

        with open(_BOOKS_FILE,"w", encoding="utf-8") as fbooks2:
            fbooks2.write("\n".join(updated_books) + "\n")

        updated_rentals = []
        datetemp = None

        for line in rentals_lines:
            parts = line.split("/")
            if len(parts) != 6:
                continue
            rental_num, rental_user, rental_book_id, rental_date_start, rental_date_end, rental_date_return = parts
            if rental_book_id == book and rental_user == id and rental_date_return == "NONE":
                datetemp = rental_date_end
                rental_date_return = date
            updated_rentals.append(f"{rental_num}/{rental_user}/{rental_book_id}/{rental_date_start}/{rental_date_end}/{rental_date_return}")

        with open(_RENTALS_FILE,"w", encoding="utf-8") as frentals2:
            frentals2.write("\n".join(updated_rentals) + "\n")

        print(f"[도서번호] {book}")
        print("도서 반납이 완료되었습니다.")
        return



def search_book():
    """도서 검색"""
    while True:
        print("\n--------------------------------------------------")
        book = input("찾고 싶은 도서의 제목을 입력하세요(전체를 확인하려면 0을 입력): ").strip()

        book_title_is_invalid = False
        if len(book) > 32:
            print("도서 제목은 32글자를 넘을 수 없습니다.")
            book_title_is_invalid = True

        if len(book) == 0:
            print("빈칸은 입력할 수 없습니다.")
            book_title_is_invalid = True

        invalid_char = re.compile(r"[^a-zA-Z0-9가-힣 ]")
        if invalid_char.search(book):
            print("도서 제목에는 한글, 영문, 숫자, 공백만 입력할 수 있습니다.")
            book_title_is_invalid = True

        if book_title_is_invalid:
            print("옳지 않은 입력입니다. 다시 입력해주세요.")
            continue

        books_lines = load_books()

        if book == "0":
            print("[도서 목록]")
            for line in books_lines:
                print("- " + line)
        else:
            book_is_found = False
            keywords = book.split()
            print(f'검색어="{",".join(keywords)}"')
            print("[도서 목록]")

            for line in books_lines:
                book_id, book_category, book_title, book_author, book_status = line.split("/")
                all_found = True
                for keyword in keywords:
                    if keyword not in book_title:
                        all_found = False
                        break
                if all_found:
                    print("- " + line)
                    book_is_found = True

            if not book_is_found:
                print("검색 결과가 없습니다.")

        temp = input("사용자 프롬프트로 돌아가려면 0을 입력하세요: ").strip()
        while True:
            if temp == "0":
                print("--------------------------------------------------")
                return
            temp = input("옳지 않은 입력입니다. 다시 입력해주세요.")


def view_book(id):
    """내 대출 현황 조회"""

    book_id_width = 11
    title_width = 50
    due_date_width = 10
    print('\n')
    print("-" * (book_id_width + title_width + due_date_width + 2))
    print("[대출 현황]")
    print(
    f"{fit_display('도서번호', book_id_width)} "
    f"{fit_display('제목', title_width)} "
    f"{fit_display('반납예정일', due_date_width)}"
    )
    print("-" * (book_id_width + title_width + due_date_width + 2))
    found = False
    rentals_lines = load_rentals()
    books_lines = load_books()

    for line in rentals_lines:
        parts = line.split("/")
        if len(parts) != 6:
            continue
        rental_num, rental_user, rental_book_id, rental_date_start, rental_date_end, rental_date_return = parts
        if rental_user == id and rental_date_return == "NONE":
            for line2 in books_lines:
                book_id, book_category, book_title, book_author, book_status = line2.split("/")
                if book_id == rental_book_id:
                    print(
                        f"{fit_display(book_id, book_id_width)} "
                        f"{fit_display(book_title, title_width)} "
                        f"{fit_display(rental_date_end, due_date_width)}"
                    )
                    found = True

    if not found:
        print("검색 결과가 없습니다.")
    temp = input("사용자 프롬프트로 돌아가려면 0을 입력하세요: ").strip()
    while True:
        if temp == "0":
            break
        temp = input("옳지 않은 입력입니다. 다시 입력해주세요.")
    print("--------------------------------------------------")

def _render_loan_status(id):
    """대출 현황 표를 출력한다. (도서 연장 부 프롬프트용)"""
    book_id_width = 11
    title_width = 50
    due_date_width = 10

    print("-" * (book_id_width + title_width + due_date_width + 2))
    print("[대출 현황]")
    print(
        f"{fit_display('도서번호', book_id_width)} "
        f"{fit_display('제목', title_width)} "
        f"{fit_display('반납예정일', due_date_width)}"
    )
    print("-" * (book_id_width + title_width + due_date_width + 2))

    rentals_lines = load_rentals()
    books_lines = load_books()

    found = False
    for line in rentals_lines:
        parts = line.split("/")
        if len(parts) != 6:
            continue
        rental_num, rental_user, rental_book_id, rental_date_start, rental_date_end, rental_date_return = parts
        if rental_user == id and rental_date_return == "NONE":
            for line2 in books_lines:
                book_parts = line2.split("/")
                if len(book_parts) >= 5 and book_parts[0] == rental_book_id:
                    print(
                        f"{fit_display(rental_book_id, book_id_width)} "
                        f"{fit_display(book_parts[2], title_width)} "
                        f"{fit_display(rental_date_end, due_date_width)}"
                    )
                    found = True

    if not found:
        print("대출 중인 도서가 없습니다.")


def extend_book(id, date):
    """대출 기한 연장 (기획서 6.3.5)"""

    # 이용 제한(연체) 상태를 현재 날짜 기준으로 동기화 (rent_book과 동일)
    update_overdue_ban(id, date)

    current_date = datetime.strptime(date, "%Y-%m-%d")
    pattern = re.compile(r"^[0-9]{6}-[0-9]{2}$")

    print("\n--------------------------------------------------")
    _render_loan_status(id)

    while True:
        book = input("연장할 도서의 도서번호를 입력하세요 (뒤로가려면 0): ").strip()

        # 0 입력 시 회원 프롬프트로 복귀
        if book == "0":
            print("--------------------------------------------------")
            return

        # 문법 규칙: 도서번호 형식 위반
        if not pattern.fullmatch(book):
            print("옳지 않은 입력입니다. 다시 입력해주세요.")
            continue

        rentals_lines = load_rentals()
        books_lines = load_books()

        # 의미 규칙 1: 본인이 현재 대출 중인 도서여야 한다.
        target_parts = None
        for line in rentals_lines:
            parts = line.split("/")
            if len(parts) != 6:
                continue
            rental_num, rental_user, rental_book_id, rental_date_start, rental_date_end, rental_date_return = parts
            if rental_book_id == book and rental_user == id and rental_date_return == "NONE":
                target_parts = parts
                break

        if target_parts is None:
            print("대여가 불가능합니다.")
            continue

        target_num, target_user, target_book, target_start, target_end, target_return = target_parts
        rent_date = datetime.strptime(target_start, "%Y-%m-%d")
        due_date = datetime.strptime(target_end, "%Y-%m-%d")

        # 의미 규칙 2: 연체 중이 아니어야 한다. (현재 날짜 > 반납예정일이면 연체)
        if current_date > due_date:
            print("대여가 불가능합니다.")
            continue

        # 의미 규칙 3: 연장 횟수가 2회 미만이어야 한다.
        # 연장 횟수 = (반납기한 - 대여일 - 14) / 7  (기본 대출 14일, 연장 1회당 +7일)
        extend_count = ((due_date - rent_date).days - 14) // 7
        if extend_count < 0:
            extend_count = 0
        if extend_count >= 2:
            print("대여가 불가능합니다.")
            continue

        # 의미 규칙 4: 반납 예정일과 시스템 날짜가 7일 이내여야 한다.
        if (due_date - current_date).days > 7:
            print("대여가 불가능합니다.")
            continue

        # 모든 조건 통과 → 반납 예정일 7일 연장
        new_due_date = due_date + timedelta(days=7)
        new_due_str = new_due_date.strftime("%Y-%m-%d")

        updated_rentals = []
        for line in rentals_lines:
            parts = line.split("/")
            if len(parts) != 6:
                updated_rentals.append(line)
                continue
            rental_num, rental_user, rental_book_id, rental_date_start, rental_date_end, rental_date_return = parts
            if rental_num == target_num:
                rental_date_end = new_due_str
            updated_rentals.append(
                f"{rental_num}/{rental_user}/{rental_book_id}/{rental_date_start}/{rental_date_end}/{rental_date_return}"
            )

        with open(_RENTALS_FILE, "w", encoding="utf-8") as frentals2:
            frentals2.write("\n".join(updated_rentals) + "\n")

        # 제목 조회
        title = ""
        for line in books_lines:
            book_parts = line.split("/")
            if len(book_parts) >= 5 and book_parts[0] == book:
                title = book_parts[2]
                break

        print(f"[{book}]{title}의 연장이 완료되었습니다. 반납 예정일이 {new_due_str}로 변경되었습니다.")
        print("--------------------------------------------------")
        return