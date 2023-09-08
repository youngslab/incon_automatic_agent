
import random
from automatic import browser
from selenium.webdriver.common.by import By


# class Bid:
#     def __init__(self, webdriver, listitem):
#         self.__driver = webdriver
#         self.__listitem = listitem
#         self.__data = incon_bid_listitem_get_data(self.__listitem)
#         self.title = self.__data['공고명']
#         self.number = self.__data['공고번호']
#         self.deadline = self.__data['입찰마감']
#         self.market = incon_bid_listitem_get_market(self.__listitem)
#         self.is_ready = incon_bid_listitem_is_ready(self.__listitem)
#         self.price = incon_bid_listitem_get_price(self.__listitem)

#     def __str__(self):
#         return f"market={to_code(self.market):7s}, code={self.number:20s}, price={int(self.price):12,} KRW, title={self.title}"

#     def is_completed(self):
#         # find element in the list...
#         element = incon_bid_get_listitem_by_title(self.__driver, self.title)
#         if not element:
#             raise Exception("Failed to find an element.")
#         return incon_listitem_is_completed(element)

#     def complete(self):
#         # find element in the list...
#         element = incon_bid_get_listitem_by_title(self.__driver, self.title)
#         if not element:
#             raise Exception("Failed to find an element.")
#         return incon_listitem_complete(self.__driver, element)


class Callbacks():
    def __init__(self, complete):
        self.complete = complete


class Bid:
    def __init__(self, market, text, price, callbacks):
        tokens = text.split('\n')
        self.text = text
        self.market = market
        self.number = tokens[0].strip()
        self.title = tokens[1].strip()
        self.price = price.replace(",", "")
        self.callbacks = callbacks

        # TODO: define more specific
        self.is_ready = True

    def complete(self):
        self.callbacks.complete(self.number)

    def is_completed(self):
        return "입찰참여완료" in self.text

    def __str__(self):
        return f"market={self.market:7s}, code={self.number:20s}, price={int(self.price):12,} KRW, title={self.title}"


class Preregistration:
    def __init__(self, text, callbacks):
        self.callbacks = callbacks
        self.table = dict()
        self.text = text
        tokens = text.split('\n')
        for token in tokens:
            sep = token.find(":")
            if sep < 0 or token.find("**") >= 0:
                self.table['etc'] = f"{self.table.get('etc','')} \n{token}"
            else:
                self.table[token[:sep].strip()] = token[sep+1:].strip()

    def complete(self):
        self.callbacks.complete(self.number)

    def is_completed(self):
        return "사전등록완료" in self.text


    def __str__(self):
        return f"market={self.market:7s}, code={self.number:20s}, title={self.title}"


class PreDataKepco(Preregistration):
    def __init__(self, text, callbacks):
        super().__init__(text, callbacks)
        self.number = self.table["공고번호"]
        self.title = self.table["공고명"]
        self.market = "한국전력"


class PreDataG2B(Preregistration):
    def __init__(self, text, callbacks):
        super().__init__(text, callbacks)
        self.number = self.table["세부품명번호"]
        self.title = self.table["세부품명"]
        self.market = "나라장터(기타)"


class PreDataD2B(Preregistration):
    def __init__(self, text, callbacks):
        super().__init__(text, callbacks)
        self.number = self.table["공고번호"]
        self.title = self.table["공고명"]
        self.market = "국방전자조달"


# New Incon MRO mall
class InconMRO:
    def __init__(self, driver, id, pw):
        self.context = browser.Context(
            driver, "https://www.incon-mro.com", default_timeout=30)

        self.id = id
        self.pw = pw

    def __del__(self):
        pass

    def login(self):
        self.context.set_url("https://www.incon-mro.com/bbs/login.php?url=%2F")
        login_id_input = browser.TypeableElement(
            self.context, "id", "login_id")
        login_pw_input = browser.TypeableElement(
            self.context, "id", "login_pw")
        login_button = browser.ClickableElement(
            self.context, "xpath", "//button[text()='로그인']")

        login_id_input.type(self.id)
        login_pw_input.type(self.pw)

        login_button.click()

    # 전체 소싱 요청
    def request_all_sourcing(self):
        self.context.set_url(
            "https://www.incon-mro.com/shop/sourcingrequestlist.php")
        request_button = browser.ClickableElement(
            self.context, "xpath", "//button[text()='전체소싱요청']")
        request_button.click()

        # popup - "전체를   소싱    하시겠습니까?"
        popup = browser.Alert(self.context)
        popup.accept("전체를 소싱요청하시겠습니까?")
        popup.accept("전체소싱요청 하실 항목이 존재하지 않습니다.", timeout=3, ignore=True)

        # 화면이 잘 로딩될때 까지 기다린다.
        button = browser.Element(
            self.context, "xpath", "//a[text()='사전등록']")
        return button.exist()

    def get_pre_data(self):
        # # 전체 소싱 요청
        if not self.request_all_sourcing():
            print("ERROR: 전체 소싱 요청 실패")
            return None

        # 사전등록 tab으로 이동
        self.context.set_url(
            "https://www.incon-mro.com/shop/preregistrationlist.php")

        markets = browser.TextableElements(
            self.context, "xpath", "//td[@class='td_pa_num']")

        descriptions = browser.TextableElements(
            self.context, "xpath", "//td[@class='td_pa_name']")

        callbacks = Callbacks(self.complete_pre)

        items = []

        for market, description in zip(markets.text(), descriptions.text()):
            # filter: 1. 취소
            if "취소" in description:
                continue
            if market == "한국전력":
                items.append(PreDataKepco(description, callbacks))
            elif market == "나라장터(기타)":
                items.append(PreDataG2B(description, callbacks))
            elif market == "국방전자조달":
                items.append(PreDataD2B(description, callbacks))

        return items

    def get_bid_data(self):

        # 소싱완료탭으로 이동
        self.context.set_url(
            "https://www.incon-mro.com/shop/sourcingcompletelist.php")

        # 가능한 모든 아이템들에 대해 가격 산정
        success = self.bid_init()
        if not success:
            print("Failed to init bid items")
            return False

        # bid 정보 추출
        descriptions = browser.TextableElements(
            self.context, "xpath", "//td[@class='td_pa_name']").text()

        markets = browser.TextableElements(
            self.context, "xpath", "//td[@class='td_pa_site']").text()

        # 가격
        prices = browser.TextableElements(
            self.context, "xpath", "//td[@class='td_pa_calamount']").text()

        # 구분
        sorts = browser.TextableElements(
            self.context, "xpath", "//td[@class='td_pa_sort']").text()

        callbacks = Callbacks(complete=self.bid_complete)

        # generate data
        bids = []
        for market, price, description, sort in zip(markets, prices, descriptions, sorts):
            if "개시전" in sort:
                continue            
            bids.append(Bid(market, description, price, callbacks))

        return bids

    def calculate_price(self, num):
        # 견적서로 이동
        estimate_btn = browser.ClickableElement(
            self.context, "xpath", f'//*[contains(text(),"{num}")]/../../../td/a[@title="견적서 보기"]')
        estimate_btn.click()

        price_btn = browser.ClickableElement(
            self.context, "xpath", "//button[text()='채택 후 가격산정하기']")
        price_btn.click()

        alert = browser.Alert(self.context)
        alert.accept("채택 후 가격산정 하시겠습니까?")

        # 가격산정 버튼
        price_btn = browser.ClickableElement(
            self.context, "xpath", "//a[text()='가격을 산정 하겠습니다.']")
        price_btn.click()

        # 사정율 범위
        range_text = browser.TextableElement(
            self.context, "xpath", '//th[text()="사정율 범위"]/../td')

        random_range = range_text.text().replace("%", "").split("~")
        min = float(random_range[0])
        max = float(random_range[1])
        ratio = round(random.uniform(min, max), 4)

        ratio_input = browser.TypeableElement(
            self.context, "id", "assessment_rate")
        ratio_input.type(ratio)

        save_btn = browser.ClickableElement(
            self.context, "xpath", "//button[text()='가격 저장' and @class='btn_bid_amount']")
        save_btn.click()

        alert = browser.Alert(self.context)
        alert.accept("가격산정을 저장하시겠습니까?")
        alert.accept("해당하는 가격을 저장했습니다.")

    def bid_init(self):

        # list를 얻어오고, list의 item들이 모두 산정 될때 까지 가격산정을 반복한다.
        descriptions = browser.TextableElements(
            self.context, "xpath", "//td[@class='td_pa_name']")

        # No items
        if not descriptions:
            print("No bid items")
            return True

        # 구분
        sorts = browser.TextableElements(
            self.context, "xpath", "//td[@class='td_pa_sort']").text()

        nums = []
        for sort, description in zip(sorts, descriptions.text()):
            if "개시전" in sort:
                continue
            if "채택완료" in description:
                continue

            nums.append(description.split("\n")[0].strip())

        for num in nums:
            self.calculate_price(num)

        return True

    def complete_pre(self, num):
        # pre condition: should be in the pre-registration page        
        pre_reg_page = "https://www.incon-mro.com/shop/preregistrationlist.php"
        if self.context.get_url is not pre_reg_page:
            self.context.set_url(pre_reg_page)

        # NOTE: 
        # text() -> . 
        # 열이 다른 항목은 text()[1] 혹은 text()[2] 와 같이 접근해야 한다.
        # ex) <td> xxx <br> yyy </td> 
        check_btn = browser.ClickableElement(
            self.context, "xpath", f"//td[contains(.,'{num}')]/../td/label")
        check_btn.click()

        btn = browser.ClickableElement(
            self.context, "xpath", f"//button[text()='사전등록완료']")
        btn.click()

        popup = browser.Alert(self.context)
        return popup.accept("선택한 입찰공고를 사전등록하셨습니까?")

    def bid_complete(self, num):
        # pre condition: should be in the sourcing page        
        sourcing_page = "https://www.incon-mro.com/shop/sourcingcompletelist.php"
        if self.context.get_url is not sourcing_page:
            self.context.set_url(sourcing_page)

        check_btn = browser.ClickableElement(
            self.context, "xpath", f"//p[contains(.,'{num}')]/../../../td/label")
        check_btn.click()

        btn = browser.ClickableElement(
            self.context, "xpath", f"//button[text()='입찰참여완료']")
        btn.click()

        popup = browser.Alert(self.context)
        popup.accept("입찰참여완료 하시겠습니까?")
        popup.accept("아래와 같이 입찰참여완료가 진행됩니다.")
