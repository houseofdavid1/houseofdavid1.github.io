"""ptlresearch.com Research 페이지 생성기 (research.html의 <main> 부분을 다시 만듦)

사용법:  python3 gen_research.py <저장소 경로>      예) python3 gen_research.py houseofdavid1.github.io
필요:    Python 3, Pillow (pip install pillow)

- 연구 내용은 아래 TABS 목록에 있음: 탭(dict) → blocks(연구 블록) → text(초록 문단 목록), main/side 그림, pubs(논문 번호)
- 그림: <repo>/assets/research/fig-NAME.jpg  → F("NAME", "설명")
- main=[V(..), V(..)] → 대표 그림 두 개를 글 위에 같은 높이로 나란히 배치 (PAIR_H)
  동영상: <repo>/assets/research/NAME.mp4 (+ 포스터 NAME.jpg) → V("NAME", "설명")
- pubs의 번호는 publications.html의 data-n 번호 (제목·저자·저널은 거기서 자동으로 가져옴)
- 화면 구성(블록마다 같음): 제목 → 대표 그림(main, 좌우 번갈아 배치, 글이 그림을 둘러쌈) + 초록(text)
         → "그림 더 보기" 버튼을 누르면 나머지 그림(side)만 펼쳐짐 (side가 없으면 버튼 없음)
         → 수식 상자(EQ)는 접지 않고 항상 표시 → 관련 논문(pubs, 기본으로 접힘)이 블록 맨 아래
- stats=[...], spec="..." → 현재 화면에 표시하지 않음 (핵심 수치·실험 조건 메모용)
- FLOAT_H, FLOAT_W, TOP_H, GAL_H → 대표 그림·펼친 그림의 최대 크기 / STACK_AR → 이보다 가로로 긴 대표 그림은 글 위에 배치
- 수식 상자: EQ = {...}  (TAGS는 현재 화면에 표시하지 않음)
- research.js, style.css 버전 번호(?v=)를 바꾸면 브라우저 캐시가 갱신됨
"""
import re, html, sys, json, subprocess, os
from PIL import Image

R = sys.argv[1]
MD = R + "/assets/research/"
M = "assets/research/"
E = html.escape

pubs_html = open(R + "/publications.html", encoding="utf-8").read()
PUB = {}
for n, li in re.findall(r'<li data-n="(\d+)"[^>]*>(.*?)</li>', pubs_html, re.S):
    title = html.unescape(re.sub(r"<[^>]+>", "", re.search(r'<span class="pub-title">(.*?)</span>', li, re.S).group(1))).strip()
    venue = re.search(r'<span class="pub-venue">(.*?)</span>', li, re.S).group(1)
    jr = re.search(r"<em>(.*?)</em>", venue)
    jr = html.unescape(jr.group(1)) if jr else ("Submitted" if "Submitted" in venue else "")
    yr = re.search(r"\((\d{4})", html.unescape(re.sub(r"<[^>]+>", "", venue)))
    doi = re.search(r'href="(https://doi\.org/[^"]+)"', li)
    au = re.search(r'<span class="pub-authors">(.*?)</span>', li, re.S)
    au = re.sub(r"\s+", " ", au.group(1)).strip() if au else ""   # keeps <strong>H. Ki</strong>, * and + marks
    PUB[int(n)] = dict(title=title.rstrip("."), jr=jr, yr=yr.group(1) if yr else "", doi=doi.group(1) if doi else "", au=au)


def vdims(name):
    o = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "json", MD + name + ".mp4"])
    s = json.loads(o)["streams"][0]; return s["width"], s["height"]


def fdims(name):
    return Image.open(MD + "fig-" + name + ".jpg").size


# Display caps (CSS px) so low-resolution sources are never blown up past ~1.3x their native size.
HMAX = {"sim-bounce": 560, "wj-coupling": 470, "sim-fdtd-demo": 504, "ai-monitor-demo": 504, "ai-bead-demo": 504, "weld-keyhole-demo": 504, "weld-foil-demo": 504, "sim-fsi-demo": 504, "uf-phase-map": 480,   # px: per-figure height limit (floated or stacked)
        "ht-duo": 560, "v2c-demo": 540, "sim-fs-compare": 460, "sim-plasma4": 340}
FORCE_STACK = {"ht-duo", "v2c-demo", "sim-fs-compare", "sim-fdtd-demo", "ai-monitor-demo", "ai-bead-demo", "weld-keyhole-demo", "weld-foil-demo", "sim-fsi-demo"}   # always put these above the text
WMAX = {}   # px: fixed display width for stacked figures (Process Monitoring 01·02 same width)
CAP = {"ai-keyhole-detect": 420, "sim-lid": 600,  "weld-coaxial-grid": 620, "ai-defect": 640}
MAIN_MAX_H = 420  # px: tallest a main item may be


EQ = {'sim-keyhole': (['Level set (narrow band)', '광선 추적 · 다중 반사', 'Knudsen 층 증발', '혼합 연속체 모델', '유한체적법'], [('자유 표면 (level set)', '\\frac{\\partial \\phi}{\\partial t} + F_{lv}\\,|\\nabla\\phi| = 0,\\quad F_{lv}=F_e+\\mathbf{n}\\cdot\\mathbf{U},\\quad \\mathbf{n}=\\frac{\\nabla\\phi}{|\\nabla\\phi|}'), ('운동량', '\\rho\\Big(\\frac{\\partial \\mathbf{u}}{\\partial t}+\\mathbf{u}\\cdot\\nabla\\mathbf{u}\\Big)=-\\nabla p+\\nabla\\cdot(\\mu\\nabla\\mathbf{u})+\\big(\\sigma\\kappa\\,\\mathbf{n}+\\nabla_s\\sigma-p_r\\mathbf{n}\\big)\\,\\delta(\\phi)'), ('에너지', "\\frac{\\partial(\\rho C_p T)}{\\partial t}+\\mathbf{u}\\cdot\\nabla(\\rho C_p T)=k\\nabla^2 T+q''\\,\\delta(\\phi)")]), 'sim-ablation': (['Level set · 광선 추적', 'Knight 증발 모델', '고전 핵생성 이론', 'Redlich–Kwong 상태방정식', 'Watson · Somayajulu 물성 모델'], [('임계 기포 반경', 'R_{crit}=\\frac{2\\sigma}{p_{sat}(T_l)\\,\\exp\\!\\big[(p_l-p_{sat}(T_l))/(\\rho_l R T_l)\\big]-p_l}'), ('균일 핵생성', "\\dot H'''\\propto N_l\\exp\\!\\Big(-\\frac{4\\pi R_{crit}^2\\,\\sigma}{3k_BT_l}\\Big),\\qquad \\dot m'''_{boiling}=m_{bubble}\\,\\dot H'''"), ('증발 잠열 (Watson)', 'L_v(T)=L_{v,b}\\Big(\\frac{T_c-T}{T_c-T_b}\\Big)^{0.38}')]), 'sim-em': (['FDTD (Yee 격자)', 'Drude 분산 모델', 'PML 흡수 경계'], [('맥스웰 방정식', '\\frac{\\partial \\mathbf{H}}{\\partial t}=-\\frac{1}{\\mu}\\nabla\\times\\mathbf{E},\\qquad \\frac{\\partial \\mathbf{E}}{\\partial t}=\\frac{1}{\\varepsilon}\\big(\\nabla\\times\\mathbf{H}-\\mathbf{J}\\big)'), ('Drude 모델', '\\varepsilon(\\omega)=\\varepsilon_\\infty-\\frac{\\omega_p^2}{\\omega^2+i\\gamma\\omega}')]), 'sim-fs': (['BOR-FDTD', '2온도 모델', '이온화 · 전기전도도 모델', 'PML 흡수 경계'], [('전자기장', '\\frac{\\partial \\mathbf{E}}{\\partial t}=\\frac{1}{\\varepsilon}\\big(\\nabla\\times\\mathbf{H}-\\sigma(n_e,T_e)\\,\\mathbf{E}\\big),\\qquad \\frac{\\partial \\mathbf{H}}{\\partial t}=-\\frac{1}{\\mu}\\nabla\\times\\mathbf{E}'), ('2온도 모델', 'C_e\\frac{\\partial T_e}{\\partial t}=\\nabla\\cdot(k_e\\nabla T_e)-G(T_e-T_l)+S,\\qquad C_l\\frac{\\partial T_l}{\\partial t}=G(T_e-T_l)')]), 'sim-plasma': (['격자 볼츠만 방법 (BGK)', '재스케일링 기법', 'LBM–유한차분 혼합 MHD', 'Level set (자기장 속 2상 유동)'], [('입자 종별 LBM (s = e, i, n)', 'f_i^{s}(\\mathbf{x}+\\mathbf{c}_i\\Delta t,\\,t+\\Delta t)-f_i^{s}(\\mathbf{x},t)=-\\frac{1}{\\tau_s}\\big(f_i^{s}-f_i^{s,eq}\\big)+\\Delta t\\,F_i^{s}'), ('자기장 유도 방정식', '\\frac{\\partial \\mathbf{B}}{\\partial t}=\\nabla\\times(\\mathbf{u}\\times\\mathbf{B})+\\eta\\nabla^2\\mathbf{B}')]), 'sim-fsi': (['통합 운동량 방정식 (일체형)', '유한체적법', 'SIMPLE 알고리즘'], [('유체 · 고체 공통', '\\rho\\frac{\\partial \\mathbf{u}}{\\partial t}+\\rho\\nabla\\cdot(\\mathbf{u}\\mathbf{u})=\\nabla\\cdot\\boldsymbol{\\sigma}+\\mathbf{f}'), ('구성 방정식', '\\boldsymbol{\\sigma}_f=-p\\mathbf{I}+\\mu(\\nabla\\mathbf{u}+\\nabla\\mathbf{u}^{T}),\\qquad \\boldsymbol{\\sigma}_s=\\lambda\\,\\mathrm{tr}(\\boldsymbol{\\varepsilon})\\mathbf{I}+2G\\boldsymbol{\\varepsilon}')])}
EQ["sim-ablation"] = (['Level set · 광선 추적', '얇은 용융층 유동 모델', 'Knudsen 층 증발 (Knight)', '고전 핵생성 이론', 'Redlich–Kwong · Watson · Somayajulu 물성'], [('자유 표면 (level set)', '\\frac{\\partial \\phi}{\\partial t}+F\\,|\\nabla\\phi|=0,\\qquad F=F_e+F_f+F_{ho}'), ('L/V 에너지 수지', '\\dot q_{laser}=\\rho_l L_v A F_e+\\dot q_{\\phi}+\\dot q_{loss}'), ('임계 기포 반경', 'R_{crit}=\\frac{2\\sigma}{p_{sat}(T_l)\\,\\exp\\!\\big[(p_l-p_{sat}(T_l))/(\\rho_l R T_l)\\big]-p_l}')])
EQ["sim-magnetic"] = (['Level set', '정자기 방정식 (벡터 퍼텐셜)', '유한체적법 · 엇갈림 격자', 'SIMPLE 알고리즘'], [('운동량 (자기력 포함)', '\\frac{\\partial(\\rho\\mathbf{u})}{\\partial t}+\\nabla\\cdot(\\rho\\mathbf{u}\\mathbf{u})=-\\nabla p+\\nabla\\cdot(\\rho\\nu\\nabla\\mathbf{u})+\\rho\\mathbf{g}-\\sigma\\kappa\\,\\delta(\\phi)\\,\\mathbf{n}+f_m\\,\\delta(\\phi)\\,\\mathbf{n}'), ('정자기 방정식', '\\nabla\\cdot\\mathbf{B}=0,\\quad \\nabla\\times\\mathbf{H}=\\mathbf{J}_f,\\qquad \\mathbf{B}=\\nabla\\times\\mathbf{A},\\quad \\mathbf{B}=\\mu(\\phi)\\,\\mathbf{H}'), ('자유 표면', '\\frac{\\partial \\phi}{\\partial t}+\\mathbf{u}\\cdot\\nabla\\phi=0')])
EQ['sim-keyhole'] = (['Level set (narrow band)', '광선 추적 · 다중 반사', 'Knudsen 층 증발 (Knight)', '혼합 연속체 모델', '유한체적법 · SCGS'], [('자유 표면 (level set)', '\\frac{\\partial \\phi}{\\partial t} + F_{lv}\\,|\\nabla\\phi| = 0,\\qquad F_{lv}=F_e+\\mathbf{n}\\cdot\\mathbf{U},\\qquad \\mathbf{n}=\\frac{\\nabla\\phi}{|\\nabla\\phi|}'), ('운동량', '\\frac{\\partial(\\rho\\mathbf{u})}{\\partial t}+\\nabla\\cdot(\\rho\\mathbf{u}\\mathbf{u})=\\nabla\\cdot\\Big(\\mu_l\\frac{\\rho}{\\rho_l}\\nabla\\mathbf{u}\\Big)-\\frac{\\mu_l}{K}\\frac{\\rho}{\\rho_l}(\\mathbf{u}-\\mathbf{V}_s)-\\nabla p-\\big(\\sigma\\kappa\\,\\mathbf{n}^{*}-\\nabla_s\\sigma\\big)\\,\\delta(\\phi)'), ('에너지', "\\frac{\\partial(\\rho C_p T)}{\\partial t}+\\mathbf{u}\\cdot\\nabla(\\rho C_p T)=k\\nabla^2 T+q''\\,\\delta(\\phi),\\qquad q''=q''_{L/V}-\\rho_l L_v F_e-\\sigma_{SB}\\,\\varepsilon\\,(T^4-T_\\infty^4)")])
EQ['sim-fs'] = (['BOR-FDTD', '2온도 모델', '이온화 모델 (에너지 수지)', '플라즈마 전기전도도 모델', 'PML 흡수 경계'], [('전자기장', '\\frac{\\partial \\mathbf{E}}{\\partial t}=\\frac{1}{\\varepsilon}\\big(\\nabla\\times\\mathbf{H}-\\sigma(n_e,T_e)\\,\\mathbf{E}\\big),\\qquad \\frac{\\partial \\mathbf{H}}{\\partial t}=-\\frac{1}{\\mu}\\nabla\\times\\mathbf{E}'), ('2온도 모델', '\\tfrac{3}{2}n_e k_B\\frac{\\partial T_e}{\\partial t}=\\nabla\\cdot(\\kappa_e\\nabla T_e)-G(T_e-T_l)+\\frac{\\partial \\varepsilon}{\\partial t},\\qquad C_l\\frac{\\partial T_l}{\\partial t}=\\nabla\\cdot(\\kappa_l\\nabla T_l)+G(T_e-T_l)'), ('전자로 가는 레이저 에너지', '\\frac{\\partial \\varepsilon}{\\partial t}=\\sigma E^2-U_i\\frac{\\partial n_e}{\\partial t}\\qquad (U_i=8.15\\ \\mathrm{eV})')])
EQ['sim-plasma'] = (['격자 볼츠만 방법 (D2Q9, BGK)', '재스케일링 기법', 'FDTD (Yee 격자)', 'LBM–유한차분 혼합 MHD'], [('입자 종별 LBM (s = e, i, n)', 'f_s^{\\alpha}(\\mathbf{x}+\\mathbf{e}_s^{\\alpha}\\Delta t,\\,t+\\Delta t)=f_s^{\\alpha}(\\mathbf{x},t)-\\frac{1}{\\tau_{sn}}\\big[f_s^{\\alpha}-f_{sn}^{eq,\\alpha}\\big]+\\Delta t\\,\\frac{\\mathbf{a}_s\\cdot(\\mathbf{e}_s^{\\alpha}-\\mathbf{u}_s)}{\\theta_s^{2}}\\,f_s^{eq,\\alpha}'), ('플라즈마 전류', '\\mathbf{J}=e\\,(n_i\\mathbf{u}_i-n_e\\mathbf{u}_e)\\quad\\text{(FDTD 맥스웰 방정식의 전류항)}'), ('자기장 유도 방정식', '\\frac{\\partial \\mathbf{B}}{\\partial t}=\\eta\\nabla^2\\mathbf{B}+(\\mathbf{B}\\cdot\\nabla)\\mathbf{u}-(\\mathbf{u}\\cdot\\nabla)\\mathbf{B},\\qquad \\eta=(\\mu\\sigma)^{-1}')])
EQ['sim-magnetic'] = (['Level set', '정자기 방정식 (벡터 퍼텐셜)', '유한체적법 · 엇갈림 격자', 'SIMPLE 알고리즘'], [('운동량', '\\begin{aligned}\\frac{\\partial(\\rho\\mathbf{u})}{\\partial t}+\\nabla\\cdot(\\rho\\mathbf{u}\\mathbf{u})&=-\\nabla p+\\nabla\\cdot(\\rho\\nu\\nabla\\mathbf{u})+\\rho\\mathbf{g}-\\sigma\\kappa\\,\\delta(\\phi)\\,\\mathbf{n}\\\\&\\quad+\\Big(\\frac{1}{\\mu_g}-\\frac{1}{\\mu_l}\\Big)B_n^2\\,\\delta(\\phi)\\,\\mathbf{n}-\\frac12\\Big[(\\mu_g-\\mu_l)H^2+\\bar\\mu\\Big(\\frac{1}{\\mu_g^2}-\\frac{1}{\\mu_l^2}\\Big)B_n^2\\Big]\\delta(\\phi)\\,\\mathbf{n}\\end{aligned}'), ('정자기 방정식', '\\nabla^2\\xi+\\mu\\Big(\\frac{1}{\\mu_g}-\\frac{1}{\\mu_l}\\Big)\\delta(\\phi)\\,\\mathbf{n}\\cdot\\nabla\\xi=0,\\qquad \\mathbf{B}=\\Big(\\frac{\\partial\\xi}{\\partial y},\\,-\\frac{\\partial\\xi}{\\partial x}\\Big)'), ('자유 표면', '\\frac{\\partial \\phi}{\\partial t}+\\mathbf{u}\\cdot\\nabla\\phi=0')])
EQ['sim-fsi'] = (['통합(하이브리드) 운동량 방정식 · 일체형', '유한체적법 · 엇갈림 격자', 'SIMPLE 알고리즘'], [('공통 운동량 방정식', '\\frac{\\partial(\\rho\\mathbf{u})}{\\partial t}=\\nabla\\cdot\\mathbf{J}+\\mathbf{f}'), ('응력 텐서 J', '\\mathbf{J}=\\begin{cases}-\\rho\\mathbf{u}\\mathbf{u}-p\\mathbf{I}+\\mu\\nabla\\mathbf{u} & \\text{유체}\\\\ \\tilde\\mu\\,\\nabla\\mathbf{d}+(\\tilde\\lambda+\\tilde\\mu)(\\nabla\\cdot\\mathbf{d})\\,\\mathbf{I} & \\text{고체}\\end{cases},\\qquad \\mathbf{d}^{\\,n+1}\\approx\\mathbf{d}^{\\,n}+\\mathbf{u}^{\\,n+1}\\Delta t')])
EQ["sim-em"] = (['FDTD (Yee 격자)', 'Drude 분산 모델', '파장 확대 기법', 'CPML 흡수 경계'], [('Drude 모델', '\\varepsilon(\\omega)=\\varepsilon_0\\Big(\\varepsilon_\\infty-\\frac{\\omega_p^2}{\\omega^2+i\\gamma_p\\omega}\\Big)'), ('파장 확대 조건', '(n,\\kappa)\\ \\text{유지}\\iff \\sigma\\lambda=\\sigma_{new}\\lambda_{new}\\ \\ \\text{(표준 FDTD)},\\qquad \\varepsilon_1,\\varepsilon_2\\ \\text{유지}\\ \\ \\text{(Drude)}'), ('키홀 흡수율', 'A=1-\\frac{\\int_{bottom}(\\mathbf{E}\\times\\mathbf{H})\\cdot\\mathbf{n}\\,dA}{\\int_{top}(\\mathbf{E}\\times\\mathbf{H})\\cdot\\mathbf{n}\\,dA}')])
EQ["sim-waterjet"] = (['FDTD (Yee 격자)', '파장 확대 기법', 'CPML 흡수 경계', '에너지 방정식 (유한차분)'], [('맥스웰 방정식', '\\frac{\\partial \\mathbf{H}}{\\partial t}=-\\frac{1}{\\mu}\\nabla\\times\\mathbf{E},\\qquad \\frac{\\partial \\mathbf{E}}{\\partial t}=\\frac{1}{\\varepsilon}\\big(\\nabla\\times\\mathbf{H}-\\mathbf{J}\\big)'), ('투과율', 'T=\\frac{\\int \\mathbf{n}\\cdot(\\mathbf{E}\\times\\mathbf{H})\\,dA_{bottom}}{\\int \\big|\\mathbf{n}\\cdot(\\mathbf{E}\\times\\mathbf{H})\\big|\\,dA_{incident}}'), ('줄 가열 · 에너지 방정식', 'J_h=\\sigma_\\lambda E^2,\\qquad \\frac{\\partial T}{\\partial t}+\\mathbf{u}\\cdot\\nabla T=\\alpha\\nabla^2 T+\\frac{J_h}{\\rho c_p}')])
EQ["sim-fsi-move"] = (['통합 운동량 방정식 · 완전 오일러 일체형', '정밀 보존형 level set (5차 HOUC · fast marching)', '변위장 확장(외삽)', '유한체적법 · 엇갈림 격자 · SIMPLE'], [('통합 운동량 방정식', '\\frac{\\partial(\\rho\\mathbf{u})}{\\partial t}+\\nabla\\cdot(\\rho\\mathbf{u}\\mathbf{u})=\\nabla\\cdot\\big(\\bar\\mu(\\nabla\\mathbf{u}+\\nabla\\mathbf{u}^{T})+\\bar\\lambda(\\nabla\\cdot\\mathbf{u})\\mathbf{I}+\\bar{\\mathbf{b}}\\big)+\\mathbf{f},\\qquad \\mathbf{d}\\approx\\mathbf{u}\\Delta t+\\mathbf{d}^{o}'), ('유체 · 고체 항', '\\bar\\mu=\\begin{cases}\\eta & \\text{유체}\\\\ \\mu\\Delta t & \\text{고체}\\end{cases}\\quad \\bar\\lambda=\\begin{cases}0\\\\ \\lambda\\Delta t\\end{cases}\\quad \\bar{\\mathbf{b}}=\\begin{cases}-p\\mathbf{I}\\\\ \\mu(\\nabla\\mathbf{d}^{o}+\\nabla\\mathbf{d}^{oT})+\\lambda(\\nabla\\cdot\\mathbf{d}^{o})\\mathbf{I}\\end{cases}'), ('경계면 이동', '\\psi=\\tfrac{1}{2}\\Big(\\tanh\\frac{\\phi}{2\\varepsilon}+1\\Big),\\qquad \\frac{\\partial \\psi}{\\partial t}+\\nabla\\cdot(\\mathbf{u}\\,\\psi)=0'), ('재초기화', '\\frac{\\partial \\psi}{\\partial \\tau}+\\nabla\\cdot\\big(\\psi(1-\\psi)\\,\\mathbf{n}\\big)=\\nabla\\cdot\\big(\\varepsilon\\,(\\nabla\\psi\\cdot\\mathbf{n})\\,\\mathbf{n}\\big)'), ('변위장 확장', '\\frac{\\partial \\mathbf{d}}{\\partial \\tau}+U(\\phi)\\,\\mathbf{n}\\cdot\\nabla\\mathbf{d}=0,\\qquad U=\\begin{cases}1 & \\phi\\ge\\alpha\\\\ 0 & \\phi<\\alpha\\end{cases},\\qquad \\mathbf{n}=\\frac{\\nabla\\phi}{|\\nabla\\phi|}')])
EQ["weld-scaling"] = (['1차원 열전도 해석해', '무차원 용입 깊이', '다중 반사 지수 γ'], [('표면 온도 상승', '\\Delta T_s=\\frac{2\\eta I_0}{k}\\sqrt{\\frac{\\alpha t_i}{\\pi}}\\ \\propto\\ \\eta I_0\\sqrt{t_i},\\qquad t_i=\\frac{D}{V_s}'), ('스케일링 법칙', '\\delta^{*}=\\frac{\\delta}{D}=f\\big(I_0\\,t_i^{\\,\\theta}\\big),\\qquad \\theta=\\frac{1}{2(1+\\gamma)}\\quad(\\gamma=0:\\ \\text{열전도 용접},\\ \\gamma>0:\\ \\text{키홀 용접})')])


def KX(texs):
    o = subprocess.run(["node", os.path.dirname(os.path.abspath(__file__)) + "/ktx.js"], input=json.dumps(texs), capture_output=True, text=True, check=True)
    return json.loads(o.stdout)


def eqbox(bid):
    meth, eqs = EQ[bid]
    rendered = KX([t for _, t in eqs])
    m = "".join(f"<span>{E(x)}</span>" for x in meth)
    q = "".join(f'<div class="rq-eq"><p>{E(l)}</p>{r}</div>' for (l, _), r in zip(eqs, rendered))
    return f'<div class="rq"><div class="rq-top"><p class="rq-h">수치 기법 · 지배 방정식</p><div class="rq-m">{m}</div></div><div class="rq-eqs">{q}</div></div>'


def V(name, cap):
    return ("v", name, cap)


def F(name, cap):
    return ("f", name, cap)


def media(item, main, wide=False):
    kind, name, cap = item
    alt = re.sub(r"<[^>]+>", "", cap)
    w, h = vdims(name) if kind == "v" else fdims(name)
    maxw = (min(900, round(480 * w / h)) if wide else round(MAIN_MAX_H * w / h)) if main else None
    if main and name in CAP: maxw = min(maxw, CAP[name])
    st = f' style="max-width:{maxw}px"' if (main and maxw and maxw < (1100 if wide else 760)) else ""
    full = M + (name + ".mp4" if kind == "v" else "fig-" + name + ".jpg")
    if kind == "v":
        inner = (f'<video muted loop playsinline preload="none" data-poster="{M}{name}.jpg" data-src="{full}" aria-label="{E(alt)}"></video>')
    else:
        inner = f'<img src="{full}" alt="{E(alt)}" loading="lazy" decoding="async">'
    cls = "rm " + ("rm-main" if main else "rm-thumb") + (" rm-video" if kind == "v" else " rm-fig")
    ar = f"{w}/{h}"
    zoom = '<span class="rm-zoom" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg></span>'
    return (f'<figure class="{cls}"{st}><button type="button" class="rm-frame" style="aspect-ratio:{ar}" data-full="{full}" data-kind="{kind}" '
            f'aria-label="크게 보기: {E(alt)}">{inner}{zoom}</button><figcaption>{cap}</figcaption></figure>')


def papers(nums):
    out = []
    for n in nums:
        p = PUB[n]
        link = (f'<a href="{p["doi"]}" target="_blank" rel="noopener">{E(p["title"])}</a>' if p["doi"] else E(p["title"]))
        meta = f'<span class="rp-jr">{E(p["jr"])}</span> · {p["yr"]}' if p["jr"] != "Submitted" else '<span class="rp-sub">Submitted · ' + p["yr"] + "</span>"
        au = f"<span class='rp-au'>{p['au']}</span>" if p["au"] else ""
        out.append(f"<li>{link}{au}<span class='rp-meta'>{meta}</span></li>")
    return "<ul class='rp-list'>" + "".join(out) + "</ul>"


# ---------------------------------------------------------------- content
TABS = [
 dict(id="ai", en="AI for Process Monitoring", ko="AI 기반 공정 모니터링", ten="Process Monitoring", tko="AI 공정 모니터링", color="navy",
  icon='<path d="M2 12s3.6-6.5 10-6.5S22 12 22 12s-3.6 6.5-10 6.5S2 12 2 12z"/><circle cx="12" cy="12" r="3"/><path d="M12 2v1.5M12 20.5V22"/>',
  lead="레이저 가공의 품질을 좌우하는 현상은 대부분 재료 안에서 일어나 밖에서는 보이지 않습니다. 동축 카메라와 적외선 카메라 영상을 딥러닝으로 읽어 이 보이지 않는 상태를 <b>공정이 진행되는 동안 실시간으로</b> 알려 줍니다. 레이저 용접에서는 공정의 원인인 <b>키홀 흡수율</b>과 결과인 <b>비드 폭·용입 깊이</b>를, 레이저 열처리에서는 단면의 <b>상 분포</b>와 그 결과인 <b>경도 분포</b>를 모니터링합니다. 실험으로는 잴 수 없는 흡수율과 온도장은 광선 추적·열해석 시뮬레이션으로 정답을 만들어 학습시키는 <b>물리 기반 데이터</b> 전략이 핵심이며, 같은 개념을 펨토초 레이저 가공의 플룸 영상 모니터링으로 넓히고 있습니다.",
  chips=['흡수율 모니터링', '비드 폭·용입 깊이', '단면 상 분포', '단면 경도 분포', '시뮬레이션 사전학습'],
  blocks=[
   dict(kind="sub", en="Laser Welding Monitoring", ko="레이저 용접 모니터링"),
   dict(id="ai-monitor", en="Absorptance-based Keyhole Welding Monitoring", ko="흡수율 기반 키홀 용접 모니터링",
    main=V("ai-monitor-demo", "흡수율 모니터링 데모 (약 53초): ① 동축 카메라 한 대로 키홀 상·하부 개구를 함께 검출 (Al 5052, 1740 W · 7.6 mm/s), ② 두 개구를 이어 3차원 키홀을 만들고 광선 추적으로 학습한 ResNet-34로 흡수율 계산, ③ 용접 중 시간 평균 흡수율로 용접 모드 변화와 용락 결함 판별 (위: 카메라 두 대, 아래: 한 대), ④ 부분 용입 용접(Al 1050, 665 W · 11.2 mm/s)의 실시간 흡수율 — 키홀이 무너지는 지점에서 9 %로 떨어집니다"),
    side=[],
    text=["키홀 용접의 품질은 키홀 안에서 레이저가 얼마나 흡수되느냐에 달려 있지만, 흡수율은 공정 중에 직접 잴 수 없습니다. 본 연구실은 레이저와 같은 축에 둔 카메라로 키홀 입구(개구)를 촬영하고, 딥러닝으로 개구를 찾아 3차원 키홀을 재구성한 뒤, 광선 추적 데이터로 학습한 흡수율 대리모델(ResNet-34, Process Prediction 탭)로 그 순간의 흡수율을 계산합니다. 흡수율은 재료에 실제로 들어가는 에너지, 즉 용접 결과를 만드는 원인을 보여 주는 지표입니다.",
          "완전 용입 용접에서는 동기화한 고속 카메라 두 대로 윗면과 아랫면을 함께 찍고, YOLOv4로 키홀 상·하부 개구를 찾습니다(mIoU 98.23% · 95.6%, 156 fps). 냉연강판(A366)에서는 열린 하부 개구가 적을수록, 하부 개구가 작을수록, 키홀 앞벽이 기울수록 흡수율이 커지고, 결함이 생기는 구간에서는 하부 개구가 커지며 흡수율이 급락합니다. 반사율과 열전도도가 높아 용접이 까다로운 알루미늄(Al 5052-H32)에서는 키홀의 열림·닫힘과 흡수 패턴을 세 유형으로 분류합니다. 에너지가 과도하면 키홀이 닫히지 않고 열린 채 커지다가, 정규화한 개구 면적이 문턱값(상부 600 · 하부 500)을 넘으면 용락(burn-through)이 생깁니다. 아랫면 보호 가스를 아르곤에서 헬륨으로 바꾸면 가벼운 헬륨이 아랫면을 잘 덮고 높은 열전도도로 열을 빼앗아, 공정이 안정되고 결함이 줄어듭니다.",
          "윗면 영상 한 장에서 상·하부 개구를 함께 검출하는 YOLOR-CSP 모델(정밀도 0.980 · 재현율 0.988 · mAP@0.5 0.992)을 쓰면 카메라를 한 대로 줄일 수 있습니다. 하부 개구가 키홀 벽에 가끔 가려져도 두 대를 쓸 때만큼 효과적이며, 순간 흡수율보다 용접 모드를 잘 나타내는 시간 평균 흡수율로 두 가지 용접 모드와 용락 결함의 발생을 구분합니다. 키홀 바닥이 보이지 않는 부분 용입에서는 용융풀 영상에서 YOLOv7로 상부 개구를, CNN(VoVNet27-slim)으로 용입 깊이를 추정해 2채널 키홀 영상을 만들고, 두 번째 CNN으로 흡수율을 예측합니다(광선 추적 대비 R² 0.997). 부분 용입 키홀에 흡수율 모니터링을 처음 적용한 것으로, Al 1050P-H16에서 세 가지 흡수 패턴을 구분하고 흡수율이 급락하는 순간으로 키홀 붕괴·용융물 분출·언더필 결함을 잡아냅니다. 가정한 키홀 형상이 달라도 흡수율의 상대 변화는 거의 같기 때문에, 모니터링에서는 절댓값보다 변화 추이를 봅니다."],
    stats=[('R² 0.997', '부분 용입 흡수율 예측'), ('156 fps', '키홀 개구 검출 속도')], spec="2 kW 멀티모드 파이버 레이저 (1070 nm) · A366 강 · Al 5052-H32 · Al 1050P-H16 · 동축 고속 카메라",
    pubs=[27, 24, 19, 11]),
   dict(id="ai-bead", en="Bead Width & Penetration Depth Monitoring", ko="비드 폭·용입 깊이 모니터링",
    main=V("ai-bead-demo", "비드 형상 모니터링 데모 (약 46초): ① 532 nm 조명과 소형 동축 카메라로 투명하게 보이는 알루미늄 용융풀 촬영, ② 비드 윗면·아랫면 폭 실시간 예측 — 영상 한 장 모델(위)과 두 장 모델(아래) 비교 (739 W · 8.2 mm/s), ③ 비드 윗면 폭과 용입 깊이 실시간 예측"),
    side=[],
    text=["흡수율이 공정에 들어가는 에너지, 즉 원인을 보여 준다면 비드 폭과 용입 깊이는 그 결과인 용접부의 크기를 직접 보여 줍니다. 녹은 알루미늄은 투명해서, 532 nm 조명과 필터를 달고 소형 카메라로 동축 촬영하면 용융풀 경계와 키홀이 선명하게 보입니다. 이 영상 한 장에 비드 폭과 용입 깊이를 판단할 정보가 충분히 담겨 있으므로, 딥러닝으로 용접하는 동안 비드 윗면·아랫면 폭과 용입 깊이를 예측합니다. 시편을 자르지 않고도 용접선 전체의 품질을 확인할 수 있습니다.",
          "비드 폭은 VoVNet27-slim 회귀 모델로 윗면과 아랫면을 동시에 예측합니다. 윗면 폭은 영상 한 장으로도 정확하지만, 위에서 보이지 않고 변동이 큰 아랫면 폭은 0.1 mm 직전 위치의 영상을 함께 넣으면 뚜렷이 좋아집니다. 과거 정보가 더해지고 잡음이 줄어드는 효과로, 부분 용입에서 완전 용입으로 넘어가는 구간과 용융물 분출·강한 반사 같은 오차 상황에서도 더 잘 따라갑니다. 영상 한 장의 예측에 1.30 ms가 걸리고, 잡음·흐림을 섞어 학습해 흐린 영상에도 견고합니다.",
          "용입 깊이는 용접부를 용접선 방향으로 잘라 측정한 깊이를 정답으로 학습한 CNN(VoVNet27-slim)으로 용융풀 영상에서 추정해, 용입이 갑자기 얕아지는 구간과 언더필 결함을 잡아냅니다. 이 깊이는 부분 용입 키홀을 재구성해 흡수율을 계산하는 입력으로도 쓰여, 원인(흡수율)과 결과(용입 깊이) 모니터링이 하나의 시스템으로 이어집니다."],
    stats=[('1.30 ms', '영상 한 장당 비드 폭 예측')], spec="Al 1050P-H16 · 소형 동축 카메라 (FLIR Blackfly) · 532 nm LED 조명 · VoVNet27-slim",
    pubs=[14, 11]),
   dict(kind="sub", en="Laser Heat Treatment Monitoring", ko="레이저 열처리 모니터링"),
   dict(id="ht-monitor", en="Real-time Phase & Hardness Monitoring", ko="열화상 기반 단면 상 분포·경도 실시간 모니터링",
    main=V("ht-duo", "표면 열화상만으로 단면 상 분포(왼쪽)와 경도 분포(오른쪽)를 실시간으로 예측하는 두 모델: 각각 IR 카메라 영상을 입력으로 받아, 열처리 경로를 따라 용융부·열처리부·열영향부의 폭·깊이와 경화층 폭·깊이를 추적합니다 (왼쪽 실선·오른쪽 파랑: 실측, 왼쪽 점선·오른쪽 검정: AI)"),
    side=[V("ht-phase", "표면 열화상(왼쪽 위, 입력) → AI가 예측한 단면 상 분포(왼쪽 아래: 실측 vs. AI)와, 열처리 경로를 따라 추적한 용융부(빨강)·열처리부(초록)·열영향부(파랑)의 폭·깊이(오른쪽, 실선: 실측, 점선: AI)"),
          V("ht-hardness", "표면 열화상(왼쪽 위) → AI가 예측한 단면 경도 분포(왼쪽 아래). 오른쪽은 열처리 경로를 따라 추적한 경화층 폭·깊이(파랑: 실측, 검정: AI)와 위치별 단면 경도 지도(위: AI, 아래: 실측)입니다"),
          F("ht-phase-seq", "100 mm 열처리 경로에서 레이저가 한 위치를 지나가기 전후 20장의 표면 온도 영상(T₁–T₂₀)을 입력으로, 그 위치의 단면 상 분포(빨강: 용융부, 초록: 열처리부, 파랑: 열영향부)를 예측합니다"),
          F("ht-phase-prof", "시험 조건 B–E(865–1800 W, 5–10.4 mm/s)에서 열처리 경로를 따라 본 영역별 폭(왼쪽)과 깊이(오른쪽): 실선은 실측, 점선은 AI 예측이며 빨강·초록·파랑은 용융부·열처리부·열영향부입니다. 출력이 높을수록 용융부가 생기고 모든 영역이 넓고 깊어집니다"),
          F("ht-two-stage", "물리 기반 2단계 학습: (a) 열해석으로 만든 표면 온도 영상 두 장과 위치·시간 정보로 단면 ECDT 지도를 예측하도록 사전학습하고, ECDT–경도 상관관계로 경도 분포를 얻습니다. (b) 사전학습한 ConvGRU 모델을 그대로 가져와 실제 IR 카메라 영상과 측정 경도로 미세조정합니다"),
          F("ht-finetune", "시험 조건 E–J의 단면 경도 예측: 미세조정 전(왼쪽)에는 경화층이 끊기거나 비어 보이지만, 미세조정 후(오른쪽)에는 경화층의 형상과 깊이가 실측과 잘 맞습니다 (경도 220–810 HV)")],
    text=["레이저 열처리는 표면을 국부적으로 경화하지만, 경화층이 제대로 생겼는지 확인하려면 시편을 잘라 조직과 경도를 봐야 합니다. 본 연구실은 적외선 카메라로 찍은 표면 열화상만으로, 열처리가 진행되는 동안 단면의 상 분포(용융부·열처리부·열영향부)와 경도 분포를 실시간으로 예측합니다. 상 분포는 어떤 조직이 생겼는지를, 경도 분포는 그 결과로 얻은 성질을 알려 주며, 레이저 열처리의 단면 상 분포를 실시간으로 예측한 것은 본 연구가 처음입니다.",
          "상 분포 모델은 레이저가 지나가기 전후 20장의 연속 열화상과 위치 정보를 합성곱 게이트 순환 유닛(ConvGRU) 인코더–디코더가 공간·시간 특징으로 읽어, 픽셀 단위로 단면 상 분포 영상을 생성합니다. 학습에는 S45C 강에 출력(600–1800 W)과 주사 속도(5–15 mm/s)를 바꾼 16개 조건의 실험과, 윗면·단면 광학 현미경 분석으로 합성한 단면 상 지도를 씁니다. 열영향부·열처리부·용융부의 폭은 평균 97.9%·96.3%·86.8%, 깊이는 94.5%·92.1%·80.5% 정확도로 예측하며, 주사 방향으로 열이 쌓여 열처리부가 점점 넓고 깊어지는 현상과 방향성 온도 구배 때문에 생기는 단면의 좌우 비대칭도 잡아냅니다.",
          "경도 분포 모델은 적은 실험 데이터로도 정확하도록 시뮬레이션과 실험을 잇는 물리 기반 2단계 학습을 씁니다. 먼저 열해석으로 만든 표면 온도 영상 두 장과 위치·시간 정보로 단면의 등가 탄소 확산 시간(ECDT) 지도를 예측하도록 사전학습합니다. ECDT는 열해석 기반 공정 설계 연구(Laser Processing 탭)에서 경도와 강하게 상관되는 지표로, ECDT–경도 관계를 거쳐 단면 경도 분포가 됩니다. 시뮬레이션은 정답을 얼마든지 만들 수 있으므로 모델은 이 단계에서 열처리의 물리를 먼저 익히고, 이어 실제 IR 카메라 열화상과 측정한 경도로 미세조정합니다(S45C 강). 미세조정 전에는 경화층이 끊기거나 비어 보이던 조건에서도 미세조정 후에는 경화층의 형상과 깊이가 실측과 잘 맞으며, 열처리 경로를 따라 경화층 폭과 깊이를 실시간으로 추적합니다."],
    stats=[('97.9%', '열영향부 폭 예측 정확도'), ('16개', '실험 조건 (S45C)')], spec="2 kW 멀티모드 파이버 레이저 (1070 nm) · S45C 탄소강 · IR 카메라 (FLIR T650SC) · N₂ 보호 가스",
    pubs=[10, 5]),
  ]),
 dict(id="aipred", en="AI for Process Prediction & Surrogate Modeling", ko="AI 기반 공정 예측 모델", ten="Process Prediction", tko="AI 예측 모델", color="coral",
  icon='<path d="M3 3v18h18"/><path d="M7 15l3.5-4 3 2.5L19 7"/><circle cx="19" cy="7" r="1.5"/>',
  lead="공정 조건만 넣으면 수치해석이나 실험의 결과를 <b>분포와 영상으로 바로 그려 내는 생성형 AI</b>를 개발합니다. 수 시간에서 하루가 걸리는 열·유동·응력·전자기 해석을 1초 안에 대신하는 <b>시뮬레이션 대리모델</b>은 공정 디지털 트윈과 실시간 모니터링의 계산 엔진이 되고, 적은 실험 데이터만으로 용접부 단면, 경도·상 분포, 표면 형상과 반사율, 실리콘 결정상을 예측하는 <b>공정 결과 예측</b> 모델은 시편을 만들기 전에 결과를 알려 줍니다.",
  chips=['생성형 대리모델', 'cGAN · ResNet', '임의 빔 형상', '키홀 흡수율', '과도 전자기 해석', '합성 데이터 학습', '경도·상 분포', '결정상 지도'],
  blocks=[
   dict(kind="sub", en="Simulation Surrogates", ko="시뮬레이션 대리모델"),
   dict(id="ai-surrogate", en="Generative Surrogate for Laser Melting", ko="레이저 용융 멀티피직스 생성형 대리모델",
    main=F("ai-surrogate-result", "레이저 용융 후 남은 잔류응력 세 성분(σ<sub>R,xx</sub> · σ<sub>R,yy</sub> · σ<sub>R,xy</sub>): 각 그림의 왼쪽 절반은 AI 예측, 오른쪽 절반은 수치해석 결과이며, 흰 선은 용융풀 경계, 검은 선은 마르텐사이트 경계입니다 (R² 0.983–0.998)"),
    side=[F("ai-surrogate-arch", "생성형 대리모델 구성: 레이저 출력·빔 직경·조사 시간을 넣으면, 보조 분류기·판별기와 함께 학습한 생성기가 가열 직후(t₁)의 온도·유동·응력장과 냉각 후(t₂)의 마르텐사이트 분율·잔류응력 등 12개 분포를 한 번에 생성합니다"),
          F("ai-surrogate-table", "12개 물리량(고상률, 응력 세 성분, 속도 두 성분, 온도, 압력, 마르텐사이트 분율, 잔류응력 세 성분)의 AI 예측·정답·오차(10배 확대)와 MAE·R²: 모든 물리량에서 R² 0.975 이상입니다")],
    text=["용융·응고·상변태·응력이 얽힌 멀티피직스 해석은 한 조건에 수 시간이 걸려 공정 최적화에 쓰기 어렵습니다. 본 연구실은 통합 운동량 방정식 기반 수치해석 824건으로 학습한 조건부 GAN으로, 레이저 출력·빔 직경·조사 시간 세 값만 넣으면 가열 직후와 완전히 식은 뒤의 단면 분포 12종(온도, 용융풀, 유동, 마르텐사이트, 잔류응력 등)을 한 번에 그려 냅니다. 레이저 가공의 잔류응력을 예측한 첫 생성형 대리모델입니다.",
          "모델은 생성기·판별기에 보조 분류기를 더한 조건부 GAN으로, 세 공정 변수와 잠재 벡터에서 바로 분포 영상을 만들어 냅니다. 적대 손실에 L1·보조 분류·WRN 손실을 더해, 응력처럼 국부 변화가 큰 분포도 선명하게 재현합니다. 12종 분포의 예측 정확도는 R² 0.975–0.999이고, 잔류응력 세 성분은 R² 0.98 이상, 평균 오차 2–3 MPa 수준입니다. 한 번 예측에 0.13초가 걸려 2.5–8시간 걸리는 수치해석을 대신합니다. 수많은 가상 실험을 순식간에 수행할 수 있어, 정규화한 용융 깊이가 레이저 플루언스(I·t)로 잘 정리된다는 점과 출력이 커질수록 잔류응력이 커지고 그 영역이 넓어지는 경향도 정량적으로 파악합니다."],
    stats=[('0.13 s', '예측 시간 (수치해석 2.5–8 h)'), ('R² 0.975–0.999', '12종 분포 예측')], spec="탄소강 레이저 용융 · 입력: 레이저 출력 · 빔 직경 · 조사 시간",
    pubs=[15]),
   dict(id="ai-beam", en="Surrogate for Arbitrary Beam Shapes", ko="임의 빔 형상 대리모델",
    main=F("ai-arbitrary-beam", "학습에 쓰지 않은 빔 형상(왼쪽: 가우시안, 오른쪽: 다중 피크)의 (a) 빔 강도 분포, (b) 온도, (c) von Mises 잔류응력. 각 그림의 왼쪽 절반은 수치해석, 오른쪽 절반은 AI 예측이며, 선은 용융풀·마르텐사이트 경계입니다"),
    side=[F("ai-beam-stages", "단계적 학습 전략: ① 무작위로 만든 합성 빔과 해석식으로 계산한 결과로 사전학습 → ② CFD 해석 결과로 학습 → ③ 실제의 임의 빔 형상으로 시험. 출력은 잔류응력·온도·용융풀·마르텐사이트 분포입니다"),
          F("ai-beam-ring", "가우시안 코어 빔에 탑햇 링 빔을 더한 효과(초록: 링 없음, 빨강·파랑: 링 강도 3.92·7.84 × 10⁵ W/cm²): (a) 코어 강도에 따른 용융풀 폭(실선)·깊이(점선), (b) 최대 잔류응력, (c) 용융풀 면적에 따른 최대 잔류응력 — 용융풀이 일정 크기를 넘으면 빔 구성과 관계없이 600–700 MPa에 머뭅니다")],
    text=["빔 성형(beam shaping)은 용융풀과 잔류응력을 제어하는 강력한 수단이지만, 빔 모양마다 22시간짜리 CFD 해석을 돌릴 수는 없습니다. 어떤 빔 강도 분포를 넣어도 온도·고상률·마르텐사이트·잔류응력 분포를 약 0.013초 만에 그려 내는 생성형 대리모델로 이 문제를 해결합니다.",
          "조각별 선형 hat 함수들의 무작위 가중합으로 임의의 빔을 만들고, 간단한 해석식으로 만든 합성 결과로 먼저 사전학습한 뒤 CFD 결과로 학습하는 단계적 전략을 씁니다. 조건부 GAN은 L1과 마스크 L2를 결합한 손실로 최적화합니다. 학습에 쓰지 않은 가우시안·탑햇·링·베셀 빔에서도 온도는 R² 0.996, von Mises 잔류응력은 R² 0.972로 예측하며, 문헌에서 실측된 불규칙하고 잡음 섞인 빔에도 견고합니다.",
          "이 모델로 빔 구성을 바꿔 보면, 가우시안 코어에 링 빔을 더할 때 용융풀이 커지고 특히 깊이가 민감하게 늘어나지만, 최대 잔류응력은 용융풀이 일정 크기(약 0.05 mm²)를 넘으면 빔 구성과 관계없이 600–700 MPa 범위에 머뭅니다. 코어–링 간격에 따른 용융풀 변화도 바로 탐색할 수 있어 빔 성형 설계와 최적화의 도구가 됩니다."],
    stats=[('~0.013 s', '예측 시간 (CFD 22 h)'), ('R² 0.996', '처음 보는 빔의 온도장')], spec="탄소강 레이저 용융 · 입력: 임의 빔 강도 분포 · CFD 22시간 → 약 0.013초",
    pubs=[7]),
   dict(id="ai-absorb", en="Keyhole Absorptance Surrogate", ko="키홀 흡수율 예측 대리모델",
    main=F("ai-abs-schem", "(a) 학습 데이터 만들기: 상·하부 개구를 이은 3차원 키홀 안에서 광선 추적으로 흡수율을 계산하고(전자기 해석으로 검증) 정답으로 씁니다. (b) 예측: 상부(빨강)·하부(초록) 개구를 담은 2차원 영상 한 장을 딥러닝 모델에 넣으면 흡수율이 바로 나옵니다"),
    side=[F("ai-abs-apert", "학습용으로 만든 가상 개구 영상(빨강: 상부, 노랑·초록: 하부 개구)과 광선 추적으로 계산한 흡수율: 하부 개구가 작아질수록 흡수율이 3.4%에서 96.8%까지 커집니다"),
          F("ai-abs-param", "(a) 키홀 형상 변수(앞벽 기울기 θ, 하부 개구 면적 A<sub>b</sub> 등)와, 흡수율과 (b) 기울기 θ, (c) 정규화 하부 개구 면적, (d) 두 값의 비 θ/A<sub>b,n</sub>의 관계 — 검정: 광선 추적, 빨강: AI 예측")],
    text=["키홀 안의 레이저 흡수율은 광선 추적이나 전자기 해석으로 계산하지만, 키홀 모양이 바뀔 때마다 계산을 처음부터 다시 해야 합니다. 완전 용입 키홀의 위·아래 개구 영상만 넣으면 흡수율을 곧바로 알려 주는 딥러닝 대리모델로 이 계산을 대신하며, 이 모델이 흡수율 기반 실시간 용접 모니터링의 계산 엔진입니다.",
          "학습 데이터는 위·아래 개구를 직선으로 이어 만든 3차원 키홀의 흡수율을 광선 추적으로 계산한 가상 개구 형상 7,418개이며, 광선 추적은 15가지 키홀 형상에서 FDTD 전자기 해석과 비교해 검증했습니다. 깊이가 다른 ResNet 다섯 가지 중 가장 좋은 ResNet-34는 시험 키홀 740개의 흡수율을 1.66초 만에 R² 99.76%로 예측합니다. 흡수율을 좌우하는 변수는 키홀 앞벽의 기울기, 정규화한 하부 개구 면적, 그리고 두 값의 비입니다. 앞벽이 기울수록, 하부 개구가 작을수록 다중 반사가 늘어 흡수율이 커집니다."],
    stats=[('R² 99.76%', '시험 키홀 740개의 흡수율'), ('1.66 s', '740개 예측 시간')], spec="완전 용입 키홀 · 광선 추적 (FDTD 검증) · ResNet-34",
    pubs=[29]),
   dict(id="ai-em-gan", en="Generative Electrodynamic Simulation", ko="생성형 AI 과도 전자기 해석",
    main=F("ai-em-result", "(a) FDTD로 계산한 경사면 반사 패턴(|E<sub>y</sub>|)과 2D FFT, (b) 학습하지 않은 경사각 12.5°·32.5°·52.5°·70°에서 FDTD 정답과 AI 예측의 반사 패턴·2D FFT 비교 (숫자: 정답과의 유사도 97.3–98.9%)"),
    side=[F("ai-em-schem", "모델 구성: 경사면 형상과 시간 정보를 색으로 담은 입력 영상을 GAN이 반사 패턴으로 바꾸며, FDTD 결과를 정답으로 학습합니다. 생성한 반사 영상은 ResNet-18이 흡수율로 바꿉니다"),
          F("ai-em-time", "FDTD로 계산한 반사 패턴의 시간 변화(경사각 32.5°, 0.106 ps 간격): 빔이 내려와 경사면에 닿은 뒤 반사파가 옆으로 퍼져 나가는 과정을 펨토초 단위로 보여 줍니다")],
    text=["레이저 반사와 흡수의 시간 변화를 가장 정확히 계산하는 방법은 FDTD 전자기 해석이지만 계산 비용이 매우 큽니다. 본 연구실은 시간 정보를 색으로 입력 영상에 담는 방식으로, 기울어진 표면에서 레이저 빔이 반사되는 과정을 펨토초 단위로 그려 내는 GAN 기반 과도 전자기 해석 모델을 처음으로 만들었습니다.",
          "표면 경사각을 0°–75°로 바꾼 FDTD 해석 16건(학습 9 · 검증 3 · 시험 4)으로 잔차 블록을 쌓은 생성기와 스펙트럼 정규화 판별기를 학습시켜, 0.106 ps 간격의 반사 패턴을 생성합니다. 반사 영상에서 흡수율을 구하는 두 번째 모델(ResNet-18)은 Fresnel 식으로 만든 정답으로 학습합니다. 학습하지 않은 경사각에서도 반사 패턴을 평균 SSIM 96.7%, R² 98.0%로 재현하고 흡수율은 R² 99.8%로 예측하며, 2D FFT 분석으로 보면 모델은 그림을 흉내 내는 것이 아니라 경사면의 반사 특성을 이해하고 있습니다.",
          "꺾인 면과 곡면에서도 각도 차이 3° 이하, 정규화 곡률 0.032 이하에서는 비교적 정확합니다. 반사 패턴을 예측하면 흡수 패턴을 알 수 있어 열처리·용접·3D 프린팅의 흡수 제어에 쓸 수 있습니다."],
    stats=[('SSIM 96.7%', '처음 보는 경사각의 반사 패턴'), ('R² 99.8%', '흡수율 예측')], spec="FDTD 600 µm 영역 · 경사각 0–75° · GAN + ResNet-18",
    pubs=[9]),
   dict(kind="sub", en="Process Outcome Prediction", ko="공정 결과 예측"),
   dict(id="weld-predict", en="Weld Cross-section Prediction", ko="용접부 단면 예측",
    main=F("weld-bead-pred", "시험 조건 A–D의 레이저 강도·조사 시간(입력, 왼쪽)으로 생성한 용접부 단면 형상(G₁)과 광학 현미경 이미지(G₂)를 실제와 비교: 강도가 높고 조사 시간이 길수록 용융부가 넓고 깊어지는 경향을 그대로 재현합니다"),
    side=[F("ai-bead-arch", "2단계 생성 모델: 첫 번째 생성기 G₁(CNN 인코더–디코더)이 레이저 강도·조사 시간으로 단면 용융 영역을 만들고, 두 번째 생성기 G₂(잔차 블록을 넣은 cGAN)가 이를 실제 광학 현미경 사진처럼 바꿉니다")],
    text=["용접 조건만으로 용접부 모양을 미리 아는 것이 목표입니다. 딥러닝으로 용접부 단면의 형상과 현미경 이미지 자체를 생성해 비드 크기와 모양을 예측합니다. AISI 1020 강의 레이저 키홀 용접에서 레이저 강도와 조사 시간 두 값을 입력하면, 첫 번째 생성기(CNN)가 단면의 용융 영역 형상을 만들고 두 번째 생성기(CNN + cGAN)가 이 형상을 실제 광학 현미경 사진처럼 바꿉니다.",
          "실험 45회(학습 39 · 검증 2 · 시험 4)의 데이터만으로 학습해도, 학습에 쓰지 않은 조건에서 비드 전체의 모양과 크기가 실제 단면과 잘 맞습니다. 시편을 잘라 연마·에칭하지 않고도 용접 조건별 단면을 미리 볼 수 있습니다."],
    stats=[('45회', '실험 (학습 39 · 검증 2 · 시험 4)')],
    spec="AISI 1020 강",
    pubs=[34]),
   dict(id="ht-ai", en="Hardness & Phase Prediction in Laser Heat Treatment", ko="레이저 열처리 경도·상 분포 예측",
    main=F("ht-hardness-pred", "0.5초 간격으로 구한 두 단면 온도 분포(c₁, c₂, 입력)와 시험 조건 A–D의 경도 분포: 정답, AI 예측, 상대 오차 — SSIM 87.7–95.3%"),
    side=[F("ht-phase-pred", "상 분포 예측(시험 조건 A–D): 두 온도 분포를 넣으면(가운데) 용융부 아래의 연화 영역까지 87.7–93.7% 정확하지만, 온도 분포 하나만 넣으면(오른쪽) 74.7–91.7%로 떨어집니다"),
          F("ht-model", "경도·상 분포 생성 모델(cGAN): 두 온도 분포를 입력받는 잔차 인코더–디코더 생성기(G)와 판별기(D)로 이루어지며, 출력은 경도 분포(1채널) 또는 상 분포(4채널)입니다")],
    text=["열처리 결과는 온도 이력이 결정하지만, 온도에서 경도로 가는 관계는 복잡합니다. 본 연구실은 열해석으로 얻은 두 단면의 온도 분포를 넣으면 경도와 상(경화층·연화층) 분포를 이미지로 바로 그려 내는 딥러닝 모델을 씁니다. 유한요소 열전도 해석으로 0.5초 간격의 두 단면 온도 분포를 구해 입력하고, 2 kW 파이버 레이저 실험으로 얻은 경도·상 분포를 정답으로 잔차 신경망 기반 GAN을 학습시킵니다. 두 온도 분포는 열처리에서 가장 중요한 냉각 속도 정보를 모델에 전달합니다.",
          "16개 실험(학습 9 · 검증 3 · 시험 4)만으로 AH36 강의 단면 경도 분포를 SSIM 87.7–95.3%(평균 92.2%)로 예측합니다. 온도 분포를 하나만 쓰면 경화만 예측되지만, 두 개를 쓰면 용융부 바로 아래의 연화 영역까지 정확히 예측됩니다(연화 영역 깊이 정확도 60.3% → 90.7%). 상 분포도 두 온도를 입력할 때 최대 13%p 더 정확합니다.",
          "AISI H13 공구강에서는 표면 온도가 최고일 때의 단면 온도 분포 하나만으로 경도 분포를 그리는 cGAN 모델을 씁니다. 세 가지 공정 조건(주사 창으로 213개로 증강)만으로 평균 94.4% 정확도를 얻어, 탄소 확산 시간 모델보다 약 10% 정확합니다."],
    stats=[('95.3%', '단면 경도 분포 SSIM (최대)'), ('9회', '학습에 쓴 실험 수')],
    spec="조건부 GAN (cGAN) · 입력: 두 단면의 온도 분포",
    pubs=[39, 17]),
   dict(id="ai-lipss", en="LIPSS Surface Morphology & Reflectance Prediction", ko="LIPSS 표면 형상·반사율 예측",
    main=F("uf-morph", "스테인리스 LIPSS 표면 세 조건(A–C): 실제 전자현미경 이미지(위)와 cGAN이 플루언스·주사 속도만으로 생성한 이미지(아래) — 리플의 주기와 폭, 2차 구조까지 재현합니다"),
    side=[F("uf-reflect", "세 표면(a–c)의 반사 스펙트럼(350–750 nm): 실측(초록), 실제 이미지로 예측(빨강), 생성 이미지로 예측(파랑) — 세 곡선이 거의 겹칩니다"),
          F("ai-reflect-flow", "합성 표면 학습: (a) 역피라미드·원뿔로 만든 합성 표면의 550 nm 반사율을 광선 추적으로 계산해 ResNet-34를 학습 → (b) 실제 공초점 현미경(CLSM) 표면 영상 1–3장으로 검증 → (c) 처음 보는 실제 표면 영상으로 반사율을 예측합니다"),
          F("ai-reflect-pred", "처음 보는 실제 LIPSS 표면 네 개의 CLSM 영상과 반사율: AI 예측(빨강) / 실측(흰색) — 실측 반사율 8.54–55.40%의 넓은 범위에서 잘 맞습니다")],
    text=["펨토초 레이저로 만든 LIPSS 표면은 공정 조건에 따라 형상과 반사율이 크게 달라지지만, 조건마다 시편을 만들어 전자현미경과 분광기로 재야 합니다. 공정 조건에서 표면 이미지를, 표면 이미지에서 반사율과 반사 스펙트럼을 예측하는 모델로 이 과정을 대신하고, 합성 표면만으로 학습한 모델로 실제 표면의 반사율도 예측합니다.",
          "먼저 cGAN이 플루언스와 주사 속도만으로 SEM 표면 이미지를 만들어, 학습하지 않은 조건에서도 리플의 주기와 폭을 98.2%·94.6% 정확도로 재현합니다(32개 조건 중 26개로 학습). 이어 ResNet152–LSTM 모델이 표면 이미지로 550 nm 반사율과 350–750 nm 반사 스펙트럼을 예측합니다. 생성한 이미지로 예측한 스펙트럼도 실측과 잘 맞아, 스펙트럼 오차(L₂ 노름)가 4% 미만입니다.",
          "합성 표면 학습에서는 역피라미드와 원뿔을 섞어 만든 표면의 반사율을 각도별 Fresnel 반사를 고려한 광선 추적으로 계산하고, 이 합성 표면 영상으로 ResNet-34를 학습시킵니다(최적 조건: 패턴 배열 28 × 28, 혼합비 5:5). 실제 표면의 공초점 현미경(CLSM) 높이 영상을 넣으면 반사율을 예측하며, 스테인리스(SUS 304) LIPSS 표면 32개(반사율 8.54–55.40%) 중 3개만 검증에 쓰고 나머지 29개를 시험한 결과는 R² 92.40%, 평균 절대 오차 2.98%입니다."],
    stats=[('98.2%', '리플 주기 재현 정확도'), ('R² 92.4%', '합성 표면만으로 학습한 반사율')], spec="펨토초 레이저 · 스테인리스강 304 · SEM · 공초점 현미경 (CLSM) · 분광 반사율",
    pubs=[21, 13]),
   dict(id="uf-anneal", en="Crystalline Phase Prediction of Laser-processed Silicon", ko="레이저 가공 실리콘의 결정상 예측",
    main=F("uf-phase-map", "49개 공정 조건(세로: 플루언스, 가로: 주사 속도) 전체의 실리콘 결정상 분포 지도: 110만 개가 넘는 라만 스펙트럼을 1차원 CNN으로 분류해 그렸습니다 (빨강: c-Si, 초록: a-Si, 노랑: n-Si, 하늘: poly+a-Si, 파랑: poly-Si)"),
    side=[F("uf-phase", "시험 조건 5개(플루언스·주사 속도)의 실리콘 결정상 분포: AI 예측 영상, 라만 분석으로 만든 정답 영상, 위치별 결정상 개수 분포(실선: 예측, 점선: 정답). 색: c-Si(빨강), a-Si(초록), n-Si(노랑), poly+a-Si(하늘), poly-Si(파랑)"),
          F("uf-annealing", "펨토초 레이저 어닐링 장치(왼쪽)와 플루언스(0.183–2.64 J/cm²) × 주사 속도(13.9–200 mm/s) 49개 조건의 가공 표면(오른쪽, 색 띠: 라만 스펙트럼 유형)"),
          F("uf-raman", "라만 스펙트럼 형태로 나눈 결정상: (a) 결정질 c-Si(520 cm⁻¹), (b) 비정질 a-Si, (c) 나노결정 n-Si(512.5 cm⁻¹), (d) 비정질+다결정, (e) 다결정 poly-Si(517.5 cm⁻¹), (f) 분류 불가 — 점: 측정, 선: 피팅")],
    text=["펨토초 레이저로 실리콘을 어닐링하면 레이저 세기와 주사 속도에 따라 결정 상태가 달라지고, 이는 반도체 소자의 특성을 좌우합니다. 본 연구실은 라만 스펙트럼을 자동 분류해 결정질·비정질·나노결정·다결정 실리콘의 분포를 지도로 만들고, 공정 조건만으로 이 지도를 예측합니다.",
          "단결정 실리콘을 플루언스 0.183–2.64 J/cm², 주사 속도 13.9–200 mm/s의 49개 조건으로 가공하고, 시편마다 22,500개 지점에서 라만 스펙트럼을 측정합니다. 첫 번째 모델(1차원 OS-CNN)은 110만 개가 넘는 스펙트럼을 결정질·비정질·나노결정·다결정 등 여섯 유형으로 95.52% 정확도로 분류해, 시편 전체의 결정상 분포를 색 지도로 그려 냅니다. 학습에서 한 가지 스펙트럼 유형을 빼고 시험해도 정확도는 94.89%로 거의 같습니다.",
          "이렇게 만든 49장의 상 분포 지도로 두 번째 모델(cGAN)을 학습시켜, 플루언스와 주사 속도만으로 결정상 분포 영상을 생성합니다. 데이터가 적은데도 평균 픽셀 정확도 86.60%로 실제 분포와 잘 맞습니다. 라만 스펙트럼 해석에 드는 시간을 크게 줄이고, 원하는 결정상 분포를 얻는 공정 조건을 설계하는 데 쓸 수 있습니다."],
    stats=[('95.52%', '라만 스펙트럼 6종 분류'), ('86.60%', '공정 조건만으로 결정상 지도 예측')],
    spec="펨토초 레이저 · 갈바노 스캐너 · 라만 분광",
    pubs=[20]),
  ]),
 dict(id="auto", en="AI for Autonomous Laser Processing", ko="AI 기반 자율 레이저 가공", ten="Autonomous Processing", tko="AI 자율 가공", color="mint",
  icon='<path d="M9 3v2M15 3v2M9 19v2M15 19v2M3 9h2M3 15h2M19 9h2M19 15h2"/><rect x="5" y="5" width="14" height="14" rx="3"/><path d="M9.5 15l1.6-6h1.8l1.6 6M10 13h4"/>',
  lead="카메라 영상을 보고 장비가 <b>스스로 제어 코드를 만들어 움직이는</b> 자율 레이저 가공을 연구합니다. 핵심은 본 연구실이 제안한 <b>Vision-to-Code</b> 방식입니다. 영상 처리, 위치 보정, 장비 프로그래밍으로 나뉘어 있던 단계를 하나의 모델로 합쳐, 영상 한 장에서 <b>바로 실행할 수 있는 제어 코드</b>를 생성합니다. 사람이 규칙을 짜지 않아도 장비가 상황을 판단해 동작 순서까지 정하며, 단일 카메라만으로 굴곡진 3차원 용접선을 사람의 개입 없이 용접합니다.",
  chips=['Vision-to-Code', 'Physical AI · VLA', 'Transformer 디코더', '실행 가능한 C# 코드', '단일 카메라 3D', '용접선 추적'],
  blocks=[
   dict(id="ai-v2c", en="Vision-to-Code Autonomous Laser Welding", ko="Vision-to-Code 자율 레이저 용접",
    main=F("ai-v2c-arch", "Vision-to-Code 모델 개략도: 용접선 영상 → CNN 영상 인코더 → 시맨틱 검색 모듈 + 비자기회귀 Transformer 디코더 → DSL 토크나이저 → 실행 가능한 코드 토큰을 한 번에 생성"),
    side=[F("ai-v2c-concept", "작동 방식: 프레임마다 용접선 영상을 찍으면 모델이 목표 위치와 해야 할 작업을 인식해 C# 코드를 생성하고, 이 코드를 컴파일·실행해 3축 스테이지와 파이버 레이저를 움직입니다. 첫 프레임에서는 시작점을 정렬하고(alignToStart), 이어서 용접선을 추적하며(seamTracking), 마지막 프레임에서는 끝점 정렬 뒤 원점으로 돌아가 용접을 시작합니다"),
          V("v2c-demo", "3D 자율 용접 시연: 카메라 영상(오른쪽 위)만 보고 모델이 생성한 제어 코드(오른쪽 아래)로 3축 스테이지가 굴곡진 용접선을 따라 움직이며 용접합니다"),
          F("ai-v2c-result", "3D 확장 결과: (a) 실측 3차원 용접선(검정)과 AI가 생성한 경로(빨강), (b) 굴곡진 협개선 맞대기 시편, (c) 평면(x–y) 경로, (d) 높이(z) 경로 — 생성 경로가 레이저 초점 심도(파랑 실선)와 카메라 피사계 심도(파랑 점선) 안에 듭니다")],
    text=["기존 자동 용접선 추적은 영상 처리로 용접선을 찾고, 정해 둔 규칙으로 위치를 보정하고, 장비 프로그램을 따로 짜는 여러 단계로 나뉘어 있어, 작업이 바뀔 때마다 사람이 규칙과 프로그램을 다시 만들어야 합니다. 본 연구실이 제안한 Vision-to-Code는 카메라 영상 한 장을 보고 장비가 바로 실행할 제어 코드를 생성해, 이 단계들을 하나의 딥러닝 모델로 합칩니다. 영상을 보고 판단해 행동까지 만들어 내는 Vision-Language-Action(VLA) 개념을 용접선 추적에 처음 도입한 Physical AI 연구입니다.",
          "이 방식에는 세 가지 장점이 있습니다. 첫째, 영상 처리 규칙이나 정렬 로직을 손으로 만들 필요가 없는 end-to-end 구조입니다. 둘째, 출력이 좌표값이 아니라 실행 가능한 코드이므로 용접선 추적뿐 아니라 시작점 정렬, 용접 시작, 원점 복귀, 용접선 미검출 경고처럼 무엇을 어떤 순서로 할지까지 한 번에 정합니다. 셋째, 라인 레이저 방식은 0.1 mm보다 좁은 틈에서 추적이 어렵지만, 이 모델은 한 픽셀에 해당하는 20 µm 틈까지 찾아 빔이 아주 작은 레이저 용접에 유리합니다. 제어 함수만 정의하면 같은 틀을 다른 장비와 공정으로 넓힐 수 있습니다.",
          "모델 학습을 위해 용접선 흑백 영상과 실행 가능한 C# 코드를 짝지은 데이터셋을 직접 구축하고(목표 위치 정의 → 제어 함수 정의 → 영상별 작업 계획 → 코드 라벨링), CNN 영상 인코더, 시맨틱 검색 모듈, 비자기회귀 Transformer 디코더, 전용(DSL) 토크나이저로 이루어진 모델을 처음부터 학습시킵니다. Pix2Pix로 만든 합성 영상으로 데이터를 보강하며, 모델은 상대 좌표 같은 인자까지 포함한 코드(<code>seamTracking(abspos, deltapos)</code> 등)를 한 번에 만들어 냅니다. 알루미늄(Al 1050P-H16) 맞대기 용접에서 코드 생성 정확도는 BLEU-4 0.949, pass@1 99.62%이고, 추적 오차는 평균 절대 오차 1–9 µm, 최대 편차 20–60 µm입니다. 코드 생성 22 ms, 실행 9 ms를 포함해 한 프레임 처리에 약 38 ms가 걸리며, 학습에 없던 곡선 용접선과 압연 방향이 다른 표면 질감, 잡음·흐림이 더해진 영상에서도 사람의 개입 없이 용접합니다.",
          "같은 방식을 3차원으로 넓혀, 렌즈의 초점 흐림(defocus blur)과 조명 밝기가 높이에 따라 달라지는 점을 단서로 카메라 한 대의 영상에서 높이까지 읽어 냅니다. 3D 스캐너 없이 3축 제어 코드를 생성해 굴곡진 협개선 맞대기 용접을 수행하며, 생성한 경로는 실측 용접선과 레이저 초점 심도 이내로 일치합니다. 영상에서 펨토초 레이저 패터닝 제어 코드를 직접 생성해 여러 영역으로 나뉜 삼각형 패턴을 자동 가공하는 연구로도 확장하고 있습니다."],
    stats=[('99.62%', '코드 생성 정확도 (pass@1)'), ('~38 ms', '한 프레임 처리 시간'), ('20 µm', '추적 가능한 틈')], spec="2 kW 멀티모드 파이버 레이저 · 3축 스테이지 · 단일 비전 카메라 · Al 1050P-H16 맞대기 용접",
    pubs=[8, 4, 3]),
  ]),
 dict(id="sim", en="Modeling, Simulation & Laser–Matter Physics", ko="모델링·시뮬레이션과 레이저–물질 상호작용", ten="Simulation & Physics", tko="시뮬레이션·물리", color="navy",
  icon='<path d="M12 3a9 9 0 1 0 9 9"/><path d="M12 7a5 5 0 1 0 5 5"/><circle cx="12" cy="12" r="1.5"/><path d="M17 3h4v4"/><path d="M21 3l-6 6"/>',
  lead="레이저 가공 중에는 열전달, 유체 유동, 용융·증발 같은 상변화, 전자기파의 전파, 플라즈마, 고체 변형이 한꺼번에 일어납니다. 본 연구실은 이 현상들을 푸는 수치 기법을 <b>직접 개발</b>하고 이론과 실험으로 레이저–물질 상호작용의 물리를 밝혀 왔으며, 여기서 얻은 물리 이해와 시뮬레이션 데이터가 AI 연구의 바탕이 됩니다.",
  chips=['Level Set', 'Ray Tracing', 'FDTD', 'Two-Temperature Model', 'Lattice Boltzmann', 'Unified Momentum Equation', '증발·상폭발'],
  blocks=[
   dict(id="sim-ablation", en="Laser Drilling, Ablation & Vaporization Physics", ko="레이저 드릴링·어블레이션과 증발 물리",
    main=V("sim-drilling", "레이저 드릴링 시뮬레이션 (10⁸ W/cm²): 시간에 따라 깊어지는 구멍 형상(왼쪽), 다중 반사로 구멍 중심에 모이는 빔 강도(가운데), 구멍 표면의 온도 분포(오른쪽)"),
    side=[],
    text=["드릴링처럼 레이저 세기가 매우 높으면 표면 온도가 끓는점을 훨씬 넘어 임계점 가까이 올라가고, 재료는 액체 분출·증발·균일 핵생성 비등(상폭발)의 세 가지 방식으로 제거됩니다. 구멍 형상이 스스로 진화하도록 자유 표면·용융 유동·열전달·증발을 함께 계산하는 모델(이후 키홀 용접 해석의 바탕)을 개발하고, 실리콘 실험과 결합해 레이저 세기에 따라 에너지가 어떻게 흡수되고 재료가 어떤 방식으로 제거되는지 분석합니다.",
          "구멍 표면(기체–액체 경계)은 level set으로 추적하고, 그 법선으로 광선 추적을 해 다중 반사된 레이저 에너지 분포를 구합니다. 표면 아래의 얇은 용융층에서는 반발압력과 열모세관력이 밀어내는 액체 유동을 Navier–Stokes 방정식을 셀 단위로 적분해 계산하고, 각 셀의 질량·에너지 수지(Stefan 조건)로 증발·액체 분출·상폭발에 의한 표면 후퇴 속도를 각각 구해 level set을 갱신합니다. 고체로 빠져나가는 열은 이동 경계를 갖는 반무한 고체의 해석해로 계산합니다. 상폭발이 일어나는 조건을 정하기 위해 밀도, 증발 잠열, 표면장력 같은 물성을 임계점까지 이론적으로 확장하고, 고온 증발의 반발압력(임계점에서 포화압력의 약 51%)과 균일 핵생성 속도를 계산합니다.",
          "구멍이 깊어질수록 다중 반사로 유효 흡수율이 약 80%까지 오르고, 레이저 에너지가 구멍 중심에 원래보다 약 100배 집중됩니다. 반면 키홀 용접에서는 최대 약 5배에 그쳐 에너지가 넓게 퍼집니다. 즉 드릴 구멍은 에너지를 한 점에 모으는 모양이고 키홀은 고르게 나누는 모양이며, 흔히 가정하는 포물면 구멍은 흡수 특성을 크게 틀리게 예측합니다. 철에 10⁷과 10⁸ W/cm²의 레이저를 조사하면, 다중 반사가 에너지를 중심에 모아 다중 반사를 고려하지 않은 경우보다 구멍 폭이 약 50% 좁아집니다. 세기를 10배 높이면 용융층 두께는 약 60% 얇아지고 재료 제거의 주된 방식도 액체 분출에서 증발로 바뀝니다. 3차원으로 완전히 관통된 구멍의 형성도 처음으로 계산했습니다.",
          "Q-스위치 다이오드 여기 고체 레이저로 실리콘에 단일 펄스 드릴링을 하면, 세기가 10⁸에서 10⁹ W/cm²로 오를 때 주된 제거 방식이 액체 분출에서 상폭발로 바뀝니다. 같은 질량을 제거하는 데 드는 에너지는 액체 분출 : 증발 : 상폭발이 약 1 : 8 : 9로, 액체 분출이 가장 효율적이고 증발의 기여는 작습니다."],
    stats=[("~80%", "드릴링 구멍의 최대 유효 흡수율"), ("1 : 8 : 9", "분출 : 증발 : 상폭발의 단위 질량당 에너지")],
    spec="CW 레이저 10⁷–10⁸ W/cm² (철) · Q-스위치 DPSSL 10⁸–10⁹ W/cm² (실리콘)",
    pubs=[83, 82, 76, 70]),
   dict(id="sim-em", en="Electrodynamic (FDTD) Simulation", ko="전자기장 해석",
    main=V("sim-fdtd-demo", "FDTD 데모 (약 26초): ① 기울기 0–70°인 철 표면에서의 전기장 (s 편광, 파장 1.06 → 21.2 µm 확대), ② 40° 입사에서 입사파와 반사파가 간섭 무늬를 만드는 과정, ③ 20° 기운 키홀에서 s·원·p 편광 비교, ④ 실측 키홀 형상(DP590, GA DP590 · 1403 W, 1830 W)에서의 레이저 전파"),
    side=[],
    text=["레이저는 전자기파이므로 흡수는 재료, 파장, 편광, 입사각에 따라 달라지고, 키홀처럼 빛이 여러 번 반사되는 구조에서는 그 차이가 커집니다. 맥스웰 방정식을 직접 푸는 FDTD가 가장 정확한 방법이지만, 파장당 격자 10개가 필요해 수 mm 크기의 용접 문제는 사실상 계산할 수 없었습니다. 본 연구실은 반사 특성은 그대로 두고 파장만 크게 늘리는 기법을 개발해, 레이저 가공 공정을 처음으로 전자기 해석으로 풀었습니다.",
          "금속의 반사율은 굴절률 n과 소광계수 κ, 입사각으로만 정해집니다. 표준 FDTD에서는 전기전도도와 파장의 곱(σλ)을 유지하면, 분산 매질 FDTD에서는 Drude 모델의 ε∞, 플라즈마 주파수, 감쇠 상수를 새로 골라 유전율을 유지하면 파장을 늘려도 n과 κ가 그대로입니다. 1.06 µm 빛을 212 µm(200배)로 바꾸면 3차원 격자 수가 1/8,000,000로 줄어듭니다. κ가 n보다 큰 철은 반사율이 거의 같은 새 (n, κ) 쌍을 찾아 표준 FDTD로도 풉니다. 철과 주석의 경사면(0–70°)에서 s, p, 원편광의 반사율이 이론값과 일치하고, 철 원기둥에 가우시안 빔을 비춘 3차원 문제에서도 오차가 4.6% 이하이며, 파장을 20배 늘린 결과와 원래 파장의 결과는 사실상 같습니다.",
          "이 기법으로 완전 관통 키홀을 기울어진 원기둥으로 모델링하고 철·주석·알루미늄, 1.06·10.6 µm, 세 가지 편광, 기울기 0–45°를 계산합니다. 키홀이 기울수록 반사 횟수가 늘어 흡수율이 커지며, 철(1.06 µm)은 수직 키홀에서 25–30%, 45°에서 90–100%(반사 약 4회)이지만 알루미늄은 45°에서도 30–45%에 그칩니다. 전기장이 키홀 기울기(용접) 방향을 향한 편광이 가장 잘 흡수되고, 원편광은 두 선편광의 평균입니다. 용접 속도가 빨라지면 키홀이 더 기울어 흡수가 늘어나는 자기 조절 능력도 이것으로 설명됩니다.",
          "같은 기법을 아연도금 강판의 키홀 에너지 흡수와 워터젯 유도 레이저 가공(다음 항목)에도 적용합니다. 최근에는 FDTD 결과로 GAN 대리모델을 학습시켜, 기울어진 표면(0–75°)에서 레이저 빔이 반사되는 시간별 패턴을 영상 한 장으로 예측합니다(SSIM 96.7%, R² 98.0%)."],
    stats=[('1/8,000,000', '줄어든 3차원 격자 수 (파장 200배)'), ('90–100%', '45° 기운 철 키홀의 흡수율')],
    spec="Fe · Sn · Al · 1.06 / 10.6 µm · 확대 파장 212 µm · 빔 직경 600 µm · 키홀 직경 1 mm · CPML 흡수 경계",
    pubs=[60, 59, 51]),
   dict(id="sim-waterjet", en="Waterjet-guided Laser Processing", ko="워터젯 유도 레이저 가공 해석",
    main=F("wj-coupling", "물 챔버에서 물기둥 입구로 집속된 레이저 빔이 물기둥 안으로 들어가는 과정 (FDTD 전기장, N.A. 0.665): 위 줄은 532 nm, 아래 줄은 1064 nm이고 왼쪽부터 물기둥 반지름 25·50·100 µm입니다. L은 입구에서 새는 에너지로, 물기둥이 굵을수록 줄어들지만 가는 물기둥에서는 내부 다중 반사와 간섭으로 빔이 더 강하게 모입니다 (흰 선: 물–공기 경계)"),
    side=[F("wj-setup", "워터젯 유도 레이저 가공 장치: 렌즈로 집속한 빔이 창을 지나 물 챔버의 노즐로 들어가고, 노즐에서 나온 가는 물줄기 안에서 전반사되며 가공물까지 전달됩니다"),
          F("wj-prop", "길이 2 cm 물기둥 속 레이저 전파 (위: 532 nm, 아래: 1064 nm / 왼쪽부터 원기둥, 사인파 출렁임 1주기·진폭 5 µm, 1주기·15 µm, 3주기·15 µm): T는 끝까지 투과한 비율로, 532 nm는 약 90%, 1064 nm는 약 23%이며 출렁임이 클수록 조금씩 줄어듭니다 (가로 방향은 늘려 표시)"),
          F("wj-joule", "같은 조건의 줄 가열 분포: 물기둥이 잘록한 곳에서는 전기장이 모여 줄 가열이 강해지고, 볼록한 곳에서는 약해집니다. A는 물에 흡수된 비율(1 − T)이며, 532 nm는 잘 보이도록 색 범위를 따로 맞췄습니다"),
          F("wj-temp532", "532 nm 빔의 줄 가열로 생기는 물기둥 온도 (정상 상태, 위: 반지름 25 µm, 아래: 50 µm / 왼쪽부터 유속 0.1·2·50 m/s): 검은 선은 100 °C 등온선입니다. 유속이 느리면 100 °C를 넘어 증발이 생길 수 있지만, 유속이 빨라지면 온도가 거의 오르지 않습니다 (가로 10배 확대)"),
          F("wj-temp1064", "1064 nm 빔의 경우 (배치는 왼쪽과 같음): 물의 흡수가 커서 온도가 훨씬 높고, 50 m/s의 빠른 유속에서도 증발이 일어나 실제 가공에는 적합하지 않습니다")],
    text=["워터젯 유도 레이저 가공은 머리카락 굵기의 물줄기를 광섬유처럼 써서 레이저를 가공물까지 보내는 기술입니다. 물과 공기의 굴절률 차이로 빔이 물기둥 안에서 전반사되며 갇혀 진행하므로, 초점을 맞추지 않아도 긴 작업 거리에서 일정한 크기의 빔으로 가공할 수 있고 물이 열과 부산물을 함께 씻어 냅니다. 그러나 빔이 물기둥 안에서 어떻게 전파되고 얼마나 흡수되는지는 거의 연구되지 않았습니다. 본 연구실은 파장 확대 FDTD로 맥스웰 방정식을 풀고 열전도 방정식을 함께 풀어, 워터젯 속 레이저 전파를 처음으로 전자기 해석으로 다룹니다.",
          "1064 nm 레이저와 그 2배파인 532 nm 레이저가 물기둥 입구에 집속되어 들어가는 과정을 3차원(150 µm × 150 µm × 2 cm)으로 계산합니다. 개구수(N.A. 0.1–0.665)와 물기둥 반지름(25–100 µm)에 따라 입구에서 새는 에너지는 0.02%에서 27%까지 달라지며, 집속 빔이 물기둥에 비해 작을수록 손실이 줄어듭니다. 굵은 물기둥은 손실이 거의 없지만 빔이 약하고 고르게 모이지 않으므로, 집속 빔을 물기둥 지름보다 약간 작게 하는 것이 가공 품질에 유리합니다.",
          "실제 물줄기는 표면장력 때문에 출렁이므로(Plateau–Rayleigh 불안정성) 표면을 사인파로 모델링해 길이 2 cm 물기둥의 투과율을 비교합니다. 532 nm는 약 90%, 1064 nm는 약 23%만 투과하며, 출렁임이 커질수록 투과율이 조금씩 줄어듭니다. 물기둥이 잘록한 곳에서는 전기장이 모여 줄 가열이 강해집니다. 줄 가열을 열원으로 물 흐름까지 고려한 열해석에서는, 532 nm도 유속이 0.1 m/s로 느리면 100 °C를 넘어 증발이 생길 수 있지만 유속이 빨라지면 온도가 거의 오르지 않습니다. 반면 1064 nm는 50 m/s에서도 증발이 일어나, 워터젯 유도 가공에는 물의 흡수가 작은 532 nm가 적합합니다."],
    stats=[("90% vs 23%", "2 cm 물기둥 투과율 (532 vs 1064 nm)"), ("0.02–27%", "입구 결합 손실")],
    spec="532 · 1064 nm (확대 파장 5.89 · 11.78 µm) · 물기둥 반지름 25–100 µm, 길이 2 cm · N.A. 0.1–0.665 · 유속 0.1–50 m/s · CPML 흡수 경계",
    pubs=[35]),
   dict(id="sim-fs", en="Femtosecond Laser–Silicon Interaction", ko="펨토초 레이저–실리콘 상호작용",
    main=V("sim-fs-compare", "80 fs 펄스가 실리콘에 흡수되는 과정 (각 쌍의 왼쪽: 반경 방향 전기장, 오른쪽: 열로 바뀐 전자기 에너지): 이온화를 고려하지 않으면(왼쪽 쌍) 빛이 실리콘 속으로 그대로 들어가 깊은 곳까지 가열되지만, 이온화를 고려하면(오른쪽 쌍) 자유전자가 급증해 빛이 막히고 에너지가 표면의 얇은 층에서 거의 다 흡수됩니다"),
    side=[],
    text=["펨토초 펄스는 원자 격자가 데워지기(약 1 ps) 전에 끝날 만큼 짧아서, 레이저 에너지가 먼저 전자로 들어가고 전자와 격자의 온도가 따로 움직입니다. 펨토초 레이저는 문턱값이 뚜렷하고 가공 품질이 좋은 것으로 알려져 있지만, 반도체 미세가공에서는 오히려 결과가 좋지 않다는 보고가 있고 그 이유는 분명히 설명되지 않았습니다. 본 연구실은 맥스웰 방정식(FDTD)에 2온도 모델과 이온화·전기전도도 모델을 결합해, 실리콘 안에서 빛이 전파되고 전자가 들뜨는 과정을 펨토초 단위로 추적합니다. 전자기장은 원통 좌표 FDTD로 풀고, 전자–격자 에너지 교환은 2온도 모델로 계산합니다. 레이저 에너지 수지를 바탕으로 한 이온화 모델로 자유전자 밀도를 구하고, 전자 밀도와 온도로 고밀도 플라즈마의 전기전도도를 예측해 다시 맥스웰 방정식에 넣습니다.",
          "이온화를 고려하지 않으면 빛이 실리콘 속으로 그대로 들어가지만, 이온화를 고려하면 자유전자가 급증해 전기전도도가 약 10⁵배(1.4 → 3×10⁵ S/m 이상) 커지고 실리콘이 금속처럼 행동합니다. 레이저가 표면의 얇은 층(스킨 깊이)에서 거의 다 흡수되고 그 두께가 고르게 정해지는데, 이것이 펨토초 레이저의 뚜렷한 문턱값과 깨끗한 가공 품질을 설명합니다.",
          "이온화를 고려하지 않은 초기 모델에서도 전자 온도는 200 fs 안에 50,000 K 이상 오르지만 격자 온도는 약 10 K만 오르고, 이온화를 고려하면 전자 온도가 80 fs 안에 약 250,000 K까지 치솟습니다. 가우시안 빔 가장자리는 세기가 약해 이온화가 덜 되므로 빛이 안쪽으로 새어 들어가고, 이 부분이 열 용융과 결함의 원인이 될 수 있습니다. 문턱값 이상에서는 흡수율이 펄스 에너지와 거의 무관하게 약 0.38로 수렴합니다."],
    stats=[("~10⁵배", "이온화로 증가한 실리콘 전기전도도"), ("50,000 K", "200 fs 안에 도달하는 전자 온도 (격자는 +10 K)")],
    spec="800 nm · 80 fs · 7.5–60 µJ · BOR-FDTD + PML",
    pubs=[79, 75]),
   dict(id="sim-plasma", en="Plasma & MHD (Lattice Boltzmann Method)", ko="플라즈마·자기유체 해석",
    main=[V("sim-plasma4", "CO₂ 레이저(2 × 10⁷ W/cm²)가 약하게 이온화된 헬륨 플라즈마를 지날 때의 전기장, 줄 가열, 전자 밀도, 전자 온도 (격자 볼츠만 방법): 레이저가 지나는 길을 따라 전자 충돌 이온화로 전자가 늘고 가열됩니다"),
          V("sim-mhd", "격자 볼츠만–유한차분 혼합 기법으로 계산한 Orszag–Tang 와류: 자기유체 난류의 대표적인 검증 문제로, 자기장과 유동이 얽히며 복잡한 구조로 발달합니다")],
    side=[],
    text=["용접 중 키홀 위에 생기는 플라즈마는 레이저 에너지를 흡수·산란시켜 용접 품질에 큰 영향을 줍니다. 플라즈마는 전자·이온·중성 입자가 전자기장과 함께 움직이는 복잡한 계라서 기존 유체 해석으로는 다루기 어렵습니다. 본 연구실은 병렬 계산에 유리한 격자 볼츠만 방법(LBM)으로 플라즈마와 자기유체를 해석합니다.",
          "전자·이온·중성 입자 각각에 대한 볼츠만 방정식을 LBM으로 풀고, 전기장은 포아송 방정식(정전기 문제)이나 FDTD로 푼 맥스웰 방정식(레이저 문제)으로 구합니다. 실제 물성값을 그대로 쓰면 LBM의 이완 시간이 지나치게 커지는데, 점성과 외력에 의한 특성 속도를 보존하는 재스케일링 기법으로 이 문제를 해결합니다. 이온화도 1–3% 헬륨 플라즈마의 확산과 정전기파 문제로 기법을 검증했고, CW CO₂ 레이저(1.25–2 × 10⁷ W/cm²)가 헬륨 플라즈마를 지날 때 전자 충돌 이온화로 이온화도와 전자 온도가 어떻게 변하는지 계산합니다. 자기유체역학(MHD)은 유동을 LBM으로, 자기장 유도 방정식을 유한차분법으로 푸는 혼합 기법으로 다루며, Hartmann 유동, 2·3차원 Orszag–Tang 와류, 자기 재결합 문제로 검증했습니다."],
    stats=[("3종 입자", "전자·이온·중성 입자를 각각 계산"), ("2D·3D", "MHD 혼합 LBM–유한차분 기법 검증")],
    spec="CW CO₂ 레이저 1.25–2 × 10⁷ W/cm² · 약전리 헬륨 플라즈마",
    pubs=[74, 72, 68, 73]),
   dict(id="sim-magnetic", en="Two-Phase Flow under Magnetic Fields", ko="자기장 속 2상 유동 해석",
    main=V("sim-magdrop", "자기장 속 2상 유동: 투자율이 다른 두 유체의 경계면에서 자기력선(검은 선)이 휘고, 경계면을 따라 생기는 자기력(색)이 경계면을 변형시킵니다"),
    side=[],
    text=["자성유체와 공기처럼 투자율이 다른 두 유체가 자기장 속에 있으면, 경계면에서 자기장이 휘고 그 결과 유동을 움직이는 자기력이 생깁니다. 자기장은 유동 제어나 열전달 향상에 쓰이지만, 경계면이 움직이면서 자기장과 유동이 서로 영향을 주기 때문에 계산이 까다롭습니다. Level set 방법으로 이 2상 유동을 자기장과 함께 푸는 기법을 개발했습니다.",
          "투자율 차이로 생기는 자기력을 level set 함수로 표현해 운동량 방정식에 넣고, 투자율이 경계면에서 불연속인 점을 반영한 정자기 방정식도 level set 함수로 유도했습니다. 자기장은 벡터 퍼텐셜로 구하고, 운동량·연속 방정식은 엇갈림 격자 위의 유한체적법과 SIMPLE 알고리즘으로 풉니다. 자기장의 효과는 경계면에 집중되는데, Maxwell 응력 텐서의 발산을 직접 계산하면 경계면 근처의 자기력이 불규칙하게 나오지만 이 level set 기법은 복잡한 경계면에서도 대칭적이고 잘 정리된 자기력 분포를 얻습니다.",
          "자기장이 있을 때와 없을 때 액체 풀로 떨어지는 액적, 자기장에 의한 액적의 진동과 늘어남, 자기장 속에서 떠오르는 기포를 계산합니다. 액체의 투자율이 더 크면 자기력선이 액적 쪽으로 휘고, 기포에서는 자기력이 바깥에서 안쪽으로 향하며 옆면에서 강해집니다."],
    stats=[],
    spec="6 × 9 cm(낙하 액적) · 6 × 6 cm 영역 · 균일 자기장 0.002–0.003 T · 액체 투자율 = 기체의 2–10배",
    pubs=[69]),
   dict(id="sim-fsi", en="Fluid–Structure Interaction & Residual Stress", ko="유체–구조 연성과 잔류응력",
    main=V("sim-fsi-demo", "유체–구조 연성 데모 (약 29초): ① 덮개 구동 유동과 벽의 응력을 하나의 운동량 방정식으로 계산 (COMSOL과 비교 검증), ② 레이저 가열·냉각 중 온도(위)와 열 잔류응력(아래) — 소성 변형률, 마르텐사이트 변태, 용융 유동의 영향"),
    side=[],
    text=["녹았다 굳는 동안 액체와 고체가 함께 있는 영역은 흔히 단순화되지만, 실제로는 잔류응력과 변형을 크게 좌우합니다. 유체는 속도와 압력으로, 고체는 변위로 기술하기 때문에 보통 두 가지 해석기를 번갈아 돌려야 합니다. 본 연구실은 유체와 고체를 하나의 운동량 방정식으로 다루는 일체형 기법을 개발해, 한 격자 안에서 유동과 응력을 동시에 계산합니다.",
          "고체의 정역학 대신 탄성동역학 방정식을 쓰면 유체의 Navier–Stokes 방정식과 같은 형태로 쓸 수 있습니다. 이를 격자 셀에 대해 적분해, 유체–고체 경계 조건이 자동으로 맞춰지는 하나의 운동량 방정식을 얻었습니다. 기존 유동 해석 기법(SIMPLE)으로 그대로 풀 수 있어 번갈아 푸는 방식보다 안정적이고 수렴이 좋습니다. 임의 형상의 고정 경계는 부호 거리 함수(level set)로 유체–고체 경계를 일정 두께로 퍼뜨려, 경계에 맞춘 격자 없이 직교 격자 위에서 경계 조건이 저절로 만족됩니다. 같은 틀을 움직이는 탄성 구조물로 넓힌 연구는 바로 아래 항목에서 소개합니다.",
          "평판 사이 유동이 평판에 만드는 응력은 상용 구조해석(ABAQUS)과 최대 오차 약 5%로 일치하고, 정사각형·원형 용기 안의 덮개 구동 유동과 원기둥을 지나는 유동에서도 유체와 구조물의 속도·응력장을 한 번에 구해 문헌값 및 물체 맞춤 격자를 쓰는 COMSOL Multiphysics의 분리형 해석 결과와 잘 일치합니다.",
          "나아가 통합 운동량 방정식을 비압축성 유체와 탄소성 고체로 확장하고 엔탈피 기반 열해석을 결합해, 액체·고체·머시 영역이 함께 있는 용융·응고 과정의 열 잔류응력을 하나의 연속체로 계산합니다. 가우시안 빔으로 가열한 탄소강 판에서는 오스테나이트–마르텐사이트 변태까지 고려해 고체 변형률, 용융 유동, 머시 영역 크기, 가열 시간이 잔류응력에 미치는 영향을 분석합니다. AH36 강의 레이저 표면 용융은 온도·용융 유동·미세조직·응력을 서로 직접 연성해 3차원으로 풉니다. 열영향부 근처에는 높은 인장 잔류응력이, 용융부 근처에는 마르텐사이트·베이나이트 변태의 부피 팽창으로 압축 잔류응력이 남습니다. 입열이 클수록 잔류응력이 커지지만 속도가 매우 느리면 온도 구배가 줄어 오히려 작아지며, 미세조직은 광학 현미경 관찰과, 잔류응력은 컨투어법 측정과 일치합니다. 이 해석 결과가 생성형 대리모델의 학습 데이터가 됩니다."],
    stats=[('1개 방정식', '유체·고체 통합 해석'), ('~5%', 'ABAQUS 대비 최대 오차')],
    spec="",
    pubs=[71, 47, 43, 22]),
   dict(id="sim-fsi-move", en="Fully Eulerian FSI for Moving Elastic Structures", ko="움직이는 탄성 구조물의 유체–구조 연성",
    main=V("sim-bounce", "바닥에 떨어져 튕기는 탄성 공: 낙하할 때 주위 공기에 흐름(화살표)이 생기고, 튕겨 오른 뒤에는 공 아래에 와류가 남습니다"),
    side=[F("fsi-ball-snap", "공의 낙하·충돌·반등 과정의 속도장(화살표)과 수직 응력 σ<sub>yy</sub> (기준 조건, t = 0.01–0.276 s): 첫 충돌(c)과 두 번째 충돌(g) 순간 접촉부에 압축응력이 집중되며, 두 번째 충돌의 응력이 더 약합니다"),
          F("fsi-ball-height", "세 조건의 공 중심 높이: A(기준), B(낙하 높이 33% 증가), C(B에서 탄성 계수 2배) — 충돌할수록 튕기는 높이가 줄고, 단단한 C는 덜 튕겨 오릅니다"),
          F("fsi-rod", "채널 속 유연 막대: 왼쪽 입구의 주기적 압력으로 막대가 휘었다 되돌아오는 동안의 속도장과 x방향 수직 응력 σ<sub>xx</sub> (t = 0.25 · 0.5 · 0.75 · 1 s)")],
    text=["유체 속에서 움직이고 부딪히는 구조물을 계산하려면 보통 경계면을 따라 격자를 계속 다시 만들거나, 유체와 구조물을 서로 다른 좌표계로 기술해야 합니다. 본 연구실은 통합 운동량 방정식을 움직이는 탄성 구조물로 확장해, 고정된 직교 격자 하나로 유체와 구조물을 함께 푸는 완전 오일러(fully Eulerian) 일체형 기법을 개발했습니다. 유체와 구조물의 운동뿐 아니라 구조물 내부의 응력장까지 한 번에 계산하는 것이 특징입니다.",
          "선형 탄성 고체의 탄성동역학 방정식과 비압축성 Navier–Stokes 방정식을 속도 기반의 하나의 운동량 방정식으로 통합해 유한체적법으로 풀고, 움직이는 경계면은 정밀 보존형 level set 방법으로 추적합니다. 경계면이 움직이면 새로 구조물에 들어온 셀에는 변위 값이 없는데, 구조물의 변위장을 주변 유체 셀로 확장(외삽)해 이 문제를 해결합니다. 구조물끼리 부딪히는 충돌 문제에서는 경계면 두께를 조금 넓게 잡아, 두 구조물이 합쳐지기 전에 탄성력이 충분히 커져 튕겨 나가도록 합니다.",
          "유체 속에서 떨어지는 원판은 문헌의 속도·변위 결과와 거의 일치하고, 채널 안에서 주기적인 압력을 받아 흔들리는 유연 막대에서는 막대의 변형과 함께 고정된 바닥 쪽에 집중되는 응력과 휘는 방향에 따라 뒤집히는 응력장을 계산합니다. 바닥에 떨어져 튕기는 공에서는 충돌 순간 접촉부에 큰 압축응력이 생기고, 일부 운동 에너지가 탄성 에너지로 바뀌었다가 소산되면서 튕겨 오르는 높이가 점점 낮아집니다. 반발 계수는 첫 번째와 두 번째 충돌에서 거의 같고(기준 조건 0.851 · 0.850), 탄성 계수를 두 배로 높이면 공이 덜 눌려 0.806에서 0.720으로 줄어듭니다. 구조물이 벽에 부딪히는 문제도 다룰 수 있어, 초탄성 공을 쓴 문헌 문제에서 충돌 전까지의 궤적이 문헌 결과와 거의 같습니다."],
    stats=[],
    spec="2차원 · 평면 변형률 가정 · 균일 엇갈림 격자",
    pubs=[31]),
   dict(id="uf-grass", en="Laser Interaction with Plant Tissues", ko="레이저–식물 조직 상호작용",
    main=F("uf-grass-regimes", "CO₂ 레이저와 잔디 잎의 상호작용 영역: (a) 변화 없음 → (b) 탈색 → (c) 부분 절단 → (d) 탄화 동반 부분 절단 → (e) 완전 절단 → (f) 탄화 동반 완전 절단 (눈금 800 µm)"),
    side=[F("uf-grass-absorb", "잔디 구성 성분의 파장별 흡수(흡수 계수 × 농도): 엽록소·카로티노이드는 가시광을, 물은 적외선을 강하게 흡수하며 건조 물질은 그 사이를 채웁니다 — 화살표: 2.94 µm(Er:YAG)·10.6 µm(CO₂) 등"),
          F("uf-grass-sem", "355 nm 피코초 레이저로 자른 잔디 잎의 광학(50×)·전자현미경(500–1000×) 사진: 탄화(위), 탄화 시작(가운데), 완전 절단(아래) — 깨끗하게 자르면 물관 등 조직이 살아 있어 절단면에 물방울이 맺힙니다")],
    text=["잔디 같은 식물 잎은 물, 엽록소·카로티노이드 색소, 건조 물질로 이루어진 복합 광학 재료입니다. 본 연구실은 잎을 손상 없이 자르는 레이저 기술을 목표로, 식물 잎과 레이저의 상호작용을 처음으로 체계적으로 연구했습니다. 성분별 흡수 특성을 이론적으로 계산하고, 실험으로 상호작용 영역을 분류해 파장별 공정 맵을 만듭니다.",
          "피코초 레이저의 경우 355·532 nm는 주로 엽록소가, 1064 nm는 건조 물질이 빛을 흡수합니다. 상호작용은 변화 없음, 탈색, 부분 절단, 완전 절단, 탄화의 다섯 영역으로 나뉘며, 피코초 펄스인데도 열적이어서 에너지가 높으면 탄화가 일어납니다. 탈색에는 문턱 강도가, 탄화에는 문턱 에너지가 존재하고 이 문턱은 파장이 길수록 높아집니다. 적외선인 Er:YAG(2.94 µm)와 CO₂(10.6 µm) 레이저는 잎의 약 66%를 차지하는 물이 흡수를 지배하고 잎의 흡수율은 98% 이상이며, 유효 침투 깊이는 각각 약 2 µm와 30 µm입니다. 이때 절단은 물의 기화로 일어나는 기계적 과정이고, 탄화는 조직이 직접 가열되는 열적 과정입니다.",
          "빔 직경을 1 mm에서 180 µm로 줄이면 탄화 문턱 에너지가 약 100배 높아지므로, 작은 빔이 손상 없는 절단에 유리합니다. Er:YAG는 CO₂보다 조직 손상이 적지만, 침투 깊이가 얕고 건조 물질의 흡수가 작아 완전 절단에 더 큰 에너지가 필요합니다."],
    stats=[('~100배', '작은 빔에서 높아진 탄화 문턱'), ('98%+', '적외선 레이저 중 물의 흡수 비율')], spec="Kentucky bluegrass (두께 약 110 µm) · 피코초 355/532/1064 nm · Er:YAG 2.94 µm · CO₂ 10.6 µm",
    pubs=[64, 63]),
  ]),
 dict(id="proc", en="Laser Materials Processing", ko="레이저 가공", ten="Laser Processing", tko="레이저 가공", color="coral",
  icon='<path d="M12 2v6"/><path d="M9 8h6l-1.5 5h-3z"/><path d="M4 21h16"/><path d="M7 21c1.5-4 3-6 5-8 2 2 3.5 4 5 8"/>',
  lead="레이저 용접과 열처리는 이차전지, 자동차, 조선, 금형에서 가장 널리 쓰이는 레이저 가공입니다. 고속 동축 관찰로 <b>키홀 거동을 직접 측정</b>해 아연도금 강판·초박판·구리처럼 까다로운 재료의 용접 문제를 풀고, 열해석 기반 공정 맵으로 열처리 조건을 설계합니다. 펨토초 레이저로 <b>기능성 표면</b>을, 듀얼빔 펄스 레이저 증착과 레이저 어닐링으로 <b>기능성 박막</b>을 만듭니다.",
  chips=['키홀 동역학', '아연도금 강판', '초박판·구리 용접', '열처리 공정 맵', 'CFRP 절단', 'LIPSS 표면 기능화', '듀얼빔 PLD', '투명 전도막'],
  blocks=[
   dict(kind="sub", en="Laser Welding", ko="레이저 용접"),
   dict(id="weld-keyhole", en="Keyhole Dynamics by Coaxial Observation", ko="동축 고속 관찰을 통한 키홀 거동 분석",
    main=V("weld-keyhole-demo", "키홀 관찰 데모 (약 29초): ① 아연도금 강판 겹치기 용접에서 키홀 내부를 봐야 하는 이유, ② 레이저와 같은 축으로 5,000 fps로 촬영한 키홀 개구, ③ 시간 평균 3차원 키홀 — 일반 강판(DP590)과 아연도금 강판(GA DP590)의 차이와 좋은 용접을 얻는 조건"),
    side=[],
    text=["키홀 내부는 밖에서 직접 볼 수 없습니다. 본 연구실은 레이저 빔과 같은 축으로 고속 카메라를 설치해, 외부 조명 없이 키홀 자체에서 나오는 빛으로 시편 윗면과 아랫면의 키홀 입구(개구)를 초당 5,000장으로 촬영합니다. 겉으로 불규칙하게 흔들리는 개구 영상에서 키홀의 3차원 평균 형상, 기울어짐, 흔들림을 정량화해 키홀 내부 거동을 추적합니다.",
          "윗면과 아랫면을 따로 촬영한 연속 영상에서 개구의 지름과 위치를 측정하고, 물리 기반 반통계적 프레임 분석으로 시간 평균 개구를 구합니다. 두 개구를 레이저 빔 중심 기준의 공통 좌표계에 놓고 이어 3차원 키홀을 재구성합니다. 2 kW 파이버 레이저로 넓은 출력·속도 범위에서 일반 강판(DP590)과 아연도금 강판(GA DP590)을 비교해 보면, 일반 강판은 아연 증발이 없어 키홀 내부 압력이 낮고, 레이저 에너지를 더 흡수하려고 하부 개구가 닫히는 경향이 있으며 하부 개구는 대부분 빔 안에 있습니다. 아연도금 강판은 강한 아연 증발로 하부가 대부분 열려 있고, 키홀을 유지하려고 앞벽이 기울어 빔이 앞벽에 놓입니다. 앞벽 기울기는 일반 강판이 6–9°로 거의 일정한 반면 아연도금 강판은 7–16°로 크게 변해, 아연도금 강판에서는 기울기가, 일반 강판에서는 빔–키홀 상호작용 면적이 핵심 변수입니다.",
          "키홀 팽창 계수, 요동 범위 계수, 평균 개구 지름, 질량 손실률, 용융풀 부피를 정의해 키홀이 레이저 빔에 어떻게 반응하는지도 분석합니다. 하부 개구 지름과 하부 팽창 계수는 두 강판 모두 질량 손실(스패터)에 대체로 비례합니다. 이 동축 관측 기법은 이후 딥러닝 기반 키홀 모니터링의 출발점이 되었습니다."],
    stats=[("5,000 fps", "동축 고속 촬영"), ("3D", "키홀 형상 재구성")],
    spec="2 kW 파이버 레이저 · DP590 / GA DP590 · 알루미늄 합금",
    pubs=[53, 50, 24]),
   dict(id="weld-zinc", en="Zero-gap Welding of Zinc-coated Steels", ko="아연도금 강판의 제로갭 용접",
    main=F("weld-zinc", "제로갭 겹치기 용접의 아연 증발과 키홀 거동: (a) 빔이 키홀 앞벽에서 떨어져 있으면 두 판 사이의 아연 증발이 약하고 스패터가 적지만, (b) 키홀이 기울어 빔이 앞벽에 놓이면 아연 증발 영역이 직접 가열되어 증기압이 커지고 스패터가 크게 늘어납니다"),
    side=[F("weld-coaxial-zinc", "일반 강판(DP590, 왼쪽)과 아연도금 강판(GA DP590, 오른쪽)의 키홀 윗면(위)·아랫면(아래) 동축 영상: 아연도금 강판은 강한 아연 증발로 하부 개구가 대부분 열려 있습니다"),
          F("weld-fdtd-keyhole", "측정한 키홀 형상 안의 레이저 전파(FDTD, 출력 1230–1830 W × 속도 12.5–21.2 mm/s): 왼쪽 일반 강판, 오른쪽 아연도금 강판 — 칸마다 아래 숫자가 키홀 흡수율이며, 같은 조건에서 아연도금 강판이 더 낮습니다"),
          F("weld-subatm", "주변 압력 101.3 · 10 · 1 · 0.1 kPa에서의 시간 평균 키홀(노랑: 레이저 빔): 아연도금 강판(a)은 감압할수록 용접 방향으로 크게 늘어나고, 일반 강판(b)은 원형에 가까운 형상을 유지합니다")],
    text=["자동차용 아연도금 강판을 간극 없이(제로갭) 겹쳐 용접하면, 끓는점이 강보다 훨씬 낮은 아연이 두 판 사이에서 폭발적으로 증발해 용융풀을 흔들고 기공과 스패터를 만듭니다. 아연의 포화 증기압은 1800 K에서 이미 약 50 bar에 이릅니다. 동축 키홀 관측, 키홀 형상 기반 전자기 해석, 감압 실험을 결합해 아연 증기가 키홀과 용접 품질에 미치는 영향을 분석합니다.",
          "같은 조건의 일반 강판과 비교하면, 레이저 빔과 키홀의 상대 위치가 용접 품질을 가르는 가장 중요한 요인입니다. 빔이 키홀 앞벽에 놓이면 두 판 사이의 아연 증발 영역이 직접 가열되어 증기압이 급격히 커지고 용융풀이 심하게 흔들립니다. 빔이 앞벽에서 떨어져 있으면 아연 증기의 반발압력이 낮아 용융풀이 안정됩니다. 아연도금 강판은 낮은 용접 속도에서 좋은 용접부를 얻을 수 있고, 이때는 출력을 낮출수록 품질이 좋아지므로 제로갭 용접이 가능한 조건을 이론적으로 설명할 수 있습니다. 측정한 키홀 형상에 빔의 발산·집속 특성을 맞춰 FDTD로 흡수를 계산하면, 아연도금 강판은 같은 조건에서 키홀 흡수율이 훨씬 낮고 다중 반사가 더 뚜렷하며, 이는 용융풀 크기 측정으로도 확인됩니다. 일반 강판은 하부 개구 크기가 흡수율을 좌우하는데, 개구가 작아지면 그 주변에 에너지가 집중되어 개구가 다시 열리는 것이 하부 개구가 열렸다 닫히는 원리로 보입니다.",
          "주변 압력을 대기압(101.3 kPa)에서 0.1 kPa까지 낮추면, 아연 증발이 강의 증발보다 훨씬 강해져 아연도금 강판의 키홀이 용접 방향으로 길게 늘어나고 크게 요동합니다. 두 강판 모두 하부 개구가 넓어지고 열려 있는 시간이 늘어 에너지가 빠져나가므로 용융풀이 작아지고, 비드의 물결무늬 간격이 넓고 불규칙해져 용접 품질은 오히려 나빠집니다. 좋은 용접을 얻으려면 하부 개구가 적절히 열리고 닫혀야 합니다."],
    stats=[("~50 bar", "1800 K에서 아연 포화 증기압")],
    spec="2 kW 멀티모드 파이버 레이저 · DP590 / GA DP590 제로갭 겹치기 · 101.3–0.1 kPa",
    pubs=[50, 51, 44]),
   dict(id="weld-foil", en="Welding of Ultra-thin Foils", ko="초박판 정밀 용접",
    main=V("weld-foil-demo", "초박판 용접 데모 (약 32초): ① 50 µm 박판과 진공 지그, ② 접촉이 나빠지면 용융풀이 깨져 액적이 생기는 과정, ③ 빔 크기에 따른 안정성 — 빔이 클수록 표면장력이 지배해 불안정해집니다"),
    side=[],
    text=["두께 50 µm의 스테인리스 박판(AM 350)을 1 mm 판재(SUS 304)에 용접합니다. 박판은 아주 작은 틈만 있어도 녹아 끊어지기 때문에, 진공으로 시편을 밀착시키는 지그를 쓰고 빔 크기·출력·속도에 따른 용융풀 거동을 고속 촬영합니다. 빔 직경 200–1125 µm의 네 가지 조건마다 용입 깊이와 용접 모드가 비슷한 범위를 덮도록 25개 조건의 공정 변수 공간을 구성하고, 안정된 용융풀을 얻기 위해 주로 열전도 모드를 목표로 합니다. 고속 촬영으로 용융풀이 깨지고 액적이 생기는 과정을 관찰하고, 시편 표면의 먼지 입자와 미세 공동도 현미경으로 세어 크기 분포를 구합니다.",
          "박판 용접에서는 빔 직경의 영향이 매우 크며 작은 빔이 훨씬 유리합니다. 빔이 커지면 용융풀 부피에 비해 표면장력의 영향이 커져, 접촉 상태와 상관없이 용융풀이 불안정해지고 액적이 생깁니다. 625 µm 빔은 에너지가 높을 때 불안정하고, 1125 µm 빔은 모든 조건에서 불안정합니다. 표면의 먼지와 공동은 Weibull 분포를 따르고, 박판과 판재의 접촉이 불완전하면 용융풀이 깨져 경계에 액적이 생깁니다. 강도가 높은 AM 350 박판을 SUS 304에 접합할 때 인장강도는 용입 깊이에 반비례합니다."],
    stats=[("50 µm", "박판 두께"), ("4종", "빔 직경 200–1125 µm 비교")],
    spec="2 kW 멀티모드 파이버 레이저 · AM 350 / SUS 304",
    pubs=[48]),
   dict(id="weld-copper", en="Femtosecond Pre-patterning for Copper Welding", ko="펨토초 표면 패턴을 이용한 구리 용접",
    main=F("weld-cu-patterns", "펨토초 레이저로 만든 구리 표면 패턴(SEM): 가공 시간 4–27초에 따라 반사율이 47%에서 3%까지 낮아집니다 (오른쪽 아래 작은 사진: 2 × 5 mm 패턴)"),
    side=[F("weld-cu-pool", "(a) 패턴 반사율(47–3%)에 따른 용접 시작부 용융풀 고속 영상(빨강: 용융풀 경계), (b–d) 용융풀 폭·길이·면적 — 반사율이 11% 이하로 낮아질수록 용융풀이 커지고, 그 이상에서는 크게 달라지지 않습니다 (1800 W, 150 mm/s)"),
          F("weld-cu-welds", "(a) 패턴(2 × 5 mm)을 시작점에만 둔 경우와 (b) 2 cm 간격으로 작은 패턴(2 × 2.5 mm)을 더 둔 경우: 간격 배치로 용접선 끝까지 키홀이 유지됩니다")],
    text=["구리는 1 µm 파장 레이저의 97%를 반사해, 고출력 파이버 레이저로도 키홀을 만들기 어렵습니다. 본 연구실은 용접 시작점에 펨토초 레이저로 LIPSS 기반 저반사 패턴을 미리 만들어, 레이저가 구리 표면에 잘 결합되도록 합니다. 플루언스와 주사 속도에 따른 표면 형상과 반사율 지도로 패턴 조건을 고른 뒤, 2 kW 파이버 레이저 용접 시작점에 2 mm × 5 mm 패턴을 최대 27초 만에 가공해 반사율을 97%에서 최저 3%까지 낮춥니다.",
          "저반사 패턴을 쓰면 용접 속도를 최대 300%까지 높일 수 있고, 용융풀이 한번 형성되면 크기가 비교적 안정적으로 유지됩니다. 다만 구리의 큰 열전도 손실 때문에 일정 거리 뒤에는 키홀이 약해져 무너지므로, 패턴을 용접선을 따라 일정 간격으로 두어 긴 용접에서도 키홀을 유지합니다."],
    stats=[('97% → 3%', '패턴으로 낮춘 반사율'), ('최대 300%', '높아진 용접 속도')], spec="2 kW 멀티모드 파이버 레이저 (1070 nm, 최대 1800 W) · 구리 · 펨토초 LIPSS 패턴",
    pubs=[28]),
   dict(id="weld-scaling", en="Scaling Law for Penetration Depth", ko="용입 깊이 스케일링 법칙",
    main=F("weld-scaling-map", "레이저 강도 I₀–조사 시간 t<sub>i</sub> 맵 위의 실험 결과(□ 용융 없음, ◆ 열전도 모드, ● 키홀 모드, ⊕ 완전 관통)와 무차원 용입 깊이 δ* 등고선: 키홀이 깊어질수록 지수 θ가 약 0.6에서 0.21까지 작아집니다"),
    side=[F("weld-scaling-grid", "레이저 출력(58–1830 W, 세로)과 용접 속도(10.8–340 mm/s, 가로)에 따른 PO 강(4 mm) 용접부 단면: 얕은 열전도 용접부터 깊은 키홀 용접까지")],
    text=["용입 깊이는 용접에서 가장 먼저 정해야 하는 값이지만, 정밀한 해석은 비용이 너무 큽니다. 본 연구실은 1차원 열전도 해석에서 출발해 표면 온도에 비례하는 공정 변수를 찾고, 여기에 키홀 내부의 다중 반사 효과를 더해, 열전도 용접부터 키홀 용접까지 하나의 변수로 용입 깊이를 설명하는 스케일링 법칙을 제시했습니다.",
          "일정한 열유속으로 가열되는 반무한 고체에서 표면 온도 상승은 ηI₀√t<sub>i</sub>에 비례하고, 같은 표면 온도라도 빔이 작으면 열이 옆으로 빠져 용입이 얕아지므로 용입 깊이를 빔 직경으로 나눈 값(δ*)을 씁니다. 키홀이 생기면 다중 반사로 흡수율과 국부 강도가 함께 커지므로, 이 효과를 강도의 지수(1+γ)로 나타냅니다. 그러면 δ*는 I₀·t<sub>i</sub><sup>θ</sup> 하나의 변수로 정리되며, 열전도 용접에서는 θ ≈ 0.5이고 키홀이 깊어져 다중 반사가 강해질수록 θ가 약 0.2까지 줄어듭니다. 얕은 키홀에서는 γ가 음수가 될 수도 있습니다. 이 법칙은 2 kW 파이버 레이저로 4 mm PO 강판에 120회(강도 12단계 × 속도 10단계), 1 mm DP590 판을 겹친 시편에 빔 직경 200–1125 µm로 실험해 검증했습니다."],
    stats=[('θ 0.5 → 0.2', '열전도 → 깊은 키홀 용접'), ('120회', 'PO 강판 검증 실험')],
    spec="2 kW 멀티모드 파이버 레이저 (1070 nm, 탑햇 빔) · PO 강 · DP590 · 빔 직경 200–1125 µm",
    pubs=[56]),
   dict(kind="sub", en="Heat Treatment & Cutting", ko="열처리·절단"),
   dict(id="ht-design", en="Physics-based Design of Laser Heat Treatment", ko="열해석 기반 레이저 열처리 공정 설계",
    main=F("ht-map", "레이저 열처리 공정 맵: 흡수 레이저 강도와 조사 시간에 따른 예측 경화 깊이 1–6 mm (임계 ECDT 30초)"),
    side=[F("ht-ecdt", "ECDT–경도 관계의 최근 적용 예 (S45C 강, 2 kW 파이버 레이저; 실시간 경도 모니터링 연구): (위) 1800 W · 5 mm/s 열처리 단면과 경도 측정 위치(빨간 상자), (a) 측정 경도와 ECDT의 상관관계(R² 95.5%), (b) ECDT 분포를 경도 분포로 바꾼 예 (1248 W · 5 mm/s)"),
          F("ht-hs-section", "히트싱크 종류(없음 · SUS · 강 · 구리, 가로)와 레이저 강도(I₁–I₆, 세로)에 따른 경화층 단면과 깊이별 경도(파란 점, 300–600 Hv): 히트싱크의 열전도도가 높을수록 같은 조건에서 경화층이 깊고 단단해집니다"),
          F("ht-hs-deflection", "히트싱크 종류에 따른 평균 변형 각도(빨강: DP590, 파랑: 보론강; 점선: 절단 전, 실선: 절단 후): 히트싱크를 대면 약 0.9°에서 0.4–0.6°로 줄어듭니다")],
    text=["경화가 잘 되려면 탄소가 충분히 확산될 만큼 가열되고, 다시 충분히 빨리 식어야 합니다. 본 연구실은 두 조건을 등가 탄소 확산 시간(ECDT)과 등가 냉각 시간(ECT)으로 정량화하고, 레이저 강도와 조사 시간으로 그린 공정 맵 위에서 열처리 가능 영역과 함께 보여 주는 방법으로 열처리 공정을 설계합니다. 경화 깊이는 임계 ECDT로 계산하며, 공정 맵은 3 kW 다이오드 레이저로 AISI 1020·1035 강을 체계적으로 열처리해 검증했습니다. ECDT는 경도와 강하게 상관되어, 최근 S45C 강에서는 R² 95.5%로 단면 경도 분포를 추정하는 데 쓰입니다(AI 공정 모니터링 탭의 실시간 경도 모니터링).",
          "열전도 해석해로 두께 1 mm–10 cm 판의 공정 맵을 그려 보면, 두께가 약 15 mm보다 얇아질 때 열처리 가능 영역이 낮은 레이저 강도 쪽으로 옮겨 가며 좁아집니다. 두꺼운 판에서는 탄소 확산 시간이 경화를 좌우하지만, 얇은 판에서는 탄소 확산은 충분하고 오히려 냉각이 부족해집니다. AISI 1020 강판(20, 10, 5, 1.3 mm) 125회 실험에서도 1.3 mm 판은 어떤 조건에서도 약 200 Hv 이상 경화되지 않았습니다. 이 냉각 부족은 판 아래에 히트싱크를 대서 해결합니다. 히트싱크의 열전도도와 판–히트싱크 사이의 접촉 열저항이 두 핵심 변수이며, 히트싱크를 쓰면 열처리 가능 영역은 그대로이면서 냉각과 탄소 확산 특성은 두꺼운 판 수준이 됩니다. 2 mm 보론강은 히트싱크로 500 Hv 이상, DP590은 350 Hv를 안정적으로 얻을 수 있고, 향상 정도는 히트싱크의 열전도도(SUS < 강 < 구리)에 비례합니다.",
          "히트싱크는 열변형도 크게 줄입니다. 가열이 약해져 소성 변형이 줄고, 냉각이 빨라져 마르텐사이트가 더 생기기 때문입니다. 소성 변형은 판을 한쪽으로, 마르텐사이트 변태는 반대쪽으로 휘게 하므로, 조사 시간이 길 때 변형 방향이 뒤집히며 그 사이에 변형이 거의 없는 영역이 생깁니다. 이 영역을 이용하면 변형을 최소화하는 공정 조건을 고를 수 있고, 열영향부 깊이와 판 두께의 비가 변형을 분석하는 핵심 변수입니다.",
          "AISI H13 공구강은 3차원 열전도 해석과 2 kW 파이버 레이저 실험을 결합해 경도와 열변형을 함께 예측합니다. 두꺼운 판의 경화 특성이 그대로 유지되는 최소 두께를 해석으로 구해, 얇은 시편에서 변형 각도를 정확히 측정합니다. 경도는 ECDT와 잘 맞아 여섯 조건의 경도 분포 예측이 실측과 일치했고, 최대 약 800 Hv를 얻었습니다. ECT를 최고 온도가 A₃ 아래인 영역(음의 값)까지 확장하면, 변형 각도는 소성 변형 영역(R² 0.779)과 상변태 영역(R² 0.986) 모두에서 ECT와 강하게 상관됩니다."],
    stats=[('~800 Hv', 'H13 공구강 레이저 경화 최대 경도'), ('500 Hv+', '히트싱크로 얻은 보론강 경도')],
    spec="3 kW 다이오드 레이저 (AISI 1020 · 1035 · DP590 · 보론강) · 2 kW 파이버 레이저 (H13)",
    pubs=[66, 61, 57, 55, 46]),
   dict(id="cut-cfrp", en="Fiber Laser Cutting of CFRP", ko="CFRP 파이버 레이저 절단",
    main=F("cut-cfrp", "(a) 레이저로 절단한 CFRP 윗면(SEM, 250 mm/s · 1600 W · 5회), (b) 절단 품질 인자 정의: 커프 폭·깊이, 기지 증발 폭(MEW), 기지 후퇴 폭(MRW), 커프 경사각, 기지 손상 영역, (c) 조건별 절단면"),
    side=[F("cut-cfrp-fiber", "조건별 절단면의 탄소섬유(SEM, 주사 속도 · 출력 · 반복 횟수 n): 반지름 방향 열 융착으로 섬유에 원·타원형 고리가 생기고, 반복 횟수가 많을수록 섬유끼리 융착되어 절단면이 매끈해집니다")],
    text=["탄소섬유강화플라스틱(CFRP)은 가볍고 강하지만 섬유와 수지의 열 특성이 크게 달라, 레이저로 자르면 수지가 타거나 섬유가 빠지기 쉽습니다. 2 kW 파이버 레이저의 출력(200–1600 W)과 주사 속도(125–1000 mm/s)를 로그 간격으로 4단계씩 바꾸고 반복 횟수를 달리해, 커프 폭·깊이, 기지 증발·후퇴 폭, 커프 경사각, 기지 손상 영역, 절단면 형상을 측정하며 절단 품질이 어떻게 달라지는지 체계적으로 분석합니다.",
          "커프 폭은 표면 온도 상승을 나타내는 변수와, 커프 깊이는 단위 면적당 에너지와 가장 잘 맞습니다. 기지의 열손상은 주사 속도를 높일수록 줄어, 주사 속도가 열손상을 줄이는 핵심 변수입니다. 절단면의 탄소섬유에는 반지름 방향 열 융착으로 보이는 고리가 생기고, 반복 횟수가 많을수록 섬유끼리 융착되어 박리와 빠짐을 막아 절단면이 매끈해집니다. 요구하는 품질에 따라 최적 조건은 여러 개일 수 있습니다."],
    stats=[], spec="2 kW 멀티모드 파이버 레이저 (1070 nm, 연속파) · CFRP 1 mm",
    pubs=[40]),
   dict(kind="sub", en="Ultrafast Surface Processing", ko="초단펄스 표면 가공"),
   dict(id="uf-lipss", en="Femtosecond Surface Structuring & Functionalization", ko="펨토초 레이저 표면 구조화·기능화",
    main=F("uf-ball", "(a) 22가지 반사율(550 nm 기준 60–8%)과 각 반사율을 내는 플루언스·주사 속도로 설계한 다면체 공, (b) 스테인리스 표면에 새긴 결과: 반사율 차이만으로 입체감이 나타납니다 (눈금 1 cm)"),
    side=[F("uf-slips", "벌레잡이통풀(a)에서 착안한 미끄러운 유리 표면(SLIPS): 펨토초 레이저로 유리 내부에 미세 공극 배열을 만들고(b), 불산 습식 식각으로 서로 연결된 공동을 형성한 뒤(c), 실리콘 오일을 채웁니다(d). 오른쪽은 각 단계의 단면입니다"),
          F("uf-microlens-sem", "펨토초 레이저·습식 식각 금형 → PDMS 복제 → DLC/실리콘 경사 코팅으로 완성한 적외선 복합 마이크로렌즈 어레이 (SEM, 45° 기울여 촬영)"),
          F("uf-microlens-img", "같은 렌즈 어레이의 결상 시험: 렌즈마다 글자 ‘S’의 상이 맺힘 (할로겐 램프, 가시광–근적외선)")],
    text=["펨토초 레이저를 쬐면 표면에 빛의 파장 정도 간격의 주기 구조(LIPSS)가 저절로 생기고, 조건에 따라 다양한 2차 구조로 바뀝니다. 본 연구실은 이 구조로 금속 표면의 반사율, 젖음성, 끓음 열전달을 바꾸고, 유리 내부 가공과 습식 식각을 결합해 광학·유체 기능 표면을 만듭니다. 플루언스와 주사 속도에 따라 LIPSS 형상과 반사율이 바뀌는 넓은 공정 창을 확보해 스테인리스 반사율을 66%(가공 전)에서 5%까지 거의 연속적으로 조절하고, 22가지 반사율로 입체감 있는 다면체 공 무늬를 새깁니다. 반사율이 바뀌는 원리와 보호 가스가 표면 형상·패턴 품질에 주는 영향도 밝혔습니다. 또한 구리와 구리 소결 표면에 주기 구조를 만들어 풀 비등·유동 비등의 열전달과 임계 열유속을 높이고(공동 연구), 실리콘 웨이퍼의 펨토초 레이저 홀 드릴링 공정도 최적화했습니다.",
          "유리 내부에는 펨토초 레이저로 미세 공극 배열을 만들고 습식 식각해 서로 연결된 공동을 만듭니다. 공극 간격과 식각·실란화 처리로 접촉각을 0°에서 137°까지 조절하고, 10 µm처럼 촘촘한 공동에 윤활액을 가둬 액체가 미끄러지는 표면(SLIPS)을 만들며, 윤활액의 굴절률 정합으로 투과율도 크게 높입니다. 같은 방법으로 용융 실리카에 오목 금형을 만들고 PDMS로 복제해 렌즈 지름 6 µm, 초점 거리 4.5 µm(FDTD 4.12 µm)의 쌍곡면 마이크로렌즈 어레이를 만듭니다. 여기에 듀얼빔 PLD로 DLC/실리콘 경사 코팅(GRIN 렌즈)을 올리면 초점 거리가 2.9 µm로 줄고 가시광이 차단되며, 할로겐 램프와 1000 nm 레이저로 한 결상 시험에서 모든 렌즈에 선명한 상이 맺혔습니다."],
    stats=[('66% → 5%', '스테인리스 반사율 조절'), ('0–137°', '유리 표면 접촉각 조절')], spec="펨토초 레이저 · 스테인리스강 304 · 구리 · 용융 실리카 · 실리콘",
    pubs=[36, 32, 37, 38, 23, 18, 16, 12]),
   dict(kind="sub", en="Thin Films", ko="박막"),
   dict(id="uf-pld", en="Laser Thin-film Processing: Dual-beam PLD & Laser Annealing", ko="레이저 박막 공정: 듀얼빔 PLD와 레이저 어닐링",
    main=F("uf-dbpld", "듀얼빔 PLD 장치: 피코초 레이저 빔을 빔 분할기로 둘로 나누고, 모터 감쇠기로 각 빔의 출력을 따로 바꾸며 진공 챔버 속 두 타깃(예: 흑연 · 316L 스테인리스)에 조사합니다. 두 플라즈마가 섞여 위쪽 기판에 쌓입니다"),
    side=[F("uf-fgdlc", "(a) 증착 시간에 따라 반대로 바꾼 두 빔의 출력(흑연 0 → 4 W, 316L 약 0.9 → 0 W), (b) 그로써 만든 약 510 nm 경사 DLC 박막(316L → DLC 경사층 + 순수 DLC 53 nm), (c) 스크래치 시험 임계 하중: 일반 DLC 27 N → 경사 DLC 47 N"),
          F("uf-arc", "실리콘·유리 두 타깃의 듀얼빔 PLD로 만든 굴절률 경사 반사방지 코팅: 공정과 태양전지 구조(왼쪽 위), FDTD로 계산한 빛의 전파(왼쪽 아래), 맨 실리콘·선형·Southwell 분포 시편(오른쪽 위)과 반사율(오른쪽 아래) — Southwell 분포에서 400–1000 nm 반사율 2.2–4%"),
          F("uf-tcf", "(a) 유리 위 DLC 박막을 보호 가스 속에서 선형 빔으로 어닐링해 투명 전도막을 만드는 공정, (b) 어닐링 전 시편, (c) 어닐링 후 투명해진 시편, (d) 투과 스펙트럼(400–800 nm, 550 nm에서 약 80%)")],
    text=["두 개의 레이저 빔으로 서로 다른 두 재료를 동시에 증착하면서 출력을 서로 반대로 바꾸면, 조성이 기판에서 표면까지 끊김 없이 변하는 경사 기능 박막을 만들 수 있습니다. 본 연구실은 이 듀얼빔 PLD로 벗겨지지 않는 경사 DLC, 굴절률 경사 반사방지 코팅, YSZ 열차폐 코팅을 만들고, 증착한 DLC 박막을 파이버 레이저로 어닐링해 유리 위에 바로 투명 전도막을 만듭니다. 355 nm 피코초 레이저 빔을 둘로 나누고, 모터 감쇠기로 각 빔의 출력을 시간에 따라 따로 조절해 진공 속 두 타깃에 조사합니다. 두 플라즈마는 공간에서 섞인 뒤 기판에 쌓이며, 타깃과 기판의 배치는 고속 ICCD 카메라로 플라즈마를 관찰해 최적화했습니다. 피코초 레이저는 낮은 펄스 에너지와 높은 반복률 덕분에 스패터 없이 매끄러운 표면을 만듭니다.",
          "DLC(다이아몬드상 탄소)는 단단하고 마모에 강하지만 약 10 GPa의 압축응력 때문에 두께가 0.1–0.2 µm만 넘어도 기판에서 벗겨집니다. 흑연 쪽 출력은 올리고 316L 스테인리스 쪽은 낮춰, 스테인리스에서 DLC로 조성이 연속적으로 변하는 경사 기능 DLC(FGDLC)를 만들었습니다. 약 510 nm 박막에서 탄소 함량은 설계대로 거의 직선적으로 늘고 맨 위층은 sp³ 비율 43%의 일반 DLC 품질입니다. 일반 DLC는 약 400 nm를 넘으면 좌굴·박리가 일어나지만 경사 DLC는 500 nm 이상에서도 박리가 없고, 스크래치 임계 하중도 27 N에서 47 N으로 높아집니다. 이어 원하는 조성 분포(선형·2차·3차·제곱근·세제곱근·사인)를 미리 설계하고 두 빔의 출력 곡선을 거꾸로 계산해 그대로 증착하는 방법을 처음으로 개발했으며, 조성 분포 오차 3% 이하, 두께 오차 1.04%로 구현했습니다.",
          "실리콘과 소다석회 유리를 두 타깃으로 쓰면, 조성이 실리콘(태양전지 쪽)에서 유리(덮개 유리 쪽)로 서서히 바뀌는 굴절률 경사 반사방지 코팅이 됩니다. 400 nm 유리층을 덮은 Southwell 굴절률 분포는 400–1000 nm에서 반사율 2.2–4%로, 덮개 유리가 있는 실리콘 태양전지에서 이론적으로 가능한 최고 성능에 가깝습니다. FDTD 해석 결과도 측정과 일치하며, 한 번의 증착 공정으로 만들 수 있어 태양전지 구조를 크게 단순화할 수 있습니다. 스테인리스 기판에서 YSZ(이트리아 안정화 지르코니아)로 조성이 선형으로 바뀌는 경사 열차폐 코팅은 로크웰 압입 균열 시험으로 구한 밀착 지표(dP/dc)가 9.41 N/µm로 순수 YSZ 코팅(8.35 · 8.43 N/µm)보다 높고, 열전도도는 약 1.14 W/m·K로 열차폐 성능이 좋습니다.",
          "유리는 통과하고 DLC에만 흡수되는 1070 nm 연속파 파이버 레이저로 DLC 박막을 어닐링하면, 비정질 탄소가 그래핀으로 바뀌어 투명 전도막이 됩니다. 510 nm DLC 막을 헬륨 분위기에서 200 µm 탑햇 빔으로 1 m/s로 어닐링하면 sp³ 결합 비율이 43.1%에서 8.1%로 줄고, 투과율 약 80%(550 nm)와 면저항 약 2050 Ω/sq를 얻습니다. 전사나 촉매 없이 유리 위에 바로 만들 수 있고, 15 mm 폭 선형 빔으로 면적을 쉽게 키울 수 있습니다. 투과율은 낮지만 전도도가 높은 막은 피코초 레이저로 일부 제거(패터닝)하고 질산으로 도핑해 성능을 끌어올립니다. 초기 막의 면저항·투과율과 제거 면적 비율의 모든 조합에 대해 결과를 미리 보여 주는 예측 맵으로 조건을 정하며, 예를 들어 면저항 578 Ω/sq, 투과율 25%인 막을 사각 패턴으로 73% 제거하고 도핑하면 2823 Ω/sq, 80.6%가 됩니다."],
    stats=[('27 → 47 N', '경사 DLC 스크래치 임계 하중'), ('~80%', '투명 전도막 투과율 (550 nm)')], spec="355 nm 피코초 레이저 (6 W, 10–15 ps, 200 kHz) · 타깃: 흑연 · 316L · 실리콘 · 유리 · YSZ · 2 kW CW 파이버 레이저 어닐링 (1070 nm)",
    pubs=[67, 62, 52, 41, 49, 45]),
  ]),
 dict(id="apps", en="AI beyond Lasers", ko="레이저 외 분야의 AI 응용", ten="AI beyond Lasers", tko="레이저 외 AI 응용", color="mint",
  icon='<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1"/>',
  lead="레이저 가공에서 다듬은 방법론, 즉 <b>적은 실험 데이터로 영상·분포를 생성하고 예측하는 딥러닝</b>을 다른 제조·공학 문제에도 적용합니다. 자동차 이종소재 접합, 조선 구조물 변형, 유체 유동, 반도체 장비까지 산업 현장의 문제를 함께 풀고 있습니다.",
  chips=["자가 천공 리벳(SPR)", "조선 구조물 변형", "PIV 유동장", "반도체 웨이퍼 정렬"],
  blocks=[
   dict(id="app-spr", en="Self-Piercing Riveting", ko="자가 천공 리벳(SPR) 접합 예측",
    main=F("ai-spr", "강판 4종(행) × 알루미늄 3종(열) 조합의 SPR 단면 예측(빨강: 리벳, 초록·파랑: 윗판·아랫판): 빨간 상자(Al5754)와 파란 상자(SPFC590DP)는 학습에 쓰지 않은 시험 조합입니다"),
    side=[F("ai-spr-arch", "(a) 단면 광학 현미경 사진을 Xception–ASPP 기반 분할 모델이 리벳과 두 판재로 나눈 분할 지도, (b) 펀치력 하나를 넣으면 생성기가 단면 분할 지도를 만들고, 판별기와 경쟁하며 학습합니다"),
          F("ai-spr-results", "펀치력(25–70 kN)에 따른 머리 높이·인터록 길이·바닥 두께·인장강도: 실측(회색)과 AI 예측(빨강). 왼쪽 위는 29 kN 단면에서 잰 형상 인자의 예입니다")],
    text=["자가 천공 리벳(SPR)은 강·알루미늄·CFRP처럼 용접이 어려운 이종 소재를 잇는 자동차 경량화 핵심 기술입니다. 접합 품질을 보려면 시편을 잘라 단면을 봐야 하는데, 본 연구실은 딥러닝으로 펀치력이나 소재 조합만으로 접합 단면 형상을 예측합니다. 단면 광학 현미경 사진을 CNN이 두 판재와 리벳별로 분할하고(mIoU 98.50%, 픽셀 정확도 99.78%), 잔차 블록을 넣은 조건부 GAN이 펀치력 하나만으로 단면 분할 지도를 생성합니다. 머리 높이·인터록 길이·바닥 두께의 세 핵심 형상 인자는 CFRP–GA590DP 접합에서 평균 94.20%, SPFC590DP–Al5052 접합에서 96.31% 정확도로 예측합니다.",
          "소재 조합으로도 일반화해, 강판 4종(SPRC440 · SPFC590DP · GI780DP · SGAF980Y)과 알루미늄 3종(Al5052 · Al5754 · Al5083)의 12가지 조합에서 영률·푸아송비·인장강도만 입력해 학습에 쓰지 않은 소재 조합의 단면을 예측합니다. 물성을 벡터로 넣는 모델과 색으로 칠한 이미지로 넣는 모델의 평균 정확도는 각각 91.95%와 92.22%입니다. 후속 연구에서는 인장강도까지 함께 예측하고 있습니다."],
    stats=[('94.2%', '세 핵심 형상 인자 예측'), ('12가지', '강·알루미늄 소재 조합')],
    spec="CFRP 1.3 mm / GA590DP 2.3 mm · 펀치력 29–70 kN",
    pubs=[33, 30]),
   dict(id="app-ship", en="Shipbuilding: Deck Plate Deformation", ko="조선: 갑판 구조물 변형 예측",
    main=F("ai-deck", "갑판 2차 변형: AI 예측과 유한요소 해석 결과의 평면 분포(위 왼쪽 두 그림), x = 2600 mm 단면의 변형 곡선(위 오른쪽), 3차원 형상(아래) — 시험 사례 R² 99.84%"),
    side=[F("ai-deck-structure", "주판·거더·프레임·카링으로 이루어진 갑판 구조(유한요소 모델, 왼쪽)와 이를 이미지로 바꾼 구조물 입력(오른쪽: 보강재의 위치와 치수)"),
          F("ai-deck-model", "초기 변형 · 구조물 · 반력 분포 이미지 세 장을 합성곱 인코더–디코더 생성기에 넣어 2차 변형 이미지를 생성합니다")],
    text=["선박 건조의 탑재(erection) 단계에서 갑판은 무거운 하중을 받아 면외 변형이 생기고, 이를 바로잡는 데 큰 비용이 듭니다. 본 연구실은 변형된 갑판 형상(2차 변형)을 생성하는 GAN 모델로 이 변형을 미리 예측합니다. 변형에 영향을 주는 세 정보, 즉 조립 후의 초기 변형, 거더·프레임·카링 등 보강재의 위치와 치수(주판 두께 포함), 경계를 따라 작용하는 수직 반력을 각각 이미지로 바꿔 넣으면, 조건부 GAN으로 학습한 CNN 인코더–디코더 생성기가 이를 변형 형상 이미지로 번역합니다. 학습 데이터는 비선형 좌굴 유한요소 해석으로 만듭니다.",
          "세 종류의 상선(LNG선·LPG선·컨테이너선) 갑판에서 유한요소 해석 결과를 R² 99.78%, 구조 유사도 99.77%, 평균 절대 오차 0.124 mm(평균 상대 오차 0.68%)로 재현하며, 예측은 수 초 안에 끝납니다. 같은 접근을 선상가열(line heating) 판재 성형의 전체 변형장 예측으로 넓히고 있습니다."],
    stats=[('R² 99.78%', '유한요소 해석 재현'), ('0.124 mm', '평균 절대 오차')],
    spec="MLNG · LPG · 컨테이너선 갑판 (주판 10–13 mm)",
    pubs=[26, 2]),
   dict(id="app-piv", en="Fluid Flow: PIV Flow Field & Rotor Thrust", ko="유체: PIV 유동장·로터 추력 예측",
    main=F("ai-piv", "드론 로터 아래 유동의 x·y 방향 속도(U, V)와 와도: AI 예측(위)과 PIV 정답(아래), 왼쪽 위 숫자는 R²(%)입니다"),
    side=[F("ai-piv-input", "입력으로 쓰는 고해상도 PIV 입자 영상 두 장(위)과 상호상관 PIV로 구한 정답 속도장(아래: U, V, 와도, d/R = 0.13)")],
    text=["입자 영상 유속계(PIV)는 입자 영상의 상호상관 계산으로 속도장을 구하는데, 고해상도 영상에서는 시간이 오래 걸립니다. 최대 9000 RPM으로 도는 드론 로터 아래의 난류에서 고해상도 입자 영상(2048 × 2048)만으로 순간 유동장을 예측하고, 그 유동장에서 로터 추력까지 예측하는 딥러닝 구조를 제안했습니다. 순간 유동장 예측에는 처음으로 GAN(스펙트럼 정규화 잔차 조건부 GAN)을 도입했고, ResNet-50이 유동장에서 추력을 회귀합니다. 정답으로는 FFT 상호상관 PIV 결과와 로드셀로 측정한 추력을 씁니다.",
          "순간 유동장은 R² 97.21%, 추력은 R² 94.57%로 예측하며, 기존 상호상관 PIV보다 약 600배 빠릅니다(시험 데이터 270개에 12.5초 대 120–125분). 클래스 활성화 지도로 보면 모델은 로터에서 운동 에너지를 받는 영역을 보고 추력을 판단합니다. 유체역학 분야 대표 학술지(Journal of Fluid Mechanics)에 게재되었습니다."],
    stats=[('~600배', '기존 상호상관 PIV 대비 속도'), ('R² 97.21%', '순간 유동장 예측')],
    spec="드론 로터 3000–9000 RPM · 입자 영상 2048 × 2048 px",
    pubs=[25]),
   dict(id="app-wafer", en="Semiconductor: Wafer Edge Segmentation", ko="반도체: 웨이퍼 정렬용 에지 분할",
    main=F("app-wafer", "학습 전략: 파티클·잔여물·조명 변화를 넣은 합성 웨이퍼 영상(2448 × 2048)으로 먼저 학습한 뒤, 소수의 실제 영상으로 미세조정해 웨이퍼 에지 분할 지도를 출력합니다"),
    side=[F("app-wafer-pipe", "이중 해상도 U²-Net: ① 입력 영상을 306 × 256으로 줄여 ② 에지 위치를 찾고 ③ 그 영역을 추출한 뒤, ④ 고해상도 원본에서 480 × 2048 영역만 잘라 ⑤ 정밀 분할하고 ⑥ 원래 크기로 되돌립니다"),
          F("app-wafer-real", "실제 시험 영상에서 학습 방식(A–G)별 분할 결과와 IoU: 배경 대비가 낮은 아래 웨이퍼에서 제안 방식(G)이 IoU 0.969로 가장 높습니다")],
    text=["3차원 집적회로 제조에서 웨이퍼를 정확히 정렬하려면 영상에서 웨이퍼 가장자리를 정밀하게 찾아야 하지만, 실제 영상에서는 파티클이나 접착제 잔여물, 조명 변화 때문에 가장자리가 잘 보이지 않습니다. 본 연구실은 이중 해상도 딥러닝과 합성 데이터 학습으로 이런 조건에서도 웨이퍼 에지를 픽셀 단위로 분할합니다. 고해상도(2448 × 2048) 영상을 저해상도(306 × 256)로 줄여 에지 위치를 먼저 찾고, 해당 고해상도 영역만 잘라 정밀 분할하는 이중 해상도 U²-Net을 씁니다. 학습에는 파티클·접착제 잔여물·조명 변화를 무작위로 넣은 자체 시뮬레이터의 합성 영상을 쓰고, 기하학적으로 그럴듯한 형상을 강제하는 비지도 GAN 보정 단계를 더합니다.",
          "실제 영상 단 1장으로 미세조정해도 실제 시험 영상에서 mIoU 0.960, 7장이면 0.964로, 기존 방법과 일반 GAN 변형보다 우수합니다. 가장자리가 일부 가려져도 에지 형상을 복원해 3차원 집적회로 적층의 정밀 정렬에 쓸 수 있습니다."],
    stats=[('mIoU 0.960', '실제 영상 1장으로 미세조정')], spec="", pubs=[6]),
  ]),
]

ICON = lambda p: f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{p}</svg>'

tabbar = "".join(
    f'<button type="button" role="tab" class="rt-tab rt-{t["color"]}" id="tab-{t["id"]}" aria-controls="panel-{t["id"]}" aria-selected="false" data-tab="{t["id"]}">'
    f'<span class="rt-ic">{ICON(t["icon"])}</span><span class="rt-txt"><b>{E(t.get("ten", t["en"]))}</b><small>{E(t.get("tko", t["ko"]))}</small></span><span class="rt-chev" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"/></svg></span></button>'
    for t in TABS)

FT = [("weld", "용접"), ("ht", "열처리·용융"), ("cut", "절단·드릴링"), ("uf", "초단펄스"), ("surf", "표면"), ("film", "박막")]
FTL = dict(FT)
TAGS = {"ai-monitor": ["weld"], "ai-bead": ["weld"], "ht-monitor": ["ht"], "ht-hard-mon": ["ht"], "ai-beam": ["ht"], "ai-absorb": ["weld"], "ai-em-gan": [], "ai-lipss": ["uf", "surf"], 
        "ai-surrogate": ["ht"], "ht-ai": ["ht"], "weld-predict": ["weld"], "uf-anneal": ["uf"],
        "ai-v2c": ["weld"],
        "sim-keyhole": ["weld"], "sim-ablation": ["cut"], "sim-em": ["weld"], "sim-waterjet": ["cut"], "sim-fs": ["uf"], "sim-plasma": ["weld"],
        "sim-magnetic": [], "sim-fsi": ["ht"], "uf-grass": ["cut", "uf"],
        "weld-keyhole": ["weld"], "weld-zinc": ["weld"], "weld-foil": ["weld"], "weld-copper": ["weld", "uf"], "weld-scaling": ["weld"],
        "ht-design": ["ht"], "cut-cfrp": ["cut"], "uf-lipss": ["uf", "surf"], "uf-pld": ["film"]}

GAL_H = 320      # px: height of figures inside the "자세히 보기" panel
TOP_H = 330      # px: tallest a wide (stacked) representative figure may be
FLOAT_H = 380    # px: tallest a floated representative figure may be (text wraps around it)
FLOAT_W = 520    # px: widest a floated representative figure may be (also capped at 48% by CSS)
STACK_AR = 2.0   # representative figures wider than this go above the text instead of beside it


def keys_html(stats):
    if not stats: return ""
    return '<dl class="rbx-keys">' + "".join(f'<div><dt>{v}</dt><dd>{E(l)}</dd></div>' for v, l in stats) + "</dl>"


def gallery(items):
    """Side figures in rows of up to 3, all at the same height."""
    if not items: return ""
    rows = [items[i:i + 3] for i in range(0, len(items), 3)]
    out = ""
    for row in rows:
        cells = ""
        for it in row:
            kind, name, cap = it
            w, h = vdims(name) if kind == "v" else fdims(name)
            mw = min(w, round(w / h * GAL_H))
            cells += media(it, False).replace('<figure class="rm rm-thumb', f'<figure style="flex:{w/h:.3f} 1 0;max-width:{mw}px" class="rm rm-gal', 1)
        out += f'<div class="rb-galrow">{cells}</div>'
    return f'<div class="rb-gal">{out}</div>'


def top_figure(item):
    """Main figure: wide ones (aspect > STACK_AR) go above the text, the rest float beside it (text wraps)."""
    kind, name, cap = item
    w, h = vdims(name) if kind == "v" else fdims(name)
    stack = w / h > STACK_AR or name in FORCE_STACK
    if stack:
        maxw = min(w, WMAX[name]) if name in WMAX else min(w, round(HMAX.get(name, TOP_H) * w / h), 1100)
    else:
        maxw = min(w, round(HMAX.get(name, FLOAT_H) * w / h), FLOAT_W)
    if name in CAP: maxw = min(maxw, CAP[name])
    return media(item, False).replace('<figure class="rm rm-thumb', f'<figure style="max-width:{maxw}px" class="rm rm-top', 1), stack, maxw


PAIR_H = 340   # px: tallest a side-by-side pair of representative figures may be (main=[V(..), V(..)])


def pair_figure(items):
    """Two (or more) representative figures side by side above the text, all at the same height."""
    cells = ""; tot = 0
    for it in items:
        kind, name, cap = it
        w, h = vdims(name) if kind == "v" else fdims(name)
        tot += w / h
        cells += media(it, False).replace('<figure class="rm rm-thumb', f'<figure style="flex:{w/h:.3f} 1 0" class="rm rm-top rm-pair{" rm-pair-tall" if w / h < 1.2 else ""}', 1)
    maxw = round(PAIR_H * tot + 24 * (len(items) - 1))
    return f'<div class="rbx-pair" style="max-width:{maxw}px">{cells}</div>', True, maxw


panels = []
for t in TABS:
    blocks = []; toc = []; groups = []; k = 0
    for b in t["blocks"]:
        if b.get("kind") == "sub":
            groups.append((b["ko"], []))
            blocks.append(f'<div class="rp-sec"><span>{E(b["en"])}</span><b>{E(b["ko"])}</b></div>')
            continue
        k += 1
        link = f'<a href="#{b["id"]}"><span>{k:02d}</span>{E(b["ko"])}</a>'
        (groups[-1][1] if groups else toc).append(link)
        paras = "".join(f"<p>{x}</p>" for x in b["text"])
        spec = ""   # SETUP line removed from the page (2026-11); b["spec"] kept below only as a memo
        pubs = (f'<details class="rb-pubs"><summary>관련 논문 <span>{len(b["pubs"])}</span></summary>{papers(b["pubs"])}</details>' if b["pubs"] else "")
        tg = TAGS.get(b["id"], [])
        head = (f'<header class="rb-head"><span class="rb-num">{k:02d}</span><div><h3>{E(b["en"])}</h3>'
                f'<p class="h-ko">{E(b["ko"])}</p></div></header>')
        # equations stay visible at the bottom of the block; the fold holds only the extra figures (side)
        eqh = eqbox(b["id"]) if b["id"] in EQ else ""
        nfig = len(b["side"])
        did = "d-" + b["id"]
        if nfig:
            lab = "그림 더 보기"
            more = (f'<button type="button" class="rbx-more" aria-expanded="false" aria-controls="{did}" data-l="{lab}">'
                    f'<span class="rbx-more-l">{lab}</span><small>{nfig}장</small>'
                    f'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg></button>')
            detail = f'<div class="rbx-detail" id="{did}" hidden>{gallery(b["side"])}</div>'
        else:
            more = detail = ""
        foot = f'<div class="rb-foot">{spec}<div class="rb-fr">{more}</div></div>' if (spec or more) else ""   # papers go after the equations
        if b["main"]:
            fig, stack, fw = pair_figure(b["main"]) if isinstance(b["main"], list) else top_figure(b["main"])
            if stack:
                body = f'<div class="rbx-body rbx-stack"><div class="rbx-fig">{fig}</div><div class="rb-abs">{paras}</div>{foot}</div>'
            else:
                side = "r" if k % 2 == 0 else "l"
                body = (f'<div class="rbx-body"><div class="rbx-fig rbx-fl rbx-fl-{side}" style="width:{fw}px">{fig}</div>'
                        f'<div class="rb-abs">{paras}</div>{foot}</div>')
        else:
            body = f'<div class="rbx-body rbx-nofig"><div class="rb-abs">{paras}</div>{foot}</div>'
        blocks.append(f'<article class="rb rbx" id="{b["id"]}" data-tags="{" ".join(tg)}">{head}{body}{detail}{eqh}{pubs}</article>')
    chips = "".join(f"<span>{E(c)}</span>" for c in t["chips"])
    if groups:
        tochtml = '<nav class="rp-toc rp-toc-g" aria-label="세부 연구">' + "".join(f'<div class="rp-tg"><b>{E(g)}</b><div>{"".join(ls)}</div></div>' for g, ls in groups) + "</nav>"
    elif k > 1:
        tochtml = f'<nav class="rp-toc" aria-label="세부 연구">{"".join(toc)}</nav>'
    else:
        tochtml = ""
    panels.append(
        f'<section class="rp-panel rt-{t["color"]}" role="tabpanel" id="panel-{t["id"]}" aria-labelledby="tab-{t["id"]}" hidden>'
        f'<div class="rp-intro"><header class="rp-head"><span class="rp-ic">{ICON(t["icon"])}</span><div><h2>{E(t["en"])}</h2><p class="rp-ko">{E(t["ko"])}</p></div></header>'
        f'<p class="rp-lead">{t["lead"]}</p><div class="rp-chips">{chips}</div></div>'
        f'{tochtml}{"".join(blocks)}</section>')

filt = ('<div class="rf" role="group" aria-label="공정별 보기"><span class="rf-l">공정별 보기</span>'
        '<button type="button" class="rf-b" data-f="" aria-pressed="true">전체</button>'
        + "".join(f'<button type="button" class="rf-b" data-f="{c}" aria-pressed="false">{E(l)}</button>' for c, l in FT)
        + '<span class="rf-n" aria-live="polite"></span></div>')

ARW = '<svg viewBox="0 0 40 16" aria-hidden="true"><path d="M2 8h32M28 2l7 6-7 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
overview = f"""<div class="rov" aria-label="연구 구조">
        <a class="rov-box rov-src" href="#sim" data-go="sim"><small>Foundation</small><b>Simulation &amp; Experiment</b><span>멀티피직스 해석 · 레이저–물질 물리 · 가공 실험</span></a>
        <div class="rov-arw">{ARW}<span>물리 기반 · <br>실험 데이터</span></div>
        <div class="rov-box rov-ai"><small>Core</small><b>AI for Laser Processing</b>
          <div class="rov-pills"><a href="#ai" data-go="ai">모니터링</a><a href="#aipred" data-go="aipred">예측 모델</a><a href="#auto" data-go="auto">자율 가공</a></div>
          <a class="rov-ext" href="#apps" data-go="apps">방법론 확장 → AI beyond Lasers</a></div>
        <div class="rov-arw">{ARW}<span>적용 · <br>검증</span></div>
        <a class="rov-box rov-proc" href="#proc" data-go="proc"><small>Application</small><b>Laser Processing</b><span>용접 · 열처리 · 절단 · 표면</span></a>
      </div>"""

main = f'''<main>
  <section class="page-hero research-hero">
    <div class="wrap">
      <h1>Research</h1>
      <p>본 연구실은 <b>레이저 가공을 위한 인공지능</b>을 연구합니다. 공정을 실시간으로 읽는 모니터링, 수치해석과 실험을 대신하는 생성형 예측 모델, 영상만 보고 스스로 움직이는 자율 가공이 세 축입니다. 그 바탕에는 오랫동안 직접 개발해 온 멀티피직스 시뮬레이션과 레이저–물질 상호작용 연구, 그리고 용접·열처리·초단펄스 가공·박막 증착 실험이 있습니다.</p>
      {overview}
    </div>
  </section>

  <div class="wrap"><p class="rt-hint"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 5v14M6 13l6 6 6-6"/></svg>아래에서 연구 분야를 선택하세요 <span>Select a research area</span></p></div>
  <div class="rt-bar">
    <div class="wrap"><div class="rt-tabs" role="tablist" aria-label="Research areas">{tabbar}</div></div>
  </div>

  <section class="section research-body">
    <div class="wrap">
      {"".join(panels)}
    </div>
  </section>

  <dialog class="rm-lb" id="rm-lb" aria-label="확대 보기">
    <button type="button" class="rm-lb-x" aria-label="닫기">&times;</button>
    <div class="rm-lb-body"></div>
    <p class="rm-lb-cap"></p>
  </dialog>
</main>'''

p = R + "/research.html"
t = open(p, encoding="utf-8").read()
i = t.index("<main>"); j = t.index("</main>") + len("</main>")
t = t[:i] + main + t[j:]
t = re.sub(r'<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex[^>]*>\n', "", t)
if "katex.min.css" not in t:
    t = t.replace('<link rel="stylesheet" href="assets/style.css', '<link rel="stylesheet" href="assets/katex/katex.min.css?v=1">\n<link rel="stylesheet" href="assets/style.css', 1)
t = re.sub(r'\n?<script src="assets/research\.js[^"]*"></script>', "", t)
t = t.replace("</body>", '<script src="assets/research.js?v=12"></script>\n</body>', 1)
open(p, "w", encoding="utf-8").write(t)
print("ok", sum(len(x["blocks"]) for x in TABS), "blocks")
