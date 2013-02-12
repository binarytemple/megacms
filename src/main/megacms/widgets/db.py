from google.appengine.ext import db
from google.appengine.ext.db import BadValueError
from django.template import Template, TemplateSyntaxError


class TemplateStringProperty(db.TextProperty):

    def validate(self, value):
        from megacms.basewidgets.widgetmodels import FORCED_LOAD_TAG
        # TODO: How can we forcably include a tag library without getting
        # the front end user to write {% load %} tags?
        value = super(TemplateStringProperty, self).validate(value)
        try:
            Template('\n'.join([FORCED_LOAD_TAG, value]))
        except TemplateSyntaxError:
            raise BadValueError('Property is not a valid template')
        else:
            return value
