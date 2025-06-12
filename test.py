from collections import Counter
from itertools import product

훈련석_점수표 = {
    # 난이도
    "난이도 - 하드중급": 130, "난이도 - 하드일반": 100, "난이도 - 상급": 70, "난이도 - 중급": 50,
    # 인원수
    "인원수-4인": 0, "인원수-6인": 0, "인원수-무제한": -30,
    # 파티원
    "파티원-최대 대미지 50%": 45, "파티원-생명력 50%": 30,
    # 몬스터
    "몬스터-대미지 500%": 45, "몬스터-생명력 500%": 45,
}

# 훈련석 그룹 분류
grouped_stones = {
    "난이도": [k for k in 훈련석_점수표 if k.startswith("난이도")],
    "인원수": [k for k in 훈련석_점수표 if k.startswith("인원수")],
    "파티원": [k for k in 훈련석_점수표 if k.startswith("파티원")],
    "몬스터": [k for k in 훈련석_점수표 if k.startswith("몬스터")],
}

# 입력 재고
입력 = [
    "난이도 - 하드중급 2개, 몬스터-대미지 500% 1개, 파티원-최대 대미지 50% 1개",
    "인원수-6인 2개, 인원수-무제한 1개, 파티원-생명력 50% 2개, 몬스터-생명력 500% 2개, 숨겨진 층-보석 낙원 1개",
    "난이도 - 하드일반 1개, 몬스터-대미지 500% 1개, 파티원-최대 대미지 50% 1개, 숨겨진 층 - 기사단의 장 1개",
]

# 파싱
재고 = Counter()
for line in 입력:
    for part in line.split(","):
        for key in 훈련석_점수표:
            if key in part:
                count = int("".join(filter(str.isdigit, part))) or 1
                재고[key] += count

# 가능한 조합 탐색
가능한_조합 = []
for 조합 in product(*grouped_stones.values()):
    if len(set(조합)) < 4:
        continue  # 중복 제거
    점수 = sum(훈련석_점수표[x] for x in 조합)
    if 점수 >= 190:
        조합_카운트 = Counter(조합)
        if all(재고[k] >= v for k, v in 조합_카운트.items()):
            가능한_조합.append(조합)
            for k in 조합_카운트:
                재고[k] -= 조합_카운트[k]
        if len(가능한_조합) == 3:
            break

# 출력
print(f"가능한 SS 조합 수: {len(가능한_조합)}")
for i, 조합 in enumerate(가능한_조합, 1):
    print(f"{i}회차 조합: {조합}")
