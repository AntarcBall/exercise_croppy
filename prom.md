아래는 첨부된 교과서 패턴에 맞춰 로컬에서 바로 구현할 수 있는 코딩 프롬프트입니다. Claude, ChatGPT, 또는 Cursor/Copilot에 복사해서 사용하면 즉시 실행 가능한 스크립트를 얻을 수 있습니다.[1][2][3][4]

***

## 코딩 프롬프트

```
# 목표
600페이지 이상의 과학 교과서 PDF에서 "Sample Exercise" 섹션만 자동으로 추출하여, 
벡터·텍스트·배경을 유지한 상태로 새로운 PDF 파일에 모아주는 Python 스크립트를 작성하라.

# 요구사항

## 1. 입력/출력
- 입력: 로컬 경로의 PDF 파일 (예: "textbook.pdf")
- 출력: "sample_exercises_extracted.pdf" 파일로 저장
- 텍스트가 복사 가능한 PDF (OCR 불필요)

## 2. 섹션 패턴 (첨부 이미지 참조)
- 헤더: 녹색 그라디언트 배경 박스, 상단에 흰색 텍스트 "Sample Exercise X.Y" 형식
- 번호 형식: "Sample Exercise 13.9", "Sample Exercise 13.11" 등 (챕터.번호)
- 구조: 헤더 → 문제 → SOLUTION → Analyze/Plan/Solve → Comment → Practice Exercise
- 섹션은 테두리 박스로 감싸져 있고, 다음 "Sample Exercise"까지가 한 섹션

## 3. 핵심 기능
- PyMuPDF(fitz) 라이브러리를 사용
- 각 페이지에서 "Sample Exercise" 키워드를 정규식으로 탐색 (대소문자 무관, 줄바꿈 허용)
- 탐지한 헤더의 좌표를 시작점으로, 다음 "Sample Exercise" 또는 페이지 끝을 종료점으로 설정
- show_pdf_page()의 clip 파라미터로 해당 영역만 새 PDF에 삽입 (벡터·텍스트 유지)
- 각 섹션을 새 페이지로 분리하여 배치

## 4. 예외 처리
- "Sample Exercise" 문자열이 줄바꿈으로 분리된 경우 ("Sample\nExercise") 처리
- 페이지 경계를 넘는 긴 섹션은 다음 페이지 상단까지 포함
- 헤더가 아닌 본문에 "Sample Exercise"가 언급된 경우 필터링 (폰트 크기/색상 확인)

## 5. 코드 구조
```
import fitz  # PyMuPDF
import re

# PDF 열기
pdf_path = "textbook.pdf"
doc = fitz.open(pdf_path)
output_doc = fitz.open()

# 정규식: "Sample Exercise" + 번호
pattern = re.compile(r"Sample\s+Exercise\s+\d+\.\d+", re.IGNORECASE)

# 각 페이지 순회
for page_num in range(len(doc)):
    page = doc[page_num]
    
    # 1. 키워드 검색
    # 2. bbox 좌표 추출
    # 3. 다음 섹션까지 영역 계산
    # 4. show_pdf_page()로 새 PDF에 삽입
    
# 저장
output_doc.save("sample_exercises_extracted.pdf", garbage=3, deflate=True)
output_doc.close()
doc.close()
```

## 6. 추가 기능 (선택)
- 진행 상황 표시 (tqdm 사용)
- 추출된 섹션 개수 로그
- bbox 시각화 모드: 탐지된 영역을 rect로 표시한 미리보기 PDF 생성
- 실패한 섹션 리스트 출력 (헤더는 찾았지만 경계 설정 실패 등)

## 7. 중요 제약
- 이미지로 렌더링하지 말 것 (픽스맵 변환 금지)
- 텍스트 선택 가능 상태 유지
- 원본 레이아웃(녹색 박스, 아이콘, 수식 벡터) 보존
- 600페이지 처리 시간 5분 이내 목표

## 8. 테스트 시나리오
- 10페이지 샘플 PDF로 먼저 테스트
- "Sample Exercise" 개수가 예상과 일치하는지 확인
- 출력 PDF에서 텍스트 복사 가능 여부 확인
- 배경색/아이콘이 온전히 유지되는지 시각 검증

# 출력 형식
- 전체 실행 가능한 Python 스크립트 (.py 파일)
- 주석으로 각 단계 설명
- 필요한 라이브러리 설치 명령어 포함 (pip install PyMuPDF)
```

***
