import kivy

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from mongoengine import connect

from questionModule import QuestionModule
from audit_template import AuditTemplateBuilder, Question

kivy.require("1.11.1")

# Loads in the .kv file which contains the CreateAuditPage layout.
Builder.load_file("./widgets/create_audit_page.kv")


# The popup used for both the back and submit buttons
class ConfirmationPop(Popup):
    yes = ObjectProperty(None)

    def return_admin_page(self):
        self.dismiss()
        self.manager.current = 'AdminScreen'


# This class contains the functions and variables used in the audit creation page.
class CreateAuditPage(Screen, FloatLayout):
    # This counter tracks the number of questions added to the form
    q_counter = 0
    # The id for the StackLayout, Used to add questions to the layout.
    stack_list = ObjectProperty()
    # The id for the title section of the audit.
    audit_title = ObjectProperty()
    # A dictionary used to store and access questions.
    question_list = {}

    connect("testdb")

    # The add_question method creates a new instance of the question widget, adds it to the StackLayout, and adds it
    # to the question list dictionary.
    def add_question(self):
        self.stack_list.height += 200
        q_temp = QuestionModule()
        q_temp.q_id = self.q_counter
        self.q_counter += 1
        self.stack_list.add_widget(q_temp)
        q_temp.delete_question.bind(on_press=lambda x: self.del_question(q_temp.q_id))
        self.question_list[str(q_temp.q_id)] = q_temp

    # shows the confirmation popup and sets the yes button functions
    def submit_audit_pop(self, manager):
        show = ConfirmationPop()
        show.yes.bind(on_press=self.clear_page)
        show.yes.bind(on_press=self.submit_audit)
        show.manager = manager
        show.open()

    # Function called after user selects yes on the confirmation popup
    def submit_audit(self, callback):
        # Create a new audit using the supplied text the admin has entered.
        audit_template = AuditTemplateBuilder()
        audit_template.with_title(self.audit_title.text)
        for question in self.question_list.values():
            q = Question(text=question.question_text.text, yes=question.yes_severity, no=question.no_severity,
                         other=question.other_severity)
            audit_template.with_question(q)

        audit_template.build().save()

    # shows the confirmation popup and sets the yes button function
    def back(self, manager):
        show = ConfirmationPop()
        show.yes.bind(on_press=self.clear_page)
        show.manager = manager
        show.open()

    # deletes the question with the passed in q_id from the stack_list and the question_list
    def del_question(self, q_id):
        self.stack_list.remove_widget(self.question_list[str(q_id)])
        del self.question_list[str(q_id)]
        self.stack_list.height -= 200

    # deletes all questions from the stack_list and the question_list, sets all counters to their default values
    def clear_page(self, callback):
        for question in self.question_list:
            self.stack_list.remove_widget(self.question_list[question])
            self.stack_list.height -= 200
        self.question_list.clear()
        self.q_counter = 0
        self.audit_title.text = ""


class TestApp(App):
    def build(self):
        return CreateAuditPage()


if __name__ == "__main__":
    TestApp().run()
