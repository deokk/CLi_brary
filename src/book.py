# src/book.py
from pathlib import Path

from tensorflow.python.framework.test_ops import none

pathbooks = Path("..") / "data" / "books.txt"
with pathbooks.open("a+", encoding="utf-8") as fbooks:
    fbooks.seek(0)
    contentbooks = fbooks.read()
pathrentals = Path("..") / "data" / "rentals.txt"
with pathrentals.open("a+", encoding="utf-8") as frentals:
    frentals.seek(0)
    contentrentals = frentals.read()
pathusers = Path("..") / "data" / "users.txt"
with pathusers.open("a+", encoding="utf-8") as fusers:
    fusers.seek(0)
    contentusers = fusers.read()
import re
from datetime import datetime, timedelta

def rent_book(id,date):
    """도서 대여 (대여 가능 여부 확인 후 rentals.txt 및 books.txt 업데이트)"""
    while True:
        print("\n--------------------------------------------------")
        book = input("대출할 도서의 도서번호를 입력하세요: ")

        #문법 규칙
        pattern = re.compile(r'^[FSHTAPLG][0-9]{3}-[0-9]{2}$')
        if (not pattern.fullmatch(book)):
            print("옳지 않은 입력입니다. 다음 규칙에 따라 다시 입력해주세요.")
            print("C333-22 형식으로 입력해주세요. 예)F001-01, F002-02, A376-08")
            print("C   : 허용된 문자 -> ‘F’ , ‘S’, ‘H’, ‘T’, ‘A’, ‘P’, ‘L’, ‘G’")
            print("333 : 허용된 문자 -> 0 ~ 9 아라비아 숫자, 선행 0을 포함하여 입력")
            print("22  : 허용된 문자 -> 0 ~ 9 아라비아 숫자, 선행 0을 포함하여 입력")
            continue
        #의미 규칙
        invalid = False
        book_is_found = False
        for line in contentbooks.splitlines():
            book_id, book_category, book_title, book_author, book_status = line.split("/")
            if (book == book_id):
                book_is_found = True
                if(book_status == "RENTED"):
                    print("현재 대여중인 도서번호입니다. 다시 입력해주세요.")
                    invalid = True
        if (not book_is_found):
            print("존재하지 않는 도서번호입니다. 다시 입력해주세요.")
            invalid = True
        rentaled_book = 0
        for line in contentrentals.splitlines():
            rental_num, rental_user, rental_book_id, rental_date_start, rental_date_end, rental_date_return = line.split("/")
            if(rental_user == id and rental_date_return == "NONE"):
                rentaled_book += 1
        if(rentaled_book > 2):
            print("대여중인 수량이 최대(3권)입니다. 반납 후 시도해주세요.")
            invalid = True
        for line in contentusers.splitlines():
            user_id, user_pw, user_ban = line.split("/")
            if(user_id == id and user_ban != "NONE"):
                print("현재 대출 정지 중입니다. 대출정지 종료일 이후에 시도해주세요.")
        if (invalid):
            print("옳지 않은 입력입니다. 다시 입력해주세요.")
            break
        #규칙 통과
        lines = contentbooks.splitlines()
        updated_lines = []
        for line in lines:
            book_id, category, title, author, status = line.split("/")
            if book_id == book:
                status = "RENTED"
            updated_lines.append(f"{book_id}/{category}/{title}/{author}/{status}")
        with pathbooks.open("w", encoding="utf-8") as fbooks2:
            fbooks2.write("\n".join(updated_lines) + "\n")

        max_num = 0
        for line in contentrentals.splitlines():
            rental_num = line.split("/")[0]  # R0001
            num = int(rental_num[1:])
            max_num = max(max_num, num)
        new_rental_num = f"R{max_num + 1:04d}"
        start_date = datetime.strptime(date, "%Y-%m-%d")
        end_date = start_date + timedelta(days=14)
        end_date_str = end_date.strftime("%Y-%m-%d")
        new_line = f"{new_rental_num}/{id}/{book}/{date}/{end_date_str}/NONE"
        with pathrentals.open("a", encoding="utf-8") as frentals2:
            frentals2.write("\n" + new_line)
        print("--------------------------------------------------")

def return_book(id,date):
    """도서 반납 (실제 반납일 기록 및 상태 업데이트)"""
    while True:
        print("\n--------------------------------------------------")
        book = input("반납할 도서의 도서번호를 입력하세요: ")

        #문법 규칙
        pattern = re.compile(r'^[FSHTAPLG][0-9]{3}-[0-9]{2}$')
        if (not pattern.fullmatch(book)):
            print("옳지 않은 입력입니다. 다음 규칙에 따라 다시 입력해주세요.")
            print("C333-22 형식으로 입력해주세요. 예)F001-01, F002-02, A376-08")
            print("C   : 허용된 문자 -> ‘F’ , ‘S’, ‘H’, ‘T’, ‘A’, ‘P’, ‘L’, ‘G’")
            print("333 : 허용된 문자 -> 0 ~ 9 아라비아 숫자, 선행 0을 포함하여 입력")
            print("22  : 허용된 문자 -> 0 ~ 9 아라비아 숫자, 선행 0을 포함하여 입력")
            continue
        #의미 규칙
        book_is_found = False
        book_is_available = False
        for line in contentbooks.splitlines():
            book_id, book_category, book_title, book_author, book_status = line.split("/")
            if (book == book_id):
                book_is_found = True
                if(book_status == "AVAILABLE"):
                    book_is_available = True
        if (not book_is_found):
            print("존재하지 않는 도서번호입니다. 다시 입력해주세요.")
            continue
        if (book_is_available):
            print("대여하신 도서가 아닙니다. 다시 입력해주세요. ")
            continue
        rented_by_other = False
        for line in contentrentals.splitlines():
            rental_num, rental_user, rental_book_id, rental_date_start, rental_date_end, rental_date_return = line.split("/")
            if(book == rental_book_id and id != rental_user):
                rented_by_other = True
        if(rented_by_other):
            print("대여하신 도서가 아닙니다. 다시 입력해주세요. ")
            continue
        #규칙 통과
        lines = contentbooks.splitlines()
        updated_lines = []
        for line in lines:
            book_id, category, title, author, status = line.split("/")
            if book_id == book:
                status = "AVAILABLE"
            updated_lines.append(f"{book_id}/{category}/{title}/{author}/{status}")
        with pathbooks.open("w", encoding="utf-8") as fbooks2:
            fbooks2.write("\n".join(updated_lines) + "\n")

        lines = contentrentals.splitlines()
        updated_lines = []

        datetemp = None

        for line in lines:
            rental_num, rental_user, rental_book_id, rental_date_start, rental_date_end, rental_date_return = line.split("/")
            if rental_book_id == book and rental_user == id and rental_date_return == "NONE":
                datetemp = rental_date_end
                rental_date_return = date
            updated_lines.append(f"{rental_num}/{rental_user}/{rental_book_id}/{rental_date_start}/{rental_date_end}/{rental_date_return}")
        with pathrentals.open("w", encoding="utf-8") as frentals2:
            frentals2.write("\n".join(updated_lines) + "\n")

        end_date = datetime.strptime(datetemp, "%Y-%m-%d")
        return_date = datetime.strptime(date, "%Y-%m-%d")
        late_days = (return_date - end_date).days
        if(late_days > 0):
            ban_date = return_date + timedelta(days=late_days)
            ban_date_str = ban_date.strftime("%Y-%m-%d")
            updated_lines = []
            for line in contentusers.splitlines():
                user_id, user_pw, user_ban = line.split("/")
                if user_id == id:
                    user_ban = ban_date_str
                updated_lines.append(f"{user_id}/{user_pw}/{user_ban}")
            with pathusers.open("w", encoding="utf-8") as fusers2:
                fusers2.write("\n".join(updated_lines) + "\n")
            print("도서 반납이 완료되었습니다. 연체로 인한 대출정지기한은[" + ban_date_str + "]까지 입니다. 사용자 프롬포트로 이동합니다. ")
        else:
            print("도서 반납이 완료되었습니다. 사용자 프롬포트로 이동합니다. ")
        break

        print("--------------------------------------------------")

def search_book():
    """도서 검색 (키워드로 도서 찾기)"""
    while True:
        print("\n--------------------------------------------------")
        book = input("찾고 싶은 도서의 제목을 입력하세요(전체를 확인하려면 0을 입력): ")

        #규칙 검사
        book_title_is_invalid = False
        if (len(book) > 32):
            print("도서의 제목을 검색할 때 32글자를 넘을 수 없습니다.")
            book_title_is_invalid = True
        invalid_char = re.compile("[^a-zA-Z0-9가-힣 ]")
        if (invalid_char.search(book)):
            print("도서의 제목은 아라비아 숫자, 알파벳, 한글, Space 공백 문자를 제외한 문자는 입력 불가합니다.")
            book_title_is_invalid = True
        if ((len(book) > 0 and book[0] == " ") or (len(book) > 0 and book[-1] == " ")):
            print("도서의 제목을 검색할 때 시작과 끝 문자는 Space 공백일 수 없습니다.")
            book_title_is_invalid = True
        if (len(book) == 0):
            print("빈칸을 입력할 수 없습니다.")
            book_title_is_invalid = True
        if (book_title_is_invalid):
            print("옳지 않은 입력입니다. 다시 입력해주세요.")
        #규칙 통과
        else:
            #전체 도서
            if(book == "0"):
                print("[도서 목록]")
                for line in contentbooks.splitlines():
                    print("- " + line)
            #키워드 검색
            else:
                book_is_found = False
                keywords = book.split()
                print("검색어=\"", end = "")
                print(",".join(keywords), end="")
                print("\"")
                print("[도서 목록]")

                for line in contentbooks.splitlines():
                    book_id, book_category, book_title, book_author, book_status = line.split("/")

                    all_found = True
                    for keyword in keywords:
                        if(keyword not in book_title):
                            all_found = False
                            break
                    if(all_found):
                        print("- " + line)
                        book_is_found = True

                if(not book_is_found):
                    print("검색 결과가 없습니다.")

            temp = input("사용자 프롬포트로 돌아가려면 0을 입력하세요: ")
        print("--------------------------------------------------")
        if (temp == "0"):
            break

def view_book(id):
    """도서 조회 (특정 도서의 상세 정보 및 대여 상태 확인)"""
    while True:
        print("\n--------------------------------------------------")
        print("[대출 현황]")
        print("도서번호       제목                          반납예정일")
        print("--------------------------------------------------")
        found = False
        for line in contentrentals.splitlines():
            rental_num, rental_user, rental_book_id, rental_date_start, rental_date_end, rental_date_return = line.split("/")
            if(rental_user == id and rental_date_return == "NONE"):
                for line2 in contentbooks.splitlines():
                    book_id, book_category, book_title, book_author, book_status = line2.split("/")
                    if(book_id == rental_book_id):
                        print(book_id + "  " + book_title + "                          " + rental_date_end)
                        found = True
        if (not found):
            print("검색 결과가 없습니다.")
        temp = input("사용자 프롬포트로 돌아가려면 0을 입력하세요: ")
        print("--------------------------------------------------")
        if (temp == "0"):
            break
        else:
            print("옳지 않은 입력입니다. 다시 입력해주세요.")

#디버깅용, 아래 줄에 디버깅을 할 함수를 입력하면 됨
search_book()
