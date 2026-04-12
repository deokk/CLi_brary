"""
관리자 모드 기능 모듈
- 도서 추가
- 도서 삭제
- 도서 수정
- 회원 목록 조회
"""

import os
import re


_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR = os.path.join(_ROOT_DIR, "data")
_BOOKS_FILE = os.path.join(_DATA_DIR, "books.txt")
_USERS_FILE = os.path.join(_DATA_DIR, "users.txt")
_RENTALS_FILE = os.path.join(_DATA_DIR, "rentals.txt")

_ALLOWED_CATEGORIES = [
    "Fiction", "Science", "History", "Technology",
    "Art", "Philosophy", "Language", "General",
]

_CATEGORY_CODE_MAP = {
    "F": "Fiction",
    "S": "Science",
    "H": "History",
    "T": "Technology",
    "A": "Art",
    "P": "Philosophy",
    "L": "Language",
    "G": "General",
}

_CODE_CATEGORY_MAP = {v: k for k, v in _CATEGORY_CODE_MAP.items()}


def _read_lines(filepath: str) -> list[str]:
    try:
        with open(filepath, encoding="utf-8") as f:
            return [line for line in f.read().splitlines() if line.strip()]
    except Exception:
        return []


def _write_lines(filepath: str, lines: list[str]) -> bool:
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            content = "\n".join(lines)
            if content:
                f.write(content + "\n")
        return True
    except Exception:
        return False


def _is_valid_book_id(book_id: str) -> bool:
    return bool(re.fullmatch(r"[FSHTAPLG]\d{3}-\d{2}", book_id))


def _is_valid_title(title: str) -> bool:
    if not title or len(title) > 32:
        return False
    if not re.fullmatch(r"[0-9a-zA-Z가-힣 ]+", title):
        return False
    if title != title.strip():
        return False
    return True


def _is_valid_author(author: str) -> bool:
    if not author or len(author) > 32:
        return False
    if not re.fullmatch(r"[0-9a-zA-Z가-힣() ]+", author):
        return False
    if author != author.strip():
        return False
    return True


def _get_books() -> list[dict]:
    books = []
    for line in _read_lines(_BOOKS_FILE):
        parts = line.split("/")
        if len(parts) == 5:
            books.append(
                {
                    "id": parts[0],
                    "category": parts[1],
                    "title": parts[2],
                    "author": parts[3],
                    "status": parts[4],
                }
            )
    return books


def _save_books(books: list[dict]) -> bool:
    lines = [
        f"{b['id']}/{b['category']}/{b['title']}/{b['author']}/{b['status']}"
        for b in books
    ]
    return _write_lines(_BOOKS_FILE, lines)


def _get_users() -> list[dict]:
    users = []
    for line in _read_lines(_USERS_FILE):
        parts = line.split("/")
        if len(parts) >= 3:
            users.append({"id": parts[0], "pw": parts[1], "ban": parts[2]})
    return users


def _get_rentals() -> list[dict]:
    rentals = []
    for line in _read_lines(_RENTALS_FILE):
        parts = line.split("/")
        if len(parts) == 6:
            rentals.append(
                {
                    "rental_id": parts[0],
                    "user_id": parts[1],
                    "book_id": parts[2],
                    "rent_date": parts[3],
                    "due_date": parts[4],
                    "return_date": parts[5],
                }
            )
    return rentals


def _save_rentals(rentals: list[dict]) -> bool:
    lines = [
        f"{r['rental_id']}/{r['user_id']}/{r['book_id']}/{r['rent_date']}/{r['due_date']}/{r['return_date']}"
        for r in rentals
    ]
    return _write_lines(_RENTALS_FILE, lines)


def _is_book_rented(book_id: str) -> bool:
    for rental in _get_rentals():
        if rental["book_id"] == book_id and rental["return_date"] == "NONE":
            return True
    return False


def _count_rented_by_user(user_id: str) -> int:
    return sum(
        1
        for rental in _get_rentals()
        if rental["user_id"] == user_id and rental["return_date"] == "NONE"
    )


def _next_book_id(category_code: str, books: list[dict]) -> str | None:
    max_code = 0
    for book in books:
        if book["id"].startswith(category_code):
            try:
                code = int(book["id"][1:4])
                max_code = max(max_code, code)
            except ValueError:
                pass

    new_code = max_code + 1
    if new_code > 999:
        return None
    return f"{category_code}{new_code:03d}-01"


def _next_copy_id(category_code: str, book_code_3: str, books: list[dict]) -> str | None:
    prefix = f"{category_code}{book_code_3}-"
    max_copy = 0
    for book in books:
        if book["id"].startswith(prefix):
            try:
                copy = int(book["id"][5:7])
                max_copy = max(max_copy, copy)
            except ValueError:
                pass

    new_copy = max_copy + 1
    if new_copy > 99:
        return None
    return f"{category_code}{book_code_3}-{new_copy:02d}"


def _generate_book_id_for_info(
    category: str,
    title: str,
    author: str,
    books: list[dict],
    exclude_id: str | None = None,
) -> tuple[str | None, bool]:
    category_code = _CODE_CATEGORY_MAP[category]
    comparable_books = [book for book in books if book["id"] != exclude_id]

    existing = next(
        (
            book
            for book in comparable_books
            if book["category"] == category
            and book["title"] == title
            and book["author"] == author
        ),
        None,
    )

    if existing is not None:
        book_code_3 = existing["id"][1:4]
        return _next_copy_id(category_code, book_code_3, books), True

    return _next_book_id(category_code, books), False


def add_book() -> None:
    print("\n--------------------------------------------------")
    raw = input("추가할 도서 정보를 입력해주세요(카테고리/제목/저자): ").strip()

    parts = raw.split("/")
    if len(parts) != 3:
        print("옳지 않은 입력입니다. 다시 입력해주세요.")
        print("--------------------------------------------------")
        return

    category, title, author = [part.strip() for part in parts]

    if category not in _ALLOWED_CATEGORIES:
        print("올바르지 않은 카테고리입니다.")
        print(f"허용: {', '.join(_ALLOWED_CATEGORIES)}")
        print("--------------------------------------------------")
        return

    if not _is_valid_title(title):
        print("제목이 올바르지 않습니다.")
        print("(최대 32자, 한글/영문/숫자/공백만 허용)")
        print("--------------------------------------------------")
        return

    if not _is_valid_author(author):
        print("저자명이 올바르지 않습니다.")
        print("(최대 32자, 한글/영문/숫자/공백/()만 허용)")
        print("--------------------------------------------------")
        return

    books = _get_books()
    new_id, is_copy = _generate_book_id_for_info(category, title, author, books)
    if new_id is None:
        print("오류: 도서번호를 생성할 수 없습니다.")
        print("--------------------------------------------------")
        return

    books.append(
        {
            "id": new_id,
            "category": category,
            "title": title,
            "author": author,
            "status": "AVAILABLE",
        }
    )

    if not _save_books(books):
        print("오류: 도서 파일 저장에 실패했습니다.")
        print("--------------------------------------------------")
        return

    if is_copy:
        print("동일한 도서가 이미 존재하여 복본으로 추가했습니다.")
    else:
        print("새 도서를 추가했습니다.")
    print(f"도서번호: {new_id}")
    print(f"제목: {title}")
    print(f"저자: {author}")
    print("관리자 프로젝트로 이동합니다.")
    print("--------------------------------------------------")


def delete_book() -> None:
    print("\n--------------------------------------------------")
    book_id = input("삭제할 도서의 도서번호를 입력하세요: ").strip()

    if not _is_valid_book_id(book_id):
        print("올바르지 않은 도서번호 형식입니다.")
        print("예: F001-01, S002-03")
        print("--------------------------------------------------")
        return

    books = _get_books()
    target = next((book for book in books if book["id"] == book_id), None)
    if target is None:
        print("존재하지 않는 도서번호입니다. 다시 시도해주세요.")
        print("--------------------------------------------------")
        return

    if _is_book_rented(book_id):
        print("해당 도서는 대출 중이므로 삭제할 수 없습니다.")
        print("--------------------------------------------------")
        return

    print("[현재 도서 정보]")
    print(f"도서 번호: {target['id']}")
    print(f"카테고리: {target['category']}")
    print(f"제목: {target['title']}")
    print(f"저자: {target['author']}")
    print(f"상태: {target['status']}")
    confirm = input("정말 삭제하시겠습니까? 삭제하려면 'Yes!'를 입력하세요: ").strip()

    if confirm != "Yes!":
        print("삭제가 취소되었습니다. 관리자 프로젝트로 이동합니다.")
        print("--------------------------------------------------")
        return

    books = [book for book in books if book["id"] != book_id]
    if not _save_books(books):
        print("오류: 도서 파일 저장에 실패했습니다.")
        print("--------------------------------------------------")
        return

    print("도서를 삭제했습니다.")
    print(f"도서번호: {target['id']}")
    print(f"제목: {target['title']}")
    print(f"저자: {target['author']}")
    print("관리자 프로젝트로 이동합니다.")
    print("--------------------------------------------------")


def edit_book() -> None:
    print("\n--------------------------------------------------")
    book_id = input("수정할 도서의 도서번호를 입력하세요: ").strip()

    if not _is_valid_book_id(book_id):
        print("옳지 않은 입력입니다. 다시 입력해주세요.")
        print("--------------------------------------------------")
        return

    books = _get_books()
    target_idx = next((i for i, book in enumerate(books) if book["id"] == book_id), None)
    if target_idx is None:
        print("존재하지 않는 도서번호입니다. 다시 시도해주세요.")
        print("--------------------------------------------------")
        return

    target = books[target_idx]

    print("[현재 도서 정보]")
    print(f"도서 번호: {target['id']}")
    print(f"카테고리: {target['category']}")
    print(f"제목: {target['title']}")
    print(f"저자: {target['author']}")

    while True:
        print("수정할 필드를 선택하세요.")
        print("1. 카테고리")
        print("2. 제목")
        print("3. 저자")
        print("0. 돌아가기")
        field_num = input("필드: ").strip()

        if field_num == "0":
            print("수정을 취소했습니다. 관리자 프로젝트로 이동합니다.")
            print("--------------------------------------------------")
            return

        if field_num in ("1", "2", "3"):
            break

        print("옳지 않은 입력입니다. 다시 입력해주세요.")

    updated_category = target["category"]
    updated_title = target["title"]
    updated_author = target["author"]
    old_value = ""
    new_value = ""
    old_id = target["id"]

    if field_num == "1":
        new_value = input("[카테고리] 수정할 정보를 입력하세요: ").strip()
        if new_value not in _ALLOWED_CATEGORIES:
            print("올바르지 않은 카테고리입니다.")
            print(f"허용: {', '.join(_ALLOWED_CATEGORIES)}")
            print("--------------------------------------------------")
            return
        if new_value == target["category"]:
            print("현재와 동일한 카테고리입니다.")
            print("--------------------------------------------------")
            return
        old_value = target["category"]
        updated_category = new_value

    elif field_num == "2":
        new_value = input("[제목] 수정할 정보를 입력하세요: ").strip()
        if not _is_valid_title(new_value):
            print("제목이 올바르지 않습니다.")
            print("(최대 32자, 한글/영문/숫자/공백만 허용)")
            print("--------------------------------------------------")
            return
        if new_value == target["title"]:
            print("현재와 동일한 제목입니다.")
            print("--------------------------------------------------")
            return
        old_value = target["title"]
        updated_title = new_value

    else:
        new_value = input("[저자] 수정할 정보를 입력하세요: ").strip()
        if not _is_valid_author(new_value):
            print("저자명이 올바르지 않습니다.")
            print("(최대 32자, 한글/영문/숫자/공백/()만 허용)")
            print("--------------------------------------------------")
            return
        if new_value == target["author"]:
            print("현재와 동일한 저자입니다.")
            print("--------------------------------------------------")
            return
        old_value = target["author"]
        updated_author = new_value

    new_id, is_copy = _generate_book_id_for_info(
        updated_category,
        updated_title,
        updated_author,
        books,
        exclude_id=old_id,
    )
    if new_id is None:
        print("오류: 도서번호를 생성할 수 없습니다.")
        print("--------------------------------------------------")
        return

    books[target_idx]["category"] = updated_category
    books[target_idx]["title"] = updated_title
    books[target_idx]["author"] = updated_author
    books[target_idx]["id"] = new_id

    if not _save_books(books):
        print("오류: 도서 파일 저장에 실패했습니다.")
        print("--------------------------------------------------")
        return

    if old_id != new_id:
        rentals = _get_rentals()
        for rental in rentals:
            if rental["book_id"] == old_id:
                rental["book_id"] = new_id
        if not _save_rentals(rentals):
            print("오류: 대출 파일 저장에 실패했습니다.")
            print("--------------------------------------------------")
            return

    print(f"{old_value} -> {new_value}")
    if old_id != new_id:
        print(f"도서번호: {old_id} -> {new_id}")
        if is_copy:
            print("동일한 전체 정보의 도서가 있어 복본 규칙으로 도서번호를 부여했습니다.")
        else:
            print("동일한 전체 정보의 도서가 없어 새 도서 추가 규칙으로 도서번호를 부여했습니다.")
    print("수정이 완료되었습니다. 관리자 프로젝트로 이동합니다.")
    print("--------------------------------------------------")


def view_users() -> None:
    print("\n--------------------------------------------------")
    users = _get_users()

    print("[사용자 목록]")
    print(f"{'ID':<15} {'대출권수':<10} {'대출정지 종료일'}")
    print("------------------------------------------")

    for user in users:
        uid = user["id"]
        if uid == "admin":
            continue
        count = _count_rented_by_user(uid)
        ban = user["ban"]
        print(f"{uid:<15} {count:<10} {ban}")

    print("사용자 프로젝트로 돌아가려면 0을 입력하세요: ", end="")
    while True:
        answer = input().strip()
        if answer == "0":
            break
        print("옳지 않은 입력입니다. 다시 입력해주세요.")
        print("0을 입력하세요: ", end="")
    print("--------------------------------------------------")
