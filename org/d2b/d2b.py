
import random
import time
import logging
from integ_auto import *

#########
# HELPER
#########


def log():
    return logging.getLogger(__package__)


###########
# Utilities
###########
def _is_login(auto: Automatic):
    # Logout button 이 있으면 login된 상태
    logout_btn = auto.get_element(By.ID, '_logoutBtn', timeout=3)
    return True if logout_btn else False

# ID: D2B - 서약서동의(2)


def _agree_oath_2(auto: Automatic):

    # - 조세포탈 없음을 확약하는 서약서
    # - 청렴 계약 이행 서약서
    # - 행정정보 공동이용 사전동의서
    # - etc:  경우에 따라 추가 되는 경우가 있다. 

    checkboxes = auto.get_elements(By.XPATH, '//input[@type="checkbox" and @name="a1"]')
    if not checkboxes:
        return False
    
    for checkbox in checkboxes:
        auto.click(checkbox)
        time.sleep(0.5)

    # 확인 버튼
    if not auto.click(By.ID, 'btn_oath_confirm'):
        return False

    return True


def _go_bid_detail_page(auto: Automatic, number):
    # move to the page to register
    auto.go('https://www.d2b.go.kr/index.do')

    # Bid Number 입력
    if not auto.type(By.ID, "numb_divs", number):
        return False

    # 검색버튼
    if not auto.click(By.ID, 'btn_search'):
        return False

    # XXX: Check auto.click and element.click
    # 검색된 결과 중 첫번째 element를 선택한다.
    if not auto.click(
            By.XPATH, '//*[@id="SBHE_DATAGRID_WHOLE_TBODY_datagrid1"]/tr[2]/td[8]/div/span/a'):
        log().error(f"Failed to search bid item. number={number}")
        return False

    return True


# ID: D2B - 견적서 작성(w/o 참가신청)
# Precondition: 견적서작성 페이지여야 한다.
def _write_estimate(auto: Automatic, cost) -> bool:
    # 1. 견적금액 작성
    if not auto.type(By.ID, "input_amount", cost):
        log().error("Failed to find 견적금액 input")
        return False

    # 2. 복수예비가격 선택: 2개
    check_boxes = auto.get_elements(
        By.XPATH, '//input[@name="check_multi_price"]')
    check_boxes = random.choices(check_boxes, k=2)
    for box in check_boxes:
        print(box)
        auto.click(box)

    time.sleep(3)

    # 3. 제출 버튼 click
    if not auto.click(By.ID, "btn_submit"):
        log().error("Failed to find 제출 button")
        return False

    # 4. 견적서 제출 확인 popup
    if not auto.accept_alert():
        log().error("Failed to find 제출 확인 메세지")
        return False

    return True


def _need_registration(auto: Automatic, number) -> bool:
    # 1. 상세 페이지로 이동
    _go_bid_detail_page(auto, number)

    # 2. "견적서작성" vs. "입찰참가신청" 버튼
    # 견적서작성 버튼이 있으면 입찰참가가 필요 없다.
    btn = auto.get_element(
        By.XPATH, '//button[@id="btn_estimate_write"]', timeout=5)
    return True if not btn else False

# ID: D2B - 입찰참가 불필요건에 대한 견적서 작성
# Condition: 입찰건 detail page에서 "견적서작성" 버튼이 있어야 한다.


def _participate_without_registration(auto: Automatic, number, cost) -> bool:

    # 1. 아이템을 검색한다.
    _go_bid_detail_page(auto, number)

    # 2. 견적서 작성 버튼을 찾는다.
    if not auto.click(
            By.XPATH, '//button[@id="btn_estimate_write"]', timeout=5):
        log().error("Failed to find 견적서작성 button.")
        return False

    # 3. 서약서 작성
    if not _agree_oath_2(auto):
        log().error("Failed to write oath(2).")
        return False

    # 4. 견적서 작성
    if not _write_estimate(auto, cost):
        log().error("Failed to write estimate.")
        return False

    # 5. 견적서 제출 확인 - 견적서를 성공적으로 제출하였습니다.
    if not auto.accept_alert():
        log().error("견적서 제출 확인 - 견적서를 성공적으로 제출하였습니다.")

    return True


# ID: D2b - 입찰(참가신청) - 참가가능 검증
# number form example: "MDR0033-1", "UMM0424-1", "UMM0483-1"
def _can_participate(auto: Automatic, number):
    # TODO: Is there better way?
    x = auto.get_element(By.XPATH, '//a[text()="물품"]/../div')
    auto.execute_script(
        "arguments[0].setAttribute('style',arguments[1])", x, "display: block;")

    auto.click(By.XPATH, '//a[text()="입찰"]')
    auto.click(By.XPATH, '//h5/a[text()="참가신청서 조회"]')

    notices = auto.get_elements(
        By.XPATH, '//tbody[@id="SBHE_DATAGRID_WHOLE_TBODY_datagrid1"]/tr')
    notices = notices[1:]

    for notice in notices:
        if not notice or notice.find_element(By.XPATH, './/td[2]/div/span').text.find(number) < 0:
            continue

        status = notice.find_element(By.XPATH, './/td[7]/div/span').text
        if status.find("투찰가능") < 0:
            log().error(
                f"Can not participate. number={number}, status={status}")
            return False

        return True

    log().error(f"Can not find notice. number={number}")
    return False


def _write_bid(auto: Automatic, cost):
    # 1. cost 입력
    auto.type(By.ID, "bid_amnt_1", cost)

    # 2. 추첨 checkbox 선택(2개)
    boxes = auto.get_elements(By.XPATH, '//td/input[@type="checkbox"]')
    if len(boxes) != 15:
        log().error(f"Can not find all 추첨확인 checkbox.len={len(boxes)}")
        return False
    boxes = random.sample(boxes, 2)
    for box in boxes:
        auto.click(box)

    if not auto.click(By.ID, "c_box"):
        log().error(f"Can not find 동의 checkbox.")
        return False

    return True


def _sumbit_bid(auto: Automatic):
    if not auto.click(By.ID, "btn_bid_submit"):
        log().error(f"Can not find 제출 버튼.")
        return False

    if not auto.accept_alert():
        log().error(f"Failed to accept alert(1).")
        return False

    if not auto.accept_alert():
        log().error(f"Failed to accept alert(2).")
        return False

    return True

# Precondition:
#  - 입찰서제출 및 조회(경쟁입찰) 페이지 내에서 실행 되어야 한다.
# WARNING: number format is different


def _choose_bid_in_list(auto: Automatic, number):
    # 공고번호 선택
    notices = auto.get_elements(
        By.XPATH, '//tbody[@id="SBHE_DATAGRID_WHOLE_TBODY_datagrid1"]/tr')
    notice = next(filter(lambda x: x.find_element(
        By.XPATH, ".//td[1]/div").text.find(number) >= 0, notices[1:]), None)
    if not notice:
        print(f"Can not find the bid. number={number}")
        return False
    notice.click()

    # validate - Selected?
    if notice.find_element(By.XPATH, './/td[1]').get_attribute("sbgrid_select") != "true":
        log().error(f"Can not find the bid. number={number}")
        return False

    # validate - can participate?
    status = notice.find_element(By.XPATH, './/td[6]/div/span').text
    if status != "미제출":
        log().error(
            f"Fail to verify its status. number= {number}, status={status}")
        return False

    return True


# ID: D2b - 입찰(참가신청) - 입찰서 작성 페이지 이동


def _go_to_bid_write_page(auto: Automatic, number):
    # ID: D2b - 입찰(참가신청) - 입찰서 작성 페이지이동
    # 페이지 이동
    if not auto.click(By.XPATH, '//h5/a[text()="입찰서제출 및 조회(경쟁입찰)"]'):
        log().error(f"Failed to find 입찰서제출 및 조회(경쟁입찰) button")
        return False

    # 페이지내 관련 공고 선택
    if not _choose_bid_in_list(auto, number):
        log().error(f"Failed to go to the bid page")
        return False

    # 입찰서 작성 버튼 클릭
    if not auto.click(By.ID, 'btn_bid_regi'):
        log().error(f"Failed to find 입찰서 작성 button")
        return False

    return True


def _participate_with_registration(auto: Automatic, number, cost):
    # validate it's ready
    # WARNING: number format is different
    # ID: D2b - 입찰(참가신청) - 참가가능 검증
    if not _can_participate(auto, number):
        log().error(
            f"Failed to validate the bid. number={number}, cost={cost}")
        return False

    # ID: D2b - 입찰(참가신청) - 입찰서 작성 페이지 이동
    if not _go_to_bid_write_page(auto, number):
        log().error(f". number={number}, cost={cost}")
        return False

    # ID: D2b - 입찰(참가신청) - 입찰서 작성

    # 입찰서 작성
    if not _write_bid(auto, cost):
        log().error(
            f"Failed to write a bid form. number={number}, cost={cost}")
        return False

    # 입찰서 제출
    if not _sumbit_bid(auto):
        log().error(f"Failed to submit a bid. number={number}, cost={cost}")
        return False

    return True


def _login_cert(auto: Automatic, user, cert_pw):
    # Certificate
    # 1. HDD선택
    auto.click(By.ID, "NX_MEDIA_HDD")

    # 2. 사업자 인증서 선택
    auto.click(By.XPATH,
               f'//*[@id="NXcertList"]/tr/td[2]/div[text()="{user}"]')

    # XXX: 인증서 선택과정이 아래 type의 결과를 reset한다.
    #      따라서 충분한 간격을 준다.
    time.sleep(3)

    # 3. password
    auto.type(By.ID, "certPwd", cert_pw)

    # 4. ok button
    auto.click(By.XPATH, '//*[@id="nx-cert-select"]/div[4]/button[1]')


# INTERFACE

def login(auto: Automatic, token='BIO-SEAL') -> bool:
    auto.go("https://www.d2b.go.kr/index.do")

    if _is_login(auto):
        return True

    # login button
    auto.click(By.ID, "_mLogin")

    # XXX: 너무 빨리 click이 되면 문제가 발생한다.
    #       인증 프로그램 실행 준비가 안되었습니다. 설치가 안된 경우 제품을 설치 후 진행해 주시기 바랍니다
    # TODO: 적절한 수준 찾기
    # 3초: 가끔씩 메세지가 나오는 경우가 있다.
    # 5초로 변경
    time.sleep(5)

    # 지문인식 로그인 버튼
    if not auto.click(By.ID, "_fingerLoginBtn"):
        log().error("지문인식 로그인 버튼")
        return False

    # alert 창 확인 버튼
    if not auto.accept_alert():
        log().error("alert 창 확인 버튼")
        return False

    # 지문 토큰
    auto.click(By.ID, "NX_MEDIA_BIOHSM")

    # 지문 토큰 종류 선택 - BIO
    auto.click(By.XPATH, '//*[@id="nx-cert-select"]/div[3]/div[1]/div[3]')

    # 사용자로 부터 전달 받은 token을 선택
    auto.click(By.XPATH,
               f'//div[@id="cert-select-area3"]/table/tbody/tr/td[contains(text(), "{token}")]')

    # 확인버튼
    auto.click(By.XPATH,
               '//*[@id="pki-extra-media-box-contents3"]/div[3]/button')

    #####################
    # 사용자의 지문 입력 #
    #####################

    # Pin 번호 입력 - display될 때까지 기다린다.
    auto.type(By.ID, 'nx_cert_pin', "00000000", timeout=120)

    auto.click(By.XPATH,
               '//*[@id="pki-extra-media-box-contents3"]/div[2]/button')

    # 확인 버튼
    auto.click(By.XPATH, '//*[@id="nx-cert-select"]/div[4]/button[1]')

    # popup 입찰서 작성안내 (optional)
    auto.click(By.ID, '_closeBtn1', timeout=3)

    return True


def register_v2(auto: Automatic, number, user, cert_pw):
    # move to the page to register
    auto.go('https://www.d2b.go.kr/index.do')

    # type number and click search button
    auto.type(By.ID, "numb_divs", number)
    auto.click(By.ID, 'btn_search')

    # 검색된 결과 중 첫번째 element를 선택한다.
    auto.click(
        By.XPATH, '//*[@id="SBHE_DATAGRID_WHOLE_TBODY_datagrid1"]/tr[2]/td[8]/div/span/a')

    # 입찰참가신청서 작성
    auto.click(By.ID, 'btn_join')

    # 신청서 작성후 popup이 생성 된다면.. 이미 신청이 된 상태이다.
    if not auto.accept_alert_with_text("입찰참가등록이 미완료된 건", timeout=3):
        if auto.accept_alert():
            return True

    # 서약서 작성
    auto.click(By.ID, 'c_box1')
    auto.click(By.ID, 'c_box2')
    auto.click(By.ID, 'subcont_dir_pay_yn1')
    # XXX: Need to wait the above result?
    # time.sleep(3)
    auto.click(By.ID, 'btn_confirm')

    # 보증금납부 방법
    sel = auto.get_element(By.ID, 'grnt_mthd')
    auto.select(sel, '보증금면제')

    # ID: D2b - reg - 보증금 동의문
    # 보증금납부에 대한 서약서 확인
    auto.click(By.ID, 'c_box2')
    auto.click(By.ID, 'c_box3')
    auto.click(By.XPATH,
               '//div[5]/div[2]/div[2]/div/div/div[3]/button[1]')

    # 약관 동의 체크
    auto.click(By.ID, 'bidAttention_check')

    # 신청 버튼
    auto.click(By.ID, 'btn_wrt')
    auto.accept_alert()

    # 인증서 로그인
    _login_cert(auto, user, cert_pw)

    # 팝업 확인
    auto.accept_alert()

    # ID: D2B - 사후심사대상 입찰안내
    # Not Always
    # ACTION: "닫기" 버튼이 있고, 보인다면 클릭.
    auto.click(By.XPATH, '//*[@id="layer"]/div[2]/div/div/div[2]/button[3]')

    return True


def participate_v2(auto, number, cost):
    def is_alpha(c):
        try:
            return c.encode('ascii').isalpha()
        except:
            return False

    def remove_prefix(number):
        while not is_alpha(number[0]):
            number = number[1:]
        return number

    # clear pre/postfix
    number = remove_prefix(number)
    number = number[:7]

    if not _need_registration(auto, number):
        return _participate_without_registration(auto, number, cost)
    else:
        return _participate_with_registration(auto, number, cost)


class D2B:
    def __init__(self, id, pw, user, cert_pw, *, headless=True):
        log().debug("__init__")

        self.__user = user
        self.__cert_pw = cert_pw

        self.auto = Automatic.create(Automatic.DriverType.Edge)

        # go homepage
        self.auto.go("https://www.d2b.go.kr/index.do")

        login(self.auto)
        # d2b_login(self.driver, user, id, pw, cert_pw)

    def register(self, pre):
        return register_v2(self.auto, pre.number, self.__user, self.__cert_pw)

    def participate(self, bid):
        return participate_v2(self.auto, bid.number, str(bid.price))
