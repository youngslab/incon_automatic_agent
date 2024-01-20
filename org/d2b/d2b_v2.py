
import automatic as auto
import automatic.browser as b


def elem():
    pass


class D2B:
    def __init__(self, driver):

        self.driver = driver
        self.bctx = auto.browser.Context(
            driver, "https://www.d2b.go.kr/index.do", default_timeout=30)

        self.wctx = auto.win32.Context()

    def login(self, token):
        self.bctx.set_url("https://www.d2b.go.kr/index.do")

        res = (elem(self.bctx, "id", "_mLogin",
                    desc="로그인 버튼").click()
               and elem(self.bctx, "id", "_fingerLoginBtn",
                        desc="지문인식 로그인 버튼").click(differed=5)
               and b.Alert(self.bctx).accept("")
               and elem(self.bctx, "id", "NX_MEDIA_BIOHSM",
                        desc="지문 토큰").click()
               and elem(self.bctx, "xpath", "//*[@id='nx-cert-select']/div[3]/div[1]/div[3]",
                        desc="지문 토큰 - BIO").click()
               and elem(self.bctx, "xpath", f"//div[@id='cert-select-area3']/table/tbody/tr/td[contains(text(), '{token}')]",
                        desc=f"지문 토큰 - {token}").click()
               and elem(self.bctx, "xpath", "//*[@id='pki-extra-media-box-contents3']/div[3]/button",
                        desc=f"로그인 확인 버튼").click()
               and elem(self.bctx, "id", "nx_cert_pin",
                        desc=f"PIN 입력 상자").type("00000000", timeout=120)
               and elem(self.bctx, "xpath", "//*[@id='pki-extra-media-box-contents3']/div[3]/button",
                        desc=f"로그인 확인 버튼").click())

        auto.elem("b", ctx.b, by="id", path="xxx", parent=xx,
                  desc="xxx").click()
