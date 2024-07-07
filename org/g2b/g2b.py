
import threading

import automatic as am
import automatic.selenium as s
import automatic.win32 as w
from automatic.selenium.utils import create_driver
from org.g2b.res import resmgr

from automatic.utils.logger import Logger

import time
import logging


class G2B(am.Automatic):

    def __init__(self, driver, pw, id, loglevel=logging.INFO):
        self.__pw = pw
        self.__id = id

        Logger.init("G2B", loglevel)
        self.logger = Logger.get("G2B")

        selenium = s.Context(driver, timeout=20, differ=0)
        win32 = w.Context(timeout=50, differ=0)
        am.Automatic.__init__(self, [selenium, win32])

    def certificate(self, pw):
        wMain = w.Title('인증서 선택', "인증서 선택")
        self.type(w.Image('패스워드 입력상자', resmgr.get(
            'certificate_password_input.png'), parent=wMain), pw)
        self.click(w.Image('인증서 확인 버튼', resmgr.get(
            'certificate_password_confirm_button.png'), parent=wMain))

    def login(self):

        # Step: 홈페이지로 이동
        self.logger.info("로그인")
        try:
            self.go(s.Url("G2B 홈페이지", 'https://www.g2b.go.kr'))
            # 이전상태에 따라 popup이 생성되는 경우가 있다. 
            if self.exist(s.Alert("test", "", timeout=3)):
                self.accept(s.Alert("test", ""))

            fLogin = s.Id("로그인프레임", 'member_iframe')
            self.click(
                s.Id("지문인식 예외적용 버튼", 'arg_exceptionLogin', parent=fLogin))
            self.click(
                s.Xpath("로그인버튼", '//*[@id="logout"]/ul/li[1]/ul/li/a/img', parent=fLogin, differ=2))
            self.accept(s.Alert("팝업", '계속 진행하시겠습니까?', differ=2))


            self.logger.info("인증서 로그인(기업)")
            self.certificate(self.__pw)

            self.logger.info("주민번호 입력")
            fSub = s.Id("주민번호 입력 프레임", 'sub')
            token = self.__id.split('-')
            self.type(s.Id("주민번호 앞자리 상자", 'jmbeonho1', parent=fSub), token[0])
            self.type(s.Id("주민번호 둣자리 상자", 'jmbeonho2', parent=fSub), token[1])

            # WARNING!!!
            # click함수가 종료되기 위해선 개인이증서 로그인이 완료되어야 하기 때문에
            # 별도에 thread에서 click 을 동작한후 join해야 한다.
            # 그렇지 않으면 block되어서 진행이 안된다.
            def click(): return self.click(
                s.Xpath('확인버튼', '//span[text()="확인"]/..', parent=fSub))
            thr = threading.Thread(target=click)
            thr.start()

            # 개인인증서
            self.logger.info("인증서 로그인(개인)")
            self.certificate(self.__pw)

            thr.join()

            self.logger.info("예외적용자 확인")
            wConfirm = s.Title("예외적용자 확인 윈도우", "Message: 나라장터")
            self.click(
                s.Xpath("확인버튼",  "//span[text()='확인']/..", parent=wConfirm))
            return True

        except Exception as e:
            self.logger.error(e)
            return False
        
    def __register(self, code):
        myPageUrl = 'https://www.g2b.go.kr/pt/menu/selectSubFrame.do?framesrc=/pt/menu/frameMypage.do'

        try:
            self.logger.info(f"마이페이지로 이동")
            self.go(s.Url("마이페이지", myPageUrl))

            fSub = s.Id("서브프레임", "sub")
            fMain = s.Name("메인프레임", "main", parent=fSub)
            self.click(
                s.Xpath("에디트 버트", '//*[@id="container"]/div[2]/div/a[1]', parent=fMain))

            table = self.table(
                s.Xpath("공급품목표", '//*[@id="frm_supProd"]/div[3]/table', parent=fMain))
            if table['세부품명번호'].isin([int(code)]).any():
                self.logger.info(f"이미 등록되었습니다.")
                return True

            self.logger.info(f"물품품목 조회")
            self.click(s.Xpath(
                "물품검색버튼", '//*[@id="frm_addProd"]/div[3]/table/tbody/tr/td[1]/div/button', parent=fMain))

            wSearch = s.Title("물품검색창", "[팝업] 세부품명찾기: 나라장터")
            self.type(s.Id("세부물품번호 입력상자", 'detailPrdnmNo', parent=wSearch), code)
            self.click(s.Id("물품검색버튼", 'bt_search', parent=wSearch))
            self.click(s.Xpath(
                "첫번째품목", '//*[@id="container"]/div[1]/table/tbody/tr/td[2]/a', parent=wSearch))

            self.click(
                s.Xpath("등록버튼", '//*[@id="frm_addProd"]/div[2]/a', parent=fMain))
            self.accept(s.Alert("확인팝업", ""))

            # 20230415: sometime there is no messages to click
            wConfirm = s.Title("물품추가확인창", "Message: 나라장터")
            if self.exist(wConfirm):
                self.click(
                    s.Xpath("확인버튼", '//*[@id="container3"]/div[2]/div/a', parent=wConfirm))
            return True

        except Exception as e:
            self.logger.error(e)
            return False

    def register(self, code):
        codes = code.split(",")
        codes = [pn.strip() for pn in codes]
        self.logger.info(f"사전등록: {codes}")
        for code in codes:
            if not self.__register(code):
                return False
        return True

        

    def participate(self, code, price):
        # 소수점이 있을 경우 입력이 불가하다고 안내한다. 
        price = int(float(price))

        try:
            self.logger.info(f"물품등록. code={code}, price={price}.")

            self.logger.info(f"물품 검색")
            fTop = s.Id("상단프레임", 'tops')
            self.click(s.Xpath("입찰정보버튼", '//img[@alt="입찰정보"]', parent=fTop))

            fSub = s.Id("서브프레임", "sub")
            fMain = s.Name("메인프레임", "main", parent=fSub)

            self.type(s.Id("입찰번호 입력상자", "bidno1", parent=fMain), code)
            self.click(s.Id("검색버튼", "bt_search", parent=fMain))

            self.click(
                s.Xpath("지문투찰버튼", "//button[@title='지문투찰']", parent=fMain))

            # XXX: 새로운 Window 가 열릴때 너무 빨리 열리게 되면 title이 none인 경우가 생긴다.
            time.sleep(3)

            wSearch = s.Title("물품공고분류조회", "물품공고분류조회")
            self.click(s.Xpath("투찰 링크", "//a[text()='1-투찰']", parent=wSearch))

            # validation - 이미 등록되어 있는 경우
            wMessage = s.Title("메세지 창", "Message: 나라장터", timeout=5)
            if self.exist(s.Xpath("접수완료 메세지", "//div[contains(text(), '접수되었습니다.')]", parent=wMessage)):
                self.click(
                    s.Xpath("닫기버튼", '//*[@id="container3"]/div[2]/div/a/span', parent=wMessage))
                self.logger.info("이미 등록이 완료 되었습니다.")
                return True

            # validation - 이미 마감되어 있는 경우
            if self.exist(s.Title("투찰제어 창", "투찰제어", timeout=5)):
                self.logger.info("물품등록이 마감되어 진행할 수 없습니다.")
                return False

            wNotice = s.Title("투찰 공지사항", "투찰 공지사항")
            self.click(s.Id("체크버튼 - 1", "entrprsInfoCheckY", parent=wNotice))
            self.click(s.Id("체크버튼 - 2", "administInfoCheckY", parent=wNotice))
            self.click(s.Id("체크버튼 - 3", "noticeCheckY", parent=wNotice))
            self.click(
                s.Xpath("확인버튼", "//span[text()='확인']/..", parent=wNotice))

            self.logger.info("물품구매입찰서 작성")
            # 새로운 windows (사실 기존 윈도우에서 이름이 변경된다. )
            wBid = s.Title("물품구매입찰서 창", "물품구매입찰서")
            self.click(s.Id("동의버튼", "increasedAgreementCheck", parent=wBid))
            self.type(s.Id("가격입력박스", "chongDan", parent=wBid), price)

            # 가격 입력후 바로 아래과정을 진행 하게 되면 가격을 입력해야 한다는 팝업이 뜬다.
            # 가격 입력후 focus를 변경해 주어야 한다.
            # 아래 단계는 단순히 가격입력 textbox의 focus를 다른곳으로 돌리는 역할을 한다.
            self.type(s.Xpath(
                "임시 입력박스", "//*[@id='attachFile']/tbody/tr/td[2]/input", parent=wBid), "")
            self.click(s.Id("청렴 계약 동의 체크확인 버튼",
                       "checkCleanContract", parent=wBid))
            self.click(s.Id("송신버튼", "btnConfirm", parent=wBid))

            # 새로운 windows (사실 기존 윈도우에서 이름이 변경된다. )
            self.logger.info("투찰금액 확인")
            wBid = s.Title("투찰금액 확인 창", "투찰금액 확인")
            self.click(s.Id("확인 체크버튼", "noticeCheckY", parent=wBid))
            self.click(s.Xpath("확인 버튼", '//span[text()="확인"]/..', parent=wBid))

            wLottery = s.Title("추첨번호 선택 창", "추첨번호 선택")
            self.clicks(s.Name("추첨번호 체크박스", "check",
                        parent=wLottery), num_samples=2)
            # XXX: 너무 빠르게 지나가 버려 확인하기가 어렵다.
            time.sleep(3)
            self.click(
                s.Xpath("확인 버튼", '//span[text()="추첨번호전송"]/..', parent=wLottery))

            self.accept(s.Alert("전송 확인 팝업", "전송하시겠습니까?"))
            self.accept(s.Alert("입찰 확인 팝업", "입찰에 참여할 수 있습니다."))

            # 개인인증서
            self.logger.info("개인인증서")
            self.certificate(self.__pw)

            # 전송 완료 후 java에서 띄우는 팝업
            self.logger.info("나라장터: 정상접수 확인")
            wConfirm = w.Title("나라장터 Java 창", "나라장터")
            self.click(w.Text("확인 버튼","OK", parent=wConfirm))

            self.logger.info("전자입찰 송수신")
            wHistory = s.Title("전자입찰 송수신상세이력조회 창", "전자입찰 송수신상세이력조회")
            self.click(s.Xpath("닫기 버튼", "//span[text()='닫기']/..", parent=wHistory))
            return True

        except Exception as e:
            self.logger.error(e)
            return False
