from megacms.basewidgets.widgetmodels import (
    Widget, HTMLWidget, Document, ViewResource)
from megacms.widgets.register import register_widget

register_widget(Widget)
register_widget(HTMLWidget)
register_widget(Document)
register_widget(ViewResource)
