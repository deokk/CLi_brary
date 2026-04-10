# src/validator.py
import re
from datetime import date

def validate_date(date_str: str) -> bool:
    """
    [문법 및 의미 규칙] 날짜 입력 검사
    1. YYYY-MM-DD 형태인지 정규식 검사
    2. 13월 45일 같은 가짜 날짜가 아닌지 실제 달력 의미 검사
    """
    # 1. 문법 검사 (YYYY-MM-DD 형식)
    if not re.fullmatch(r"^\d{4}-\d{2}-\d{2}$", date_str):
        return False
        
    # 2. 의미 검사 (실제 존재하는 날짜인지 datetime 객체로 확인)
    y, m, d = map(int, date_str.split('-'))
    try:
        date(y, m, d)
        return True
    except ValueError:
        return False

def check_environment():
    """환경 검사 (데이터 폴더 및 필수 파일 존재 여부 등 무결성 검사)"""
    print("\n--------------------------------------------------")
    print("🛠️ [시스템] '환경 검사(무결성 검사)' 기능은 현재 구현 중입니다.")
    print("--------------------------------------------------")
    pass # 메인 로직 실행을 위해 일단 통과시킵니다.

def check_syntax_rule():
    """문법 규칙 검사 (학번 정규식, 도서 ID 규격 등 형태 검사)"""
    print("\n--------------------------------------------------")
    print("🛠️ [시스템] '문법 규칙 검사' 기능은 현재 구현 중입니다.")
    print("--------------------------------------------------")
    return True

def check_semantic_rule():
    """의미 규칙 검사 (존재하지 않는 날짜, 시간 역행 등 논리 검사)"""
    print("\n--------------------------------------------------")
    print("🛠️ [시스템] '의미 규칙 검사' 기능은 현재 구현 중입니다.")
    print("--------------------------------------------------")
    return True