from selenium.webdriver.common.by import By


class CommonLocators:
    ALERT_ALLOW    = (By.ID, "com.android.permissioncontroller:id/permission_message")
    ALLOW_BTN      = (By.ID, "com.android.permissioncontroller:id/permission_allow_button")

class ReplacedeviceLocators:
    REPLACEDEVICE_LIST_TITLE   = (By.ID, "com.initialcoms.ridi:id/title")
    REPLACEDEVICE_TOGGLE_FIRST = (By.XPATH, "(//android.widget.RadioButton[@resource-id='com.initialcoms.ridi:id/selection_radio_button'])[1]")
    REPLACEDEVICE_BTN          = (By.ID, "com.initialcoms.ridi:id/replace_button")

class MainhomeLocators:
    MY_BTN   = (By.XPATH, "//android.view.ViewGroup[@content-desc='MY']")

class LoginLocators:
    LOGIN_BTN    = (By.XPATH, "//android.view.ViewGroup[@content-desc='로그인']")
    ID_INPUT     = (By.XPATH, "//android.widget.EditText[@resource-id=':R2nmnm:']")
    PW_INPUT     = (By.XPATH, "//android.widget.EditText[@resource-id=':R2nmnmH1:']")
    LOGIN_BUTTON = (By.XPATH, "//android.widget.Button[@text='로그인']")
    LOGIN_TITLE  = (By.ID,    "com.initialcoms.ridi:id/title_text")

class MyLocators:
    MY_TITLE = (By.XPATH, "(//android.widget.TextView[@text='MY'])[1]")

