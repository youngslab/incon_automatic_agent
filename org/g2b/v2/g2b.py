
import threading

import automatic as am
import automatic.selenium as s
import automatic.win32 as w
from automatic.selenium.utils import create_driver


class G2B(am.Automatic):
    def __init__(self, driver, pw=None, headless=True):
        self.homepage = 'https://www.g2b.go.kr'
        self.__driver = driver

        selenium = s.Context(self.__driver, timeout=20, differ=0)
        win32 = w.Context(timeout=50, differ=0)
        self.pw = pw

        super().__init__([selenium])

    def login(self):
        # Step: 홈페이지로 이동
        try:
            self.go(s.Url("G2B 홈페이지", self.homepage))
            fLogin = s.Id("로그인프레임", 'member_iframe')
            self.click(s.Id("지문인식 예외적용 버튼", 'arg_exceptionLogin' ,parent=fLogin))
            self.click(s.Xpath("로그인버튼",'//*[@id="logout"]/ul/li[0]/ul/li/a/img' ,parent=fLogin))
            self.accept(s.Alert("팝업", '계속 진행하시겠습니까?'))

            wMain = w.Title('', "메인윈도우")
            self.click(w.Image('path', "로그인버튼", parent=wMain))

            # Frame이 변경되는데 변경되기전 frame에서 logout button을 찾기 때문에 실패한다.
            # element 찾을 때 frame도 다시 찾는 방법으로 문제를 해결한다.
            # 대략 30회, 즉 30초 가량의 시간동안 시도해 본다.
            num_try = 0
            while num_try < 30:
                num_try += 1
                # 로그아웃 버튼 찾기
                fTops = s.Id("Top Frame", 'tops')
                if self.exist(s.Xpath("로그아웃버튼", "//a[text()='로그아웃']",
                                      parent=fTops)):
                    return True
        except Exception as e:

            return False



    def register(self, code):
        pass


    def participate(self, code, price):
        pass
