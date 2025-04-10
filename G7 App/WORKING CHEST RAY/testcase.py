from seleniumbase import BaseCase

class AutomatedTests(BaseCase):
    
    def test_input_boxes_signup(self):
            self.open("http://127.0.0.1:5000/patient/register")
    
            # Fill the form
            self.type("#Fname", "Ray chester")

            self.type("#DOB", "1990-08-15")  # Use YYYY-MM-DD format for <input type="date">

            self.type("#HAD", "secure123")

            self.type("#CN", "0777777777")

            self.type("#Email", "raychest.pw@chestray.com")

            self.type("#NOK", "mickey chester")

            self.type("#NOKD", "brother")

            self.type("#password", "password2424")

            self.click("button[type='submit']")
 

    def test_login_validation(self):
        self.open("http://127.0.0.1:5000/login")

        # put in login credentials
        self.type("#Username", "dr.james.wilson@chestray.com")
        self.type("#Password", "password7867")
        self.click("button[type='submit']")

    def test_change_input_data(self):

        self.open("http://127.0.0.1:5000/login")

        # put in login credentials
        self.type("#Username", "dr.charlie@chestray.com")

        self.type("#Password", "password789")

        self.click("button[type='submit']")


    def test_change_input_data_1(self):

        self.open("http://127.0.0.1:5000/login")

        # put in login credentials
        self.type("#Username", "syeed.pw@chestray.com")

        self.type("#Password", "123")

        self.click("button[type='submit']")
