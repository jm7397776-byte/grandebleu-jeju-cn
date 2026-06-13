# 색인 자동화 설정 (한 번만 하면 영구 자동)

매일 새 글이 올라오면 → GitHub Action이 자동으로 구글에 "색인해줘"를 보냅니다.
사장님은 아래 **인증키 발급(1회)** 만 해주시면 됩니다.

> ⚠️ 솔직한 한계: 구글 Indexing API는 원래 "채용공고/방송" 용도라, 일반 블로그 글엔
> 구글이 100% 보장하진 않습니다. 잘 먹히는 경우가 많지만 **보조 수단**으로 보세요.
> 진짜 해결은 `content-strategy/`의 **주제 다양화**입니다.

## 1. 구글 클라우드에서 서비스 계정 만들기
1. https://console.cloud.google.com → 프로젝트 생성(아무 이름)
2. **API 및 서비스 → 라이브러리** → "Indexing API" 검색 → **사용 설정**
3. **API 및 서비스 → 사용자 인증 정보 → 사용자 인증 정보 만들기 → 서비스 계정**
4. 서비스 계정 만들고 → 그 계정의 **키 → 키 추가 → JSON** 다운로드
5. JSON 안의 `client_email`(예: `xxx@yyy.iam.gserviceaccount.com`)을 복사

## 2. 서치 콘솔에 그 계정을 "소유자"로 추가
1. https://search.google.com/search-console → 블로그 속성 선택
2. **설정 → 사용자 및 권한 → 사용자 추가**
3. 위 `client_email` 붙여넣기 → 권한 **소유자(Owner)** 로 추가

## 3. GitHub 비밀값(Secret) 등록
1. 이 저장소 → **Settings → Secrets and variables → Actions → New repository secret**
2. 이름: `GOOGLE_INDEXING_SA_JSON`
3. 값: 1번에서 받은 **JSON 파일 내용 전체** 붙여넣기 → 저장

## 4. 끝 — 동작 확인
- 매일 09:30 UTC(약 18:30 KST)에 자동 실행됩니다.
- 지금 바로 테스트하려면: 저장소 **Actions 탭 → "Auto-request Google indexing" → Run workflow**
- 로그에 `OK  https://...` 가 뜨면 색인 요청 성공입니다.

## 참고
- 대상 sitemap은 `.github/workflows/auto-index.yml`의 `BLOG_SITEMAP`에서 바꿀 수 있습니다.
- 비밀값을 안 넣으면 워크플로는 그냥 조용히 건너뜁니다(에러 안 남).
