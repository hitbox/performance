class FormGetter:
    """
    Call instances to return form instance. Useful for dynamically created
    forms.
    """

    def __init__(self, form_class, new_form_class=None):
        self.form_class = form_class
        self.new_form_class = new_form_class

    def __call__(self, instance):
        if instance:
            form = self.form_class(obj=instance)
            form.submit.label.text = 'Update'
        else:
            form_class = self.new_form_class or self.form_class
            form = form_class()
            form.submit.label.text = 'Create'
        return form
