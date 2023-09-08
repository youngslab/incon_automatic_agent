

import os
from automatic import browser
from automatic import win32
import pyautogui


def wait_user_input():
    pyautogui.alert("확인 버튼을 눌러 다음으로 넘어가세요", title="Incon Agent")
    return True


class Kogas:
    def __init__(self, driver, manager_name, manager_phone, manager_email, small_business):
        self.name = "가스공사"
        self.manager_name = manager_name
        self.manager_phone = manager_phone
        self.manager_email = manager_email
        self.small_business = small_business

        self.context = browser.Context(
            driver, "https://bid.kogas.or.kr:9443/supplier/index.jsp", default_timeout=30)

        self.win32_ctx = win32.Context()

        # windows & alert
        self.kogas_main_window_popup = browser.Alert(
            self.context)

        self.kogas_amount_check_window = browser.Window(
            self.context, url="bid_detail_write_bid_popup.jsp")

        self.kogas_amount_check_window_popup = browser.Alert(
            self.context, parent=self.kogas_amount_check_window)

        # 입찰보증금 지급각서
        self.kogas_deposit_payment_window = browser.Window(
            self.context, title="한국가스공사 전자조달시스템")

        self.kogas_deposit_payment_window_popup = browser.Alert(
            self.context, parent=self.kogas_deposit_payment_window)

        # frames
        self.kogas_body_frame = browser.Frame(
            self.context, desc="홈페이지 내 body frame", by="xpath", path="//frame[@src='/supplier/bodyframe.jsp']")

        self.kogas_body_left_frame = browser.Frame(
            self.context, desc="body frame 내 left frame", by="xpath", path="//frame[@src='/supplier/left.jsp']", parent=self.kogas_body_frame)

        self.kogas_body_body_frame = browser.Frame(
            self.context, desc="body frame 내 body frame", by="xpath", path="//frame[@src='/supplier/body.jsp']", parent=self.kogas_body_frame)

        self.kogas_top_frame = browser.Frame(
            self.context, desc="홈페이지 내 top frame", by="xpath", path="//frame[@src='/supplier/top.jsp']")

        # --------------------
        # elements
        # --------------------

        self.kogas_login_cert_login_button = browser.ClickableElement(
            self.context, desc="공동인증서로그인 버튼", by="xpath", path="//img[@alt='공동인증서로그인']")

        self.kogas_login_cert_fp_security_token_button = browser.ClickableElement(
            self.context, desc="지문보안토큰 선택 버튼", by="id", path="NX_MEDIA_BIOHSM")

        self.kogas_login_cert_fp_security_token_bio_seal_button = browser.ClickableElement(
            self.context, desc="BIO-SEAL 보안 토큰 버튼", by="id", path="(주)유니온커뮤니티 BIO-SEAL|FP_HSM.dll|1.0.2.1|설치")

        self.kogas_login_cert_fp_security_token_confirm_button = browser.ClickableElement(
            self.context, desc="보안 토큰 선택 확인 버튼", by="xpath", path="//*[@id='pki-extra-media-box-contents3']/div[3]/button[1]")

        self.kogas_login_pin_number_input_textbox = browser.TypeableElement(
            self.context, desc="핀 번호 입력 텍스트박스", by="id", path="nx_cert_pin")

        self.kogas_login_pin_number_confirm_button = browser.ClickableElement(
            self.context, desc="핀 번호 입력 확인 버튼", by="xpath", path="//*[@id='pki-extra-media-box-contents3']/div[2]/button[1]")

        self.kogas_login_cert_confirm_button = browser.ClickableElement(
            self.context, desc="인증서 선택 확인 버튼", by="xpath", path="//*[@id='nx-cert-select']/div[4]/button[1]")

        self.kogas_login_logout_button = browser.Element(
            self.context, desc="로그아웃 버튼", by="xpath", path="//img[@alt='로그아웃']", parent=self.kogas_body_left_frame)

        # --------------------

        self.kogas_register_ebidding_button = browser.ClickableElement(
            self.context, desc="전자 입찰 버튼", by="id", path="tm_01", parent=self.kogas_top_frame)

        self.kogas_register_bid_number_input = browser.TypeableElement(
            self.context, desc="입찰번호 입력 박스", by="xpath", path="//input[@title='입찰번호']", parent=self.kogas_body_body_frame)

        self.kogas_register_search_button = browser.ClickableElement(
            self.context, desc="검색 버튼", by="xpath", path="//img[@alt='검색']", parent=self.kogas_body_body_frame)

        self.kogas_register_first_element_text = browser.TextableElement(
            self.context, desc="첫번 째 검색 결과 입찰 번호", by="xpath", path="//td[text()='입찰번호']/../../tr[2]/td[1]/a", parent=self.kogas_body_body_frame)

        self.kogas_register_first_element_button = browser.ClickableElement(
            self.context, desc="첫번 째 검색 결과 선택 버튼", by="xpath", path="//tbody/tr[2]/td[2]/a/span", parent=self.kogas_body_body_frame)

        # --------------------------------------

        self.kogas_register_bidding_application_tab = browser.ClickableElement(
            self.context, desc="입찰 참가 신청 탭", by="xpath", path="//a[text()='입찰참가신청']", parent=self.kogas_body_body_frame)

        self.kogas_register_manager_name = browser.TypeableElement(
            self.context, desc="입찰당당자 이름", by="xpath", path="//input[@name='ca_name']", parent=self.kogas_body_body_frame)

        self.kogas_register_manager_phone = browser.TypeableElement(
            self.context, desc="입찰당당자 전화번호", by="xpath", path="//input[@name='ca_tel']", parent=self.kogas_body_body_frame)

        self.kogas_register_manager_email = browser.TypeableElement(
            self.context, desc="입찰당당자 email", by="xpath", path="//input[@name='ca_email']", parent=self.kogas_body_body_frame)

        self.kogas_register_application_aggreement_1_button = browser.ClickableElement(
            self.context, desc="입찰참가신청 동의 버튼(1)", by="xpath", path="//*[@id='registpanel']/table[17]/tbody/tr/td/a[1]/img", parent=self.kogas_body_body_frame)

        self.kogas_register_application_aggreement_2_button = browser.ClickableElement(
            self.context, desc="입찰참가신청 동의 버튼(2)", by="xpath", path="//*[@id='registpanel']/table[2]/tbody/tr[9]/td[3]/a/img", parent=self.kogas_body_body_frame)

        # ---------------------------------------

        self.kogas_register_deposit_payment_agreement_button = browser.ClickableElement(
            self.context, desc="입찰보증금 지급각서 동의 버튼", by="xpath", path="//img[@alt='동의']", parent=self.kogas_deposit_payment_window)

        # ----------------------------------------
        self.kogas_register_attach_file_button = browser.ClickableElement(
            self.context, desc="파일 첨부 버튼", by="name", path="FILENAME", parent=self.kogas_body_body_frame)

        # --------------------------------------

        self.file_chooser_edit_box = win32.ControlElement(
            self.win32_ctx, "[TITLE:열기; CLASS:#32770]", "Edit1")

        self.file_chooser_ok_button = win32.ControlElement(
            self.win32_ctx, "[TITLE:열기; CLASS:#32770]", "Button1")

        # --------------------------------------
        self.kogas_register_submit_button = browser.ClickableElement(
            self.context, desc="제출 버튼", by="xpath", path="//img[@alt='제출']", parent=self.kogas_body_body_frame)

        self.__init_par_elements()

    def init(self):
        self.__init_par_elements()

    def __init_par_elements(self):
        self.kogas_par_already_done_text = browser.Element(
            self.context, desc="참여 완료 텍스트박스", by="xpath", path="//*[contains(text()[2], '투찰하였습니다.')]", parent=self.kogas_body_body_frame)

        self.kogas_par_confirm_check_button = browser.ClickableElement(
            self.context, desc="확인후체크", by="name", path="vat_ck_box", parent=self.kogas_body_body_frame)

        self.kogas_par_multiple_reserve_check_boxes = browser.ClickableElements(
            self.context, desc="복수예비가 체크버튼", by="name", path="choice", parent=self.kogas_body_body_frame)

        self.kogas_par_enter_amount_input = browser.TypeableElement(
            self.context, desc="입찰금액 입력", by="name", path="tot_amt", parent=self.kogas_body_body_frame)

        self.kogas_par_submit_application = browser.ClickableElement(
            self.context, desc="입찰서제출 버튼", by="xpath", path="//img[@alt='입찰서제출']", parent=self.kogas_body_body_frame)

        # 안내 내용 확인
        self.kogas_par_confirm_guidance = browser.ClickableElement(
            self.context, desc="안내내용 확인", by="name", path="info_ck_box", parent=self.kogas_body_body_frame)

        # 견적서제출 버튼
        self.kogas_par_submit_estimate = browser.ClickableElement(
            self.context, desc="견적서제출 버튼", by="xpath", path="//img[@alt='견적서제출']", parent=self.kogas_body_body_frame)

        self.kogas_par_2nd_amount_input = browser.TypeableElement(
            self.context, desc="입찰금액 재 입력", by="name", path="confirm_tot_amt", parent=self.kogas_amount_check_window)

        self.kogas_par_2nd_submit_button = browser.ClickableElement(
            self.context, desc="제출 버튼", by="xpath", path="//img[@alt='제출']", parent=self.kogas_amount_check_window)

        self.kogas_par_cert_fp_security_token_button = browser.ClickableElement(
            self.context, desc="지문보안토큰 버튼", by="id", path="NX_MEDIA_BIOHSM", parent=self.kogas_amount_check_window)

        self.kogas_par_cert_fp_security_token_bio_seal_button = browser.ClickableElement(
            self.context, desc="BIO SEAL 토큰 선택", by="id", path="(주)유니온커뮤니티 BIO-SEAL|FP_HSM.dll|1.0.2.1|설치", parent=self.kogas_amount_check_window)

        self.kogas_par_cert_fp_security_token_confirm_button = browser.ClickableElement(
            self.context, desc="지문보안토큰 확인 버튼", by="xpath", path="//button[@onclick='NX_Issue_pubUi.moreSaveMediaHide2();return false;']", parent=self.kogas_amount_check_window)

        self.kogas_par_cert_pin_number_input = browser.TypeableElement(
            self.context, desc="핀번호입력 박스", by="id", path="nx_cert_pin", parent=self.kogas_amount_check_window)

        self.kogas_par_cert_pin_number_confirm_button = browser.ClickableElement(
            self.context, desc="핀번호 확인 버튼", by="xpath", path="//button[@onclick='NX_Issue_pubUi.moreSaveMediaHide7();return false;']", parent=self.kogas_amount_check_window)

        self.kogas_par_cert_confirm_button = browser.ClickableElement(
            self.context, desc="인증 확인 버튼", by="xpath", path="//button[@onclick='NX_Issue_pubUi.selectCertConfirm();']", parent=self.kogas_amount_check_window)

    def login(self):
        if not (self.kogas_login_cert_login_button.click()
                and self.kogas_login_cert_fp_security_token_button.click()
                and self.kogas_login_cert_fp_security_token_bio_seal_button.click()
                and self.kogas_login_cert_fp_security_token_confirm_button.click()
                and wait_user_input()
                and self.kogas_login_pin_number_input_textbox.type("00000000", timeout=120)
                and self.kogas_login_pin_number_confirm_button.click()
                and self.kogas_login_cert_confirm_button.click()
                and self.kogas_login_logout_button.exist()):  # logout button 이 있어야 합니다.
            print("ERROR: 로그인에 실패하였습니다.")
            return False

        return True

    def __go_detail_page(self, code):
        # Go to the detail page.
        return self.kogas_register_ebidding_button.click() \
            and self.kogas_register_bid_number_input.type(code, timeout=5) \
            and self.kogas_register_search_button.click() \
            and self.kogas_register_first_element_text.text() == code \
            and self.kogas_register_first_element_button.click()

    def __register(self, code, manager_name, manager_phone, manager_email, small_business):
        # move to the page to register
        self.context.set_url("https://bid.kogas.or.kr:9443/supplier/index.jsp")

        # close another windows
        self.context.close_other_windows()

        # normalize the bid's code
        code = code.split('-')[0]

        # Go to the detail page.
        if not self.__go_detail_page(code):
            print(f"ERROR: Failed to go to the detail page. {code}")
            return False

        if not self.kogas_register_bidding_application_tab.click(timeout=3):
            print(f"INFO: 이미등록 되어있습니다.")
            return True

        if not (self.kogas_register_manager_name.type(manager_name)
                and self.kogas_register_manager_phone.type(manager_phone)
                and self.kogas_register_manager_email.type(manager_email)):
            print(f"ERROR: 입찰당당자 입력에 실패하였습니다.")
            return False

        if not (self.kogas_register_application_aggreement_1_button.click()
                and self.kogas_main_window_popup.accept("약관에 동의하시겠습니까?")
                and self.kogas_register_application_aggreement_2_button.click()):
            print(f"ERROR: 입찰참가 신청 동의에 실패하였습니다.")
            return False

        # 입찰 보증금 지급각서
        if not (self.kogas_register_deposit_payment_agreement_button.click()
                and self.kogas_deposit_payment_window_popup.accept("동의 하시겠습니까?")):
            print(f"ERROR: 입찰 보증금 지급각서 동의에 실패하였습니다.")
            return False

        # 중소기업 확인서 파일 첨부
        if self.kogas_register_attach_file_button.click() \
                and self.kogas_main_window_popup.accept("", timeout=3, ignore=True) \
                and self.file_chooser_edit_box.type(small_business) \
                and self.file_chooser_ok_button.click(differed=3):
            print(f"ERROR: 중소기업 확인서 파일 첨부 실패하였습니다.")
            return False

        if self.kogas_register_submit_button.click(differed=3) \
                and self.kogas_main_window_popup.accept("제출하시겠습니까?"):
            print(f"ERROR: 사전등록 제출에 실패하였습니다.")
            return False

        return True

    def register(self, code):
        return self.__register(code, self.manager_name,
                               self.manager_phone, self.manager_email, self.small_business)

    def participate(self, code, price):
        self.context.set_url("https://bid.kogas.or.kr:9443/supplier/index.jsp")

        # close another windows
        self.context.close_other_windows()

        # normalize the bid's code
        code = code.split('-')[0]

        # Go to the detail page.
        print(f"INFO: 상세 페이지로 이동")
        if not self.__go_detail_page(code):
            print(f"ERROR: 상세 페이지로 이동에 실패하였습니다. {code}")
            return False

        # validateR
        if self.kogas_par_already_done_text.exist(timeout=3):
            print(f"INFO: 이미 참여 완료하였습니다.")
            return True

        print(f"INFO: 입찰 금액 입력")
        # 입찰서 제출
        if self.kogas_par_submit_application.exist(timeout=3):
            if not (self.kogas_par_confirm_check_button.click()
                    and self.kogas_par_multiple_reserve_check_boxes.click(num_elements=4)
                    and self.kogas_par_enter_amount_input.type(price)
                    and self.kogas_par_submit_application.click()):
                print(f"ERROR: 입찰 금액 입력에 실패하였습니다. code:{code}, price:{price}")
                return False
        else:  # 견적서 제출
            if not (self.kogas_par_confirm_guidance.click()
                    and self.kogas_par_confirm_check_button.click()
                    and self.kogas_par_multiple_reserve_check_boxes.click(num_elements=4)
                    and self.kogas_par_enter_amount_input.type(price)
                    and self.kogas_par_submit_estimate.click()):
                print(f"ERROR: 입찰 금액 입력에 실패하였습니다. code:{code}, price:{price}")
                return False

        print(f"INFO: 입찰 금액 재확인.")
        if not (self.kogas_par_2nd_amount_input.type(price, force=True)
                and self.kogas_par_2nd_submit_button.click()
                and self.kogas_amount_check_window_popup.accept("제출하시겠습니까?")
                and self.kogas_par_cert_fp_security_token_button.click()
                and self.kogas_par_cert_fp_security_token_bio_seal_button.click()
                and self.kogas_par_cert_fp_security_token_confirm_button.click()
                and self.kogas_par_cert_pin_number_input.type("00000000", timeout=120)
                and self.kogas_par_cert_pin_number_confirm_button.click()
                and self.kogas_par_cert_confirm_button.click()
                and self.kogas_amount_check_window_popup.accept("완료되었습니다.")):
            print(
                f"ERROR: 입찰 금액 재확인 과정을 마칠 수 없습니다. code:{code}, price:{price}")
            return False

        return True
