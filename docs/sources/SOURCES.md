# 데이터 출처 조사표 (승인 게이트)

수집은 **이 표에서 "승인" 처리된 출처만** 한다. 조사일 2026-10-06(Ubuntu 일부), 2026-10-09(전체 robots·접근성). 판정 열은 사람이 채운다.

## 증거 수집 방법
1. 본 조사는 클라우드 환경에서 수행했고, 네트워크 정책 때문에 `ubuntu.com`, `pypi.org` 외 대부분의 도메인이 차단되었다.
   차단된 출처는 **확인불가**로 표시하며, 아래 "사전 지식" 열은 검증되지 않은 가설이다.
2. 직접 PC(WSL2)에서 아래 명령으로 증거(robots.txt 원문, 약관·API 문서 해시와 본문, 응답 코드)를 수집한다.
   ```bash
   pip install pyyaml
   python scripts/probe_sources.py --contact 본인이메일
   # 일부만: --only nvd,osv
   ```
   결과는 `docs/sources/evidence/<id>/<날짜>/`에 저장된다(`probe.json`이 요약).
3. 증거 파일을 읽고 약관·라이선스 조항을 이 표 아래 상세 메모에 **원문 그대로 인용**하여 판정한다.
   `candidates.yaml`의 URL은 기억 기반이라 404가 나올 수 있다. 404는 "경로를 수동으로 찾아야 함"이지 "불가"가 아니다.

## 판정 기준
| 판정 | 의미 |
|---|---|
| 승인 | 자동 수집 허용이 확인되고, 라이선스상 저장·가공에 문제 없음 |
| 조건부 | 키 발급, 호출 한도 준수, 출처 표시, 문서 단위 라이선스 확인 등 조건을 지키면 가능 |
| 제외 | 약관이 자동 수집·재가공을 금지하거나 접근 조건(가입·동의)이 있음 |
| 확인불가 | 접근 못 해서 근거를 못 얻음 → 확인 전까지 수집 금지 |

## 조사표 (robots.txt·접근성 확인 완료 / 약관·라이선스는 미확인)

2026-10-09 PC(WSL)에서 `probe_sources.py` 실행 결과. 증거: `evidence/<id>/2026-10-09/{probe.json,robots_*.txt}`.
약관·라이선스 본문(`page_*.html`)은 저작권 문제로 커밋하지 않았으므로 **본문 기반 항목은 아직 비어 있다**. 아래 "robots" 열은 저장된 robots.txt를 `urllib.robotparser`(UA `opsgraph-source-survey`)로 해석한 결과이다.

| ID | 접근 확인 | robots.txt 해석 | 약관·라이선스 | 한도 | 판정 |
|---|---|---|---|---|---|
| nvd | API 샘플 200 JSON. 약관·API 안내 페이지는 JS 렌더링 셸(2,092 B)만 와서 **본문 미확보** | `nvd.nist.gov/robots.txt`가 HTML(SPA)을 반환 → 유효한 robots 없음. `services.nvd.nist.gov` 404 → 규칙 없음 | 미확인(브라우저로 직접 확인 필요) | 미확인 | 대기 |
| osv | 문서 2종 200, API 샘플 200 JSON | `api.osv.dev`, `google.github.io` 모두 404 → 규칙 없음 | 미확인(`/data/` 페이지 본문 필요) | 미확인 | 대기 |
| kisa-boho | boho.or.kr 200. **www.kisa.or.kr은 SSL 인증서 검증 실패**(PC 환경) | boho·krcert: `googlebot`·`Yeti` 그룹만 있고 `*` 그룹 없음 → 우리 UA에 적용되는 규칙 없음(검색엔진 전용 의도로 보여 약관 확인 필수). kisa.or.kr은 미확보 | 미확인 | - | 대기 |
| data-go-kr | 포털·공공누리 페이지 200 | 두 도메인 모두 `Googlebot` 그룹만 존재 → 우리 UA 규칙 없음 | 미확인(공공누리 유형은 자료별 확인) | 미확인 | 대기 |
| law-go-kr | law.go.kr 200, open.law.go.kr API 안내 200 | law.go.kr: `Allow: /`. open.law.go.kr: robots 경로가 "Page Not Found" HTML → 규칙 없음 | 미확인 | 미확인 | 대기 |
| gov-guidelines | msit·mois·nis·ncsc 메인 200 | msit·mois: 허용(msit는 검색 경로만 금지). **nis.go.kr: `User-agent: *` → `Disallow: /`(검색엔진 일부만 허용) → 수집 불가**. ncsc: robots 대신 오류 HTML → 규칙 없음 | 미확인(문서 단위) | - | **nis 제외**, 나머지 대기 |
| postgresql | 라이선스·보안 페이지 200 | `/docs/devel/` 등 일부 금지, 보안 페이지·`/docs/16/` 허용. Crawl-delay 없음 | 라이선스 페이지 확보(8 KB), 미독 | - | 대기(유력) |
| nginx | LICENSE·보안 권고 200 | `Disallow: /libxslt/`만 → 보안 권고 허용 | 미확인 | - | 대기(유력) |
| ubuntu-security | JSON API 200, IP 정책 페이지 200(미독) | `/security` 허용, Crawl-delay 1 | 미독 | 문서 미확인 | 조건부 후보 |
| debian-security | 라이선스 페이지·JSON 덤프 200 | 두 도메인 robots 404 → 규칙 없음 | 미독 | - | 대기(선택) |
| redhat-security | 약관·API 200 | `User-agent: *`에서 API 경로 허용, **Crawl-delay 10** | 미독 | 문서 미확인 | 대기(선택) |
| cis | 약관 페이지 200 | `Disallow:` 비어 있음(전체 허용), Crawl-delay 10 | 미독(가입·재배포 제한 추정) | - | 제외 가능성 높음 |

## 이번 조사에서 확정된 사실
1. **국정원(nis.go.kr)은 robots.txt가 일반 크롤러를 전부 막는다** → 수집 대상에서 제외한다.
2. **NVD의 약관·FAQ 페이지는 정적 HTML이 아니라 JS 앱**이라 스크립트로 본문을 못 읽는다. API 자체는 정상 응답한다. 약관은 브라우저에서 직접 읽어 조항을 인용해야 한다(Selenium은 약관 읽기용으로 쓰지 않는다).
3. **robots.txt 자리에 HTML이 오는 사이트가 4곳**(nvd.nist.gov, open.law.go.kr, ncsc.go.kr 등)이다. 이는 "허용"의 증거가 아니라 "규칙을 알 수 없음"이므로 약관 근거가 더 중요하다.
4. KISA·KrCERT·공공데이터포털은 robots가 **검색엔진 이름을 지정한 그룹만** 갖고 있다. 규칙상 우리 UA는 제한이 없지만, 검색엔진 색인용 설정이라 자동 수집 허용의 근거가 되지 못한다. 약관과 공공누리 유형 확인이 필수다.
5. Crawl-delay 요구: Ubuntu 1초, Red Hat 10초, CIS 10초. 승인 시 `sources.yaml`의 `min_interval_seconds`에 반영한다.
6. `www.kisa.or.kr`은 이 PC에서 TLS 검증이 실패한다. 인증서 검증을 끄지 말고(`verify=False` 금지), 원인(중간 인증서 누락 여부)을 브라우저에서 확인한 뒤 판단한다.

## 다음에 필요한 입력 (약관·라이선스 판정용)
본문 파일은 올리지 않았으므로, 판정이 필요한 출처의 **조항 원문**이 필요하다. 아래 중 편한 방식을 고르면 된다.
- (a) 우선순위 출처의 해당 조항을 채팅에 붙여넣기: NVD 약관/데이터 이용, OSV `/data/` 라이선스 문단, Ubuntu IP 정책, 공공누리 유형 설명, KISA 이용약관.
- (b) 저장소가 **private**이면 약관·라이선스 페이지 본문(`page_*.html` 중 법적 페이지만)을 커밋해서 제가 직접 읽기.

## 우선순위 제안 (승인 전 가설)
- 1순위: NVD, OSV (취약점의 근간, 공식 API)
- 2순위: 제품 공식 보안 문서(PostgreSQL, Nginx, Ubuntu)
- 3순위: KISA 가이드, 정보보호 지침 PDF (온톨로지의 CheckItem·Clause·Guideline의 근거. 접근성이 불확실하므로 먼저 수동 확인)
- 제외 가능성: CIS(재배포 제한 추정)
