import logging

from google.appengine.api import memcache

log = logging.getLogger(__name__)


def invalidate_caches_for_node(node):
    """Invalidates any caches for a node and all of its ancestor ElementNodes.
    This will invalidate caches for any Widgets and Pages.

    @param node: ElementNode
    @return: None

    """
    log.info('Invalidating caches for node "%s"' % node)
    from megacms.frontend.views import CONTENT_TYPE_HANDLERS
    from megacms.basewidgets.widgetmodels import Widget
    content_types = CONTENT_TYPE_HANDLERS.keys()

    current = node
    keys = []
    while current is not None:
        assert isinstance(node, Widget)
        keys += [cache_key_for_node(current, content_type)
                 for content_type in content_types]
        current = current.element_parent
    if not memcache.delete_multi(keys):
        log.error('Failed to delete from memcache. Keys were "%s"' % keys)


def cache_key_for_node(node, content_type):
    return '%s:%s:%s' % (
        node.__class__.__name__, str(node.key()),
        content_type)
