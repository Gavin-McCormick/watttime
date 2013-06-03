from django import forms
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.template import Template

def hidden_id(id):
  return forms.CharField(initial=id, widget=forms.HiddenInput())

# http://www.djangosnippets.org/snippets/863/ z moimi zmianami
class ChoiceWithOtherRenderer(forms.RadioSelect.renderer):
    """RadioFieldRenderer that renders its last choice with a placeholder."""
    def __init__(self, *args, **kwargs):
        super(ChoiceWithOtherRenderer, self).__init__(*args, **kwargs)
        self.choices, self.other = self.choices[:-1], self.choices[-1]

    def __iter__(self):
        for inp in super(ChoiceWithOtherRenderer, self).__iter__():
            yield inp
        id = '%s_%s' % (self.attrs['id'], self.other[0]) if 'id' in self.attrs else ''
        label_for = ' for="%s"' % id if id else ''
        checked = '' if not force_unicode(self.other[0]) == self.value else 'checked="true" '
        
        html = '<label%s><input type="radio" id="%s" value="%s" name="%s" %s/> %s</label> %%s' %        \
                   (label_for, id, self.other[0], self.name, checked, self.other[1])
        yield html

class ChoiceWithOtherWidget(forms.MultiWidget):
    """MultiWidget for use with ChoiceWithOtherField."""
    def __init__(self, choices):
        widgets = [
            forms.RadioSelect(choices=choices, renderer=ChoiceWithOtherRenderer),
            forms.TextInput
        ]
        super(ChoiceWithOtherWidget, self).__init__(widgets)

    def decompress(self, value):
        if not value:
            return [None, None]
        return value

    def format_output(self, rendered_widgets):
        """Format the output by substituting the "other" choice into the first widget."""
        return rendered_widgets[0] % rendered_widgets[1]

class ChoiceWithOtherField(forms.MultiValueField):
    """
    ChoiceField with an option for a user-submitted "other" value.
    """
    def __init__(self, *args, **kwargs):
        fields = [
            forms.ChoiceField(widget=forms.RadioSelect(renderer=ChoiceWithOtherRenderer), *args, **kwargs),
            forms.CharField(required=False)
        ]
        widget = ChoiceWithOtherWidget(choices=kwargs['choices'])
        kwargs.pop('choices')
        self._was_required = kwargs.pop('required', True)
        kwargs['required'] = False
        super(ChoiceWithOtherField, self).__init__(widget=widget, fields=fields, *args, **kwargs)

    def compress(self, value):
        if self._was_required and (not value or value[0] in (None, '')):
            raise forms.ValidationError(self.error_messages['required'])
        if not value:
            return [None, u'']
        return (value[0], value[1]
          if force_unicode(value[0]) == force_unicode(self.fields[0].choices[-1][0])
          else self.fields[0].choices[int(value[0]) - 1][1])
