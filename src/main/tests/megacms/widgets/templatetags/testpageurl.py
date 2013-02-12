from django import template

from megacms.basewidgets.widgetmodels import URLNode
from megacms.widgets.templatetags.widgets import page_url
from tests.base import DatastoreTestCase


class PageUrlTagTest(DatastoreTestCase):
    """Page URL Tag"""

    def test_tag(self):
        """Should return a URLNode's URL and collect the node in the context"""
        url_fragment = 'this-does-exist'
        node = URLNode(
            url_order=0,
            title='Title',
            url_fragment=url_fragment,
        )
        node.put()
        ctx = template.Context({})
        ret = page_url(ctx, 'this-does-exist')
        self.assertEqual(ret, node.denormalized_url)
        self.assertTrue('_linked_url_nodes' in ctx)
        self.assertEqual(
            ctx['_linked_url_nodes'][url_fragment].key(), node.key())
