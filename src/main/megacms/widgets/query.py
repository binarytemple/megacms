import logging


log = logging.getLogger(__name__)


def get_match_by_path(path):
    from megacms.basewidgets.widgetmodels import URLNode
    matches = (URLNode.all()
               .filter('denormalized_url = ', path)
               .fetch(None))
    if len(matches) > 1:
        raise Exception(
            'Found %s matches, expected only one for path '
            '"%s"' % (len(matches), path))
    return matches[0] if len(matches) == 1 else None


def get_direct_element_children(node):
    from megacms.basewidgets.widgetmodels import Widget
    return (Widget.all()
            .filter('element_parent =', node.key())
            .order('element_order')
            .fetch(limit=None))


def get_direct_url_node_children(node):
    from megacms.basewidgets.widgetmodels import URLNode
    assert isinstance(node, URLNode)
    ret = (
        URLNode.all()
        .filter('url_parent =', node.key())
        .order('url_order')
        .fetch(limit=None))
    return ret


def get_url_node_descendants(node):
    from megacms.basewidgets.widgetmodels import URLNode
    assert isinstance(node, URLNode)
    for child in get_direct_url_node_children(node):
        yield child
        for grandchild in get_url_node_descendants(child):
            yield grandchild
