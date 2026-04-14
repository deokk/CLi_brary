# src/book.py
from pathlib import Path
import re
from datetime import datetime, timedelta

pathbooks = Path("data") / "books.txt"
pathrentals = Path("data") / "rentals.txt"
pathusers = Path("data") / "users.txt"


def load_books():
    with pathbooks.open("a+", encoding="utf-8") as fbooks:
        fbooks.seek(0)
        return fbooks.read().splitlines()


def load_rentals():
    with pathrentals.open("a+", encoding="utf-8") as frentals:
        frentals.seek(0)
        return [line for line in frentals.read().splitlines() if line.strip()]


def load_users():
    with pathusers.open("a+", encoding="utf-8") as fusers:
        fusers.seek(0)
        return fusers.read().splitlines()


def rent_book(id, date):
    """도서 대여"""
    while True:
        print("\n--------------------------------------------------")
        book = input("대출할 도서의 도서번호를 입력하세요: ").strip()

        pattern = re.compile(r"^[FSHTAPLG][0-9]{3}-[0-9]{2}$")
        if not pattern.fullmatch(book):
            print("옳지 않은 입력입니다. 다시 입력해주세요.")
            continue

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
                print("현재 대출 정지 중입니다. 대출정지 종료일 이후에 시도해주세요.")
                invalid = True

        if invalid:
            print("옳지 않은 입력입니다. 다시 입력해주세요.")
            return

        updated_books = []
        for line in books_lines:
            book_id, category, title, author, status = line.split("/")
            if book_id == book:
                status = "RENTED"
            updated_books.append(f"{book_id}/{category}/{title}/{author}/{status}")

        with pathbooks.open("w", encoding="utf-8") as fbooks2:
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

        with pathrentals.open("a", encoding="utf-8") as frentals2:
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
        users_lines = load_users()

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

        with pathbooks.open("w", encoding="utf-8") as fbooks2:
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

        with pathrentals.open("w", encoding="utf-8") as frentals2:
            frentals2.write("\n".join(updated_rentals) + "\n")

        end_date = datetime.strptime(datetemp, "%Y-%m-%d")
        return_date = datetime.strptime(date, "%Y-%m-%d")
        late_days = (return_date - end_date).days

        if late_days > 0:
            ban_date = return_date + timedelta(days=late_days)
            ban_date_str = ban_date.strftime("%Y-%m-%d")
            updated_users = []

            for line in users_lines:
                parts = line.split("/")
                if len(parts) != 3:
                    continue
                user_id, user_pw, user_ban = parts
                if user_id == id:
                    user_ban = ban_date_str
                updated_users.append(f"{user_id}/{user_pw}/{user_ban}")

            with pathusers.open("w", encoding="utf-8") as fusers2:
                fusers2.write("\n".join(updated_users) + "\n")

            print(f"[도서번호] {book}")
            print(f"도서 반납이 완료되었습니다. 대출정지 종료일은 [{ban_date_str}]입니다.")
        else:
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

        invalid_char = re.compile(r"[^a-zA-Z0-9가-힣 ]")
        if invalid_char.search(book):
            print("도서 제목에는 한글, 영문, 숫자, 공백만 입력할 수 있습니다.")
            book_title_is_invalid = True

        if len(book) == 0:
            print("빈칸은 입력할 수 없습니다.")
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
        print("--------------------------------------------------")
        if temp == "0":
            break


def view_book(id):
    """내 대출 현황 조회"""
    while True:
        print("\n--------------------------------------------------")
        print("[대출 현황]")
        print("도서번호       제목                          반납예정일")
        print("--------------------------------------------------")

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
                        print(book_id + "  " + book_title + "                          " + rental_date_end)
                        found = True

        if not found:
            print("검색 결과가 없습니다.")

        temp = input("사용자 프롬프트로 돌아가려면 0을 입력하세요: ").strip()
        print("--------------------------------------------------")
        if temp == "0":
            break
        print("옳지 않은 입력입니다. 다시 입력해주세요.")


if __name__ == "__main__":
    search_book()
