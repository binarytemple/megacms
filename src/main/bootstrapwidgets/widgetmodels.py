from google.appengine.ext import db

from megacms.basewidgets.widgetmodels import Widget


class ContainerWidget(Widget):
    extra_css_classes = ['container']


class RowWidget(Widget):
    extra_css_classes = ['row']


class SpanWidget(Widget):

    columns = db.IntegerProperty()

    @property
    def extra_css_classes(self):
        return ['span', 'span%s' % self.columns]
