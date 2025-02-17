

import os
import threading

import automatic as am
import automatic.selenium as s
import automatic.win32 as w
from org.g2b.res import resmgr
from automatic.utils import Logger
import time
import logging



class Kepco(am.Automatic):
    def __init__(self, driver, id,  pw, certpw, loglevel=logging.INFO):
        self.__pw = pw
        self.__id = id
        self.__certpw = certpw

        Logger.init("Kepco", loglevel)
        self.logger = Logger.get("Kepco")

        selenium = s.Context(driver, timeout=20, differ=0)
        win32 = w.Context(timeout=50, differ=0)
        am.Automatic.__init__(self, [selenium, win32])

    def is_logged_in(self, timeout=10):
        return self.exist(s.Xpath("로그아웃버튼", "//span[text()='로그아웃']", timeout=timeout))

    def certificate(self, category,frame):
        """
        Login frame과 제출시 인증하는 frame이 서로 다르다. 
        category: ['사업자', '은행']
        """
        
        self.click(s.Id("하드디스크",'NX_MEDIA_HDD', parent=frame))
        self.click(s.Xpath("인증서",f'//td/div[contains(text(),"{category}")]', parent=frame))

        self.type(s.Id("보안토큰 비밀번호",'certPwd', parent=frame, differ=3), self.__certpw)
        self.click(s.Xpath("확인버튼",'//*[@id="nx-cert-select"]/div[4]/button[1]', parent=frame))

    def login(self):

        self.go(s.Url("홈페이지","https://srm.kepco.net/index.do?theme=default"))

        # 페이지를 이동할 때 alert가 생기는 경우가 많이 있기 때문에 있다면 accept해 준다. 
        if self.exist(s.Alert("test", "", timeout=3)):
            self.accept(s.Alert("test", ""))
                        
        if self.is_logged_in(timeout=3):
            self.logger.info("이미 로그인 되어 있습니다.")
            return True

        # fLogin = s.Id("로그인 버튼 프레임", 'mdiiframe-1010-iframeEl')
        # self.click(s.Id("로그인 버튼", "memberLogin", parent=fLogin, differ=3))
        self.click(s.Xpath("로그인 버튼", '//span[text()="로그인"]/../../..'))

        time.sleep(5)

        self.logger.info("아이디/비번 입력")
        fLogin = s.Xpath("로그인 프레임", '//div/div/iframe')
        self.type(s.Id("로그인 아이디", "username", parent=fLogin), self.__id)
        self.type(s.Id("로그인 비번", "password", parent=fLogin), self.__pw)
        self.click(s.Id("로그인 버튼", "certBtn", parent=fLogin))

        self.logger.info("인증서 로그인")

        fCert =  s.Xpath("인증서 로그인 프레임", '//iframe[contains(@title,"LOGIN")]')
        self.certificate("사업자", fCert)

        # need to wait until page reloaded
        time.sleep(10)

        return self.is_logged_in(60)
   
    def register(self, number):
        # close all tab: refresh->accept alert.
        self.go(s.Url("홈페이지","https://srm.kepco.net/index.do?theme=default"))

        if self.exist(s.Alert("test", "", timeout=3)):
            self.accept(s.Alert("test", ""))

        # home tab이 나온 이후 공고번호 조회 탭을 연다. 
        self.exist(s.Xpath("홈탭", '//span[text()="home"]'))

        self.logger.info("공고번호 조회 탭 열기")
        self.click(s.Xpath("입찰/계약 탭", '//span[text()="입찰/계약"]'))
        self.click(s.Xpath("입찰참가신청", '//h4[text()=" 입찰참가신청 "]'))
        if not self.exist(s.Xpath("닫기 버튼", '//span[@class="x-tab-close-btn"]')):
            return False
        
        # close all popup
        # 현재 아무런 팝업 나오지 않음. 
        self.logger.info("공고번호 조회")
        self.type(s.Xpath("공고번호 입력 박스", '//input[@title="공고번호"]', timeout=15, differ=3), number)
        self.click(s.Xpath("확인 버튼", '//span[text()="조회"]'))

        cnt = self.count(s.Xpath("체크박스",'//div[@class="x-grid-row-checker"]'))
        if cnt == 0:
            self.logger.error("검색 결과가 없습니다. ")
            return False
        if cnt > 1:
            self.logger.error(f"검색 결과가 한개 초과 입니다. cnt={cnt}")
            return False

        table = self.table(s.Xpath("검색결과 테이블",'/html/body/div[4]/div[2]/div[2]/div/div/div[2]/div/div/div/div[2]/div[1]/div/div/div/div[2]/div[3]/div[2]/div/div[2]/div[2]/div/div[2]/table'))
        if table[2].loc[0] in ["제출", "심사완료"]:
            self.logger.info("이미 등록완료 되었습니다.")
            return True

        # Apply
        self.click(s.Xpath("체크박스", '//div[@class="x-grid-row-checker"]'))
        self.click(s.Xpath("참가신청", '//*[contains(@class,"x-btn-icon-el x-btn-icon-el-default-toolbar-small btn-request")]'))

        # 입찰담합유의사항
        if self.exist(s.Xpath("답합유의사항 확인 체크박스", '//input[@title="위의 사항을 확인하였습니다."]', timeout=3)):
            self.click(s.Xpath("답합유의사항 확인 체크박스", '//input[@title="위의 사항을 확인하였습니다."]'))
        
        self.logger.info("모든 popup닫기")
        self.close_all_popup(timeout=20)

        # TODO: 한글입력이 안됨. 
        self.logger.info("중소기업확인서 첨부")
        filepath = os.path.join(os.path.expanduser("~"), ".iaa", "small_business_confirmation.pdf")
        self.attach_file(filepath)

        self.logger.info("약정들에 동의") 
        check_boxes = s.Xpath("체크박스", '//div/div[not(contains(@style,"display: none"))]/div[3]/div/div/div[2]/div/div/input', differ=1, multiple=True)
        if self.exist(check_boxes):
            self.clicks(check_boxes)

        self.logger.info("제출 확인") 
        self.click(s.Xpath("제출 버튼", '//span[text()="제출"]'))
        self.close_messagebox("예", timeout=10)
        self.close_messagebox("확인", timeout=10) 

        #  확인 별도 제출요구서류가 있는 경우 첨부 여부를 반드시 확인하시기 바랍니다. 입찰참가신청서를 제출하시겠습니까?
        #  예/아니오
        self.close_messagebox("예", timeout=10) 

        # certificate
        self.logger.info("인증서 제출")
        fCert =  s.Xpath("인증서 로그인 프레임", '//iframe[contains(@src,"kica/kepco/kicaCert.jsp")]')
        self.certificate("사업자", fCert)

        # 제출하였습니다. 
        self.close_messagebox("확인", timeout=10)
        return True

    def attach_file(self, filepath):
        self.logger.info(f"파일 첨부 {filepath}")
        # TODO: click is not working(clickable)
        self.clicks(s.Xpath("파일첨부 버튼", '//*[text()="파일첨부"]'))

        wFileAttach = w.Title("파일첨부 다이얼로그","[TITLE:열기; CLASS:#32770]")
        self.type(w.Control("파일입력상자", "Edit1", parent=wFileAttach, differ=3), f"\"{filepath}\"")
        # TODO: button이 한개 더 있음.. 버튼의 이름을 통해 확인을 하는 것이 좋을 것 같다. 

        self.click(w.Control("확인 버튼", "Button2", parent=wFileAttach, differ=5))


    def close_all_popup(self, timeout=10):
        start = time.time()
        cnt=0
        while True:
            # messagebox
            #  - 낙찰 후 미계약 건에 대한 공지         - 확인
            #  - 변경 미등록시 입찰무효처리에 대한 공지 - 확인
            self.close_messagebox("확인")
            self.close_all_notices()
            curr = time.time() - start
            if curr > timeout:
                break
            cnt = cnt + 1
            time.sleep(1)

    def close_messagebox(self, button, timeout=1):
        self.logger.info(f"메세지 박스 닫기: {button}")
        message_box = '//div[contains(@class,"x-window") and contains(@class,"x-message-box")]'

        # messesage box text 출력
        text = s.Xpath(f"메세지 박스 {button} 버튼 텍스트", message_box, timeout=timeout)
        if self.exist(text):
            self.logger.info(f"Messagebox: {' '.join(self.text(text).splitlines())}" )

        # message box에 button이 여러개. 
        message_box_buttons ='div[3]/div/div/a'
        message_box_button = f"span/span/span[text()='{button}']/../../.."
        button = s.Xpath(f"메세지 박스 {button} 버튼", "/".join([message_box, message_box_buttons, message_box_button]), timeout=timeout)

        if not self.exist(button):
            return

        if not self.click(button):
            self.logger.info("메세지 박스 닫기 성공")
        
    def close_all_notices(self):
        notices = '//div[contains(@class,"x-panel") and contains(@class,"x-panel-popup")]'
        notice_close_buttons = 'div/div/div/a/span/span/span[2]'
        close_button = s.Xpath(f"패널 팝업 닫기 버튼", "/".join([notices, notice_close_buttons]), timeout=1, multiple=True)
        if self.exist(close_button):
            self.clicks(close_button)

    def participate(self, code, cost):
        # 소수점이 있을 경우 입력이 불가하다고 안내한다. 
        cost = int(float(cost))
        
        # close all tab: refresh->accept alert.
        self.go(s.Url("홈페이지","https://srm.kepco.net/index.do?theme=default"))

        if self.exist(s.Alert("test", "", timeout=3)):
            self.accept(s.Alert("test", ""))

        self.exist(s.Xpath("홈탭", '//span[text()="home"]'))

        self.logger.info("입찰/계약 탭 열기")
        self.click(s.Xpath("입찰/계약 버튼", '//span[text()="입찰/계약"]'))
        self.click(s.Xpath("입찰 버튼", '//h4[text()=" 입찰(투찰진행) "]'))


        self.logger.info(f"공고번호 검색 {code}")
        self.type(s.Xpath("공고번호 입력상자", '//input[@title="공고번호"]', differ=5), code)
        self.click(s.Xpath("조회 버튼", '//span[text()="조회"]'))

         # messagebox : 공고일자의 최대 검색일자는 6개월 입니다. "확인"
        self.close_messagebox("확인")

        self.logger.info(f"검색 결과 검증")
        cnt = self.count(s.Xpath("체크박스",'//div[@class="x-grid-row-checker"]'))
        if cnt == 0:
            self.logger.error("검색 결과가 없습니다. ")
            return False
        if cnt > 1:
            self.logger.error(f"검색 결과가 한개 초과 입니다. cnt={cnt}")
            return False
        
        table = self.table(s.Xpath("검색결과 테이블",f'//*[contains(text(),"{code.split("-")[0]}")]/../../../..'))
        if table is None:
            self.logger.error("공고를 찾을 수 없습니다.")
            return False

        if table[1].loc[0] != "미제출":
            self.logger.info(f"이미 등록완료 되었습니다. {table}")
            return True
        
          # Apply
        self.click(s.Xpath("체크박스", '//div[@class="x-grid-row-checker"]'))
        self.click(s.Xpath("입찰 참여 버튼", '//span[text()="입찰참여"]'))

        # messagebox - 입찰 창여 하시겠습니까?
        self.close_messagebox("예", timeout=30)

        self.logger.info("지문인식예외투찰")
        self.click(s.Xpath("지문인식예외투찰 버튼","//td[6]/div/img"))
        self.close_messagebox("예")

        self.close_all_popup(timeout=3)

        # 개인인증서 선택
        self.logger.info("개인인증서 로그인")
        fCert =  s.Xpath("인증서 로그인 프레임", '//iframe[contains(@src,"kica/kepco/kicaCert.jsp")]')
        self.certificate("은행", fCert)

        self.close_all_popup(timeout=10)
        
        self.logger.info("추첨번호 선택")
        self.clicks(s.Xpath("추첨번호 버튼", '//span[contains(text(),"예정가격추첨갯수")]/../../div/div/table/tbody/tr/td/a/span/span/span[2]', differ=1), num_samples=4)
        
        self.logger.info(f"가격입력 f{cost}")
        # self.type(s.Xpath("가격입력", '//span[text()="숫자"]/../../div/div/table/tbody/tr/td[1]/div[1]/div/div/div[2]/input', timeout=1, visible=False), cost)
        # td[1] -> td 변경: 어떤 input(부가가치세 포함 따위의 글자가 추가됨)의 위치가 다르다. 기존 구조와 동일한지 검증해 보자.
        self.type(s.Xpath("가격입력", '//span[text()="숫자"]/../../div/div/table/tbody/tr/td/div[1]/div/div/div[2]/input', timeout=1, visible=False), cost)
        # self.click(s.Xpath("포커스 변경",  '//span[text()="숫자"]/../../div/div/table/tbody/tr/td[1]/div/div/div/div/div'))
        self.click(s.Xpath("포커스 변경",  '//span[text()="숫자"]/../../div/div/table/tbody/tr/td/div/div/div/div/div'))
        self.type(s.Xpath("가격입력", '//span[text()="확인"]/../../div/div/div/div/div[2]/div/div/div[2]/input', timeout=1, visible=False), cost)
        self.click(s.Xpath("포커스 변경",  '//span[text()="확인"]/../../div/div/div/div/div[2]/div/div/div/div'))
        self.click(s.Xpath("입력값 확인 버튼", '//span[text()="입력값확인"]'))

        self.logger.info(f"제출")
        self.click(s.Xpath("제출 버튼", '//span[text()="제출"]'))
        self.close_messagebox("예", timeout=5)
        self.close_messagebox("확인", timeout=5) # message box - 제출되었습니다.

        self.certificate("사업자", fCert)
        self.close_messagebox("확인", timeout=5) # message box - 제출되었습니다.
        return True
        