"""
포켓몬 강화하기 v2 (원작: NBS 「검 강화하기」를 바탕으로 밸런스 조정)

v2 변경점
- 최대 강화 +20 (+20 달성 시 엔딩)
- +0→+1 성공 확률 99%, 이후 단계마다 최소 1%p 이상 낮아짐
- 어느 단계에서 팔아도 그때까지 쓴 강화 비용보다 판매가가 높음
  (예: +2강 판매 350원 > 누적 비용 260원) → 저강화 반복 판매로 목돈 마련 가능
- 돈이 바닥나면 지원금으로 다시 시작 가능
- 강화 성공·실패 효과가 매번 재생됨

실행 방법
    pip install streamlit requests
    python -m streamlit run app.py
"""

import random

import requests
import streamlit as st

# ---------------------------------------------------------------------------
# 1. 기본 설정
# ---------------------------------------------------------------------------
STARTING_MONEY = 10_000
RESCUE_MONEY = 1_000         # 파산 시 지원금
WARP_SUCCESS_RATE = 50       # 워프권 성공 확률(%)
DROP_MIN, DROP_MAX = 1, 3    # 실패 시 잡템 개수
FINAL_LEVEL = 20

# ---------------------------------------------------------------------------
# 2. 단계별 포켓몬 (+0 ~ +20)
# ---------------------------------------------------------------------------
POKEMON_IDS = [
    129,  # +0  잉어킹
    16,   # +1  구구
    19,   # +2  꼬렛
    4,    # +3  파이리
    25,   # +4  피카츄
    58,   # +5  가디
    95,   # +6  롱스톤
    5,    # +7  리자드
    26,   # +8  라이츄
    123,  # +9  스라크
    131,  # +10 라프라스
    143,  # +11 잠만보
    59,   # +12 윈디
    130,  # +13 갸라도스
    6,    # +14 리자몽
    248,  # +15 마기라스
    149,  # +16 망나뇽
    376,  # +17 메타그로스
    384,  # +18 레쿠쟈
    150,  # +19 뮤츠
    493,  # +20 아르세우스 (엔딩)
]
FALLBACK_NAMES = {
    129: "잉어킹", 16: "구구", 19: "꼬렛", 4: "파이리", 25: "피카츄", 58: "가디",
    95: "롱스톤", 5: "리자드", 26: "라이츄", 123: "스라크", 131: "라프라스",
    143: "잠만보", 59: "윈디", 130: "갸라도스", 6: "리자몽", 248: "마기라스",
    149: "망나뇽", 376: "메타그로스", 384: "레쿠쟈", 150: "뮤츠", 493: "아르세우스",
}

JUNK_NAMES = {
    "iron":   "출처불명 몬스터볼 조각",   # +6~+8 실패
    "bone":   "스라크의 날개 부스러기",   # +9 실패
    "fluor":  "빛 바랜 라프라스 껍데기",  # +10 실패
    "swiss":  "고급 몬스터볼 조각",       # +11~+12 실패
    "handle": "갸라도스의 비늘",          # +13 실패
    "soul":   "리자몽의 불꽃 정수",       # +14 실패
    "axe":    "마기라스의 모래",          # +15 실패
    "clear":  "망나뇽의 비늘",            # +16 실패
}

# ---------------------------------------------------------------------------
# 3. 강화표: 단계 i = (+i → +i+1 강화 비용, 성공 확률%, +i 판매가, 실패 시 필요 방지권, 드랍)
#    · 확률: 99%에서 시작해 단계마다 최소 1%p 이상 감소
#    · 판매가: 항상 '그 단계까지 쓴 누적 강화 비용'보다 높음
#    · 방지권 None = 실패하면 바로 도망 (+0 ~ +4)
# ---------------------------------------------------------------------------
TABLE = {
    0:  (100,     99, None,          None, None),
    1:  (160,     97, 150,           None, None),
    2:  (240,     95, 350,           None, None),
    3:  (370,     92, 670,           None, None),
    4:  (580,     89, 1_200,         None, None),
    5:  (890,     85, 2_200,         1,    None),
    6:  (1_400,   81, 3_900,         1,    "iron"),
    7:  (2_100,   77, 6_800,         1,    "iron"),
    8:  (3_300,   72, 12_000,        1,    "iron"),
    9:  (5_200,   67, 22_000,        1,    "bone"),
    10: (8_000,   62, 42_000,        1,    "fluor"),
    11: (12_000,  56, 84_000,        1,    "swiss"),
    12: (19_000,  50, 180_000,       1,    "swiss"),
    13: (30_000,  44, 400_000,       2,    "handle"),
    14: (46_000,  38, 980_000,       3,    "soul"),
    15: (72_000,  32, 2_700_000,     4,    "axe"),
    16: (110_000, 26, 8_700_000,     7,    "clear"),
    17: (170_000, 20, 34_000_000,    9,    None),
    18: (270_000, 14, 170_000_000,   10,   None),
    19: (410_000, 8,  1_200_000_000, 12,   None),
}

# 상점 (+0에서만): (키, 이름, 가격, 효과)
SHOP = [
    ("guard1", "깨짐 방지권 1개", 100_000, ("guard", 1)),
    ("guard3", "깨짐 방지권 3개", 250_000, ("guard", 3)),
    ("warp9", "+9강 워프권", 15_000, ("warp", 9)),
    ("warp13", "+13강 워프권", 280_000, ("warp", 13)),
    ("warp14", "+14강 워프권", 690_000, ("warp", 14)),
    ("warp15", "+15강 워프권", 1_900_000, ("warp", 15)),
]

# 조합소 (+1에서만): (키, 잡템, 필요 개수, 보상)
RECIPES = [
    ("r_iron", "iron", 5, ("guard", 1)),
    ("r_bone", "bone", 3, ("guard", 1)),
    ("r_fluor", "fluor", 3, ("stage", 11)),
    ("r_swiss", "swiss", 3, ("guard", 2)),
    ("r_handle", "handle", 3, ("stage", 14)),
    ("r_soul_g", "soul", 4, ("guard", 4)),
    ("r_soul_s", "soul", 6, ("stage", 15)),
    ("r_axe", "axe", 6, ("guard", 10)),
    ("r_clear", "clear", 3, ("guard", 9)),
]

# ---------------------------------------------------------------------------
# 4. PokeAPI
# ---------------------------------------------------------------------------
API = "https://pokeapi.co/api/v2"
SPRITE_FALLBACK = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{}.png"
ART_FALLBACK = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{}.png"


@st.cache_data(show_spinner=False)
def fetch_pokemon(pid: int) -> dict:
    info = {"name": FALLBACK_NAMES.get(pid, f"#{pid}"),
            "sprite": SPRITE_FALLBACK.format(pid), "art": ART_FALLBACK.format(pid)}
    try:
        data = requests.get(f"{API}/pokemon/{pid}", timeout=5).json()
        info["sprite"] = data["sprites"]["front_default"] or info["sprite"]
        info["art"] = data["sprites"]["other"]["official-artwork"]["front_default"] or info["art"]
        species = requests.get(f"{API}/pokemon-species/{pid}", timeout=5).json()
        for n in species["names"]:
            if n["language"]["name"] == "ko":
                info["name"] = n["name"]
                break
    except Exception:
        pass
    return info


def poke_name(level: int) -> str:
    return fetch_pokemon(POKEMON_IDS[level])["name"]


# ---------------------------------------------------------------------------
# 5. 게임 로직
# ---------------------------------------------------------------------------
def new_state() -> dict:
    return {"level": 0, "money": STARTING_MONEY, "guards": 0, "junk": {}, "inventory": {},
            "pending_fail": None, "pending_drops": None, "msg": None, "fx": None, "fx_n": 0,
            "ended": False, "attempts": 0, "spent": 0, "best": 0, "rescues": 0}


def fmt_won(n: int) -> str:
    return f"{n:,}원"


def busy(s) -> bool:
    return s["pending_fail"] is not None or s["ended"]


def spent_to_reach(level: int) -> int:
    """+0에서 해당 단계까지 한 번도 실패 없이 올렸을 때의 누적 비용."""
    return sum(TABLE[i][0] for i in range(level))


def is_broke(s) -> bool:
    return (s["level"] == 0 and not busy(s) and s["money"] < TABLE[0][0]
            and not any(v > 0 for v in s["inventory"].values()))


def enhance(s, rng=random.random) -> None:
    if busy(s):
        return
    lvl = s["level"]
    cost, rate, _sell, guard, drop = TABLE[lvl]
    if s["money"] < cost:
        s["msg"] = ("warn", "강화 비용이 부족합니다. 포켓몬을 판매해 돈을 모으세요.")
        return
    s["pending_drops"] = None
    s["money"] -= cost
    s["spent"] += cost
    s["attempts"] += 1
    s["fx_n"] += 1
    if rng() * 100 < rate:
        s["level"] = lvl + 1
        s["best"] = max(s["best"], s["level"])
        s["fx"] = "success"
        if s["level"] == FINAL_LEVEL:
            s["ended"] = True
            s["msg"] = ("success", f"+{FINAL_LEVEL} {poke_name(FINAL_LEVEL)} 달성! 엔딩입니다.")
        else:
            s["msg"] = ("success", f"강화 성공! +{s['level']} {poke_name(s['level'])}(이)가 되었다!")
        return
    s["fx"] = "fail"
    if drop:
        s["pending_drops"] = (drop, random.randint(DROP_MIN, DROP_MAX))
    if guard is None:
        s["level"] = 0
        s["msg"] = ("error", f"강화 실패… +{lvl} {poke_name(lvl)}(이)가 도망갔다!")
    else:
        s["pending_fail"] = {"level": lvl, "need": guard}
        s["msg"] = ("error", f"강화 실패… 방지권 {guard}개로 +{lvl} {poke_name(lvl)}을(를) 붙잡을 수 있습니다.")


def use_guard(s) -> None:
    pf = s["pending_fail"]
    if pf and s["guards"] >= pf["need"]:
        s["guards"] -= pf["need"]
        s["pending_fail"] = None
        s["fx"] = None
        s["msg"] = ("info", f"방지권 {pf['need']}개 사용! +{pf['level']} {poke_name(pf['level'])}을(를) 지켜냈다.")


def give_up(s) -> None:
    pf = s["pending_fail"]
    if pf:
        s["pending_fail"] = None
        s["level"] = 0
        s["fx"] = None
        s["msg"] = ("error", f"+{pf['level']} {poke_name(pf['level'])}(이)가 도망갔다…")


def pick_up(s) -> None:
    if s["pending_drops"]:
        key, n = s["pending_drops"]
        s["junk"][key] = s["junk"].get(key, 0) + n
        s["pending_drops"] = None
        s["msg"] = ("info", f"{JUNK_NAMES[key]} {n}개를 주웠다.")


def sell(s) -> None:
    if busy(s) or s["level"] == 0:
        return
    lvl = s["level"]
    price = TABLE[lvl][2]
    s["money"] += price
    s["level"] = 0
    s["pending_drops"] = None
    s["fx"] = None
    s["msg"] = ("info", f"+{lvl} {poke_name(lvl)}을(를) {fmt_won(price)}에 판매했습니다. "
                        f"(이 단계까지 강화 비용 {fmt_won(spent_to_reach(lvl))})")


def take_out(s, stage: int) -> None:
    if busy(s) or s["level"] != 0 or s["inventory"].get(stage, 0) < 1:
        return
    s["inventory"][stage] -= 1
    s["level"] = stage
    s["fx"] = None
    s["msg"] = ("info", f"+{stage} {poke_name(stage)}을(를) 꺼냈습니다.")


def buy(s, key: str, rng=random.random) -> None:
    if busy(s) or s["level"] != 0:
        return
    _, name, price, (kind, val) = next(i for i in SHOP if i[0] == key)
    if s["money"] < price:
        s["msg"] = ("warn", "돈이 부족합니다.")
        return
    s["money"] -= price
    if kind == "guard":
        s["guards"] += val
        s["msg"] = ("info", f"깨짐 방지권 {val}개를 구입했습니다.")
    elif rng() * 100 < WARP_SUCCESS_RATE:
        s["level"] = val
        s["fx"], s["fx_n"] = "success", s["fx_n"] + 1
        s["msg"] = ("success", f"워프 성공! +{val} {poke_name(val)}(으)로 시작합니다.")
    else:
        s["fx"], s["fx_n"] = "fail", s["fx_n"] + 1
        s["msg"] = ("error", "워프 실패… 워프권이 사라졌습니다.")


def craft(s, key: str) -> None:
    if busy(s) or s["level"] != 1:
        return
    _, junk, need, reward = next(r for r in RECIPES if r[0] == key)
    if s["junk"].get(junk, 0) < need:
        s["msg"] = ("warn", "재료가 부족합니다.")
        return
    s["junk"][junk] -= need
    if reward[0] == "guard":
        s["guards"] += reward[1]
        s["msg"] = ("info", f"깨짐 방지권 {reward[1]}개를 얻었습니다.")
    else:
        lv = reward[1]
        s["inventory"][lv] = s["inventory"].get(lv, 0) + 1
        s["msg"] = ("info", f"+{lv} {poke_name(lv)}을(를) 얻어 보관함에 넣었습니다. (+0 화면에서 꺼낼 수 있음)")


def rescue(s) -> None:
    if is_broke(s):
        s["money"] += RESCUE_MONEY
        s["rescues"] += 1
        s["msg"] = ("info", f"포켓몬 센터 지원금 {fmt_won(RESCUE_MONEY)}을 받았습니다. 낮은 단계에서 팔며 다시 모아보세요!")


# ---------------------------------------------------------------------------
# 6. 화면
# ---------------------------------------------------------------------------
BASE_CSS = """
<style>
.poke-box {text-align:center; padding:12px 0; position:relative;}
.poke-box img {width:240px; height:240px; object-fit:contain;}
.pixel img {image-rendering: pixelated;}
.lvl {font-size:2rem; font-weight:800; margin:4px 0 0;}
.fx-banner {font-size:1.6rem; font-weight:900; height:2.2rem; opacity:0;}
</style>
"""


def effect_css(n: int, fx: str | None) -> str:
    """효과마다 고유한 애니메이션 이름(번호 포함)을 써서 매번 처음부터 재생되게 한다."""
    if fx == "success":
        return f"""<style>
@keyframes glow{n} {{
  0%   {{filter:brightness(2.4) drop-shadow(0 0 30px gold); transform:scale(1.25) rotate(-4deg);}}
  40%  {{filter:brightness(1.6) drop-shadow(0 0 18px gold); transform:scale(1.08) rotate(3deg);}}
  100% {{filter:none; transform:scale(1) rotate(0);}} }}
@keyframes banner{n} {{
  0% {{opacity:0; transform:translateY(12px) scale(.8);}} 15% {{opacity:1; transform:translateY(0) scale(1.15);}}
  70% {{opacity:1; transform:scale(1);}} 100% {{opacity:0;}} }}
.fx-{n} img {{animation: glow{n} 1.1s ease-out;}}
.fx-{n} .fx-banner {{animation: banner{n} 1.6s ease-out; color:#f5b301;}}
</style>"""
    if fx == "fail":
        return f"""<style>
@keyframes shake{n} {{0%,100%{{transform:translateX(0)}} 15%,55%{{transform:translateX(-14px) rotate(-3deg)}}
  35%,75%{{transform:translateX(14px) rotate(3deg)}} }}
@keyframes banner{n} {{0% {{opacity:0;}} 15% {{opacity:1;}} 70% {{opacity:1;}} 100% {{opacity:0;}} }}
.fx-{n} img {{animation: shake{n} .6s; filter: grayscale(1) brightness(.7);}}
.fx-{n} .fx-banner {{animation: banner{n} 1.6s ease-out; color:#e5484d;}}
</style>"""
    return ""


def render_pokemon(s: dict, pixel: bool) -> None:
    lvl = s["level"]
    info = fetch_pokemon(POKEMON_IDS[lvl])
    src = info["sprite"] if pixel else info["art"]
    n = s["fx_n"]
    banner = {"success": "강화 성공!", "fail": "강화 실패…"}.get(s["fx"], "")
    # 주의: 마크다운은 공백 4칸 이상 들여쓴 줄을 코드 블록으로 바꾸므로
    #       HTML은 들여쓰기 없이 한 줄로 만들고, <style>과는 빈 줄로 구분한다.
    box = (f'<div class="poke-box {"pixel" if pixel else ""} fx-{n}">'
           f'<div class="fx-banner">{banner}</div>'
           f'<img src="{src}" alt="{info["name"]}">'
           f'<div class="lvl">+{lvl} {info["name"]}</div></div>')
    css = effect_css(n, s["fx"])
    st.markdown((css + "\n\n" if css else "") + box, unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(page_title="포켓몬 강화하기", page_icon="⚔️", layout="wide")
    st.markdown(BASE_CSS, unsafe_allow_html=True)
    ss = st.session_state
    if "game" not in ss:
        ss.game = new_state()
    s = ss.game

    with st.sidebar:
        st.header("설정")
        pixel = st.toggle("도트(픽셀) 이미지", value=True)
        if st.button("새 게임", use_container_width=True):
            ss.game = new_state()
            st.rerun()
        st.caption(f"총 강화 시도 {s['attempts']:,}회 · 최고 +{s['best']} · 지원금 {s['rescues']}회")

    lvl = s["level"]
    st.title("포켓몬 강화하기")

    if s["msg"]:
        kind, text = s["msg"]
        {"success": st.success, "error": st.error, "warn": st.warning, "info": st.info}[kind](text)

    left, right = st.columns([3, 2])
    with left:
        render_pokemon(s, pixel)
        if s["ended"]:
            if not s.get("celebrated"):
                st.balloons()
                s["celebrated"] = True
            st.subheader("축하합니다! +20 아르세우스에 도달했습니다.")
            st.write(f"총 강화 시도: {s['attempts']:,}회 · 총 강화 비용: {fmt_won(s['spent'])}")

    with right:
        m1, m2 = st.columns(2)
        m1.metric("보유 금액", fmt_won(s["money"]))
        m2.metric("깨짐 방지권", f"{s['guards']}개")

        if not s["ended"]:
            cost, rate, _, guard, _ = TABLE[lvl]
            price = TABLE[lvl][2]
            st.markdown(
                f"| 항목 | 값 |\n|---|---|\n"
                f"| 강화 비용 | {fmt_won(cost)} |\n"
                f"| 성공 확률 | **{rate}%** |\n"
                f"| 지금 팔면 | {fmt_won(price) if price else '-'} |\n"
                f"| 성공 후 팔면 | {fmt_won(TABLE[lvl + 1][2]) if lvl + 1 < FINAL_LEVEL else '엔딩'} |\n"
                f"| 실패 시 방지권 | {f'{guard}개' if guard else '복구 불가'} |"
            )

        pf = s["pending_fail"]
        if pf:
            st.error(f"+{pf['level']} 강화 실패! 방지권 {pf['need']}개가 필요합니다. (보유 {s['guards']}개)")
            g1, g2 = st.columns(2)
            g1.button(f"방지권 {pf['need']}개 사용", on_click=use_guard, args=(s,),
                      disabled=s["guards"] < pf["need"], use_container_width=True)
            g2.button("포기하기", on_click=give_up, args=(s,), use_container_width=True)
        elif not s["ended"]:
            st.button("강화하기", type="primary", on_click=enhance, args=(s,), use_container_width=True)
            if lvl >= 1:
                st.button("판매하기", on_click=sell, args=(s,), use_container_width=True)

        if s["pending_drops"]:
            key, n = s["pending_drops"]
            st.button(f"줍기: {JUNK_NAMES[key]} {n}개", on_click=pick_up, args=(s,), use_container_width=True)

        if is_broke(s):
            st.warning("돈이 바닥났습니다.")
            st.button(f"포켓몬 센터 지원금 받기 ({fmt_won(RESCUE_MONEY)})", on_click=rescue, args=(s,),
                      use_container_width=True)

    st.divider()

    if lvl == 0 and not busy(s):
        t1, t2 = st.tabs(["상점", "보관함"])
        with t1:
            for key, name, price, _ in SHOP:
                c1, c2 = st.columns([3, 1])
                c1.write(f"**{name}** — {fmt_won(price)}")
                c2.button("구입", key=f"buy_{key}", on_click=buy, args=(s, key),
                          disabled=s["money"] < price, use_container_width=True)
            st.caption(f"워프권은 {WARP_SUCCESS_RATE}% 확률로 성공합니다.")
        with t2:
            items = {k: v for k, v in s["inventory"].items() if v > 0}
            if not items:
                st.write("보관한 포켓몬이 없습니다. 조합소(+1 화면)에서 얻을 수 있습니다.")
            for stage, n in sorted(items.items()):
                c1, c2 = st.columns([3, 1])
                c1.write(f"+{stage} {poke_name(stage)} × {n}")
                c2.button("꺼내기", key=f"out_{stage}", on_click=take_out, args=(s, stage),
                          use_container_width=True)

    if lvl == 1 and not busy(s):
        t1, t2 = st.tabs(["조합소", "잡템창"])
        with t1:
            for key, junk, need, reward in RECIPES:
                rtext = (f"깨짐 방지권 {reward[1]}개" if reward[0] == "guard"
                         else f"+{reward[1]} {poke_name(reward[1])}")
                c1, c2 = st.columns([3, 1])
                c1.write(f"{JUNK_NAMES[junk]} {need}개 → **{rtext}**")
                c2.button("교환", key=key, on_click=craft, args=(s, key),
                          disabled=s["junk"].get(junk, 0) < need, use_container_width=True)
        with t2:
            owned = {k: v for k, v in s["junk"].items() if v > 0}
            if not owned:
                st.write("가진 잡템이 없습니다.")
            for k, v in owned.items():
                st.write(f"{JUNK_NAMES[k]} × {v}")

    with st.expander("전체 강화표 보기"):
        lines = ["| 단계 | 포켓몬 | 다음 강화 비용 | 성공 확률 | 판매가 | 누적 강화 비용 | 방지권 |",
                 "|---|---|---|---|---|---|---|"]
        for i in range(FINAL_LEVEL):
            c, r, p, g, _ = TABLE[i]
            lines.append(f"| +{i} | {poke_name(i)} | {fmt_won(c)} | {r}% | {fmt_won(p) if p else '-'} | "
                         f"{fmt_won(spent_to_reach(i)) if i else '-'} | {f'{g}개' if g else '-'} |")
        lines.append(f"| +{FINAL_LEVEL} | {poke_name(FINAL_LEVEL)} | - | - | 엔딩 | "
                     f"{fmt_won(spent_to_reach(FINAL_LEVEL))} | - |")
        st.markdown("\n".join(lines))


if __name__ == "__main__":
    main()
