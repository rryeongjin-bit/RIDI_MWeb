from config.settings import * 

# 테스트 계정
class TestAccount:
    AOS = {
        "id": AOS_TEST_ID,
        "pw": AOS_TEST_PW,
    }
    IOS = {
        "id": IOS_TEST_ID,
        "pw": IOS_TEST_PW,
    }

# 딥링크 URL (앱 내부 페이지 진입용)
class DeepLinks:
    HOME             = "ridi://GenreHome/%EC%9B%B9%ED%88%B0/%EC%9B%B9%ED%88%B0/%EB%A1%9C%EB%A7%A8%EC%8A%A4"
    SEARCH           = "ridi://search"
    LIBRARY          = "ridi://Library"
    NOTIFICATION     = "ridi://NotificationCenter/%EC%A0%84%EC%B2%B4"
    MYRIDI           = "ridi://MyRidi"
    LOGIN            = "ridi://SignIn"
    CART             = "ridi://CartWebView/https%3A%2F%2Fridibooks.com%2Fcart/%EC%B9%B4%ED%8A%B8"

    CONTENT_ALL_AGES = "ridi://ContentsHome/5847000001"  # 로판 웹툰 > 두 명의 상속인
    CONTENT_ADULT    = "ridi://ContentsHome/2057208584"  # BL 웹소설 > 꽃은 밤을 걷는다
    CONTENT_CART     = "ridi://ContentsHome/4395000113" # 만화e북 > 마왕성 요리사


