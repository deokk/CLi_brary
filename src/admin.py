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
_CATEGORY_FILE = os.path.join(_DATA_DIR, "category.txt")

# 상수
_FIXED_CATEGORIES = [
    "FICTION", "SCIENCE", "HISTORY", "TECHNOLOGY",
    "ART", "PHILOSOPHY", "LANGUAGE", "GENERAL",
]

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
    """도서번호 문법 규칙(4.3.1, 2차): 666666-22 형식"""
    return bool(re.fullmatch(r'\d{6}-\d{2}', book_id))

def _is_valid_book_code(book_code: str) -> bool:
    """도서코드 문법 규칙 (6.5.3 확장): 도서번호에서 복본 번호를 제외한 666666형식"""
    return bool(re.fullmatch(r'\d{6}', book_code))

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
# 2차 확장 시작 (카테고리)
def load_categories() -> list[str]:
    """category.txt 전체를 파싱하여 dict 목록으로 반환."""
    categories = []
    lines = _read_lines(_CATEGORY_FILE)
    for i, line in enumerate(lines):
        if i == 0:
            for fixed in line.split("/"):
                if fixed:
                    categories.append(fixed)
        else:
            categories.append(line)
    return categories

def save_categories(categories: list[str]) -> bool:
    """categories dict 목록을 category.txt에 저장."""
    fixed = []
    normal = []
    for category in categories:
        if category in _FIXED_CATEGORIES:
            fixed.append(category)
        else:
            normal.append(category)
    lines = []
    if fixed:
        lines.append("/".join(fixed))
    for category in normal:
        lines.append(category)
    return _write_lines(_CATEGORY_FILE, lines)

def is_valid_category(category: str) -> bool:
    """카테고리 문법 규칙(4.3.2)"""
    if not category:
        return False
    if len(category) > 32:
        return False
    if not re.fullmatch(r'[A-Z]{1,32}', category):
        return False
    return True
#2차 확장 끝 (카테고리)
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

def _next_book_id(books: list[dict]) -> str | None:
    """
    사용 가능한 다음 도서번호를 반환. (6.5.1)
    삭제된 번호는 재사용하지 않는다.
    새 도서(첫 권)는 000001-01 형식으로 부여된다.
    이 함수는 "완전히 새로운 도서" 추가에 쓰이며 도서코드(6자리)를 자동 부여한다.
    999999 범위를 초과하면 None 반환.
    """
    max_code = 0
    for b in books:
        book_id = b["id"]
        if not _is_valid_book_id(book_id):
            continue
        code = int(book_id[:6])
        max_code = max(max_code, code)
    new_code = max_code + 1
    if new_code > 999999:
        return None
    return f"{new_code:06d}-01"

def _generate_book_id_for_info(
    
    # category/title/author가 같은 책이 있으면 복본 번호를,
    # 없으면 도서 추가 규칙에 따라 새 도서 번호를 생성한다.

    category: str,
    title: str,
    author: str,
    books: list[dict],
    exclude_id: str | None = None,
) -> tuple[str | None, bool]:
    comparable_books = [book for book in books if book["id"] != exclude_id]

    existing = next(
        (
            book for book in comparable_books
            if book["category"] == category
            and book["title"] == title
            and book["author"] == author
        ),
        None
    )

    if existing is not None:
        return _next_copy_id(existing["id"][:6], books), True

    return _next_book_id(books), False    


def _next_copy_id(book_code: str, books: list[dict]) -> str | None:
    """
    동일 도서코드(6자리)의 새 복본 번호를 반환. (4.3.1)
    삭제된 번호는 재사용하지 않는다. 00~99 초과 시 None 반환.
    """
    prefix = f"{book_code}-"
    max_copy = 0
    for b in books:
        if b["id"].startswith(prefix):
            try:
                copy = int(b["id"][7:9])
                max_copy = max(max_copy, copy)
            except ValueError:
                pass
    new_copy = max_copy + 1
    if new_copy > 99:
        return None
    return f"{book_code}-{new_copy:02d}"


def _has_copies(book: dict, books: list[dict]) -> bool:
    prefix = book["id"][:6]

    for b in books:
        if b["id"] != book["id"] and b["id"][:6] == prefix:
            return True
    return False
#2차 확장 시작 (카테고리)
def add_book_category(matched_books: list[dict]) -> bool:
    """동일 도서코드를 가진 복본 전체에 카테고리를 추가 """
    new_category = input("추가하고자 하는 카테고리를 입력하십시오: ").strip()

    categories = load_categories()
    current_categories = matched_books[0]["category"].split(",")

    # 의미 규칙 1: category.txt 존재 여부
    if new_category not in categories:
        print("존재하지 않는 카테고리입니다. [카테고리를 편집]에서 카테고리를 추가한 다음 다시 시도해 주세요.")
        return False

    # 의미 규칙 2: 해당 도서의 카테고리 필드 중복 여부
    if new_category in current_categories:
        print("해당 도서는 입력한 카테고리가 이미 존재합니다.")
        return False

    old_category_str = matched_books[0]["category"]
    new_category_str = old_category_str + "," + new_category

    book_code = matched_books[0]["id"][:6]
    books = _get_books()
    for book in books:
        if book["id"][:6] == book_code:
            book["category"] = new_category_str
    if not _save_books(books):
        print("오류: 도서 파일 저장에 실패했습니다.")
        return False

    for book in matched_books:
        book["category"] = new_category_str

    print("카테고리가 추가되었습니다.")
    print(f"{old_category_str.replace(',', ', ')} >> {new_category_str.replace(',', ', ')}")

    return True

def remove_book_category(matched_books: list[dict]) -> bool:
    """동일 도서코드를 가진 복본 전체에서 카테고리를 삭제"""
    remove_category = input("삭제하고자 하는 카테고리를 입력하십시오: ").strip()

    current_categories = matched_books[0]["category"].split(",")

    # 의미 규칙 1: 해당 도서의 카테고리 필드 존재 여부
    if remove_category not in current_categories:
        print("해당 도서에 존재하지 않는 카테고리입니다.")
        return False

    # 의미 규칙 2: 최소 1개 카테고리 유지
    if len(current_categories) < 2:
        print("모든 도서는 한가지 이상의 카테고리를 가지고 있어야 합니다.")
        return False

    old_category_str = matched_books[0]["category"]
    new_categories = [c for c in current_categories if c != remove_category]
    new_category_str = ",".join(new_categories)

    book_code = matched_books[0]["id"][:6]
    books = _get_books()
    for book in books:
        if book["id"][:6] == book_code:
            book["category"] = new_category_str
    if not _save_books(books):
        print("오류: 도서 파일 저장에 실패했습니다.")
        return False

    for book in matched_books:
        book["category"] = new_category_str

    print("카테고리가 삭제되었습니다.")
    print(f"{old_category_str.replace(',', ', ')} >> {new_category_str.replace(',', ', ')}")

    return True

def update_book_category(matched_books: list[dict]) -> bool:
    """동일 도서코드를 가진 복본 전체의 카테고리를 수정"""
    raw = input("수정하고자 하는 카테고리를 입력하십시오: ").strip()
    parts = raw.split()
    if len(parts) != 2:
        print("옳지 않은 입력입니다. 다시 입력해주세요.")
        return False
    old_category, new_category = parts

    categories = load_categories()
    current_categories = matched_books[0]["category"].split(",")

    # 의미 규칙 1: 기존 카테고리가 해당 도서에 존재
    cond1_fail = old_category not in current_categories
    # 의미 규칙 2: 수정 후 카테고리가 category.txt에 존재
    cond2_fail = new_category not in categories

    if cond1_fail:
        print("수정하고자 하는 해당 도서의 카테고리가 해당 도서에 존재하지 않습니다.")
    if cond2_fail:
        print("입력받은 카테고리가 존재하지 않는 카테고리입니다. [카테고리를 편집]에서 카테고리를 추가한 다음 다시 시도해 주세요.")
    if cond1_fail or cond2_fail:
        return False

    old_category_str = matched_books[0]["category"]
    new_categories = [new_category if c == old_category else c for c in current_categories]
    new_category_str = ",".join(new_categories)

    book_code = matched_books[0]["id"][:6]
    books = _get_books()
    for book in books:
        if book["id"][:6] == book_code:
            book["category"] = new_category_str
    if not _save_books(books):
        print("오류: 도서 파일 저장에 실패했습니다.")
        return False

    for book in matched_books:
        book["category"] = new_category_str

    print("카테고리가 수정되었습니다.")
    print(f"{old_category_str.replace(',', ', ')} >> {new_category_str.replace(',', ', ')}")

    return True

def category_edit_prompt(matched_books: list[dict]) -> bool:
    """도서 수정 카테고리 부 프롬프트"""
    while True:
        print("[현재 도서 정보]")
        print(f"카테고리: {matched_books[0]['category'].replace(',', ', ')}")
        print(f"제목: {matched_books[0]['title']}")
        print(f"저자: {matched_books[0]['author']}")
        print("수행할 카테고리 작업을 설정하세요.")
        print("1. 추가")
        print("2. 삭제")
        print("3. 수정")
        print("0. 돌아가기")
        choice = input("카테고리 작업: ").strip()

        if choice == "0":
            return False
        if choice == "1":
            return add_book_category(matched_books)
        if choice == "2":
            return remove_book_category(matched_books)
        if choice == "3":
            return update_book_category(matched_books)
        print("옳지 않은 입력입니다. 다시 입력해주세요.")



def add_category() -> None:
    """category.txt에 새 카테고리를 추가"""
    new_category = input("추가하고자 하는 카테고리를 입력하십시오: ").strip()

    categories = load_categories()

    # 의미 규칙 1: 존재 여부
    cond1_fail = new_category in categories
    # 의미 규칙 2: 대문자 알파벳만
    cond2_fail = not re.fullmatch(r'[A-Z]+', new_category)
    # 의미 규칙 3: 최대 32자
    cond3_fail = len(new_category) > 32

    if cond1_fail:
        print("이미 해당 카테고리가 존재합니다.")
    if cond2_fail:
        print("카테고리는 대문자 알파벳을 제외한 다른 문자열을 허용하지 않습니다.")
    if cond3_fail:
        print("카테고리는 최대 32글자만 허용합니다.")
    if cond1_fail or cond2_fail or cond3_fail:
        return

    # 정상 결과: 사용자 확인 절차
    while True:
        confirm = input(f"{new_category} 카테고리를 추가하시겠습니까? (Y/N) : ").strip()
        if confirm in ("Y", "y"):
            categories.append(new_category)
            if not save_categories(categories):
                print("오류: 카테고리 파일 저장에 실패했습니다.")
                return
            print("카테고리가 추가되었습니다.")
            print(f"고정 카테고리: {'/'.join(c for c in categories if c in _FIXED_CATEGORIES)}")
            normal_cats = [c for c in categories if c not in _FIXED_CATEGORIES]
            print(f"일반 카테고리: {'/'.join(normal_cats)}")
            return
        if confirm in ("N", "n"):
            print("카테고리 추가 작업을 취소합니다.")
            return

def modify_category() -> None:
    """category.txt의 일반 카테고리를 수정"""
    raw = input("수정하고자 하는 카테고리를 입력하십시오: ").strip()
    parts = raw.split()
    if len(parts) != 2:
        print("옳지 않은 입력입니다. 다시 입력해주세요.")
        return
    old_category, new_category = parts

    categories = load_categories()

    # 그룹 A: 기존 카테고리 (의미 규칙 1, 2)
    group_a_msg = None
    if old_category not in categories:
        group_a_msg = "수정하고자 하는 카테고리가 존재하지 않습니다."
    elif old_category in _FIXED_CATEGORIES:
        group_a_msg = "고정 카테고리는 수정이 불가합니다."

    # 그룹 B: 새 카테고리 (의미 규칙 3, 4, 5)
    group_b_msgs = []
    if new_category in categories:
        group_b_msgs.append("이미 해당 카테고리가 존재합니다.")
    else:
        if not re.fullmatch(r'[A-Z]+', new_category):
            group_b_msgs.append("카테고리는 대문자 알파벳을 제외한 다른 문자열을 허용하지 않습니다.")
        if len(new_category) > 32:
            group_b_msgs.append("카테고리는 최대 32글자만 허용합니다.")

    if group_a_msg:
        print(group_a_msg)
    for msg in group_b_msgs:
        print(msg)
    if group_a_msg or group_b_msgs:
        return

    # 정상: category.txt 수정
    new_categories = [new_category if c == old_category else c for c in categories]
    if not save_categories(new_categories):
        print("오류: 카테고리 파일 저장에 실패했습니다.")
        return

    # books.txt 일괄 갱신
    books = _get_books()
    for book in books:
        cats = book["category"].split(",")
        cats = [new_category if c == old_category else c for c in cats]
        book["category"] = ",".join(cats)
    if not _save_books(books):
        print("오류: 도서 파일 저장에 실패했습니다.")
        return

    print("카테고리가 수정되었습니다.")
    print(f"고정 카테고리: {'/'.join(c for c in new_categories if c in _FIXED_CATEGORIES)}")
    normal_cats = [c for c in new_categories if c not in _FIXED_CATEGORIES]
    print(f"일반 카테고리: {'/'.join(normal_cats)}")

def merge_category() -> None:
    """category.txt의 두 카테고리를 하나로 통합"""
    category1 = input("통합하고자 하는 카테고리를 입력하십시오: ").strip()
    category2 = input("통합하고자 하는 카테고리를 입력하십시오: ").strip()

    categories = load_categories()

    category1_fixed = category1 in _FIXED_CATEGORIES
    category2_fixed = category2 in _FIXED_CATEGORIES
    fixed_count = (1 if category1_fixed else 0) + (1 if category2_fixed else 0)

    # 2형 질문은 1형에서 고정 카테고리를 한 번도 받지 않은 경우만 출력
    raw = None
    if fixed_count == 0:
        raw = input("통합할 카테고리 이름을 입력하십시오 ('0'을 입력시 첫 번째로 입력받은 카테고리로 통합됩니다.): ").strip()

    # 오류 수집 (1형/2형 오류를 한 번에 출력)
    errors = []
    # 조건 1
    if category1 not in categories or category2 not in categories:
        errors.append("통합하고자 하는 카테고리가 존재하지 않습니다.")
    # 조건 2
    if fixed_count == 2:
        errors.append("고정 카테고리 2개를 통합할 수 없습니다.")
    # 조건 3
    if category1 == category2:
        errors.append("같은 카테고리를 통합할 수 없습니다.")
    # 조건 4~6
    if raw is not None and raw != "0":
        if raw in categories and raw != category1 and raw != category2:
            errors.append("통합할 카테고리 이름은 통합하고자 하는 카테고리 중 하나이거나, 존재하지 않은 카테고리 이어야 합니다.")
        if not re.fullmatch(r'[A-Z]+', raw):
            errors.append("카테고리는 대문자 알파벳을 제외한 다른 문자열을 허용하지 않습니다.")
        if len(raw) > 32:
            errors.append("카테고리는 최대 32글자만 허용합니다.")

    if errors:
        for e in errors:
            print(e)
        return

    # 통합 후 카테고리 결정
    if category1_fixed:
        merged = category1
    elif category2_fixed:
        merged = category2
    elif raw == "0":
        merged = category1
    else:
        merged = raw

    # category.txt 갱신: category1, category2 제거 후 merged 추가
    new_categories = [c for c in categories if c != category1 and c != category2]
    if merged not in new_categories:
        new_categories.append(merged)
    if not save_categories(new_categories):
        print("오류: 카테고리 파일 저장에 실패했습니다.")
        return

    # books.txt 갱신: category1, category2를 merged로 치환 + 중복 제거
    books = _get_books()
    for book in books:
        categories = book["category"].split(",")
        new_categories = []
        for c in categories:
            replaced = merged if c == category1 or c == category2 else c
            if replaced not in new_categories:
                new_categories.append(replaced)
        book["category"] = ",".join(new_categories)
    if not _save_books(books):
        print("오류: 도서 파일 저장에 실패했습니다.")
        return

    print("카테고리가 통합되었습니다.")
    print(f"{category1} + {category2} = {merged}")
    print(f"고정 카테고리: {'/'.join(c for c in new_categories if c in _FIXED_CATEGORIES)}")
    normal_cats = [c for c in new_categories if c not in _FIXED_CATEGORIES]
    print(f"일반 카테고리: {'/'.join(normal_cats)}")

def delete_category() -> None:
    """category.txt의 일반 카테고리를 삭제"""
    target = input("삭제하고자 하는 카테고리를 입력하십시오: ").strip()

    categories = load_categories()
    books = _get_books()

    # 조건 1: 존재
    cond1_fail = target not in categories
    # 조건 2: 고정 카테고리 아님
    cond2_fail = target in _FIXED_CATEGORIES
    # 조건 3: 해당 카테고리만 가진 책 없음
    cond3_fail = not cond2_fail and any(book["category"].split(",") == [target] for book in books)

    if cond1_fail:
        print("삭제하고자 하는 카테고리가 존재하지 않습니다.")
    if cond2_fail:
        print("고정 카테고리는 삭제 불가합니다.")
    if cond3_fail:
        print("해당 카테고리를 지닌 도서가 존재합니다. 해당 도서(들)의 카테고리를 수정 후 다시 시도해 주세요.")
    if cond1_fail or cond2_fail or cond3_fail:
        return

    # category.txt에서 제거
    new_categories = [c for c in categories if c != target]
    if not save_categories(new_categories):
        print("오류: 카테고리 파일 저장에 실패했습니다.")
        return

    # books.txt 갱신: target이 들어있는 책에서 target만 제거
    for book in books:
        cats = book["category"].split(",")
        if target in cats:
            cats = [c for c in cats if c != target]
            book["category"] = ",".join(cats)
    if not _save_books(books):
        print("오류: 도서 파일 저장에 실패했습니다.")
        return

    print("카테고리가 삭제되었습니다.")
    print(f"고정 카테고리: {'/'.join(c for c in new_categories if c in _FIXED_CATEGORIES)}")
    normal_cats = [c for c in new_categories if c not in _FIXED_CATEGORIES]
    print(f"일반 카테고리: {'/'.join(normal_cats)}")
#2차 확장 끝 (카테고리)

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
    categories = load_categories()
    if category not in categories:
        print(f"올바르지 않은 카테고리입니다.")
        print(f"허용: {', '.join(categories)}")
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

    books = _get_books()
    new_id, is_copy = _generate_book_id_for_info(category, title, author, books)

    if new_id is None:
        print("오류: 도서번호를 생성할 수 없습니다.")
        print("--------------------------------------------------")
        return

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
        print("000001-01 형식으로 입력해주세요.")
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
    book_code = input("수정할 도서의 도서번호를 입력하세요: ").strip()

    #문법 규칙
    if not _is_valid_book_code(book_code):
        print("옳지 않은 입력입니다. 다시 입력해주세요.")
        print("--------------------------------------------------")
        return

    books = _get_books()

    #의미 규칙: 도서 존재 여부
    matched_books = [b for b in books if b["id"][:6] == book_code]
    if not matched_books:
        print("존재하지 않는 도서번호입니다. 다시 시도해주세요.")
        print("--------------------------------------------------")
        return

    target = matched_books[0]

    # 현재 도서 정보 출력
    print("[현재 도서 정보]")
    print(f"도서 번호: {book_code}")
    print(f"카테고리: {target['category'].replace(',', ', ')}")
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

        if field_input == "1":
            if category_edit_prompt(matched_books):
                print("수정이 완료되었습니다. 관리자 프롬프트로 이동합니다.")
                print("--------------------------------------------------")
                return # 정상 -> 관리자 프롬프트
            continue  # 비정상 -> 도서 수정 프롬프트

        if field_input == "2":
            new_value = input("[제목]수정할 정보를 입력하세요: ").strip()
            if not _is_valid_title(new_value):
                print("제목이 올바르지 않습니다.")
                print("(최대 32자, 한글/알파벳/숫자/공백만 허용, 앞뒤 공백 불가)")
                print("--------------------------------------------------")
                return
            if new_value == target["title"]:
                print("현재와 동일한 제목입니다.")
                print("--------------------------------------------------")
                return
            old_value = target["title"]
            for book in books:
                if book["id"][:6] == book_code:
                    book["title"] = new_value
            if not _save_books(books):
                print("오류: 도서 파일 저장에 실패했습니다.")
                print("--------------------------------------------------")
                return
            for book in matched_books:
                book["title"] = new_value
            print(f"제목: {old_value} -> {new_value}")
            print("수정이 완료되었습니다. 관리자 프롬프트로 이동합니다.")
            print("--------------------------------------------------")
            return

        if field_input == "3":
            new_value = input("[저자]수정할 정보를 입력하세요: ").strip()
            if not _is_valid_author(new_value):
                print("저자명이 올바르지 않습니다.")
                print("(최대 32자, 한글/알파벳/숫자/공백/() 만 허용, 앞뒤 공백 불가)")
                print("--------------------------------------------------")
                return
            if new_value == target["author"]:
                print("현재와 동일한 저자입니다.")
                print("--------------------------------------------------")
                return
            old_value = target["author"]
            for book in books:
                if book["id"][:6] == book_code:
                    book["author"] = new_value
            if not _save_books(books):
                print("오류: 도서 파일 저장에 실패했습니다.")
                print("--------------------------------------------------")
                return
            for book in matched_books:
                book["author"] = new_value
            print(f"저자: {old_value} -> {new_value}")
            print("수정이 완료되었습니다. 관리자 프롬프트로 이동합니다.")
            print("--------------------------------------------------")
            return

        print("옳지 않은 입력입니다. 다시 입력해주세요.")

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

# 6.5.5 카테고리 편집
def category_edit() -> None:
    """category.txt의 카테고리를 추가/수정/통합/삭제한다. (6.5.5)"""
    print("\n--------------------------------------------------")
    while True:
        categories = load_categories()
        print("[현재 카테고리 정보]")
        print(f"고정 카테고리: {'/'.join(c for c in categories if c in _FIXED_CATEGORIES)}")
        normal_categories = [c for c in categories if c not in _FIXED_CATEGORIES]
        print(f"일반 카테고리: {'/'.join(normal_categories)}")
        print("수행할 작업을 설정하세요.")
        print("1. 추가")
        print("2. 수정")
        print("3. 통합")
        print("4. 삭제")
        print("0. 돌아가기")
        choice = input("작업: ").strip()

        if choice == "0":
            print("--------------------------------------------------")
            return
        if choice == "1":
            add_category()
        elif choice == "2":
            modify_category()
        elif choice == "3":
            merge_category()
        elif choice == "4":
            delete_category()
        else:
            print("옳지 않은 입력입니다. 다시 입력해주세요.")
