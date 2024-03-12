
import random

import automatic as am
import automatic.selenium as s
import logging
import pandas as pd
import numpy as np

from utils.logger import Logger


class Callbacks():
    def __init__(self, complete):
        self.complete = complete


class Bid:
    def __init__(self, data, callbacks):
        self.__data = data
        self.market = data['조달사이트']
        self.number = data['공고번호']
        self.title = data['공고명']
        self.price = data['산정금액']
        self.callbacks = callbacks

    def complete(self):
        self.callbacks(self.number)

    def is_ready(self):
        # 사전등록완료? 
        return '사전등록완료' in self.__data['공고번호 / 공고명']

    def is_completed(self):
        return '입찰참여완료' in self.__data['공고번호 / 공고명']

    def __str__(self):
        return f"market={self.market:7s}, code={self.number:20s}, price={int(float(self.price)):12,} KRW, title={self.title}"


class Preregistration:
    def __init__(self, data: pd.Series, callbacks):
        self.callbacks = callbacks
        self.__data = data
        self.number = self.__data['공고번호'] if self.__data['공고번호'] else self.__data['세부품명번호']
        self.title = self.__data['공고명'] if self.__data['공고명'] else self.__data['세부품명']
        self.market = self.__data['조달사이트']
        self.__page = self.__data['페이지']

    def complete(self):
        self.callbacks(self.number, self.__page)

    def is_completed(self):
        return '사전등록완료' in self.__data.iloc[2]

    def __str__(self):
        return f"market={self.market:7s}, code={self.number:20s}, title={self.title}"


# New Incon MRO mall
class InconMRO(am.Automatic, Logger):
    def __init__(self, driver, id, pw, loglevel=logging.DEBUG):
        self.id = id
        self.pw = pw
        selenium = s.Context(driver, timeout=10, differ=0)
        am.Automatic.__init__(self, [selenium])

        Logger.__init__(self, "Incon", loglevel=loglevel)

    def login(self):
        self.logger.info("로그인")
        try:
            self.go(s.Url("홈페이지", "https://www.incon-mro.com/bbs/login.php?url=%2F"))
            self.type(s.Id("아이디 입력 상자", "login_id"), self.id)
            self.type(s.Id("암호 입력 상자", "login_pw"), self.pw)
            self.click(s.Xpath("확인 버튼",  "//button[text()='로그인']"))

        except Exception as e:
            self.logger.error(e)
            return False

    def init_pre(self):
        self.logger.info("전체 소싱 요청")
        try:
            self.go(
                s.Url("소싱요청 페이지", "https://www.incon-mro.com/shop/sourcingrequestlist.php"))
            self.click(s.Xpath("소싱 요청 버튼", "//button[text()='전체소싱요청']"))
            self.accept(s.Alert("소싱 요청 확인 팝업", "전체를 소싱요청하시겠습니까?"))
            popup = s.Alert("소싱 완료 팝업", "전체소싱요청 하실 항목이 존재하지 않습니다.", timeout=5)
            if self.exist(popup):
                self.accept(popup)

            # 화면이 잘 로딩될때 까지 기다린다.
            return self.exist(s.Xpath("사전등록", "//a[text()='사전등록']"))

        except Exception as e:
            self.logger.error(e)
            return False

    def clean_pre_list(self, df: pd.DataFrame) -> pd.DataFrame:
        self.logger.info("사전등록 데이터 클렌징")
        # 1. 직접의무대상 제거
        df = df[~df.iloc[:, 2].str.contains('직접이행의무대상')]
        # 2. 취소 제거
        df = df[~df.iloc[:, 2].str.contains('취소')]
        # 3. 사전등록완료 제거
        # df = df[~df.iloc[:, 2].str.contains('사전등록완료')]
        # 4. 의미 없는 단어 제거
        df.iloc[:, 2] = df.iloc[:, 2].str.replace('Copy to clipboard', '')

        df['공고번호'] = df.iloc[:, 2].str.extract(
            r'공고번호 : (.+?)(?: 공고명)')  # 공고번호 추출
        df['공고명'] = df.iloc[:, 2].str.extract(
            r'공고명 : (.+?)(?: 판단번호|$)')  # 공고명 추출
        df['판단번호'] = df.iloc[:, 2].str.extract(r'판단번호 : (\d+)')  # 판단번호 추출
        df['세부품명'] = df.iloc[:, 2].str.extract(
            r'세부품명 : (.+?)(?: 세부품명번호)')  # 공고번호 추출
        df['세부품명번호'] = df.iloc[:, 2].str.extract(
            r'세부품명번호 : (.+?)')  # 공고명 추출
        return df

    def clean_bid_list(self, df: pd.DataFrame) -> pd.DataFrame:
        self.logger.info("입찰 데이터 클렌징")
        # Merge notice
        df['비고'] = df['견적서'].shift(-1)
        df = df[df['견적서'].isnull()].copy()

        df = df[~df['구분'].isin(['개시전', '취소'])]
        # df = df[~df['공고번호 / 공고명'].str.contains("채택완료")]

        df['조달사이트'] = df['조달사이트'].str.replace('황금입찰', '')

        # Drop unused columns
        columns_to_drop = [col for col in df.columns if 'Unname' in col]
        df.drop(columns_to_drop, axis=1, inplace=True)

        df['공고번호 / 공고명'] = df['공고번호 / 공고명'].str.replace('채택완료', '')
        df['공고번호 / 공고명'] = df['공고번호 / 공고명'].str.replace('사전등록완료', '')

        # Extract data
        df['공고번호'] = df.iloc[:, 3].str.split('Copy to clipboard').str[0]
        df['공고명'] = df.iloc[:, 3].str.extract(
            r'Copy to clipboard(.+?)(?:판단번호|$)')  # 공고명 추출
        df['판단번호'] = df.iloc[:, 3].str.extract(
            r'판단번호 : (\d+)Copy to clipboard')  # 판단번호 추출

        return df

    def get_num_of_predata_page(self):
        self.go(
            s.Url("사전등록 탭", "https://www.incon-mro.com/shop/preregistrationlist.php"))
        # a tag의 개수를 세어 몇개의 페이지가 존재하는지 확인한다.
        # 묶음 이동 버튼(>>) 이 포함되어 있으나, 현재 활성화 되어 있는 페이지의 경우 a tag를 갖고 있지
        # 않기 때문에 a tag의 갯수가 페이지의 갯수가 된다.
        pageButton = s.Xpath("페이지 버튼", '//*[@id="preregistrationlist"]/div/nav/span/a')
        return 1 if not self.exist(pageButton) else self.count(pageButton)
      

    def get_pre_data(self):
        self.logger.info("사전 등록 데이터 요청")
        try:
            dfs = []
            cnt = self.get_num_of_predata_page()
            for i in range(1, cnt+1):
                self.logger.info(f"사전등록데이터 요청 - {i} page")
                self.go(
                    s.Url("사전등록 탭", f"https://www.incon-mro.com/shop/preregistrationlist.php?&page={i}"))
                df = self.table(
                    s.Xpath("사전등록 리스트", '//*[@id="preregistrationlist"]/div/table'))
                df = self.clean_pre_list(df)
                df["페이지"] = i
                dfs.append(df)

            df = pd.concat(dfs, ignore_index=True)
            return [Preregistration(d, lambda num, p: self.complete_pre(num, p)) for _, d in df.iterrows()]

        except Exception as e:
            self.logger.error(e)
            return None

    def init_bid(self):
        self.logger.info("입찰 데이터 가격 산정")
        df = self.__bid_data()
        for num in df.loc[df['산정금액'].isna(), '공고번호']:
            self.calculate_price(num)

    def __bid_data(self):
        self.logger.info("입찰 데이터 요청")
        self.go(
            s.Url("소싱완료탭", "https://www.incon-mro.com/shop/sourcingcompletelist.php"))

        df = self.table(
            s.Xpath("소싱완료 리스트", '//*[@id="sourcingcomplete"]/div/table'))

        return self.clean_bid_list(df)

    def get_bid_data(self):
        return [Bid(d, lambda num: self.complete_bid(num)) for _, d in self.__bid_data().iterrows()]

    def calculate_price(self, num):
        self.logger.info(f"가격산정 {num}")
        # 견적서로 이동
        self.click(s.Xpath(
            "견적서보기 버튼",  f'//*[contains(text(),"{num}")]/../../../td/a[@title="견적서 보기"]'))

        if self.exist(s.Xpath("채택 버튼", "//button[text()='채택 후 가격산정하기']", timeout=3)):
            self.click(s.Xpath("채택 버튼", "//button[text()='채택 후 가격산정하기']"))
            self.accept(s.Alert("가격산정 확인 팝업", "채택 후 가격산정 하시겠습니까?"))

        self.click(s.Xpath("가격산정 버튼",  "//a[text()='가격을 산정 하겠습니다.']"))

        # 사정율 범위
        range_text = self.text(
            s.Xpath("사정율 범위", '//th[text()="사정율 범위"]/../td'))
        random_range = range_text.replace("%", "").split("~")
        min = float(random_range[0])
        max = float(random_range[1])
        ratio = round(random.uniform(min, max), 4)

        self.type(s.Id("범위 입력 상자", "assessment_rate"), ratio)
        self.click(
            s.Xpath("가격 저장", "//button[text()='가격 저장' and @class='btn_bid_amount']"))
        self.accept(s.Alert("저장 확인 팝업", "가격산정을 저장하시겠습니까?"))
        self.accept(s.Alert("저장 완료 팝업", "해당하는 가격을 저장했습니다."))

    def complete_pre(self, num, page):
        # pre condition: should be in the pre-registration page
        self.go(s.Url(
            "사전등록 탭", f"https://www.incon-mro.com/shop/preregistrationlist.php?&page={page}"))

        # NOTE:
        # text() -> .
        # 열이 다른 항목은 text()[1] 혹은 text()[2] 와 같이 접근해야 한다.
        # ex) <td> xxx <br> yyy </td>
        self.click(s.Xpath("체크버튼", f"//td[contains(.,'{num}')]/../td/label"))
        self.click(s.Xpath("사전등록완료 버튼", f"//button[text()='사전등록완료']"))
        self.accept(s.Alert("사전등록 확인 버튼", "선택한 입찰공고를 사전등록하셨습니까?"))

    def complete_bid(self, num):
        self.go(
            s.Url("소싱완료탭", "https://www.incon-mro.com/shop/sourcingcompletelist.php"))

        self.click(
            s.Xpath("체크버튼", f"//a[contains(.,'{num}')]/../../../td/label"))
        self.click(s.Xpath("입찰참여 완료 버튼", f"//button[text()='입찰참여완료']"))
        self.accept(s.Alert("입찰참여 완료 확인 팝업", "입찰참여완료 하시겠습니까?"))
        self.accept(s.Alert("입찰참여 완료 안내 팝업", "아래와 같이 입찰참여완료가 진행됩니다."))
