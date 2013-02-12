from megacms.basewidgets.widgetviews import default_get, default_post


REGISTER = dict()


DEFAULTS = dict(
    GET=default_get,
    POST=default_post,
)


def register_widget(widget_class, get=None, post=None):
    if widget_class in REGISTER:
        raise Exception('Duplicate widget registration')
    else:
        REGISTER[widget_class] = dict(
            GET=get,
            POST=post,
        )
