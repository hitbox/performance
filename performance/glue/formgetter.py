class FormGetter:
    """
    Call instances to return form instance. Useful for dynamically created
    forms.
    """
    main_button_attr = 'submit'

    def __init__(
        self,
        form_class,
        new_form_class = None,
        main_button_attr = None,
    ):
        """
        :param form_class:
            callable returning instance of form.
        :param new_form_class:
            optional callable for version of form appropriate for creating new objects.
        :param main_button_attr:
            optional name of attribute on form instance to relabel depending on
            whether an instance exists.
        """
        self.form_class = form_class
        self.new_form_class = new_form_class
        self.main_button_attr = main_button_attr or self.main_button_attr

    def __call__(self, instance):
        if instance:
            form = self.form_class(obj=instance)
            button = getattr(form, self.main_button_attr)
            button.label.text = 'Update'
        else:
            form_class = self.new_form_class or self.form_class
            form = form_class()
            button = getattr(form, self.main_button_attr)
            button.label.text = 'Create'
        return form
