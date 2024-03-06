
import threading
from selenium.webdriver.common.by import By
from org.g2b.safeg2b import *
from org.g2b import safeg2b

from integ_auto import Automatic


def log():
    import logging
    logger = logging.getLogger("g2b")
    logger.setLevel(logging.DEBUG)
    return logger


def _go_mypage(auto: Automatic):
    auto.go(
        'https://www.g2b.go.kr/pt/menu/selectSubFrame.do?framesrc=/pt/menu/frameMypage.do')


def _do_in_main_frame(auto: Automatic, action):
    sub_frame = auto.get_element(By.ID, 'sub')
    if not sub_frame:
        log().error("Failed to find sub frame")
        return False

    with auto.get_frame(sub_frame):
        main_frame = auto.get_element(By.NAME, 'main')
        if not main_frame:
            log().error("Failed to find main frame")
            return False

        with auto.get_frame(main_frame):
            return action()


def _edit_mypage(auto: Automatic):

    def click_edit_button():
        # Edit Button
        if not auto.click(By.XPATH, '//*[@id="container"]/div[2]/div/a[1]'):
            log().error("Failed to find edit button")
            return False
        return True

    return _do_in_main_frame(auto, lambda: click_edit_button())


def _open_item_find_window(auto: Automatic):
    def click_search_button():
        # 검색 버튼
        if not auto.click(
                By.XPATH, '//*[@id="frm_addProd"]/div[3]/table/tbody/tr/td[1]/div/button'):
            return False
        return True

    return _do_in_main_frame(auto, lambda: click_search_button())


def _find_product(auto: Automatic, pn):
    title = "[팝업] 세부품명찾기: 나라장터"
    handle = auto.get_window_handle(title)
    if not handle:
        log().error(f"Failed to find window handle. title={title}")
        return False

    with auto.get_window(handle):
        # Product Number 입력
        if not auto.type(By.ID, 'detailPrdnmNo', pn):
            log().error(f"Failed to type product number. pn={pn}")
            return False

        # 검색 버튼
        if not auto.click(By.ID, 'bt_search'):
            log().error("Failed to click search button")
            return False

        # select item(첫번째 Item 클릭)
        if not auto.click(By.XPATH, '//*[@id="container"]/div[1]/table/tbody/tr/td[2]/a'):
            log().error("Failed to click 첫번째 아이템")
            return False

    return True


def _register_product(auto: Automatic):

    def click_register_button():
        if not auto.click(By.XPATH, '//*[@id="frm_addProd"]/div[2]/a'):
            log().error("Failed to click register button")
            return False
        if not auto.accept_alert():
            log().error("Failed to accpet alert")
            return False
        return True

    if not _do_in_main_frame(auto, lambda: click_register_button()):
        return False

    # 20230415: sometime there is no messages to click
    handle = auto.get_window_handle("Message: 나라장터", timeout=5)
    if handle == None:
        return True

    with auto.get_window(handle):
        if not auto.click(By.XPATH, '//*[@id="container3"]/div[2]/div/a'):
            log().error("Failed to click 확인 버튼")
            return False

    return True

# Go to the homepage to login


def go_homepage(auto: Automatic):
    auto.go('https://www.g2b.go.kr')
    return True


# Go to the page where we can register a new product
def go_product_registration_page(auto: Automatic):
    # go mypage
    _go_mypage(auto)

    # click edit button
    if not _edit_mypage(auto):
        log().error("Failed to edit mypage")
        return False

    return True


# Register a product
def register_product(auto: Automatic, pn):
    # open the window by clicking search button
    if not _open_item_find_window(auto):
        log().error("Failed to open itme find window")
        return False

    # move to the windows and input the product number
    if not _find_product(auto, pn):
        log().error("Failed to find a product.")
        return False

    # click register button and clear popup and confirm window
    if not _register_product(auto):
        log().error("Failed to register product.")
        return False

    return True


def get_registered_products(auto: Automatic):
    def get_product_names():
        items = auto.get_elements(
            By.XPATH, '//*[@id="frm_supProd"]/div[3]/table/tbody/tr/td[3]/div')
        return [item.text for item in items]

    return _do_in_main_frame(auto, lambda: get_product_names())


# EXTERNAL INTERFACES

def register(auto: Automatic, pns):
    if not go_product_registration_page(auto):
        log().error("Failed to go product registration page.")
        return False

    registered_pns = get_registered_products(auto)
    for pn in pns:
        if pn in registered_pns:
            log().info(f"{pn} is already registered.")
            continue
        if not register_product(auto, pn):
            log().error(f"Failed to register a product. pn={pn}")

    return True


def login(auto: Automatic, password):
    go_homepage(auto)

    member_frame = auto.get_element(By.ID, 'member_iframe')
    if not member_frame:
        log().error("Failed to find member frame")
        return False

    # click the login button
    with auto.get_frame(member_frame):
        if not auto.click(By.XPATH, '//*[@id="arg_exceptionLogin"]'):
            log().error("Failed to click 지문인식 예외적용 로그인 button")
            return False
        
        if not auto.click(By.XPATH, '//*[@id="logout"]/ul/li[1]/ul/li/a/img'):
            log().error("Failed to click Login Button")
            return False

    # "계속 진행하시겠습니까?" 
    if not auto.accept_alert_with_text("계속 진행하시겠습니까?"):
        log().error("지문인식 예외적용: [계속 진행하시겠습니까?] 팝업이 생성되지 않았습니다.")
        return False



    # NOTE: 기업 인증서.   
    # try to login with certificate
    log().info("기업 인증서 로그인")
    import org.g2b.certificate
    if not org.g2b.certificate.cert_login(password):
        log().error("Failed to login with certification(w/o 지문입력)")
        return False

    # 주민번호
    sub_frame = auto.get_element(By.ID, 'sub')
    if not sub_frame:
        log().error("하단 프레임을 찾을 수 없습니다. ")
        return False

    with auto.get_frame(sub_frame):
        log().info("주민번호 입력")
        if not auto.type(By.ID, 'jmbeonho1', "831119") or not auto.type(By.ID, 'jmbeonho2', "1178813"):
            log().error("Failed to input 주민번호")
            return False

  
        # WARNING!!! 
        # click함수가 종료되기 위해선 개인이증서 로그인이 완료되어야 하기 때문에
        # 별도에 thread에서 click 을 동작한후 join해야 한다. 
        # 그렇지 않으면 block되어서 진행이 안된다.
        click = lambda: auto.click(By.XPATH, '//span[text()="확인"]/..')
        thr = threading.Thread(target=click )
        thr.start()

        # log().info("주민번화 확인버튼")
        # if not auto.click(By.XPATH, '//span[text()="확인"]/..'):
        #     log().error("Failed to click 확인 button for 주민번호")
        #     return False
    
        # time.sleep(3)
        log().info("개인인증서 로그인")
        # NOTE: 개인 인증서. password가 같아야한다.
        if not org.g2b.certificate.cert_login(password):
            log().error("Failed to login with certification(w/o 지문입력)")
            return False
        
        thr.join()

    title = "Message: 나라장터"
    log().info("Window focus 변경 - {title}")
    handle = auto.get_window_handle(title)
    if not handle:
        log().error(f"{title} 윈도우를 찾을 수 없습니다.")
        return False
    
    with auto.get_window(handle):
        log().info("예외적용자 확인")
        if not auto.click(By.XPATH, "//span[text()='확인']/.."):
            log().error(f"확인버튼을 찾을 수 없습니다.")
            return False
    
    return True

def g2b_participate(auto: Automatic, code, price, password):

    # * 입찰정보 click
    tops_frame = auto.get_element(By.ID, 'tops')
    if not tops_frame:
        log().error("상단 프레임을 찾을 수 없습니다. ")
        return False

    with auto.get_frame(tops_frame):
        if not auto.click(By.XPATH, '//img[@alt="입찰정보"]', timeout=10):
            log().error("입찰정보 버튼을 찾지 못하였습니다.")
            return False

    def search_bid_number():
        if not auto.type(By.ID, "bidno1", code):
            log().error("입찰번호를 입력 할 수 없습니다.")
            return False
        if not auto.click(By.ID, "bt_search"):
            log().error("검색버튼을 찾을 수 없습니다.")
            return False
        return True

    if not _do_in_main_frame(auto, lambda: search_bid_number()):
        log().error("입찰번호 검색을 실패하였습니다.")
        return False

    # 지문 투찰 버튼

    def click_figerprint_bid_button():
        # <button type="button" class="btn_fingerprint" onclick="bidLink_biddingProdAndBidMsg('20221119994','00');return false;" title="지문투찰"><span class="blind">지문투찰</span></button>
        if not auto.click(By.XPATH, "//button[@title='지문투찰']"):
            log().error("지문투찰 버튼을 찾을 수 없습니다.")
            return False
        return True

    if not _do_in_main_frame(auto, lambda: click_figerprint_bid_button()):
        log().error("지문투찰 버튼.")
        return False

    # XXX: 새로운 Window 가 열릴때 너무 빨리 열리게 되면 title이 none인 경우가 생긴다.
    time.sleep(3)
    # 새로운 window 열린다. "물품공고분류조회 - 프로필 1 - Microsoft Edge"
    title = "물품공고분류조회"
    handle = auto.get_window_handle(title)
    if not handle:
        log().error(f"{title} 윈도우를 찾을 수 없습니다.")
        return False

    with auto.get_window(handle):
        log().info("물품공고분류조회: 1-투찰 링크 클릭")
        if not auto.click(By.XPATH, "//a[text()='1-투찰']"):
            log().error(f"투찰 링크를 찾을 수 없습니다.")
            return False

    # validation
    time.sleep(3)
    title = "Message: 나라장터"
    handle = auto.get_window_handle(title, timeout=1)
    if handle:
        with auto.get_window(handle):
            if auto.get_element(By.XPATH, "//div[contains(text(), '접수되었습니다.')]"):
                log().info("Message: 나라장터: 이미 등록이 완료 되었습니다.")
                return True
            else:
                log().error("Message: 나라장터: 알지못하는 상태입니다. 확인이 필요합니다.")
                return False

    title = "투찰제어"
    handle = auto.get_window_handle(title, timeout=5)
    if handle:
        log().error(f"물품등록이 마감되어 진행할 수 없습니다.")
        return False

    title = "투찰 공지사항"
    handle = auto.get_window_handle(title)
    if not handle:
        log().error(f"{title} 윈도우를 찾을 수 없습니다.")
        return False

    with auto.get_window(handle):
        log().info("투찰공지사항: 동의 체크버튼(3개) 확인")
        # 투찰 공지사항으로 conentes가 바뀌면서 동의함 3개 및 확인 클릭
        if not auto.click(By.ID, "entrprsInfoCheckY") or \
                not auto.click(By.ID, "administInfoCheckY") or \
                not auto.click(By.ID, "noticeCheckY"):
            log().error("동의관련 체크박스중 하나를 찾을 수 없습니다.")
            return False

        log().info("투찰공지사항: 확인버튼")
        if not auto.click(By.XPATH, "//span[text()='확인']/.."):
            log().error("확인 버튼을 찾을 수 없습니다.")
            return False

    # 새로운 windows (사실 기존 윈도우에서 이름이 변경된다. )
    title = "물품구매입찰서"
    handle = auto.get_window_handle(title)
    if not handle:
        log().error(f"{title} 윈도우를 찾을 수 없습니다.")
        return False

    with auto.get_window(handle):
        log().info("물품구매입찰서: 동의함")
        if not auto.click(By.ID, "increasedAgreementCheck"):
            log().error("물품구매입찰서: 동의 체크확인 버튼을 찾을 수 없습니다.")
            return False

        if not auto.type(By.ID, "chongDan", price):
            log().error("물품구매입찰서: 가격 입력란을 찾을 수 없습니다.")
            return False

        # 가격 입력후 바로 아래과정을 진행 하게 되면 가격을 입력해야 한다는 팝업이 뜬다. 
        # 가격 입력후 focus를 변경해 주어야 한다. 
        # 아래 단계는 단순히 가격입력 textbox의 focus를 다른곳으로 돌리는 역할을 한다.
        if not auto.type(By.XPATH, "//*[@id='attachFile']/tbody/tr/td[2]/input", ""):
            log().error("문서명 입력 textbox를 찾을 수 없습니다.")
            return False

        if not auto.click(By.ID, "checkCleanContract"):
            log().error("물품구매입찰서: 청렴 계약 동의 체크확인 버튼을 찾을 수 없습니다.")
            return False

        if not auto.click(By.ID, "btnConfirm"):
            log().error("물품구매입찰서: 송신버튼을 찾을 수 없습니다.")
            return False

    # 새로운 windows (사실 기존 윈도우에서 이름이 변경된다. )
    title = "투찰금액 확인"
    handle = auto.get_window_handle(title)
    if not handle:
        log().error(f"{title} 윈도우를 찾을 수 없습니다.")
        return False

    with auto.get_window(handle):
        log().info("투찰금액 확인")
        # XXX: 너무 빨리 확인 버튼을 누르게 되면 금액이 입력 되지 않안 입찰급액을 확인하라는 팝업이 떴다.
        # 아마도 네트워크가 느린 상황에서 발생되는 이슈로 보인다.
        time.sleep(3)

        if not auto.click(By.ID, "noticeCheckY"):
            log().error("투찰금액 확인: 확인 체크버튼을 찾을 수 없습니다.")
            return False

        if not auto.click(By.XPATH, '//span[text()="확인"]/..'):
            log().error("투찰금액 확인: 확인 버튼을 찾을 수 없습니다.")
            return False

    # 새로운 windows (사실 기존 윈도우에서 이름이 변경된다. )
    title = "추첨번호 선택"
    handle = auto.get_window_handle(title)
    if not handle:
        log().error(f"{title} 윈도우를 찾을 수 없습니다.")
        return False

    with auto.get_window(handle):
        log().info("추첨번호 선택")
        boxes = auto.get_elements(By.NAME, "check")
        boxes = random.sample(boxes, k=2)
        for box in boxes:
            auto.click(box)

        # XXX: 너무 빠르게 지나가 버려 확인하기가 어렵다.
        time.sleep(3)

        if not auto.click(By.XPATH, '//span[text()="추첨번호전송"]/..'):
            log().error("추첨번호 선택: 추첨번호전송 버튼을 찾을 수 없습니다.")
            return False

        # 전송하시겠습니까? popup
        if not auto.accept_alert_with_text("전송하시겠습니까?"):
            log().error("추첨번호 선택: [전송하시겠습니까?] 팝업이 생성되지 않았습니다.")
            return False

        # [입찰에 참여할 수 있습니다.]
        if not auto.accept_alert_with_text("입찰에 참여할 수 있습니다."):
            log().error("개인인증서 선택창")
            return False
        
        # 개인인증서
        # 신원확인을 합니다.? popup
        # if not auto.accept_alert_with_text("신원확인을 합니다."):
        #     log().error("추첨번호 선택: [신원확인을 합니다] 팝업이 생성되지 않았습니다.")
        #     return False
        
        log().info("개인인증서 로그인")
        if not org.g2b.certificate.cert_login(password):
            log().error("Failed to login with certification(w/o 지문입력)")
            return False

    # 전송 완료 후 java에서 띄우는 팝업
    if not auto.activate("나라장터"):
        log().error("나라장터: 윈도우가 확인되지 않았습니다.")

    log().info("나라장터: 정상접수 확인")
    if not auto.click(resmgr.get('safeg2b_2_9_confirm_button.png')):
        log().error("나라장터: OK 버튼을 찾을 수 없습니다.")
        return False

    # 새로운 windows (사실 기존 윈도우에서 이
    # 름이 변경된다. )
    title = "전자입찰 송수신상세이력조회"
    handle = auto.get_window_handle(title)
    if not handle:
        log().error(f"{title} 윈도우를 찾을 수 없습니다.")
        return False

    with auto.get_window(handle):
        if not auto.click(By.XPATH, "//span[text()='닫기']/.."):
            log().error(f"{title}: 닫기버튼을 찾을 수 없습니다.")
            return False

    return True


def g2b_login_with_biotoken(auto: Automatic):
    go_homepage(auto)

    member_frame = auto.get_element(By.ID, 'member_iframe')
    if not member_frame:
        log().error("Failed to find member frame")
        return False

    # click the login button
    with auto.get_frame(member_frame):
        if not auto.click(By.XPATH, '//*[@id="logout"]/ul/li[1]/ul/li/a/img'):
            log().error("Failed to click Login Button")
            return False

    # try to login with certificate
    import org.g2b.certificate
    return org.g2b.certificate.cert_login_with_biotoken("00000000")


class G2B:
    def __init__(self, pw=None, close_windows=True, headless=True):
        self.auto = Automatic.create(Automatic.DriverType.Edge)
        self.__close_windows = close_windows
        self.pw = pw

    def login(self):
        if self.pw:
            
            if not login(self.auto, self.pw):
                log().error("Failed to login")
                return False
        else:
            if not g2b_login_with_biotoken(self.auto):
                log().error("Failed to login")
                return False

        # Frame이 변경되는데 변경되기전 frame에서 logout button을 찾기 때문에 실패한다.
        # element 찾을 때 frame도 다시 찾는 방법으로 문제를 해결한다.
        # 대략 30회, 즉 30초 가량의 시간동안 시도해 본다.
        num_try = 0
        while num_try < 30:
            # 로그아웃 버튼 찾기
            tops_frame = self.auto.get_element(By.ID, 'tops')
            if not tops_frame:
                log().error("상단 프레임을 찾을 수 없습니다. ")
                return False
            with self.auto.get_frame(tops_frame):
                logout = self.auto.get_element(
                    By.XPATH, "//a[text()='로그아웃']", timeout=1)
                if logout:
                    break

        if num_try == 30:
            log().error("로그아웃 버튼을 찾을 수 없습니다.")
            return False

        return True

    def __del__(self):
        if self.__close_windows:
            self.auto.driver.close()

    def register(self, code):
        codes = code.split(",")
        codes = [pn.strip() for pn in codes]
        return register(self.auto, codes)

    def participate(self, code, price):
        log().info(f"participate in {code} price={price}")
        return g2b_participate(self.auto, code, price, self.pw)
