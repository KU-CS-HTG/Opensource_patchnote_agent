# 데이터 출처 조사표 (승인 게이트)

수집은 **이 표에서 "승인" 처리된 출처만** 한다. 조사일 2026-10-06. 판정 열은 사람이 채운다.

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

## 조사표

| ID | 출처 | 제공 방식(사전 지식, 미검증) | robots.txt | 약관·라이선스 | 한도 | 현재 상태 | 판정 |
|---|---|---|---|---|---|---|---|
| nvd | NVD CVE API 2.0 | 공식 REST API, API 키 선택 | 확인불가 | 확인불가 | 확인불가 | 확인불가(차단) | 대기 |
| osv | OSV.dev | 공식 API + 벌크 덤프 | 확인불가 | 확인불가(DB별 라이선스 상이 가능성) | 확인불가 | 확인불가(차단) | 대기 |
| kisa-boho | KISA/KrCERT 보호나라 | API 여부 불명, HTML 게시판 가능성 | 확인불가 | 확인불가 | - | 확인불가(차단) | 대기 |
| data-go-kr | 공공데이터포털 | 파일·Open API, 공공누리 유형 표기 | 확인불가 | 확인불가 | 확인불가 | 확인불가(차단) | 대기 |
| law-go-kr | 국가법령정보센터 Open API | 행정규칙 API 존재 가능성 | 확인불가 | 확인불가 | 확인불가 | 확인불가(차단) | 대기 |
| gov-guidelines | 과기정통부·행안부·국정원·NCSC 지침 | PDF/HTML 문서 | 확인불가 | 문서 단위 확인 필요 | - | 확인불가(차단) | 대기 |
| postgresql | PostgreSQL 공식 보안 문서 | HTML | 확인불가 | 확인불가 | - | 확인불가(차단) | 대기 |
| nginx | Nginx 보안 권고 | HTML | 확인불가 | 확인불가 | - | 확인불가(차단) | 대기 |
| ubuntu-security | Ubuntu Security CVE API | JSON API (`/security/cves.json`) | **확인됨**(아래) | **미확인**(약관 페이지 접근 실패) | 문서상 한도 미확인 | 일부 확인 | 조건부 후보 |
| debian-security | Debian Security Tracker | JSON 덤프 | 확인불가 | 확인불가 | - | 확인불가(차단) | 대기(선택) |
| redhat-security | Red Hat Security Data API | 공식 REST API | 확인불가 | 확인불가 | 확인불가 | 확인불가(차단) | 대기(선택) |
| cis | CIS Benchmarks | PDF, 가입·동의 필요 추정 | 확인불가 | 확인불가 | - | 확인불가(차단) | 제외 가능성 높음 |

## 상세 메모

### ubuntu-security (2026-10-06 확인분)
- 증거: `evidence/ubuntu-security/2026-10-06/` (robots 원문, probe.json).
- `https://ubuntu.com/robots.txt` HTTP 200. `User-Agent: *`의 Disallow는 `/search`, `/account`, `/login`, `/pro/...` 등이며
  `Allow: /security`와 `Crawl-delay: 1` 및 `Crawl-delay: 2` 그룹이 존재한다(어느 그룹이 우리 UA에 적용되는지는 증거 파일에서 확인).
  파서 결과: `https://ubuntu.com/security/cves.json?limit=1`은 robots상 허용, crawl_delay=1.
- `GET https://ubuntu.com/security/cves.json?limit=1` HTTP 200, `application/json`. 인증 불필요. 응답 구조는 `{"cves":[{id, published, updated_at, description, ...}]}`.
- **미확인**: 데이터 재사용 라이선스. IP 정책 페이지(`/legal/terms-and-policies/intellectual-property-policy`)는 프록시 403으로 읽지 못했다. PC에서 확인 필요.
- **미확인**: API 호출 한도 명시 여부(`documentation.ubuntu.com/security/` 문서는 접근되었으나 조항 확인은 아직 안 함).
- 판정 제안: 라이선스 확인 전까지 "조건부 후보". 승인 시 호출 간격은 robots의 crawl-delay 이상(1 req/s 이하)으로 둔다.

### 나머지 출처
증거 수집 후 같은 형식으로 추가한다. 각 출처마다 아래 4가지를 반드시 인용한다.
1. 자동 수집(스크레이핑·API 호출)에 관한 조항
2. 저장·재가공·재배포에 관한 조항(공공누리면 유형 1~4 중 무엇인지, 변경금지·상업금지 여부)
3. robots.txt 중 우리가 접근할 경로에 대한 규칙과 Crawl-delay
4. API 키 요구, 호출 한도

## 우선순위 제안 (승인 전 가설)
- 1순위: NVD, OSV (취약점의 근간, 공식 API)
- 2순위: 제품 공식 보안 문서(PostgreSQL, Nginx, Ubuntu)
- 3순위: KISA 가이드, 정보보호 지침 PDF (온톨로지의 CheckItem·Clause·Guideline의 근거. 접근성이 불확실하므로 먼저 수동 확인)
- 제외 가능성: CIS(재배포 제한 추정)
