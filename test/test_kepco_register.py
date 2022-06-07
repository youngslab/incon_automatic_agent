

from org.kepco import *


def wait():
    input('.\n')


if __name__ == '__main__':

    id = account.account_get("kepco", "id")
    pw = account.account_get("kepco", "pw")
    cert = account.account_get("kepco", "cert")

    driver = kepco_create_driver()
    kepco_go_homepage(driver)

    wait()

    kepco_login(driver, id, pw, cert)

    wait()

    # 1.1 입찰 참가신청 페이지로 이동
    kepco_pre_go_register_page(driver)

    number = input('Please Enter notice number \n')

    # 1.2 조회
    log().info("1.2 search")
    kepco_pre_search_notice_number(driver, number)

    wait()

    #  1.3
    log().info("1.3 validate")
    if kepco_pre_is_current_registered(driver):
        log().info("Already registered")

    wait()

    log().info("1.4 apply")
    kepco_pre_apply_participation(driver)

    wait()

    # 2. Application Form
    # 2.1.  메세지등의 팝업을 처리한다.
    log().info("2.1 close popup")
    kepco_pre_close_popup(driver)

    wait()

    # 2.2. 중소기업확인서 첨부
    log().info("2.2 attach a file")
    filepath = os.path.join(os.path.expanduser("~"), ".iaa", "AR_중소기업_확인서.pdf")
    kepco_attach_small_business_confirmation_document(driver, filepath)

    wait()

    # XXX: 빠르게 진행하기 때문에 다시 제출하라는 문구가 뜨는 것 같음
    time.sleep(5)

    # 모든 조항에 동의
    log().info("2.3 aggreement")
    kepco_pre_agree_commitments(driver)

    wait()

    # XXX: 빠르게 진행하기 때문에 다시 제출하라는 문구가 뜨는 것 같음
    time.sleep(5)

    # 2.3 제출 버튼 클릭
    log().info("2.4 submit")
    kepco_pre_submit_application_form(driver)

    wait()

    # 3. 정리
    # 3.1 확인
    log().info("3.1 confirm")
    kepco_pre_confirm_submission(driver)

    wait()

    # 3.2 certificate login
    log().info("3.2 certifiate")
    kepco_certificate_login(driver, "GetLastError#2")

    wait()

    log().info("3.3 done")
    kepco_pre_confirm_done(driver)

    wait()
