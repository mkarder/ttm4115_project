# import the library
from appJar import gui
import time


class TeacherUserInterface():
    def __init__(self, teacher):
        self.teacher = teacher

        self.rat = None
        self.create_ui()

    def create_ui(self):

        def new_rat(btn):
            app.showSubWindow("create_rat")

        def create_rat(btn):
            name = app.getEntry("Name")
            size = app.getEntry("Size")
            self.rat = self.teacher.create_rat(name, size)

            app.entry("Name", "")
            app.entry("Size", "10")

            app.label("rat_name", self.rat.subject +
                      " " + name + "        " + str(int(size)))
            app.label("Question", "Question " + str(self.rat.question_counter+1))
            if self.rat.question_counter == self.rat.size:
                app.hideButton("Next")
                app.showButton("Save")
            app.showSubWindow("create_question")

            app.hideSubWindow("create_rat")

        def create_question(btn):
            q = app.getEntry("Question")
            a = app.getEntry("Correct alternative")
            b = app.getEntry("Alternative A")
            c = app.getEntry("Alternative B")
            d = app.getEntry("Alternative C")
            self.teacher.create_question(self.rat.id, q, a, [b, c, d])

            app.label("Question", "Question " + str(self.rat.question_counter + 1))
            app.entry("Question", "")
            app.entry("Correct alternative", "")
            app.entry("Alternative A", "")
            app.entry("Alternative B", "")
            app.entry("Alternative C", "")
            if self.rat.question_counter == self.rat.size - 1:
                app.hideButton("Next")
                app.showButton("Save")

        def save_rat(btn):
            create_question(btn)
            self.teacher.save_rat(self.rat.id)
            app.hideSubWindow("create_question")
            app.showButton("Next")
            app.hideButton("Save")
            self.rat = None

        def publish_rat():
            rat_name = app.getListBox("Available RATs")[0]
            self.teacher.publish_rat(rat_name)

        def refresh_rats():
            self.teacher.fetch_rat()
            time.sleep(1)
            app.clearListBox("Available RATs", callFunction=True)
            for k,v in self.teacher.available_rats.items():
                app.addListItem("Available RATs", v)

        app = gui("Teacher", "800x600")
        app.setSticky("")
        app.setExpand("both")
        app.setFont(20)

        app.addLabel("title", "RATs", 0, 0, 2)
        app.addButton("new", new_rat, 0, 2)
        app.setButton("new", "New RAT")
        app.addButton("publish", publish_rat)
        app.setButton("publish", "Publish selected RAT")
        app.addListBox("Available RATs", [], 2, 0, 2)
        refresh_rats()

        # this is a subwindow for creating a new RAT
        app.startSubWindow("create_rat", "Create a RAT", modal=True)
        app.setSize(500, 300)
        app.setSticky("")
        app.setExpand("both")
        app.addLabelEntry("Name")
        app.addLabelNumericEntry("Size")
        app.entry("Size", "10")
        app.addButton("Create new question", create_rat)
        app.stopSubWindow()

        # this is a subwindow for creating a new question
        app.startSubWindow("create_question",
                           "Create A question", modal=True)
        app.setSize(500, 300)
        app.setSticky("")
        app.setExpand("both")
        app.addLabel("rat_name", "")
        app.addLabelEntry("Question")
        app.addLabelEntry("Correct alternative")
        app.addLabelEntry("Alternative A")
        app.addLabelEntry("Alternative B")
        app.addLabelEntry("Alternative C")
        app.addButton("Save", save_rat)
        app.addButton("Next", create_question)
        app.hideButton("Save")
        app.stopSubWindow()

        # app.addButton("Update available RATs", refresh_rats)

        app.addButton('QUIT', app.stop, 2, 2, 2)
        app.addButton('Refresh RATs', refresh_rats)

        app.go()
