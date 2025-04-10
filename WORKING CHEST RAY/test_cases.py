from seleniumbase import BaseCase

class AutomatedTests(BaseCase):

    def test_change_input_data(self):
        # Login and navigate to upload page
        self.open("http://127.0.0.1:5000/health_worker/dashboard")

        # Upload first image
        self.choose_file("input[type='file']", "tests/images/xray1.jpg")
        self.click("button#submit")
        self.assert_text("Upload successful", "#status")

        # Upload a new image
        self.choose_file("input[type='file']", "tests/images/xray2.jpg")
        self.click("button#submit")

        # Validate change in output/result
        self.assert_text_not_visible("xray1.jpg", "#preview")
        self.assert_text("xray2.jpg", "#preview")

def test_state_change_on_next_button(self):
    # Open initial page
    self.open("http://127.0.0.1:5000")
    
    # Click next and check new page content
    self.click("button#next-step")
    self.assert_element("div#step2-container")

def test_input_boxes_signup(self):
    self.open("http://127.0.0.1:5000/patient/register")
    
    # Fill the form
    self.type("#Full name", "Ray chester")
    self.type("#dd/mm/yyyy", "15/08/1990")
    self.type("#home adress", "secure123")
    self.type("#contsct number", "0777777777")
    self.type("#email", "raychest.pw@chestray.com")
    self.type("#next of kin", "mickey chester")
    self.type("#next of kin details", "brpther")
    self.type("#password", "passwrod2424")
    self.click("#signup-btn")
    
    # Check if redirected or confirmed
    self.assert_text("Welcome", "#greeting")

def test_login_validation(self):
    self.open("http://127.0.0.1:5000/login")

    # put in login credentials
    self.type("#email", "dr.james.wilson.hw@chestray.com")
    self.type("#password", "password7867")
    self.click("#login-btn")

        # Check if redirected or confirmed
    self.assert_text("Welcome", "#greeting")
