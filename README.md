# Opensource_patchnote_agent
# 프로젝트: 소프트웨어 릴리스·취약점 변경 추적 지식그래프 + GraphRAG

## 1. 배경과 목적
IT 채용 포트폴리오용 개인 프로젝트다. 오픈소스 패키지의 릴리스 노트, 의존성, 취약점(CVE) 정보를
자동 수집해 지식그래프로 구축하고, 다단계 관계 질문에 답하는 GraphRAG 시스템을 만든다.
핵심 주장은 "관계와 시간이 얽힌 질문에서는 벡터 RAG보다 GraphRAG가 낫다"를 정량 평가로 입증하는 것이다.

대표 질문 예시:
- "pandas 2.0으로 올리면 영향받는 의존 패키지와 breaking change는?"
- "특정 CVE에 영향받는 버전 범위와 수정된 버전은?"
- "A 패키지의 최근 1년 breaking change를 모두 알려줘"

## 2. 환경과 제약
- OS: Windows. Airflow는 네이티브 실행이 안 되므로 Docker Compose(또는 WSL2)로 구성한다.
- 언어: Python 3.11+, 개발은 Jupyter 노트북이 아니라 `src/` 모듈 구조로 하되, 확인용 노트북은 `notebooks/`에 둔다.
- 저장소: 원본·정제 데이터는 PostgreSQL, 그래프는 Neo4j(Docker), 임베딩은 pgvector를 우선 검토한다.
- 대상 패키지는 설정 파일(`config/packages.yaml`)로 관리하고, 초기에는 5개 이내로 시작한다
  (예: apache-airflow, sqlalchemy, pandas, pydantic, fastapi).
- 수집 윤리: robots.txt와 각 사이트 약관을 준수하고, 호출 간격 제한과 캐싱을 구현한다.
  가능하면 공식 API(PyPI JSON API, GitHub REST API, OSV.dev API)를 우선 쓰고,
  Selenium 크롤링은 API가 없는 공식 문서 changelog에만 제한적으로 쓴다.
- 비밀값(API 키, DB 비밀번호)은 `.env`로 분리하고 커밋하지 않는다.
- 도메인 교체가 가능하도록 수집기(collector), 스키마, 온톨로지를 분리해 설계한다.

## 3. 아키텍처
수집(collectors) → 원본 적재(PostgreSQL raw) → 정제·정규화 →
엔티티·관계 추출(LLM, 구조화 출력) → 그래프 적재(Neo4j) + 임베딩 →
질의 계층(Vector RAG / GraphRAG) → 평가 → Airflow로 일 단위 증분 수집

## 4. 온톨로지 초안 (설계 단계에서 검토·수정할 것)
- 노드: Package, Version, ReleaseNote, Change(유형: breaking/feature/fix/deprecation),
  Vulnerability(CVE), Dependency
- 관계: HAS_VERSION, DEPENDS_ON(버전 제약 포함), INTRODUCES, REMOVES,
  AFFECTS(Vulnerability→Version 범위), FIXED_IN, NEXT_VERSION
- 모든 노드와 관계에 `source_url`, `collected_at` 속성을 두어 근거 추적을 가능하게 한다.

## 5. 진행 방식 (중요)
1. 먼저 코드를 쓰지 말고 아래 단계별 계획과 디렉터리 구조, 의존성 목록, 위험 요소를 제시하고 내 승인을 받는다.
2. 한 번에 한 단계만 구현한다. 단계가 끝나면 실행 방법, 검증 결과, 다음 단계를 요약하고 멈춘다.
3. 각 단계마다 최소한의 테스트(pytest)와 재현 가능한 실행 명령을 제공한다.
4. 모듈 단위로 작고 의미 있는 git commit을 만든다.
5. 불확실한 설계 결정(예: pgvector vs 별도 벡터DB, LLM 추출 모델)은 임의로 정하지 말고 선택지와 트레이드오프를 제시한다.

## 6. 단계 계획 (각 단계는 별도 요청으로 진행)
- **Phase 0**: 저장소 구조, Docker Compose(PostgreSQL, Neo4j, Airflow), 설정·로깅·.env 템플릿
- **Phase 1**: 수집기 3종(PyPI, GitHub Releases, OSV) + PostgreSQL 원본 스키마 + 증분 수집(중복 방지)
- **Phase 2**: 릴리스 노트에서 Change 엔티티 추출(LLM 구조화 출력, 스키마 검증, 추출 실패 재시도)과 정규화
- **Phase 3**: 온톨로지 확정, Neo4j 적재 파이프라인, 제약조건·인덱스, 샘플 Cypher 질의 모음
- **Phase 4**: 임베딩 생성·저장, Vector RAG 베이스라인, GraphRAG(그래프 탐색 + 근거 경로 반환)
- **Phase 5**: 평가셋(질문 30~50개, 정답과 근거 포함) 작성, Vector RAG vs GraphRAG 비교
  (정답률, 근거 추적 가능성, 응답 시간), 결과 표와 실패 사례 분석
- **Phase 6**: Airflow DAG(수집→적재→추출→그래프 갱신), 간단한 질의 UI(Streamlit 등) 또는 CLI
- **Phase 7**: README(아키텍처 다이어그램, 온톨로지 설계 근거, 도메인 교체 방법, 수집 윤리, 한계)와 데모 시나리오

## 7. 지금 요청
위 내용을 바탕으로 **Phase 0~1에 대한 구체적인 구현 계획**만 먼저 제시해줘.
코드는 내 승인 후에 작성한다.
