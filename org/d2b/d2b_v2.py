import os
import time
import logging
import pandas as pd
import traceback

import automatic as am
import automatic.selenium as s
import automatic.win32 as w
from automatic.selenium.utils import create_driver

LOGGER_D2B = "D2B"
logger = logging.getLogger(LOGGER_D2B)


class D2B(am.Automatic):
    
    def __init__(self, driver, id, pw, cert_pw):
        self.name = "국방전자조달"
        self.__pw = pw
        self.__id = id
        self.__cert_pw = cert_pw

        selenium = s.Context(driver, timeout=20, differ=0)
        win32 = w.Context(timeout=50, differ=0)
        am.Automatic.__init__(self, [selenium, win32])

    def _do_login(self):
        logger.info("로그인 시도")
        self.go(s.Url("로그인 페이지", "https://www.d2b.go.kr/index.do"))
        # 이전상태에 따라 popup이 생성되는 경우가 있다. 
        if self.exist(s.Alert("test", "", timeout=3)):
            self.accept(s.Alert("test", ""))

        if self.exist(s.Id("로그아웃 버튼", "_logoutBtn", timeout=3)):
            logger.info("이미 로그인 되어 있습니다.")
            return
        self.click(s.Id("로그인 버튼","_mLogin"))
        logger.info("Wait 5 secs. Too fast to login make problem.")
        time.sleep(5)

        logger.info("로그인 - 아이디 패스워드 입력")
        self.type(s.Id("아이디 입력상자", "_id"), self.__id)
        self.type(s.Id("패스워드 입력상자", "_pw"), self.__pw)
        self.click(s.Id("로그인 버튼", "_loginBtn"))
        logger.info("로그인 - 인증서")
        self.type(s.Id("인증서 비밀번호 입력상자", "certPwd"), self.__cert_pw)
        self.click(s.Xpath("인증서 선택 확인 버튼", '//*[@id="nx-cert-select"]/div[4]/button[1]'))

        # validate login is completed
        if self.exist(s.Id("로그인 버튼","_mLogin", timeout=3, differ=10)):
            logger.info("로그인 버튼이 아직 있습니다. 로그인 실패로 간주합니다.")
            raise Exception("로그인 실패")

    def login(self):
        logger.info("로그인")
        # XXX: 보안 프로그램이 설치는 되어 있지만, 로그인 시도시 설치 필요하다 팝업이 생성된다. 
        # 이 때 로그인 실패 후 다시 시도하면 정상적으로 로그인된다.     
        for attempt in range(2):
            try:
                self._do_login()
                return
            except Exception as e:
                logger.warning(f"로그인 시도 {attempt+1} 실패: {e}")
                if attempt == 1:
                    raise
                logger.info("로그인 재시도 중...")
                time.sleep(10)

    def certificate(self, type):
        self.click(s.Id("HDD", "NX_MEDIA_HDD"))
        self.click(s.Xpath(f"{type}", f'//td/div[contains(text(),"{type}")]/img/..'))
        # XXX: 인증서 선택과정이 아래 type의 결과를 reset한다.
        #      따라서 충분한 간격을 준다.
        time.sleep(3)

        # 3. password
        self.type(s.Id("패스워드 입력상자", "certPwd"), self.__cert_pw)
        # 4. ok button
        self.click(s.Xpath("확인 버튼", '//*[@id="nx-cert-select"]/div[4]/button[1]'))


    def go_detail_page(self, code):
        self.go(s.Url("홈페이지", 'https://www.d2b.go.kr/index.do'))

        # 2개가 검색되는 경우가 있음. 판단번호가 유일하지만 .. "수의"라는 단어가 중요하기 때문에 사용할 수 없음. 
        # 따라서 전체 공고에서 검색하는 것이 아니라. "용역" 과 "물품" 에서만 공고를 검색한다. 
        self.click(s.Id("물품 체크박스", "pgb"))
        self.click(s.Id("용역 체크박스", "psb"))


        self.type(s.Id("코드 검색 입력 상자", "numb_divs"), code)
        self.click(s.Id("검색 버튼",'btn_search'))
        
        # 검색된 결과 중 첫번째 element를 선택한다. 그런데 바로 클릭하게 되면 다음으로 넘어가지 않는다. 
        # table = self.table(s.Xpath("검색 결과 테이블", '//table[@id="SBHE_DATAGRID_WHOLE_TABLE_datagrid1"]', timeout=30))
       
        self.click(s.Xpath("검색결과 참여링크", '//*[@id="datagrid1_1_7_data"]/span/a', differ=1))
        
    def register(self, code):
        logger.info(f"사전등록: {code}")
        try:
            self.go_detail_page(code)

            # 입찰참가신청서 작성
            self.click(s.Id("입찰참가신청서 작성 버튼","btn_join"))
            
            alert = s.Alert("입찰참여 팝업","입찰참가등록이 미완료된 건", timeout=3)
            if self.exist(alert):
                self.accept(alert)

            # popup message: 해당 선택하신 건은 이미 입찰참가등록이 신청 완료된 건입니다. 해당건의 진행상태를 확인하세요.
            alert = s.Alert("입찰참여 완료 팝업", "입찰참가등록이 신청 완료된 건입니다.", timeout=3)
            if self.exist(alert):
                logger.info("이미 참여하였습니다.")
                self.accept(alert)
                return True
            
            time.sleep(2)
            logger.info("서약서 작성")
            self.click(s.Id("서약서 체크박스",'c_box1'))
            self.click(s.Id("서약서 체크박스",'c_box2'))
            self.click(s.Id("수의계약각서 체크박스",'c_box3') )
            self.click(s.Id("하도급 대금의 지급관련 확인 및 확약서",'subcont_dir_pay_yn1'))
            self.click(s.Id("확인 버튼",'btn_confirm'))

            logger.info("보증금납부 방법")

            self.select(s.Id("보증금 납부방법 선택", 'grnt_mthd'), '보증금면제')
            
            # 보증금납부에 대한 서약서 확인
            logger.info("보증금 동의문")
            self.click(s.Id("입찰보증금 지급확약서", 'c_box2'))
            self.click(s.Id("입찰보증금 면제사유 확약서", 'c_box3'))
            self.click(s.Xpath("확인버튼",'//div[5]/div[2]/div[2]/div/div/div[3]/button[1]'))

            # 약관 동의 체크
            logger.info("약관 동의 체크")
            self.click(s.Id("약관 동의", 'bidAttention_check'))
            self.click(s.Id("신청 버튼", 'btn_wrt'))

            self.accept(s.Alert("",""))

            logger.info("인증서 로그인(사업자)")
            self.certificate("사업자")

            # 팝업 확인
            self.accept(s.Alert("",""))

            # ACTION: "닫기" 버튼이 있고, 보인다면 클릭.
            close_btn = s.Xpath('닫기 버튼', '//*[@id="layer"]/div[2]/div/div/div[2]/button[3]', timeout=3 )
            if self.exist(close_btn):
                self.click(close_btn)
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
    def __participate_without_registration(self, code, cost):
        
        logger.info("사전등록이 필요없는 입찰 참가 시작")

        self.go_detail_page(code)

        if self.exist(s.Id("견적서조회버튼", 'btn_estimate_inquiry', timeout=3)):
            logger.info("이미 참여하였습니다.")
            return True
        
        self.click(s.Xpath('견적서작성버튼', '//button[@id="btn_estimate_write"]'))

        logger.info("서약서 작성")
        self.clicks(s.Xpath("서약서 체크박스", '//input[@type="checkbox" and @name="a1"]', differ=1))
        self.click(s.Id("확인버튼", 'btn_oath_confirm', differ=5))

        logger.info("견적서 작성")
        self.type(s.Id("견적금액 작성", "input_amount"), cost)

        # 사업자 등록증 제출
         
        filepath = os.path.join(os.path.expanduser("~"), ".iaa", "business_regstration_certificate.zip")
        self.type(s.Id("파일첨부버튼", "input_file_basic1"), filepath)
        
        self.clicks(
            s.Xpath("복수예비가격 선택", '//input[@name="check_multi_price"]'), num_samples=2)

        time.sleep(3)

        self.click(s.Id("제출 버튼", "btn_submit"))
        self.accept(s.Alert("견적서 제출 확인 팝업", ""))

        logger.info("지문인식 예외입찰 확인")
        self.click(s.Id("지문인식 예외입찰 버튼", "btn_bio_excp"))
        self.certificate("은행")
        self.accept(s.Alert("견적서 제출 확인 팝업", "견적서를 성공적으로  제출하였습니다.", timeout=20))

        return True

    def get_pre_registration_table(self):
        # 참가신청서 조회 페이지로 이동이 안되는 경우가 있다. 페이지가 아직 로딩이 안된 상태여서? 
        time.sleep(3)
        self.go(s.Url("물품 참가신청서 조회 페이지", 'https://www.d2b.go.kr/pdb/bid/goodsBidSubmitList.do'))
        time.sleep(3)
        tables = []

        # 물품 입찰서 신청의 경우 판단번호가 첫번째 column에 있다.
        goods_table = s.Id("참가신청서 테이블", 'SBHE_DATAGRID_WHOLE_TABLE_datagrid1', timeout=30)
        if self.exist(goods_table):
            tables.append(self.table(goods_table))

        self.go(s.Url("용역 참가신청서 조회 페이지", 'https://www.d2b.go.kr/psb/bid/serviceBidApplyList.do'))
        time.sleep(3)
        service_table = s.Id("참가신청서 테이블", 'SBHE_DATAGRID_WHOLE_TABLE_datagrid1', timeout=30)
        if self.exist(service_table):
            table = self.table(service_table)
            if table is not None:
                # 용역 입찰서 신청의 경우 앞에 순번 column이 있어 다른 column들이 한칸씩 뒤에 있다. 
                # table에서 첫번째 "순번" column을 삭제한다.
                table.drop(table.columns[0], axis=1, inplace=True)
                tables.append(table)

        tables = [ t for t in tables if t is not None]
        return pd.concat(tables, ignore_index=True)

    def participate_with_registration(self, code, cost):
        logger.info("사전등록이 완료된 입찰 참가 시작")

        # 사전등록이 되어 있는지 검증.
        logger.warning("참가신청서 검색.")
        regs = self.get_pre_registration_table()
        # 판단 번호 column 1
        row = regs[(regs[1].notna()) & (regs[1].astype(str).str.contains(code))]
        if row.empty:
            logger.warning("검색된 참가신청서가 없습니다.")
            logger.warning("참가신청서에 등록된 판단번호:")
            # 판단번호 컬럼을 문자열로 변환하지 않고, 원래 타입이 object(문자열)로 유지되도록 DataFrame 생성 시 처리 필요
            # 여기서는 출력만 한 줄로, float은 소수점 이하 제거
            values = regs[1].dropna().apply(lambda x: f"{int(x)}" if isinstance(x, float) and x.is_integer() else str(x))
            logger.warning(", ".join(values))
            return False
        
        status = str(row.iloc[0,5])
        logger.info(f"참가신청서 상태: {status}")
        if "제출" == status:
            logger.info("이미 투찰이 완료되었습니다.")
            return True
        
        elif "미제출" != status:
            logger.error(f"알수 없는 상태입니다. - {row.iloc[0,5]}")
            return False
        
        # TODO: 입찰서 진행 상태 확인..
        self.go(s.Url("입찰서제출(물품)", "https://www.d2b.go.kr/pdb/bid/goodsBidSubmitList.do"))
        item = s.Xpath("입찰서 선택", f'//tr/td[1]/div/span[contains(text(),"{code}")]', differ=3)
        if not self.exist(item):
            self.go(s.Url("입찰서제출(용역)", "https://www.d2b.go.kr/pdb/bid/serviceBidSubmitList.do"))
        self.click(item)
        self.click(s.Id("입찰서 작성 버튼", 'btn_bid_regi'))

        self.type(s.Id("가격 입력 상자","bid_amnt_1"), cost)
        self.clicks(s.Xpath("추첨 체크박스", '//td/input[@type="checkbox"]'), num_samples=2)
        self.click(s.Id("동의 체크박스", "c_box"))

        self.click(s.Id("제출 버튼", "btn_bid_submit"))
        self.accept(s.Alert("",""))

        self.click(s.Id("지문인식 예외 입찰 버튼", "btn_bio_excp"))
        self.certificate("은행")
        self.accept(s.Alert("견적서 제출 확인", ""))

        return True


    # 판단번호로 변경
    # 만약 공고 번호에 수의 가 포함되어 있다면 판단 번호에 확장하여 
    # code를 제공해야 한다. 
    def participate(self, code, cost):
        # decuding code to be searchable
        # ex. 수의LCJ0021-1-2024-00 -> LCJ0021
        # ex. 2023UMM032323380-01 -> UMM032323380
        logger.info(f"입찰참여: 판단코드={code}, cost={cost}")

        need_regstration = "수의" in code
        code = code.replace("수의", "")
        # 소수점이 있을 경우 입력이 불가하다고 안내한다. 
        cost = int(float(cost))

       
        try:
            
            # 견적서작성 버튼이 있으면 입찰참가가 필요 없다.
            # TODO: 코드에 "수의"가 있으면 사전등록이 필요없는 공고이다. 
            # if self.exist(s.Xpath('견적서작성버튼', '//button[@id="btn_estimate_write"]')):
            if need_regstration:
                return self.__participate_without_registration(code, cost)
            else:
                return self.participate_with_registration(code, cost)
            
        except Exception as e:
            logger.error(e)
            traceback.print_exc()
            return False