import os
import threading

import automatic as am
import automatic.selenium as s
import automatic.win32 as w
from automatic.selenium.utils import create_driver

import time
import logging

LOGGER_G2B = "G2B"
logger = logging.getLogger(LOGGER_G2B)

class G2B_new_gen(am.Automatic):

    def __init__(self, driver, pw, id, cert_public, cert_finance, name, phone, birth):
        self.name = "나라장터"
        self.__pw = pw
        self.__id = id
        self.__cert_public = cert_public
        self.__cert_finance = cert_finance
        self.__driver = driver
        self.__name = name
        self.__phone = phone
        self.__birth = birth
        
        selenium = s.Context(driver, timeout=20, differ=0)
        win32 = w.Context(timeout=50, differ=0)
        am.Automatic.__init__(self, [selenium, win32])

    def login(self):

        # Step: 홈페이지로 이동
        logger.info("로그인")

        logger.info("홈페이지로 이동")
        self.go(s.Url("G2B 홈페이지", 'https://www.g2b.go.kr'))

        # 팝업이 와전히 생성될 때까지 기다린다.
        time.sleep(5)
        
        logger.info("팝업닫기")
        popup_close_btn = s.Xpath("팝업닫기", "//input[@title='오늘 하루 이 창을 열지 않음']", multiple=True, visible=False, differ=2)
        if self.exist(popup_close_btn):
            self.clicks(popup_close_btn)

        logger.info("로그인")
        logout_btn = s.Xpath("로그아웃버튼", "//span[text()='로그아웃']/../a", differ=5, timeout=5, clickable=True)
        if self.exist(logout_btn):
            logger.info("이미 로그인 되었습니다.")
            return True 

        login_btn = s.Id("로그인버튼", 'mf_wfm_gnb_wfm_gnbTop_btnLogin')
        self.clicks(login_btn) 

        id_pw_tab = s.Xpath("아이디/암호 탭", "//a[text()='아이디/비밀번호']")
        self.click(id_pw_tab)

        id_input = s.Id("아이디입력상자", 'mf_wfm_container_tabLgn_contents_content4_body_ibxLgnId')
        self.type(id_input, self.__id)

        pw_input = s.Id("암호입력상자", 'mf_wfm_container_tabLgn_contents_content4_body_ibxLgnPswd')
        self.type(pw_input, self.__pw)

        login_btn = s.Id("로그인확인버튼", 'mf_wfm_container_tabLgn_contents_content4_body_btnLgn')
        self.click(login_btn)
        
        logger.info("팝업닫기")
        # 다른세션에 로그인 되어 있다는 팝업이 뜰 수 있음. 
        session_login_popup = s.Xpath("팝업확인", "//input[@value='예']")
        if self.exist(session_login_popup):
            self.click(session_login_popup)

        # 팝업들 열림 
        # TODO: 각 popup 들의 scroll이 맨 아래로 내려가 있어야 함.
        popup_close_btn = s.Xpath("팝업닫기", "//input[@title='오늘 하루 이 창을 열지 않음']",multiple=True, visible=False, differ=1)
        if self.exist(popup_close_btn):
            self.clicks(popup_close_btn)

        return True



    def __register(self, code):
        try:
            logger.info("입찰 참가 페이지로 이동")
            self.go(s.Url("G2B 홈페이지", 'https://www.g2b.go.kr'))

            user_management_btn = s.Xpath("이용자관리 버튼","//a[contains(@class, 'btn') and span[text()='이용자관리']]", clickable=False)
            self.click(user_management_btn)

            self_info_check_management_btn = s.Xpath("자기정보확인관리 버튼", "//a[contains(@class, 'btn') and span[text()='자기정보확인관리/등록증출력']]", differ=5)
            self.click(self_info_check_management_btn)

            supplied_items_btn = s.Xpath("공급물품 버튼", "//a[text()='공급물품']", visible=False, differ=5)
            self.click(supplied_items_btn)

            # table 로 변경 되면서 한 페이지에 모든 데이터가 보이지 않는다. table 을 사용해도 전체 데이터가 보이지 않음. 
            # 따라서 사전 검증을 하지 않는 것으로 한다. 
            # detail_item_number_text = s.Xpath("세부품목번호",f"//nobr[text()='{code}']", clickable=False, visible=False )
            # if self.exist(detail_item_number_text):
            #     print("이미등록 되어 있습니다.")
            #     return True

            modification_btn = s.Xpath("수정버튼", "//input[@value='수정(자기정보확인)']", timeout=5)
            if self.exist(modification_btn):
                self.click(modification_btn)

            # 주의: 대표물품이 설정 되어 있어야 한다. 
            add_row_btn = s.Xpath("행추가버튼", "//input[@value='행추가' and contains(@class, 'inline_block')]")
            self.click(add_row_btn)

            confirm_btn =  s.Xpath("확인버튼", "//input[@value='예']")
            self.click(confirm_btn)

            detailed_item_number_input = s.Xpath("세부품명번호 입력", "//td[@data-title='세부품명번호']/div/input")
            self.type(detailed_item_number_input, code)

            search_btn = s.Xpath("검색버튼", "//input[@value='검색' and contains(@class, 'btn')]")
            self.click(search_btn)

            detailed_item_number_btn = s.Xpath("세부품명번호 버튼", f"//a[text()='{code}']")
            self.click(detailed_item_number_btn)

            close_btn = s.Xpath("닫기버튼", "//input[@value='닫기' and contains(@class, 'btn_cm') and contains(@class, 'close') and not(@aria-hidden)]")
            self.click(close_btn)

            # 자기정보수정 저장
            save_btn = s.Xpath("저장버튼튼","//input[@title='자기정보수정 저장']")
            self.click(save_btn)

            confirm_btn = s.Xpath("확인버튼", "//input[@value='확인']")
            self.click(confirm_btn)
            return True
        
        except Exception as e:
            logger.error(e)
            return False

    def register(self, code):
        codes = code.split(",")
        codes = [pn.strip() for pn in codes]
        logger.info(f"사전등록: {codes}")
        for code in codes:
            if not self.__register(code):
                return False
        return True

        

    def participate(self, code, price):
        # 소수점이 있을 경우 입력이 불가하다고 안내한다. 
        price = int(float(price))

        try:
            logger.info("입찰 참가 페이지로 이동")
            self.go(s.Url("G2B 홈페이지", 'https://www.g2b.go.kr'))
            
            bid_btn = s.Xpath("입찰 버튼","//a[contains(@class, 'btn') and span[text()='입찰']]")
            self.click(bid_btn)

            # 입찰공고목록 버튼이 두 개 존재하기 때문에 둘중 하나를 클릭해야 한다. 
            bid_notice_list = s.Xpath("입찰공고목록 버튼", "//a[contains(@class, 'btn') and span[text()='입찰공고목록']]", visible=False, multiple=True, differ=3)
            self.clicks(bid_notice_list, num_samples=1)

            bid_notice_number_btn = s.Xpath("입찰공고번호 입력", "//input[@title='입찰공고번호']")
            self.type(bid_notice_number_btn, code)

            search_btn = s.Xpath("검색버튼", "//input[@value='검색']")
            self.click(search_btn)
            
            participate_process_btn = s.Xpath("입찰진행 버튼", "//button[text()='입찰진행']", visible=False, differ=1)
            self.click(participate_process_btn)

            if self.exist(s.Xpath("완료 버튼","//button[text()='완 료']", visible=False, differ=1, timeout=10)):
                logger.info("이미 완료되었습니다.")
                return True

            participate_btn = s.Xpath("투찰 버튼","//button[text()='투 찰']", visible=False, differ=1)
            self.click(participate_btn)

            # 인증
            logger.info("금융인증")
            certi_btn = s.Xpath("금융인증서", "//span[text()='금융인증서']/..",timeout=5)
            if self.exist(certi_btn):
                self.click(certi_btn)

                agree = s.Xpath("개인정보 이용동의", "//input[@title='개인정보 이용에 동의합니다.']")
                self.click(agree)

                request = s.Xpath("본인확인요청","//input[@value='본인확인요청']", differ=5)
                self.click(request)

                # 필요하다면 한번 더 클릭 요청 
                request = s.Xpath("본인확인요청","//input[@value='본인확인요청']", differ=5)
                if self.exist(request):
                    self.click(request)

                # 금융인증서
                time.sleep(5)
                cert_srv_frame = s.Id("금융인증서비스 개인", "finCertSdkIframe")
                need_wait = False
                if self.exist(s.Id("전화번호","CLOUD_ID_2",parent=cert_srv_frame)):
                    screenshot_path = os.path.join(os.path.expanduser("~"), ".iaa", "log", "cert_error.png")
                    self.__driver.save_screenshot(screenshot_path)
                    logger.info("첫 번째 접속으로 금융인증서 셋업을 위한 사용자 액션이 필요합니다. 2분안에 작업을 완료하세요.")
                    self.type(s.Id("이름","CLOUD_ID_1",parent=cert_srv_frame), self.__name)
                    self.type(s.Id("전화번호","CLOUD_ID_2",parent=cert_srv_frame), self.__phone)
                    self.type(s.Id("생년월일","CLOUD_ID_3",parent=cert_srv_frame), self.__birth)
                    self.click(s.Xpath("자동로그인","//span[text()='자동로그인']",parent=cert_srv_frame))
                    self.click(s.Xpath("문자인증", "//button[@title='휴대폰 문자인증']",parent=cert_srv_frame))
                    cert_code = self.text(s.Xpath("코드값", "//div[@class='code_confirm_number']",parent=cert_srv_frame))
                    logger.info(f"코드값: {cert_code}")
                    need_wait = True

                logger.info("금융인증서 로그인 시작")
                cert = s.Xpath("금융인증서", "//button[text()='인증이력']/..", parent=cert_srv_frame, timeout= 5 if not need_wait else 120)
                self.click(cert)
                def cert_password(pw):
                    for digit in pw:
                        cert = s.Xpath("금융인증서", f"//img[@aria-label='{digit}']", parent=cert_srv_frame,)
                        self.click(cert)

                cert_password(self.__cert_finance)

            logger.info("투찰 시작")
            # 가격 입찰서 작성(투찰)하러 가기
            # 버튼이 위/아래 두 개 존재하기 때문에 둘중 하나를 클릭해야 한다. 
            btn = s.Xpath("가격 입찰서 작성(투찰)하러 가기", "//input[@value='가격 입찰서 작성(투찰)하러 가기']", multiple=True)
            self.clicks(btn, num_samples=1)

            company_info_agree = s.Xpath("기업정보제공동의", "//input[@title='기업정보 제공에 동의합니다.']", visible=False)
            self.click(company_info_agree)

            pbadms_info_agree = s.Xpath("행정정보 공동이용 동의", "//input[@title='행정정보 공동이용에 동의합니다.']", visible=False)
            self.click(pbadms_info_agree)

            all_info_agree = s.Xpath("위 사항 동의의", "//input[@title='위 사항을 모두 이해 하였으며, 이에 동의합니다.']", visible=False)
            self.click(all_info_agree)

            confirm_btn = s.Xpath("투찰하러 가기 확인", "//input[@value='확인']")
            self.click(confirm_btn)

            agree = s.Xpath("투찰금액 동의", "//input[@title='위 투찰금액 결정 관련 유의사항을 숙지하고, 이에 동의합니다.']") 
            self.click(agree)

            # 알림 메세지가 있을 수 있음. - 본 사업은 면세사업으로....
            confirm_btn = s.Xpath('확인 버튼', "//input[@value='확인']", timeout=5)
            if self.exist(confirm_btn):
                self.click(confirm_btn)

            cost_input = s.Xpath("총액", "//input[@title='총액']") 
            self.type(cost_input, price)

            aggree = s.Xpath("청렴계약 동의", "//input[@title='청렴계약서 및 입찰관련 유의사항들을 숙지하였으며, 이에 동의합니다.']", visible=False)
            self.click(aggree)

            transfer_btn = s.Xpath("송신 버튼", "//input[@value='송신']", visible=False)
            self.click(transfer_btn)

            confirm_btn = s.Xpath('확인 버튼', "//input[@value='확인']", differ=5)
            self.click(confirm_btn)

            aggree = s.Xpath("동의", "//input[@title='위 사항을 모두 확인하였으며, 이에 동의합니다.']")
            self.click(aggree)

            confirm_btn = s.Xpath('확인 버튼', "//input[@value='확인']")
            self.click(confirm_btn)

            lottery_check_box = s.Xpath("체크박스", "//div[@class='w2group ltt_con']/ul/li/input")
            self.clicks(lottery_check_box, num_samples=2)

            transfer_lottery_num_btn = s.Xpath("추첨번호 전송", "//input[@value='추첨번호 전송']")
            self.click(transfer_lottery_num_btn)

            yes_btn = s.Xpath("예 버튼", "//input[@value='예']")
            self.click(yes_btn)

            logger.info("공동인증 시작")
            # 이전에 사용한 공동인증을 다시 사용할 것인지 확인
            popup = s.Xpath("팝업", "//div[contains(text(),'선택한 공동인증서를 계속 사용')]", differ=3, timeout=3)
            if self.exist(popup):
                self.click(yes_btn) 
                confirm_btn = s.Xpath("확인 버튼", "//input[@value='확인']", differ=3)
                self.click(confirm_btn)
            else:
                auth_btn = s.Xpath("공동인증 버튼", "//input[@value='공동인증']")
                self.click(auth_btn)
                # 복수 ID에 대한 경고
                confirm_btn = s.Xpath("확인 버튼", "//input[@value='확인']", differ=3)
                self.click(confirm_btn)

                frame = s.Id("인증서 프레임", "dscert")
                cert_pw_input = s.Id("패스워드입력성자 ", "input_cert_pw", parent=frame, differ=10)
                self.type(cert_pw_input, self.__cert_public)

                btn = s.Id("확인버튼", "btn_confirm_iframe", parent=frame, differ=3)
                self.click(btn)

            confirm_btn = s.Xpath("확인", "//input[@value='확인']", differ=3)
            self.click(confirm_btn)

            btn = s.Xpath("종료버튼", "//input[@value='종료']")
            self.click(btn)
            return True

        except Exception as e:
            logger.error(e)
            return False
