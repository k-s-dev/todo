from django import forms as djf


class CustomModelForm(djf.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if visible.field.widget.__class__.__name__ == djf.Select().__class__.__name__:
                visible.field.widget.attrs["class"] = "form-select"
            elif visible.field.widget.__class__.__name__ == djf.CheckboxInput().__class__.__name__:
                visible.field.widget.attrs["class"] = "form-check-input"
                visible.field.widget.attrs["role"] = "switch"
            elif visible.field.widget.__class__.__name__ == djf.Textarea().__class__.__name__:
                visible.field.widget.attrs["rows"] = "5"
                visible.field.widget.attrs["class"] = "form-control"
            else:
                visible.field.widget.attrs["class"] = "form-control"
