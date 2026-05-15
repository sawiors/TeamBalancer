# Team Balancing

발로란트/리그오브레전드(LoL) 5 vs 5 팀 밸런싱 GUI 프로그램입니다.

## 주요 기능

- 게임 선택: 발로란트, 리그오브레전드
- 모드 선택: 팀 구성(정확히 10명), 팀 모집(후보에서 최적 10명 선발)
- 닉네임 + 티어 기반 점수화 후 팀 간 점수 차이 최소 조합 계산
- 모집 모드에서 확정 인원(잠금) 지원
- 결과 패널 캐시/복원 및 다중 후보 결과 표시

발로란트 전용 옵션:

- 동일 포지션 3명 이상 방지 옵션

LoL 전용 규칙:

- 탑/정글/미드/원딜/서폿 포지션을 팀별 1명씩 맞추는 5:5 고정 분할

## 라이선스

이 프로젝트는 MIT 라이선스를 사용합니다.

- 상업적/비상업적 이용, 수정, 배포, 판매 모두 제한 없이 가능합니다.
- 자세한 내용은 LICENSE 파일을 확인하세요.

## 의존성 라이선스 안내

런타임 직접 의존성은 `customtkinter` 하나이며,
함께 사용되는 `darkdetect`, `packaging`까지 확인한 결과 강한 카피레프트(GPL/AGPL) 강제는 없습니다.

참고:

- EXE 빌드에 사용하는 `pyinstaller`는 GPLv2 계열이지만, 상용/비공개 프로그램 배포를 허용하는 예외 조항이 함께 제공됩니다.
- 빌드 보조 패키지(`pyinstaller-hooks-contrib`)는 Apache-2.0/GPLv2 신호가 함께 존재하므로, 릴리스 시점에 버전 고정 상태로 재검토하는 것을 권장합니다.

- 요약 문서: THIRD_PARTY_LICENSES.md
- 향후 추가 정책: LICENSE_POLICY.md

주의:

- 배포 시에는 프로젝트 LICENSE(MIT)와 함께 서드파티 라이선스 고지를 포함하는 것을 권장합니다.
- 의존성 버전이 바뀌면 라이선스 조건도 달라질 수 있으므로 릴리스 전 재확인이 필요합니다.

## 설치

1. Python 3.10+ 설치
2. 아래 명령 실행 (런타임 의존성)

```bash
pip install -r requirements.txt
```

## 실행

```bash
python main.py
```

실행하면 메인 화면이 열리고, 발로란트 버튼 클릭 시 팀 구성 화면으로 이동합니다.

## 테스트

현재 순수 로직 경계에 대한 단위 테스트가 포함되어 있습니다.

- 입력 어댑터/입력 파이프라인: tests/test_input_pipeline.py
- 계산 서비스 경계: tests/test_team_services.py
- 결과 캐시 경계: tests/test_result_cache.py
- 결과 텍스트 렌더링: tests/test_result_renderer_text.py

전체 테스트 실행:

```bash
python -m unittest tests.test_input_pipeline tests.test_team_services tests.test_result_cache tests.test_result_renderer_text
```

개별 테스트 실행 예시:

```bash
python -m unittest tests.test_input_pipeline
python -m unittest tests.test_team_services
python -m unittest tests.test_result_cache
python -m unittest tests.test_result_renderer_text
```

권장 검증 순서:

1. 코드 변경 후 단위 테스트 실행
2. 필요 시 python -c "import app; print('OK')"로 앱 import 확인
3. UI 변경이 있었다면 실제 화면에서 모드 전환/결과 복원까지 수동 확인

## EXE 빌드 (선택)

원한다면 exe로 빌드할 수 있습니다.

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name TeamBalancing main.py
```

빌드 후 실행 파일:

- dist/TeamBalancing.exe

## 티어 점수화 규칙

랭크 매핑:

- 아이언=0, 브론즈=1, 실버=2, 골드=3, 플래티넘=4, 다이아몬드=5, 초월자=6, 불멸=7, 레디언트=8

수식:

- 일반 티어: 3 * R + T - 1
- 레디언트: 3 * R

예시:

- 아이언1: 3 * 0 + 1 - 1 = 0
- 골드2: 3 * 3 + 2 - 1 = 10
- 레디언트: 3 * 8 = 24
