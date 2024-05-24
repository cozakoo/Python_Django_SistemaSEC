from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.forms import AuthenticationForm

class SecAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        #self.helper.form_id = 'id-exampleForm'
        #self.helper.form_class = 'blueForms'
        #self.helper.form_method = 'post'
        #self.helper.form_action = 'submit_survey'

        self.helper.add_input(
            Submit('submit', 'Ingresar', css_class="w-100 btn btn-lg btn-primary"))
