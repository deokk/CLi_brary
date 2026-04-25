from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
USERS_FILE = DATA_DIR / "users.txt"


def load_users() -> dict[str, tuple[str, str]]:
    users: dict[str, tuple[str, str]] = {}

    if not USERS_FILE.exists():
        return users

    with open(USERS_FILE, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue

            parts = line.split("/")
            if len(parts) != 3:
                continue

            user_id, password, ban_until = parts
            users[user_id] = (password, ban_until)

    return users


def login() -> dict | bool:
    print("\n" + "-" * 50)
    print("[시스템] 로그인 메뉴로 진입했습니다.")
    print("[안내] '0'을 입력하면 언제든지 돌아갈 수 있습니다.")
    print("-" * 50)

    user_id = input("ID를 입력해주세요: ").strip()
    if user_id == "0":
        return False

    password = input("비밀번호를 입력해주세요: ").strip()
    if password == "0":
        return False

    users = load_users()
    if user_id not in users:
        print("ID 혹은 비밀번호가 잘못되었습니다.")
        return False

    saved_password, ban_until = users[user_id]
    if password != saved_password:
        print("ID 혹은 비밀번호가 잘못되었습니다.")
        return False

    # 1. 관리자 로그인
    if user_id == "admin":
        print("관리자 계정으로 로그인 성공!")
        return {"id": user_id}

    # 2. 학생 로그인
    print(f"{user_id} 학생으로 로그인 성공!")

    if ban_until != "NONE":
        print(f"[안내] 현재 대출 정지 상태입니다. 정지 기한 : {ban_until} 까지.")

    return {"id": user_id}

def register() -> None:
    print("\n" + "-" * 50)
    print("[시스템] 회원가입 메뉴로 진입했습니다.")
    print("[안내] '0'을 입력하면 언제든지 돌아갈 수 있습니다.")
    print("-" * 50)

    path_users = USERS_FILE
    path_users.parent.mkdir(parents=True, exist_ok=True)

    # ── 단계 1. ID 입력 ──────────────────────────────────
    while True:
        user_id = input("ID를 설정해주세요 (본인의 학번): ").strip()

        if user_id == "0":
            return

        if not (len(user_id) == 9 and user_id.isdigit()):
            print("ID의 형식이 올바르지 않습니다.")
            continue

        existing_ids = load_users().keys()
        if user_id in existing_ids:
            print("이미 등록된 ID입니다.")
            continue

        break

    # ── 단계 2. 비밀번호 입력 ────────────────────────────
    allowed_special = set("!@#")

    while True:
        password = input("비밀번호를 설정해주세요.\n\n비밀번호 규칙\n1. 숫자+문자+특수기호 !@#의 조합\n2. 8자 ~ 16자\n3. 연속된 문자 3회 미만\n\n비밀번호 입력: ").strip()

        if password == "0":
            return

        has_digit   = any(c.isascii() and c.isdigit() for c in password)
        has_alpha   = any(c.isascii() and c.isalpha() for c in password)
        has_special = any(c in allowed_special for c in password)
        has_invalid = any(
            (not c.isdigit()) and (not c.isalpha()) and (c not in allowed_special)
            for c in password
        )
        is_valid_length = 8 <= len(password) <= 16
        has_triple = any(
            password[i] == password[i + 1] == password[i + 2]
            for i in range(len(password) - 2)
        )

        if has_triple:
            print("같은 문자는 3번 이상 반복될 수 없습니다.")
            continue
        if not is_valid_length:
            print("길이는 8자 이상 16자 이하여야 합니다.")
            continue
        if not has_digit or not has_alpha or not has_special:
            print("숫자, 알파벳, 특수기호(!@#만 허용)는 각각 최소 1개 이상 포함되어야 합니다.")
            continue
        if has_invalid:
            print("허용되지 않은 문자가 포함되었습니다.")
            continue

        break

    # ── 완료 메시지 출력 ─────────────────────────────────
    print("\n회원가입을 완료했습니다!")
    print(f"  ID       : {user_id}")
    print(f"  비밀번호 : {password}")

    existing_content = path_users.read_text(encoding="utf-8").strip() if path_users.exists() else ""

    with open(path_users, "a", encoding="utf-8") as f:
        if existing_content:
            f.write("\n")
        f.write(f"{user_id}/{password}/NONE")
