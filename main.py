from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import random
import re


# FastAPI 애플리케이션 생성 
app = FastAPI()

# 템플릿 디렉토리 설정 (HTML 파일을 저장할 곳)
templates = Jinja2Templates(directory="templates")


# ComplimentModel 클래스는 칭찬을 관리하는 기능을 제공
class ComplimentModel:
    def __init__(self):
        # 기본 칭찬문구 리스트 (두 개의 칭찬문구가 포함됨)
        self.compliments = [
"""의사선생님, 저 수술 끝났나요? 마취가 안 풀린 것 같아서요.
네, 수술 무사히 마쳤습니다. 마취도 곧 풀리실 겁니다.
하지만 전 태어날 때부터 아이 러브 {0} 쏘 마취였는데 이건 언제 풀리죠?
환자분, 안타깝게도 그건 {0}{{이/}}의 팬이라면 누구나 계속 풀리지 않을 마취입니다.""",

"""여러분 제가 오늘 어이 있는 일을 겪었는데요...
원래 탕후루란 게 제철이고 수요 많은 과일들로 만드는 거 아닌가요...?
오늘 탕후루 가게에 갔는데
글쎄 {0} 탕후루가 있다는 거예요!!
그래서 맛있게 먹고 꼬치와 종이컵은 집에 가서 버렸답니다!""",

"""사람들이 의외로 모르는 무례한 말 TOP3

1. 안녕하세요 - {0}{{이/가}} 내 옆에 없는데 안녕하겠냐
2. 밥은 드셨나요? - {0}{{이/가}} 내 곁에 없는데 밥이 넘어가겠냐
3. 잘 자요 - {0}{{이/가}} 내 곁에 없는데 잠에 들 수 있겠냐""",

'''"미국은 어디 있지?"
"북위 24-48, 경도 67-125도, 북아메리카에."

"대한민국은?"
"동경 127도, 북위 37도, 동북아시아에."

"{0}{{은/는}}-"
".여기, 내 심장에."''',

'''버스를 탔을 때, 기사님이 의아한 표정으로 물었다.
"학생, 1명인데 왜 2명 찍어?"
"제 마음속에는 언제나 {0}{{이/가}} 살고 있기 때문이죠."''',

'''“{0} 좋아하지 마..”
“그게 뭔데?”
“{0} 좋아하지 말라고..”
”그거 어떻게 하는 건데?”''',

"""{0} 그거 알아? 사람이 너무 예쁜 걸 보면 단기 기억상실증에 걸린대..
{0} 그거 알아? 사람이 너무 예쁜 걸 보면 단기 기억상실증에 걸린대..
{0} 그거 알아? 사람이 너무 예쁜 걸 보면 단기 기억상실증에 걸린대..
{0} 그거 알아? ... """,

"""{0}, 나의 사랑. {0}, 나의 빛. {0}, 나의 어둠.
{0}, 나의 삶. {0}, 나의 기쁨. {0}, 나의 슬픔.
{0}, 나의 고통. {0}, 나의 안식. {0}, 나의 영혼.
.
.
.
{0}, 나.""",

"""그거 기억나요?
사람들한테 {0} 좋아하는 사람 손 접어했더니
지구가 반으로 접힌 거 그거 겨우겨우 되돌렸잖아요
나 그때 내 눈앞에 브라질 있어서 깜짝 놀랐잖아""",

"""공룡이 왜 멸종된 줄 알아요?
{0} 미모를 보고 박수를 안 쳐서 내가 다 없애버림""",

"""{0} 승마장 출입 금지당했어요...
{0} 외모 보면 말이 안 나와서…""",

"""{0}{{은/는}} 미술관 입장료 안 받고 들어가도 돼 
왜냐면 {0}{{이/가}} 작품이야""",

"""{0} 맨날 두 명이랑 같이 잔다면서요? 
스캔들 났던데.... 칭찬이랑 소문이 자자해서""",

"""{0} 미모 보고 이거다!!! 싶어서 이마 쳤는데 거북목 완치됨....;;;""",

"""영어시간에 perfect 외우기 힘들어서 "{0}"{{이/}}라고 외웠죠.."""



        ]

    # 사용자의 이름을 받아서 무작위 칭찬문구를 반환하는 메소드
    def print_compliment(self, name: str) -> str:
        compliment = random.choice(self.compliments).format(name)
        compliment_with_particle = self.apply_particle(name, compliment)
        return compliment_with_particle.replace("\n", "<br>") # 줄바꿈을 HTML에서의 <br>로 변환

    # 새로운 칭찬문구를 리스트에 추가하는 메소드
    def add_compliment(self, compliment: str):
        self.compliments.append(compliment)

    # 리스트에서 특정 칭찬문구를 삭제하는 메소드
    def delete_compliment(self, compliment: str):
        if compliment in self.compliments:
            self.compliments.remove(compliment)
    
    # 입력된 문자열이 한글인지 확인하는 메소드
    def is_korean(self, text: str) -> bool:
        return all('가' <= char <= '힣' for char in text)


    # 이름의 마지막 글자에 종성(받침)이 있는지 확인하는 메소드
    def has_final_consonant(self, korean_name: str) -> bool:
        if not self.is_korean(korean_name):
            return False
        last_char = korean_name[-1]
        code = ord(last_char) - 0xAC00
        jongseong = code % 28
        return jongseong != 0
    
    # 종성 여부에 따라 문구에 포함된 {이/가}, {은/는}, {을/를} 플레이스홀더를 교체하는 메소드
    def apply_particle(self, name: str, text: str) -> str:
        def replace_particle(match):
            particle = match.group(0)
            if particle == "{이/가}":
                return "이" if self.has_final_consonant(name) else "가"
            elif particle == "{은/는}":
                return "은" if self.has_final_consonant(name) else "는"
            elif particle == "{을/를}":
                return "을" if self.has_final_consonant(name) else "를"
            elif particle == "{이/}":
                return "이" if self.has_final_consonant(name) else ""
            else:
                return particle

        # 정규 표현식을 이용해 {이/가}, {은/는}, {을/를} 패턴을 찾아 교체
        result = re.sub(r"{이/가}|{은/는}|{을/를}|{이/}", replace_particle, text)
        return result
        


# ComplimentModel 인스턴스 생성 (전역적으로 사용)
compliment_model = ComplimentModel()

# 메인 페이지 ("/" 경로) - 선택할 수 있는 옵션들을 제공
@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# 칭찬받기 기능 (이름을 입력하면 칭찬 출력) - POST 요청
@app.post("/compliment", response_class=HTMLResponse)
async def give_compliment(request: Request, name: str = Form(...)):
    # ComplimentModel을 사용하여 이름에 맞는 칭찬을 생성
    compliment = compliment_model.print_compliment(name)
    return templates.TemplateResponse("compliment.html", {"request": request, "compliment": compliment, "name": name})


# 칭찬문구 추가 페이지 - GET 요청 (새 칭찬문구를 입력할 수 있는 페이지 출력)
@app.get("/add_compliment", response_class=HTMLResponse)
async def add_compliment_page(request: Request):
    return templates.TemplateResponse("add_compliment.html", {"request": request})


# 새로운 칭찬문구를 추가하는 기능 - POST 요청
@app.post("/add_compliment", response_class=HTMLResponse)
async def add_compliment(request: Request, compliment: str = Form(...)):
    # 새로운 칭찬문구를 ComplimentModel에 추가
    compliment_model.add_compliment(compliment)
    # 메인 페이지로 리디렉션
    return templates.TemplateResponse("index.html", {"request": request})


# 칭찬문구 삭제 페이지 - GET 요청 (삭제할 칭찬을 선택할 수 있는 페이지 출력)
@app.get("/del_compliment", response_class=HTMLResponse)
async def delete_compliment_page(request: Request):
    # 현재 ComplimentModel에 저장된 모든 칭찬문구를 전달
    return templates.TemplateResponse("delete_compliment.html",
                                      {"request": request, "compliments": compliment_model.compliments})


# 선택된 칭찬문구를 삭제하는 기능 - POST 요청
@app.post("/del_compliment", response_class=HTMLResponse)
async def delete_compliment(request: Request, compliment: str = Form(...)):
    # ComplimentModel에서 선택된 칭찬문구를 삭제
    compliment_model.delete_compliment(compliment)
    # 삭제 후 리디렉션
    return templates.TemplateResponse("delete_compliment.html", {"request": request})


