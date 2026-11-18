# ptlresearch.com 관리 도구

홈페이지 저장소: github.com/houseofdavid1/houseofdavid1.github.io (GitHub Pages → www.ptlresearch.com)

**백업:** 이 폴더의 파일은 Project(homepage-tools/)와 저장소의 `tools/` 폴더 두 곳에 같은 내용으로 보관함. 저장소 쪽은 변경 기록(git)도 남음.

## 파일
- `gen_research.py` — Research 페이지(research.html) 생성기. 연구 내용(탭·블록·글·그림·논문 번호)과 화면 구성이 모두 이 파일 안에 있음.
  - `main=V("NAME", "설명")` 대표 동영상 · `main=F(...)` 대표 그림 · `main=[V(..), V(..)]` 대표 두 개를 글 위에 나란히
  - 데모 동영상은 `FORCE_STACK`(글 위 배치)과 `HMAX`(504 → 폭 896px)에 이름을 넣음
- `ktx.js` — 수식(KaTeX) 미리 렌더링 보조 스크립트. 처음 한 번 이 폴더에서 `npm install katex@0.16.11` 필요 (Node.js 필요).
- `watermark_demos.py` — 데모 동영상 6편(+포스터)에 워터마크를 파일로 새기는 스크립트. 사용: `python3 watermark_demos.py <저장소 경로>`
- `blur_home_code.py` — Home 동영상의 코드 창 글자를 흐리게 하는 스크립트 (아래 "Home 첫 화면 동영상" 참고).
- `vbuild_reference.py` — 동영상 캡션 띠 스타일 참고용 (그대로 실행되지 않음).
- `ht_duo_reference.py` — Process Monitoring 03의 열처리 합성 동영상(ht-duo.mp4) 제작 참고용 (그대로 실행되지 않음).
- `demo_kit_reference.py`, `demos_reference.py`, `fdtd_demo_reference.py` — 여러 영상·그림을 장면별 설명과 함께 한 편으로 엮은 "데모" 동영상 제작 스크립트 (참고용, 원본 소스 파일 경로가 작업 환경 기준이라 그대로 실행되지 않음).

## 데모 동영상 (여러 영상·그림 + 장면별 설명을 한 편으로)
- 1600×900, 장면마다 제목·설명·단계 표시(01, 02 …), 장면 사이 어둡게 전환. 영상 안 글자는 영어.
- 현재 6편: Process Monitoring 01 `ai-monitor-demo`, 02 `ai-bead-demo` · Simulation 02 `sim-fdtd-demo`, 07 `sim-fsi-demo` · Laser Processing 01 `weld-keyhole-demo`, 03 `weld-foil-demo`
- 데모로 합친 원래 영상·그림 파일은 저장소에서 지웠음 (필요하면 git 기록에서 되살릴 수 있음).

## Research 수정 순서
1. 저장소를 내려받음: `git clone https://github.com/houseofdavid1/houseofdavid1.github.io`
2. `gen_research.py`의 TABS에서 해당 블록을 고침 (새 그림은 `assets/research/fig-NAME.jpg`로 저장)
3. 실행 (gen_research.py와 ktx.js가 같은 폴더에 있어야 함): `python3 gen_research.py houseofdavid1.github.io` → research.html이 다시 만들어짐
   - 저장소 안에서 바로 실행: `cd tools && npm install` (처음 한 번) → `cd .. && python3 tools/gen_research.py .`
4. 화면 확인 후 커밋·푸시 → 1–2분 뒤 사이트에 반영

## 저장소 안에서 직접 고치는 파일 (생성기 없음)
- `assets/news.js` — Home 연구실 소식
- `assets/member-pubs.js` — 재학생 카드 팝업의 논문 목록 (publications.html에서 자동 추출해 만든 것)
- `assets/member-patents.js` — 학생 팝업의 특허 목록 (특허 먼저, 논문 다음 순서로 표시). Publications 페이지에는 넣지 않음.
- `people.html` — 졸업생 표(학위·Thesis·논문·특허 팝업 내용 포함)
- `sitemap.xml`, `robots.txt` — 검색엔진용

## 이미지·동영상 보호 (모든 페이지)
- `assets/view.js` 맨 아래: 그림·동영상에서 마우스 오른쪽 버튼("다른 이름으로 저장")과 끌어서 저장 차단, 동영상의 다운로드·PIP 버튼 제거. `assets/style.css` 맨 아래: 휴대폰에서 길게 눌러 저장 차단.
- 억지 효과만 있음: 화면 캡처, 개발자 도구, 공개 저장소(GitHub)에서 직접 받는 것은 막을 수 없음.
- **워터마크** "© Laser Processing & AI Lab · UNIST" — 캡처해도 출처가 남도록 항상 표시됨 (캡처할 때만 나타나게 하는 것은 웹에서 불가능).
  - 화면 워터마크: Research의 모든 그림·동영상(크게 보기 창 포함)과 Home 동영상 위에 반투명 글자. 파일은 그대로. 끄기: `gen_research.py`에서 `WATERMARK = False`로 바꿔 다시 생성하고, `index.html`의 `<span class="wm">` 한 줄 삭제 (또는 `style.css`에 `.wm { display: none; }` 한 줄 추가).
  - 파일에 새긴 워터마크: 데모 동영상 6편과 포스터(오른쪽 위 띠). `watermark_demos.py`로 만듦. 되돌리기: 저장소에서 `git checkout 360af67 -- assets/research/이름.mp4 assets/research/이름.jpg` (6편 각각), 그리고 `gen_research.py`의 `WM_BURNED`를 비우고 다시 생성.

## Home 첫 화면 동영상 — 코드 창 흐림
- `assets/video/home-demo.mp4`(+포스터)의 "AI-GENERATED CODE" 창 안 글자만 흐리게 처리함(코드 유출 방지). 나머지 화면은 원래와 같은 화질(같은 원본·같은 인코딩 설정). `blur_home_code.py`로 만듦.
- **원본(코드가 선명한 영상) 보관:** 교수님께 파일로 전달함 — `home-demo_ORIGINAL_2.2MB.mp4`(사이트에 쓰던 것), `home-demo_ORIGINAL_HQ_5MB.mp4`(고화질), `home-demo-poster_ORIGINAL.jpg`. 공개 저장소에는 다시 올리지 않음. (예전 저장소 기록 20a48d3·91b0a96에도 남아 있음)
- **선명한 영상으로 되돌리기:** 원본 파일을 `assets/video/home-demo.mp4`, `assets/video/home-demo-poster.jpg`로 덮어쓰고 `index.html`의 두 `?v=` 번호를 하나씩 올림.

## 방문자 통계
- GoatCounter (계정 이름 ptlresearch, 대시보드 https://ptlresearch.goatcounter.com).
- 각 페이지 맨 아래의 보이지 않는 1픽셀 이미지(`class="gc-px"`)로 집계. 자바스크립트 없음, 쿠키 없음.
- 새 페이지를 만들면 같은 이미지 한 줄을 `</body>` 앞에 넣을 것 (`?p=/페이지이름`).

## 주의
- **Research를 수정할 때마다 `gen_research.py`를 Project와 저장소 `tools/` 두 곳 모두 같은 내용으로 갱신할 것.** 이 파일이 Research 페이지의 원본(마스터)이며, 자동으로 동기화되지 않음.
- research.html은 생성 결과물이므로 직접 고치지 말 것 (다음 실행 때 덮어써짐).
- 논문 원고(docx·PDF)와 특허증 PDF는 공개 저장소에 올리지 않음 (특허증에는 개인정보가 있음).
- 이메일 주소는 이미지나 난독화 형태로만 표시.
