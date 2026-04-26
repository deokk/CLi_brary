# src/validator.py
import os
import re
import sys
from dataclasses import dataclass
from datetime import date
from typing import Optional

# ─────────────────────────────────────────────────────────
# 경로 설정
# src/validator.py 기준으로 한 단계 위가 프로젝트 루트.
# 루트 기준으로 data/ 폴더를 찾는다.
# ─────────────────────────────────────────────────────────

_ROOT_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR      = os.path.join(_ROOT_DIR, "data")
_USERS_FILE    = os.path.join(_DATA_DIR, "users.txt")
_BOOKS_FILE    = os.path.join(_DATA_DIR, "books.txt")
_RENTALS_FILE  = os.path.join(_DATA_DIR, "rentals.txt")
_SYSTIME_FILE  = os.path.join(_DATA_DIR, "system_time.txt")

# ─────────────────────────────────────────────────────────
# 상수
# ─────────────────────────────────────────────────────────

_ALLOWED_CATEGORIES = {
    "Fiction", "Science", "History", "Technology",
    "Art", "Philosophy", "Language", "General"
}

_CATEGORY_CODE_MAP = {
    "F": "Fiction",    "S": "Science",      "H": "History",
    "T": "Technology", "A": "Art",          "P": "Philosophy",
    "L": "Language",   "G": "General",
}

# 기획서 이미지에서 확인한 파일별 한글 이름
_FILE_KOREAN_NAME = {
    "users.txt":       "사용자 데이터 파일",
    "books.txt":       "도서 데이터 파일",
    "rentals.txt":     "대여 데이터 파일",
    "system_time.txt": "현재 시간 데이터 파일",
}

# ─────────────────────────────────────────────────────────
# 위반 항목 데이터 클래스
# ─────────────────────────────────────────────────────────

@dataclass
class ViolationItem:
    """문법/의미 규칙 위반 항목 하나."""
    filename: str       # 예: "users.txt"
    line_number: int    # 1-based
    line_content: str   # 해당 줄 원문


# ─────────────────────────────────────────────────────────
# 내부 유틸리티
# ─────────────────────────────────────────────────────────

def _parse_date(s: str) -> Optional[date]:
    """
    YYYY-MM-DD 형식 문자열을 date 객체로 변환.
    형식 오류 또는 존재하지 않는 날짜이면 None 반환.
    기획서 4.1.1: 2000년 이후만 허용.
    """
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', s):
        return None
    y, m, d = s.split('-')
    if int(y) < 2000:
        return None
    try:
        return date(int(y), int(m), int(d))
    except ValueError:
        return None


def _read_lines(filepath: str) -> tuple[bool, list[str]]:
    """
    파일을 UTF-8로 읽어 줄 목록 반환.
    반환: (성공여부, 줄목록)
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            return True, f.read().splitlines()
    except Exception:
        return False, []


def _is_valid_password(pw: str) -> bool:
    """
    비밀번호 문법 규칙 (기획서 4.2.2)
    - 8~16자
    - 숫자/알파벳/!@# 만 허용
    - 숫자, 알파벳, 특수기호 각 최소 1개 포함
    - 동일 문자 3회 이상 연속 금지
    """
    if not (8 <= len(pw) <= 16):
        return False
    if not re.fullmatch(r'[0-9a-zA-Z!@#]+', pw):
        return False
    if not re.search(r'[0-9]', pw):
        return False
    if not re.search(r'[a-zA-Z]', pw):
        return False
    if not re.search(r'[!@#]', pw):
        return False
    if re.search(r'(.)\1\1', pw):
        return False
    return True


def _is_valid_book_id(book_id: str) -> bool:
    """도서번호 문법 규칙 (기획서 4.3.1): C333-22 형식"""
    return bool(re.fullmatch(r'[FSHTAPLG]\d{3}-\d{2}', book_id))


def _is_valid_rental_id(rental_id: str) -> bool:
    """대여번호 문법 규칙 (기획서 4.4.1): R0001~R9999"""
    return bool(re.fullmatch(r'R\d{4}', rental_id))


def _get_saved_system_time() -> Optional[date]:
    """system_time.txt 에 저장된 날짜를 반환한다. 없으면 None."""
    if not os.path.exists(_SYSTIME_FILE):
        return None
    ok, lines = _read_lines(_SYSTIME_FILE)
    if not ok or not lines:
        return None
    return _parse_date(lines[0].strip())


# ─────────────────────────────────────────────────────────
# 공개 API - clibrary.py 에서 직접 호출하는 함수들
# ─────────────────────────────────────────────────────────

def validate_date(date_str: str) -> bool:
    """
    날짜 존재 여부 검사 (기획서 4.1.1)
    - YYYY-MM-DD 형식
    - 실제 존재하는 날짜
    - 2000년 이후
    """
    return _parse_date(date_str) is not None


def validate_date_not_past(date_str: str) -> bool:
    """
    입력 날짜가 system_time.txt 의 마지막 기록일보다 이전이 아닌지 검사.
    (기획서 5.4.2 시간의 비가역성)
    True  → 정상 (같거나 이후)
    False → 오류 (이전 날짜)
    저장된 날짜가 없으면 True 반환 (첫 실행 허용).
    """
    saved = _get_saved_system_time()
    if saved is None:
        return True
    new_date = _parse_date(date_str)
    if new_date is None:
        return False
    return new_date >= saved


def get_saved_system_time_str() -> Optional[str]:
    """
    system_time.txt 에 저장된 날짜 문자열을 반환한다.
    clibrary.py 의 날짜 입력 프롬프트에서 마지막 기록일 표시에 사용.
    저장된 날짜가 없거나 형식이 올바르지 않으면 None 반환.
    """
    saved = _get_saved_system_time()
    if saved is None:
        return None
    return saved.strftime("%Y-%m-%d")


def save_system_time(date_str: str) -> bool:
    """
    검증을 통과한 날짜를 system_time.txt 에 저장한다.
    기존 내용을 덮어쓴다. (기획서 5.4.1 시간의 유일성)
    성공 시 True, 실패 시 False 반환.
    """
    try:
        os.makedirs(_DATA_DIR, exist_ok=True)
        with open(_SYSTIME_FILE, "w", encoding="utf-8") as f:
            f.write(date_str + "\n")
        return True
    except Exception:
        return False


def _exit_with_violations(violations: list[ViolationItem]) -> None:
    """위반 목록을 출력하고 프로그램을 종료한다."""
    for item in violations:
        filepath = os.path.join(_DATA_DIR, item.filename)
        print(f"'{filepath}'가 올바르지 않습니다. 프로그램을 종료합니다.")
        print(f"- 줄: {item.line_number}, 내용: {item.line_content}")
    sys.exit(1)


def check_environment() -> None:
    """
    환경 검사 (기획서 5절)

    - 홈 경로 및 data/ 폴더 확인
    - 4개 파일 존재/권한 확인
    - 문법 규칙 + 의미 규칙 검사 (위반 시 종료)

    프로그램 실행 직후에만 호출된다. (기획서 5.1.3 / 5.2.3 / 5.3.3 / 5.4.2)
    """
    # ── 홈 경로 파악 (기획서 5.1.3 1단계) ──
    if not os.path.exists(_ROOT_DIR):
        print("오류: 홈 경로를 파악할 수 없습니다. 프로그램을 종료합니다.")
        sys.exit(1)

    # ── data/ 폴더 확인 ──
    if not os.path.exists(_DATA_DIR):
        try:
            os.makedirs(_DATA_DIR)
        except Exception:
            print("오류: 홈 경로를 파악할 수 없습니다. 프로그램을 종료합니다.")
            sys.exit(1)

    # ── 4개 파일 존재/권한 확인 ──
    _check_file_fatal(_SYSTIME_FILE, fatal_if_missing=True)
    _check_file_fatal(_USERS_FILE, fatal_if_missing=False)
    _check_file_fatal(_BOOKS_FILE, fatal_if_missing=False)
    _check_file_fatal(_RENTALS_FILE, fatal_if_missing=False)

    # ── 문법 + 의미 규칙 검사 ──
    all_violations = _check_syntax_rule() + _check_semantic_rule()
    if all_violations:
        _exit_with_violations(all_violations)


def _check_file_fatal(filepath: str, fatal_if_missing: bool) -> None:
    """
    파일 존재/권한 확인. 문제 있으면 기획서 메세지 출력 후 즉시 종료.
    fatal_if_missing=False 면 없을 때 빈 파일 생성 시도.
    """
    fname = os.path.basename(filepath)
    korean_name = _FILE_KOREAN_NAME.get(fname, fname)

    if not os.path.exists(filepath):
        if fatal_if_missing:
            # 기획서 5.4.2 image17
            print(f"오류: {korean_name}이 존재하지 않습니다. 프로그램을 종료합니다.")
            sys.exit(1)
        else:
            # 기획서 5.1.3 image28: 경고 → 생성 시도 → 경로 출력
            print(f"경고: {korean_name}이 존재하지 않습니다.")
            try:
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, "w", encoding="utf-8"):
                    pass
                print(f"data\\에 {korean_name}을 생성하였습니다.")
                print(filepath)
                return
            except Exception:
                # 기획서 5.1.3 image42: 생성 실패
                print(f"오류: data\\에 {korean_name}을 생성하지 못했습니다. 프로그램을 종료합니다.")
                sys.exit(1)

    # 권한 확인 (기획서 5.1.3 image65)
    if not os.access(filepath, os.R_OK | os.W_OK):
        print(f"오류: {filepath}에 대한 입출력 권한이 없습니다.")
        print("프로그램을 종료합니다.")
        sys.exit(1)


def _check_syntax_rule() -> list[ViolationItem]:
    """
    문법 규칙 검사 (기획서 5.1.1 / 5.2.1 / 5.3.1 / 5.4)
    위반 항목 목록을 반환한다.
    """
    violations: list[ViolationItem] = []
    violations += _check_syntax_system_time()
    violations += _check_syntax_users()
    violations += _check_syntax_books()
    violations += _check_syntax_rentals()
    return violations


def _check_semantic_rule() -> list[ViolationItem]:
    """
    의미 규칙 검사 (기획서 5.1.2 / 5.2.2 / 5.3.2)
    위반 항목 목록을 반환한다.
    """
    violations: list[ViolationItem] = []
    violations += _check_semantic_users()
    violations += _check_semantic_books()
    violations += _check_semantic_rentals()
    return violations


# ─────────────────────────────────────────────────────────
# 내부 - 파일별 문법 검사
# ─────────────────────────────────────────────────────────

def _check_syntax_system_time() -> list[ViolationItem]:
    """기획서 5.4: YYYY-MM-DD 1줄만 존재해야 함."""
    filename = "system_time.txt"
    ok, lines = _read_lines(_SYSTIME_FILE)
    if not ok:
        return []

    non_empty = [l for l in lines if l.strip()]
    if len(non_empty) != 1 or _parse_date(non_empty[0].strip()) is None:
        content = non_empty[0].strip() if non_empty else ""
        return [ViolationItem(filename, 1, content)]
    return []


def _check_syntax_users() -> list[ViolationItem]:
    """
    users.txt 문법 규칙 (기획서 5.1.1)
    레코드 형식: <ID>/<비밀번호>/<대출정지_종료일> (3필드)

    관리자 여부는 ID가 "admin"인지로 판별한다. (기획서 4.2.1)
    """
    filename = "users.txt"
    ok, lines = _read_lines(_USERS_FILE)
    if not ok:
        return []

    violations = []
    for line_num, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line:
            continue

        parts = line.split('/')
        if len(parts) != 3:
            violations.append(ViolationItem(filename, line_num, line))
            continue

        uid, pw, ban = [p.strip() for p in parts]

        # 아이디: 9자리 숫자 또는 "admin" (기획서 4.2.1)
        if not (re.fullmatch(r'\d{9}', uid) or uid == "admin"):
            violations.append(ViolationItem(filename, line_num, line))
            continue

        # 비밀번호 (기획서 4.2.2)
        if not _is_valid_password(pw):
            violations.append(ViolationItem(filename, line_num, line))
            continue

        # 대출정지 종료일: NONE 또는 유효한 날짜 (기획서 4.2.3)
        if ban != "NONE" and _parse_date(ban) is None:
            violations.append(ViolationItem(filename, line_num, line))

    return violations


def _check_syntax_books() -> list[ViolationItem]:
    """
    books.txt 문법 규칙 (기획서 5.2.1)
    레코드 형식: <도서번호>/<카테고리>/<제목>/<저자>/<현재상태> (5필드)
    """
    filename = "books.txt"
    ok, lines = _read_lines(_BOOKS_FILE)
    if not ok:
        return []

    violations = []
    for line_num, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line:
            continue

        parts = line.split('/')
        if len(parts) != 5:
            violations.append(ViolationItem(filename, line_num, line))
            continue

        book_id, category, title, author, status = [p.strip() for p in parts]

        # 도서번호 (기획서 4.3.1)
        if not _is_valid_book_id(book_id):
            violations.append(ViolationItem(filename, line_num, line))
            continue

        # 카테고리 (기획서 4.3.2)
        if category not in _ALLOWED_CATEGORIES:
            violations.append(ViolationItem(filename, line_num, line))
            continue

        # 카테고리 코드 일치 (기획서 4.3.2 의미규칙)
        if _CATEGORY_CODE_MAP.get(book_id[0]) != category:
            violations.append(ViolationItem(filename, line_num, line))
            continue

        # 제목 (기획서 4.3.3): 최대32자, 숫자/알파벳/한글/공백만, 앞뒤공백불가
        if not title or len(title) > 32 \
                or not re.fullmatch(r'[0-9a-zA-Z가-힣 ]+', title) \
                or title != title.strip():
            violations.append(ViolationItem(filename, line_num, line))
            continue

        # 저자 (기획서 4.3.4): 최대32자, 숫자/알파벳/한글/()/공백만, 앞뒤공백불가
        if not author or len(author) > 32 \
                or not re.fullmatch(r'[0-9a-zA-Z가-힣 ()]+', author) \
                or author != author.strip():
            violations.append(ViolationItem(filename, line_num, line))
            continue

        # 현재상태 (기획서 4.3.5)
        if status not in ("RENTED", "AVAILABLE"):
            violations.append(ViolationItem(filename, line_num, line))

    return violations


def _check_syntax_rentals() -> list[ViolationItem]:
    """
    rentals.txt 문법 규칙 (기획서 5.3.1)
    레코드 형식: <대여번호>/<ID>/<도서번호>/<대여일>/<반납기한>/<실제반납일> (6필드)

    기획서 4.4절 구성 및 5.3.1에 연장횟수 필드가 정의되어 있지 않으므로
    6필드로 구현한다.
    """
    filename = "rentals.txt"
    ok, lines = _read_lines(_RENTALS_FILE)
    if not ok:
        return []

    violations = []
    for line_num, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line:
            continue

        parts = line.split('/')
        if len(parts) != 6:
            violations.append(ViolationItem(filename, line_num, line))
            continue

        rental_id, uid, book_id, rent_date, due_date, return_date = \
            [p.strip() for p in parts]

        # 대여번호 (기획서 4.4.1)
        if not _is_valid_rental_id(rental_id):
            violations.append(ViolationItem(filename, line_num, line))
            continue

        # 아이디: 9자리 숫자만 (기획서 4.4.2 - admin 제외)
        if not re.fullmatch(r'\d{9}', uid):
            violations.append(ViolationItem(filename, line_num, line))
            continue

        # 도서번호 (기획서 4.4.3)
        if not _is_valid_book_id(book_id):
            violations.append(ViolationItem(filename, line_num, line))
            continue

        # 대여일 (기획서 4.4.4)
        if _parse_date(rent_date) is None:
            violations.append(ViolationItem(filename, line_num, line))
            continue

        # 반납기한 (기획서 4.4.5)
        if _parse_date(due_date) is None:
            violations.append(ViolationItem(filename, line_num, line))
            continue

        # 실제반납일 (기획서 4.4.6): NONE 또는 유효한 날짜
        if return_date != "NONE" and _parse_date(return_date) is None:
            violations.append(ViolationItem(filename, line_num, line))

    return violations


# ─────────────────────────────────────────────────────────
# 내부 - 파일별 의미 규칙 검사
# ─────────────────────────────────────────────────────────

def _check_semantic_users() -> list[ViolationItem]:
    """
    users.txt 의미 규칙 (기획서 5.1.2)
    - 같은 ID는 두 개 이상 존재할 수 없다.
    """
    filename = "users.txt"
    ok, lines = _read_lines(_USERS_FILE)
    if not ok:
        return []

    violations = []
    seen: dict[str, int] = {}
    for line_num, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line:
            continue
        parts = line.split('/')
        if len(parts) != 3:
            continue  # 문법 오류는 이미 처리됨
        uid = parts[0].strip()
        if uid in seen:
            violations.append(ViolationItem(filename, line_num, line))
        else:
            seen[uid] = line_num
    return violations


def _check_semantic_books() -> list[ViolationItem]:
    """
    books.txt 의미 규칙
    - 5.2.2: 같은 도서 ID는 두 개 이상 존재할 수 없다.
    - 4.3.1: 같은 prefix(C+333)를 가진 도서들은 같은 도서이므로
            카테고리/제목/저자가 모두 동일해야 한다.
            (suffix 22만 다르고, 나머지가 다른 경우는 위반)
    """
    filename = "books.txt"
    ok, lines = _read_lines(_BOOKS_FILE)
    if not ok:
        return []

    violations = []
    seen_id: dict[str, int] = {}
    # prefix_record: prefix -> (첫 등장 줄번호, 카테고리, 제목, 저자)
    prefix_record: dict[str, tuple[int, str, str, str]] = {}

    for line_num, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line:
            continue

        parts = line.split('/')
        if len(parts) != 5:
            continue  # 문법 오류는 이미 처리됨

        book_id = parts[0].strip()
        category = parts[1].strip()
        title = parts[2].strip()
        author = parts[3].strip()

        if not _is_valid_book_id(book_id):
            continue  # 문법 오류는 이미 처리됨

        # 1) 도서 ID 중복 검사 (5.2.2)
        if book_id in seen_id:
            violations.append(ViolationItem(filename, line_num, line))
            continue
        seen_id[book_id] = line_num

        # 2) 동일 prefix(C+333) 일치성 검사 (4.3.1)
        prefix = book_id[:4]  # 예: 'F001'
        if prefix in prefix_record:
            _, prev_category, prev_title, prev_author = prefix_record[prefix]
            if (category, title, author) != (prev_category, prev_title, prev_author):
                violations.append(ViolationItem(filename, line_num, line))
                continue
        else:
            prefix_record[prefix] = (line_num, category, title, author)

    return violations


def _check_semantic_rentals() -> list[ViolationItem]:
    """
    rentals.txt 의미 규칙 (기획서 5.3.2)
    1. 대여번호 중복 없음
    2. 도서번호가 books.txt 에 존재해야 함
    3. ID가 users.txt 에 존재해야 함
    """
    filename = "rentals.txt"
    ok, lines = _read_lines(_RENTALS_FILE)
    if not ok:
        return []

    users_ids = _parse_user_ids()
    books_ids = _parse_book_ids()

    violations = []
    seen: dict[str, int] = {}

    for line_num, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line:
            continue
        parts = line.split('/')
        if len(parts) != 6:
            continue  # 문법 오류는 이미 처리됨

        rental_id, uid, book_id = [p.strip() for p in parts[:3]]

        # 1. 대여번호 중복
        if rental_id in seen:
            violations.append(ViolationItem(filename, line_num, line))
            continue
        seen[rental_id] = line_num

        # 2. 도서번호가 books.txt에 존재
        if book_id not in books_ids:
            violations.append(ViolationItem(filename, line_num, line))
            continue

        # 3. ID가 users.txt에 존재
        if uid not in users_ids:
            violations.append(ViolationItem(filename, line_num, line))

    return violations


# ─────────────────────────────────────────────────────────
# 내부 - 교차 검증용 파싱 헬퍼
# ─────────────────────────────────────────────────────────

def _parse_user_ids() -> set[str]:
    """users.txt 에서 아이디 목록을 파싱한다. (3필드 구조)"""
    ok, lines = _read_lines(_USERS_FILE)
    if not ok:
        return set()
    result = set()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split('/')
        if len(parts) == 3:
            result.add(parts[0].strip())
    return result


def _parse_book_ids() -> set[str]:
    """books.txt 에서 도서번호 목록을 파싱한다."""
    ok, lines = _read_lines(_BOOKS_FILE)
    if not ok:
        return set()
    result = set()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split('/')
        if len(parts) >= 5:
            result.add(parts[0].strip())
    return result