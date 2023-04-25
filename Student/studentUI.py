# import the library
from appJar import gui
rat = {"name": "name1",
       "size": "10",
       "q1": {"q": "Hva er ost laget av?",
              "alternatives": {
                  "a": "meeee eeee e eeee eee eeeee eeee ee eee e eeeeee eeeeeeeee eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeelk",
                  "b": "ost",
                  "c": "blomster",
                  "d": "høy"}},
       "q2": {"q": "Hva er ost laget av?",
              "alternatives": {
                  "a": "melk",
                  "b": "ost",
                  "c": "blomster",
                  "d": "høy"}}}


class StudentUI():
    def __init__(self):
        self.rat = None
        self.answers = []

    def start_irat(self):
        self.app.showSubWindow("conduct_irat")
        self.app.setMessage("irat_name", self.rat["name"])
        self.app.setMessage("irat_q", self.rat["1"]["question"])
        alt = ["correct", "a", "b", "c"]
        i = 1
        for alternative in alt:

            self.app.setMessage("irat_" + str(i), self.rat["1"][alternative])

        if "2" not in self.rat:
            self.app.hideButton("irat_next")
            self.app.showButton("irat_send")

    def create_ui(self):

        def sign_in():
            student_id = self.app.getEntry("id")
            name = self.app.getEntry("Name")
            team = self.app.getEntry("Team")
            self.student = {"student_id": student_id,
                            "name": name, "team": team, "subject": "TTM4115"}
            self.app.hideSubWindow("sign_in")
            self.app.removeAllWidgets()
            self.app.addLabel("info", "Waiting")
            self.stm_driver.send("sign_in", "student")

        def open_login():
            self.app.showSubWindow("sign_in")

        def cancel():
            self.stm_driver.send("cancel", "student")
            self.app.hideSubWindow("sign_in")

        def next_irat_question():
            ans =
            alt = ""

            self.answers.append(check_answer(rat[]))

            q_num = "q" + str(int(self.app.getMessage("irat_q")[1]) + 1)
            print(q_num)
            self.app.setMessage("irat_q", q_num.capitalize() + ": " +
                                self.rat[q_num]["q"])
            self.app.setMessage("irat_a", self.rat[q_num]["alternatives"]["a"])
            self.app.setMessage("irat_b", self.rat[q_num]["alternatives"]["b"])
            self.app.setMessage("irat_c", self.rat[q_num]["alternatives"]["c"])
            self.app.setMessage("irat_d", self.rat[q_num]["alternatives"]["d"])
            next_q_num = "q" + str(int(q_num[1]) + 1)
            if next_q_num not in self.rat:
                self.app.hideButton("irat_next")
                self.app.showButton("irat_send")

        def send_irat_answers():
            self.irat_answers.append(self.app.getMessage(
                "irat_" + self.app.getRadioButton("irat_answer")))
            self.stm_driver("irat_done", "student")

            self.app.hideSubWindow("conduct_irat")
            self.app.setLabel("info", "Waiting for your teammates to finish")

        def next_trat_question():
            pass

        def send_trat_answers():
            pass

        def check_answer():
            pass

        # Here comes the GUI
        self.app = gui("Student", "500x300")
        self.app.setSticky("")
        self.app.setExpand("both")
        self.app.setFont(14)

        self.app.addLabel("welcome", "Welcome")
        self.app.addButton("Login", open_login)

        # this is a subwindow for login
        self.app.startSubWindow("login", "Login", modal=True)
        self.app.addLabel("login", "Login", 0, 0, 3)
        self.app.addLabelEntry("Name")
        self.app.addLabelEntry("Team")
        self.app.addButton("cancel", cancel, 3, 1)
        self.app.setButton("cancel", "Cancel")
        self.app.addButton("login", sign_in, 3, 2)

        self.app.setButton("login", "Sign in")
        self.app.stopSubWindow()

        # this is a subwindow for correct answer
        self.app.startSubWindow("correct", "Correct Answer", modal=True)
        self.app.setSize(500, 300)
        self.app.addLabel("Correct")
        self.app.stopSubWindow()

        # this is a subwindow for incorrect answer
        self.app.startSubWindow("incorrect", "Incorrect Answer", modal=True)
        self.app.setSize(500, 300)
        self.app.addLabel("Incorrect")
        self.app.stopSubWindow()

        # this is a subwindow for conducting a iRAT
        self.app.startSubWindow("conduct_trat",
                                "Conduct a tRAT", modal=True)
        self.app.setSize(600, 800)
        self.app.setSticky("")
        self.app.setExpand("both")

        self.app.addMessage("trat_name", "", colspan=6)
        self.app.setMessageWidth("trat_name", 650)
        self.app.addMessage("trat_q", "", colspan=6)
        self.app.setMessageWidth("trat_q", 650)

        self.app.addRadioButton("trat_answer", "a", 3, 0, colspan=1)
        self.app.addMessage("trat_a", "", 3, 1, colspan=5)
        self.app.setMessageWidth("trat_a", 500)
        self.app.addRadioButton("trat_answer", "b", 4, 0, colspan=1)
        self.app.addMessage("trat_b", "", 4, 1, colspan=5)
        self.app.setMessageWidth("trat_b", 500)
        self.app.addRadioButton("trat_answer", "c", 5, 0, colspan=1)
        self.app.addMessage("trat_c", "", 5, 1, colspan=5)
        self.app.setMessageWidth("trat_c", 500)
        self.app.addRadioButton("trat_answer", "d", 6, 0, colspan=1)
        self.app.addMessage("trat_d", "", 6, 1, colspan=5)
        self.app.setMessageWidth("trat_d", 500)

        self.app.addButton("trat_send", send_trat_answers, colspan=6)
        self.app.setButton("trat_send", "Send")
        self.app.addButton("Check", check_answer, colspan=6)
        self.app.addButton("trat_next", next_trat_question, colspan=6)
        self.app.setButton("trat_next", "Next question")
        self.app.hideButton("trat_send")
        self.app.hideButton("trat_next")
        self.app.stopSubWindow()

        # this is a subwindow for conducting a iRAT
        self.app.startSubWindow("conduct_irat",
                                "Conduct a iRAT", modal=True)
        self.app.setSize(600, 800)
        self.app.setSticky("")
        self.app.setExpand("both")

        self.app.addMessage("irat_name", "", colspan=6)
        self.app.setMessageWidth("irat_name", 650)
        self.app.addLabel("irat_q_nr", "1")
        self.app.addMessage("irat_q", "", colspan=6)
        self.app.setMessageWidth("irat_q", 650)

        self.app.addRadioButton("irat_answer", "a", 3, 0, colspan=1)
        self.app.addMessage("irat_a", "", 3, 1, colspan=5)
        self.app.setMessageWidth("irat_a", 500)
        self.app.addRadioButton("irat_answer", "b", 4, 0, colspan=1)
        self.app.addMessage("irat_b", "", 4, 1, colspan=5)
        self.app.setMessageWidth("irat_b", 500)
        self.app.addRadioButton("irat_answer", "c", 5, 0, colspan=1)
        self.app.addMessage("irat_c", "", 5, 1, colspan=5)
        self.app.setMessageWidth("irat_c", 500)
        self.app.addRadioButton("irat_answer", "d", 6, 0, colspan=1)
        self.app.addMessage("irat_d", "", 6, 1, colspan=5)
        self.app.setMessageWidth("irat_d", 500)

        self.app.addButton("irat_send", send_irat_answers, colspan=5)
        self.app.setButton("irat_send", "Send")
        self.app.addButton("irat_next", next_irat_question, colspan=5)
        self.app.setButton("irat_next", "Next question")
        self.app.hideButton("irat_send")
        self.app.stopSubWindow()

        self.app.go()


def check_answer(question, answer):
    if answer == question["correct"]:
        return "correct"
    elif answer == question["a"]:
        return "a"
    elif answer == question["b"]:
        return "b"
    elif answer == question["c"]:
        return "c"
