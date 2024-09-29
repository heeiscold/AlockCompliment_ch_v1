from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import random
from fastapi.staticfiles import StaticFiles


# FastAPI 애플리케이션 생성
app = FastAPI()

# 템플릿 디렉토리 설정 (HTML 파일을 저장할 곳)
templates = Jinja2Templates(directory="templates")


# ComplimentModel 클래스는 칭찬을 관리하는 기능을 제공
class ComplimentModel:
    def __init__(self):
        # 기본 칭찬문구 리스트 (두 개의 칭찬문구가 포함됨)
        self.compliments = [
                        """의사선생님, 저 수술 끝났나요? 마취가 안 풀린것 같아서요.
네, 수술 무사히 마쳤습니다. 마취도 곧 풀리실 겁니다.
하지만 전 태어날때부터 알러뷰 {} 쏘 마취였는데 이건 언제 풀리죠?
환자분, 안타깝게도 그건 {}의 팬이라면 누구나 계속 풀리지 않을 마취입니다.""",
            """여러분 제가 오늘 어이있는 일을 겪었는데요...

원래 탕후루란게 제철이고 수요많은 과일들로 만드는거 아닌가요...?

오늘 탕후루 가게에 갔는데

글쎄 {} 탕후루가 있다는거에요!!

그래서 맛있게 먹고 꼬치와 종이컵은 집에 가서 버렸답니다!""",
            """사람들이 의외로 모르는 무례한 말 TOP3

1. 안녕하세요 - {}이 내 옆에 없는데 안녕하겠냐

2. 밥은 드셨나요? - {}이 내 곁에 없는데 밥이 넘어가겠냐

3. 잘 자요 - {}이 내 곁에 없는데 잠에 들 수 있겠냐""",
            '''"미국은 어디있지?"

"북위 24-48, 경도 67-125도,

북아메리카에."

"대한민국은?"

"동경 127도, 북위 37도,

동북아시아에."

"{}은-"

".여기, 내 심장에."''',
            '''버스를 탔을 때,

기사님이 의아한 표정으로 물었다.

"학생, 1명인데 왜 2명찍어?"

"제 마음속에는 언제나 {}이 살고있기 때문이죠."''',
            '''“{} 좋아하지마..”

“그게 뭔데?”

“{} 좋아하지말라고..”

”그거 어떻게 하는건데?”'''
        ]

    # 사용자의 이름을 받아서 무작위 칭찬문구를 반환하는 메소드
    def print_compliment(self, name: str) -> str:
        return random.choice(self.compliments).format(name, name)

    # 새로운 칭찬문구를 리스트에 추가하는 메소드
    def add_compliment(self, compliment: str):
        self.compliments.append(compliment)

    # 리스트에서 특정 칭찬문구를 삭제하는 메소드
    def delete_compliment(self, compliment: str):
        if compliment in self.compliments:
            self.compliments.remove(compliment)


# ComplimentModel 인스턴스 생성 (전역적으로 사용)
compliment_model = ComplimentModel()

# 정적 파일을 "/static" 경로에서 서빙하도록 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

# 메인 페이지 ("/" 경로) - 선택할 수 있는 옵션들을 제공
@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# 칭찬받기 기능 (이름을 입력하면 칭찬 출력) - POST 요청
@app.post("/compliment", response_class=HTMLResponse)
async def give_compliment(request: Request, name: str = Form(...)):
    # ComplimentModel을 사용하여 이름에 맞는 칭찬을 생성
    compliment = compliment_model.print_compliment(name)
    return templates.TemplateResponse("compliment.html", {"request": request, "compliment": compliment})


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


