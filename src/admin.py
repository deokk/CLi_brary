# src/admin.py
"""
관리자 모드 기능 모듈 (기획서 6.5절)
- 6.5.1 도서 추가
- 6.5.2 도서 삭제
- 6.5.3 도서 수정
- 6.5.4 회원 목록 조회
"""

import os
import re

# 경로 설정
_ROOT_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR     = os.path.join(_ROOT_DIR, "data")
_BOOKS_FILE   = os.path.join(_DATA_DIR, "books.txt")
_USERS_FILE   = os.path.join(_DATA_DIR, "users.txt")
_RENTALS_FILE = os.path.join(_DATA_DIR, "rentals.txt")


# 상수
_ALLOWED_CATEGORIES = [
    "Fiction", "Science", "History", "Technology",
    "Art", "Philosophy", "Language", "General"
]

_CATEGORY_CODE_MAP = {
    "F": "Fiction",    "S": "Science",      "H": "History",
    "T": "Technology", "A": "Art",          "P": "Philosophy",
    "L": "Language",   "G": "General",
}

_CODE_CATEGORY_MAP = {v: k for k, v in _CATEGORY_CODE_MAP.items()}


# 내부
def _read_lines(filepath: str) -> list[str]:
    """파일을 UTF-8로 읽어 비어있지 않은 줄 목록을 반환."""
    try:
        with open(filepath, encoding="utf-8") as f:
            return [line for line in f.read().splitlines() if line.strip()]
    except Exception:
        return []

def _write_lines(filepath: str, lines: list[str]) -> bool:
    """줄 목록을 UTF-8로 파일에 저장."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            content = "\n".join(lines)
            if content:
                f.write(content + "\n")
        return True
    except Exception:
        return False

def _is_valid_book_id(book_id: str) -> bool:
    """도서번호 문법 규칙(4.3.1): C333-22 형식"""
    return bool(re.fullmatch(r'[FSHTAPLG]\d{3}-\d{2}', book_id))

def _is_valid_title(title: str) -> bool:
    """도서 제목 문법 규칙(4.3.3)"""
    if not title or len(title) > 32:
        return False
    if not re.fullmatch(r'[0-9a-zA-Z가-힣 ]+', title):
        return False
    if title != title.strip():
        return False
    return True

def _is_valid_author(author: str) -> bool:
    """저자 문법 규칙(4.3.4)"""
    if not author or len(author) > 32:
        return False
    if not re.fullmatch(r'[0-9a-zA-Z가-힣 ()]+', author):
        return False
    if author != author.strip():
        return False
    return True

def _get_books() -> list[dict]:
    """books.txt 전체를 파싱하여 dict 목록으로 반환."""
    books = []
    for line in _read_lines(_BOOKS_FILE):
        parts = line.split("/")
        if len(parts) == 5:
            books.append({
                "id": parts[0], "category": parts[1],
                "title": parts[2], "author": parts[3], "status": parts[4]
            })
    return books

def _save_books(books: list[dict]) -> bool:
    """books dict 목록을 books.txt에 저장."""
    lines = [
        f"{b['id']}/{b['category']}/{b['title']}/{b['author']}/{b['status']}"
        for b in books
    ]
    return _write_lines(_BOOKS_FILE, lines)

def _get_users() -> list[dict]:
    """users.txt 전체를 파싱하여 dict 목록으로 반환."""
    users = []
    for line in _read_lines(_USERS_FILE):
        parts = line.split("/")
        # 기획서: ID/비밀번호/대출정지종료일
        if len(parts) >= 3:
            users.append({
                "id": parts[0], "pw": parts[1], "ban": parts[2]
            })
    return users

def _get_rentals() -> list[dict]:
    """rentals.txt 전체를 파싱하여 dict 목록으로 반환."""
    rentals = []
    for line in _read_lines(_RENTALS_FILE):
        parts = line.split("/")
        if len(parts) == 6:
            rentals.append({
                "rental_id": parts[0], "user_id": parts[1],
                "book_id": parts[2], "rent_date": parts[3],
                "due_date": parts[4], "return_date": parts[5]
            })
    return rentals

def _save_rentals(rentals: list[dict]) -> bool:
    """rentals dict 목록을 rentals.txt에 저장."""
    lines = [
        f"{r['rental_id']}/{r['user_id']}/{r['book_id']}/{r['rent_date']}/{r['due_date']}/{r['return_date']}"
        for r in rentals
    ]
    return _write_lines(_RENTALS_FILE, lines)

def _is_book_rented(book_id: str) -> bool:
    """해당 도서번호가 현재 대출 중인지 확인."""
    for r in _get_rentals():
        if r["book_id"] == book_id and r["return_date"] == "NONE":
            return True
    return False

def _count_rented_by_user(user_id: str) -> int:
    """해당 회원의 현재 대출 중인 도서 수를 반환."""
    return sum(
        1 for r in _get_rentals()
        if r["user_id"] == user_id and r["return_date"] == "NONE"
    )

def _next_book_id(category_code: str, books: list[dict]) -> str | None:
    """
    해당 카테고리에서 사용 가능한 다음 도서번호를 반환. (6.5.1)
    삭제된 번호는 재사용하지 않는다.
    새 도서(첫 권)는 XX-01로 부여된다.
    같은 책의 추가 복본은 동일한 카테고리코드+3자리코드에 다른 2자리를 부여한다.
    이 함수는 "완전히 새로운 도서" 추가에 쓰이며 도서코드(3자리)를 자동 부여한다.
    000~999 범위를 초과하면 None 반환.
    """
    # 해당 카테고리의 기존 도서코드(3자리) 최댓값 파악
    max_code = 0
    for b in books:
        if b["id"].startswith(category_code):
            try:
                code = int(b["id"][1:4])
                max_code = max(max_code, code)
            except ValueError:
                pass
    new_code = max_code + 1
    if new_code > 999:
        return None
    return f"{category_code}{new_code:03d}-01"

def _next_copy_id(category_code: str, book_code_3: str, books: list[dict]) -> str | None:
    """
    동일 도서(카테고리코드+3자리코드 동일)의 새 복본 번호를 반환. (4.3.1)
    삭제된 번호는 재사용하지 않는다. 00~99 초과 시 None 반환.
    """
    prefix = f"{category_code}{book_code_3}-"
    max_copy = 0
    for b in books:
        if b["id"].startswith(prefix):
            try:
                copy = int(b["id"][5:7])
                max_copy = max(max_copy, copy)
            except ValueError:
                pass
    new_copy = max_copy + 1
    if new_copy > 99:
        return None
    return f"{category_code}{book_code_3}-{new_copy:02d}"

# 6.5.1 도서 추가
def add_book() -> None:
    """
    새 도서를 books.txt에 추가. (6.5.1)
    입력 형식: 카테고리/제목/저자
    - 동일한 카테고리/제목/저자가 이미 존재하면 복본(copy) 자동 추가
    - 하나라도 다르면 새 도서로 추가
    도서번호는 자동 부여되며 삭제된 번호는 재사용하지 않는다.
    """
    print("\n--------------------------------------------------")
    raw = input("추가할 도서의 정보를 입력해주세요(카테고리/제목/저자): ").strip()

    parts = raw.split("/")
    if len(parts) != 3:
        print("옳지 않은 입력입니다. 다시 입력해주세요.")
        print("--------------------------------------------------")
        return

    category, title, author = [p.strip() for p in parts]

    # 카테고리 검증 (4.3.2)
    if category not in _ALLOWED_CATEGORIES:
        print(f"올바르지 않은 카테고리입니다.")
        print(f"허용: {', '.join(_ALLOWED_CATEGORIES)}")
        print("--------------------------------------------------")
        return

    # 제목 검증 (4.3.3)
    if not _is_valid_title(title):
        print("제목이 올바르지 않습니다.")
        print("(최대 32자, 한글/알파벳/숫자/공백만 허용, 앞뒤 공백 불가)")
        print("--------------------------------------------------")
        return

    # 저자 검증 (4.3.4)
    if not _is_valid_author(author):
        print("저자명이 올바르지 않습니다.")
        print("(최대 32자, 한글/알파벳/숫자/공백/() 만 허용, 앞뒤 공백 불가)")
        print("--------------------------------------------------")
        return

    category_code = _CODE_CATEGORY_MAP[category]
    books = _get_books()

    # ── 동일 도서(카테고리+제목+저자 모두 일치) 존재 여부 확인
    existing = next(
        (b for b in books
         if b["category"] == category
         and b["title"] == title
         and b["author"] == author),
        None
    )

    if existing is not None:
        # 복본 추가: 동일 그룹(카테고리코드+3자리코드)에 새 복본 번호 부여
        book_code_3 = existing["id"][1:4]
        new_id = _next_copy_id(category_code, book_code_3, books)
        if new_id is None:
            print("오류: 해당 도서의 복본 번호가 소진되었습니다. (최대 99권)")
            print("--------------------------------------------------")
            return
        is_copy = True
    else:
        # 새 도서 추가: 새 도서코드(3자리) 자동 부여
        new_id = _next_book_id(category_code, books)
        if new_id is None:
            print("오류: 해당 카테고리에 더 이상 도서를 추가할 수 없습니다. (번호 소진)")
            print("--------------------------------------------------")
            return
        is_copy = False

    new_book = {
        "id": new_id,
        "category": category,
        "title": title,
        "author": author,
        "status": "AVAILABLE"
    }
    books.append(new_book)

    if not _save_books(books):
        print("오류: 도서 파일 저장에 실패했습니다.")
        print("--------------------------------------------------")
        return

    if is_copy:
        print("동일한 도서가 이미 존재하여 복본으로 추가되었습니다.")
    else:
        print("새로운 도서가 성공적으로 추가되었습니다.")
    print(f"도서 번호: {new_id}")
    print(f"제목: {title}")
    print(f"저자: {author}")
    print("관리자 프롬프트로 이동합니다.")
    print("--------------------------------------------------")


# 6.5.2 도서 삭제
def delete_book() -> None:
    """
    books.txt에서 도서를 삭제. (6.5.2)
    - 도서번호가 존재해야 함
    - 현재 대출 중인 회원이 없어야 함
    - Yes! 입력 시 삭제, 그 외는 취소
    """
    print("\n--------------------------------------------------")
    book_id = input("삭제할 도서의 도서번호를 입력하세요: ").strip()

    # ── 문법 규칙 ──
    if not _is_valid_book_id(book_id):
        print("올바르지 않은 도서번호 형식입니다.")
        print("C333-22 형식으로 입력해주세요. 예) F001-01, S002-03")
        print("--------------------------------------------------")
        return

    books = _get_books()

    #의미 규칙 1: 도서 존재 여부
    target = next((b for b in books if b["id"] == book_id), None)
    if target is None:
        print("존재하지 않는 도서번호입니다. 다시 시도해주세요.")
        print("--------------------------------------------------")
        return

    #의미 규칙 2: 대출 중 여부
    if _is_book_rented(book_id):
        print("해당 도서는 대여중이므로 삭제할 수 없습니다. 다른 도서를 선택해주세요.")
        print("--------------------------------------------------")
        return

    #삭제 최종 확인
    print("[현재 도서 정보]")
    print(f"도서 번호: {target['id']}")
    print(f"카테고리: {target['category']}")
    print(f"제목: {target['title']}")
    print(f"저자: {target['author']}")
    print(f"상태: {target['status']}")
    confirm = input("정말 삭제하시겠습니까? 삭제하려면 'Yes!'를 입력하세요: ")

    if confirm != "Yes!":
        print("삭제가 취소되었습니다. 관리자 프롬프트로 이동합니다.")
        print("--------------------------------------------------")
        return

    books = [b for b in books if b["id"] != book_id]
    if not _save_books(books):
        print("오류: 도서 파일 저장에 실패했습니다.")
        print("--------------------------------------------------")
        return

    print("도서가 성공적으로 삭제되었습니다.")
    print(f"도서 번호: {target['id']}")
    print(f"제목: {target['title']}")
    print(f"저자: {target['author']}")
    print("관리자 프롬프트로 이동합니다.")
    print("--------------------------------------------------")


# 6.5.3 도서 수정
def edit_book() -> None:
    """
    books.txt의 도서 정보를 수정한다. (6.5.3)
    수정 가능 필드: 카테고리, 제목, 저자
    """
    print("\n--------------------------------------------------")
    book_id = input("수정할 도서의 도서번호를 입력하세요: ").strip()

    #문법 규칙
    if not _is_valid_book_id(book_id):
        print("옳지 않은 입력입니다. 다시 입력해주세요.")
        print("--------------------------------------------------")
        return

    books = _get_books()

    #의미 규칙: 도서 존재 여부
    target_idx = next((i for i, b in enumerate(books) if b["id"] == book_id), None)
    if target_idx is None:
        print("존재하지 않는 도서번호입니다. 다시 시도해주세요.")
        print("--------------------------------------------------")
        return

    target = books[target_idx]

    # 현재 도서 정보 출력
    print("[현재 도서 정보]")
    print(f"도서 번호: {target['id']}")
    print(f"카테고리: {target['category']}")
    print(f"제목: {target['title']}")
    print(f"저자: {target['author']}")

    # 수정 필드 선택 루프
    while True:
        print("수정할 필드를 설정하세요.")
        print("1. 카테고리")
        print("2. 제목")
        print("3. 저자")
        print("0. 돌아가기")
        field_input = input("필드: ").strip()

        if field_input == "0":
            print("수정이 취소되었습니다. 관리자 프롬프트로 이동합니다.")
            print("--------------------------------------------------")
            return

        if field_input not in ("1", "2", "3"):
            print("옳지 않은 입력입니다. 다시 입력해주세요.")
            continue

        field_num = field_input
        break

    # 새 값 입력
    if field_num == "1":
        new_value = input("[카테고리]수정할 정보를 입력하세요: ").strip()
        if new_value not in _ALLOWED_CATEGORIES:
            print("올바르지 않은 카테고리입니다.")
            print(f"허용: {', '.join(_ALLOWED_CATEGORIES)}")
            print("--------------------------------------------------")
            return
        
        new_code = _CODE_CATEGORY_MAP[new_value]
        if new_code == target["id"][0]:
            print("현재와 동일한 카테고리입니다.")
            print("--------------------------------------------------")
            return
        
        # 새 카테고리에서 동일 제목+저자 도서 존재 여부 확인 (복본 or 신규)
        existing = next(
            (b for b in books
             if b["category"] == new_value
             and b["title"] == target["title"]
             and b["author"] == target["author"]),
            None
        )
        if existing is not None:
            # 동일 도서가 새 카테고리에 이미 있으면 복본번호
            book_code_3 = existing["id"][1:4]
            new_id = _next_copy_id(new_code, book_code_3, books)
            if new_id is None:
                print("오류: 해당 도서의 복본 번호가 소진되었습니다. (최대 99권)")
                print("--------------------------------------------------")
                return
        else:
            # 없으면 새 도서번호
            new_id = _next_book_id(new_code, books)
            if new_id is None:
                print("오류: 해당 카테고리에 더 이상 도서를 추가할 수 없습니다. (번호 소진)")
                print("--------------------------------------------------")
                return
        
        old_value = target["category"]
        books[target_idx]["category"] = new_value
        books[target_idx]["id"] = new_id
        old_id = target["id"]        

    elif field_num == "2":
        new_value = input("[제목]수정할 정보를 입력하세요: ").strip()
        if not _is_valid_title(new_value):
            print("제목이 올바르지 않습니다.")
            print("(최대 32자, 한글/알파벳/숫자/공백만 허용, 앞뒤 공백 불가)")
            print("--------------------------------------------------")
            return
        old_value = target["title"]
        books[target_idx]["title"] = new_value

    else:
        new_value = input("[저자]수정할 정보를 입력하세요: ").strip()
        if not _is_valid_author(new_value):
            print("저자명이 올바르지 않습니다.")
            print("(최대 32자, 한글/알파벳/숫자/공백/() 만 허용, 앞뒤 공백 불가)")
            print("--------------------------------------------------")
            return
        old_value = target["author"]
        books[target_idx]["author"] = new_value

    if not _save_books(books):
        print("오류: 도서 파일 저장에 실패했습니다.")
        print("--------------------------------------------------")
        return

    # 카테고리 변경 시 도서번호도 함께 출력
    if field_num == "1":
        rentals = _get_rentals()
        for r in rentals:
            if r["book_id"] == old_id:
                r["book_id"] = new_id
        if not _save_rentals(rentals):
            print("오류: 대출 파일 저장에 실패했습니다.")
            print("--------------------------------------------------")
            return
        print(f"카테고리: {old_value} -> {new_value}")
        print(f"도서번호: {old_id} -> {new_id}")
    else:
        print(f"{old_value} -> {new_value}")
    print("수정이 완료되었습니다. 관리자 프롬프트로 이동합니다.")
    print("--------------------------------------------------")


# 6.5.4 회원 목록 조회
def view_users() -> None:
    """
    users.txt의 전체 회원 목록을 조회한다. (6.5.4)
    출력: 아이디, 대출 권수, 대출정지 종료일
    0 입력 시 관리자 프롬프트로 돌아간다.
    """
    print("\n--------------------------------------------------")
    users = _get_users()

    print("[사용자 목록]")
    print(f"{'ID':<15} {'대출 권수':<10} {'대출정지 종료일'}")
    print("------------------------------------------")

    for u in users:
        uid = u["id"]
        # 관리자는 목록에서 제외 (기획서상 회원만 표시)
        if uid == "admin":
            continue
        count = _count_rented_by_user(uid)
        ban = u["ban"]
        print(f"{uid:<15} {count:<10} {ban}")

    print("사용자 프롬프트로 돌아가려면 0을 입력하세요: ", end="")
    while True:
        ans = input().strip()
        if ans == "0":
            break
        print("옳지 않은 입력입니다. 다시 입력해주세요.")
        print("0을 입력하세요: ", end="")
    print("--------------------------------------------------")
