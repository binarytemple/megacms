# These are node 'views'. Every node can respond to a request, but returns
# a dict rather than an HTTPResponse.
from megacms.basewidgets.widgetmodels import Widget

from megacms.common.utils import camel_case_to_hyphenated
from megacms.widgets.noderesponses import NodeResponse


def _node_to_dict(node):
    return dict([(k, getattr(node, k))
                 for k in node.properties().keys()
                 if not k.startswith('_') and not k.endswith('_parent')])


def default_get(request, node):
    """Handle GET at the widget level.

    """
    data = _node_to_dict(node)
    css_classes = getattr(node, 'extra_css_classes', [])[:]
    css_classes.append(camel_case_to_hyphenated(node.__class__.__name__))

    data.update(
        css_classes=css_classes,
        key=str(node.key()),
        class_name=node.__class__.__name__,
        is_terminal=node.is_terminal,
    )
    return NodeResponse(data)


def default_post(request, node):
    """Handle POST at the widget level.

    """
    return default_get(request, node)
