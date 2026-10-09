# 설치·기동 (Phase 0)

전제: Windows 11 + WSL2(Ubuntu) + Docker Desktop(WSL 통합 켜기), Git. RAM 8GB면 아래 `.wslconfig`를 먼저 설정한다.

```ini
# %UserProfile%\.wslconfig   (설정 후 PowerShell에서 wsl --shutdown)
[wsl2]
memory=6GB
swap=4GB
```

## 1. 코드와 Python 환경 (WSL Ubuntu 터미널)
```bash
cd ~ && git clone <저장소 URL> opsgraph && cd opsgraph
git checkout claude/zealous-bohr-081jz8
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## 2. 비밀값
```bash
cp .env.example .env && chmod 600 .env
# 모든 change-me를 서로 다른 강한 값으로 교체. HTTP_CONTACT에는 본인 이메일.
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"  # AIRFLOW_FERNET_KEY (cryptography 필요: pip install cryptography)
```

## 3. 사전 점검과 기동
```bash
bash scripts/preflight.sh
docker compose up -d --wait postgres neo4j
docker compose --profile airflow up -d --build --wait     # Airflow(선택)
```

## 4. 검증
```bash
pytest                         # 단위 테스트
pytest -m integration          # DB 권한 매트릭스 (DB가 떠 있어야 함. .env를 자동 로드)
set -a; . ./.env; set +a
docker compose exec postgres psql -U "$POSTGRES_SUPERUSER" -d "$POSTGRES_DB" -c "SELECT extname FROM pg_extension;"   # vector
docker compose exec postgres psql -U "$POSTGRES_SUPERUSER" -d "$POSTGRES_DB" -c "\du"                             # 4개 역할
docker compose ps                                                                                                  # healthy 확인
```
Neo4j 브라우저: http://localhost:7474 (loopback 전용). 초기화 스크립트를 다시 실행하려면 `docker compose down -v`(데이터 삭제).

## 5. 출처 조사 (승인 게이트)
`docs/sources/SOURCES.md`의 절차대로 `python scripts/probe_sources.py --contact 이메일`을 실행한다.
