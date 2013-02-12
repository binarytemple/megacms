from megacms.basewidgets.widgetmodels import Widget, URLNode
from megacms.common.exceptions import InvalidURLNodeReference
from megacms.widgets.db import TemplateStringProperty
from tests.base import DatastoreTestCase


class DummyWidget(Widget):
    content = TemplateStringProperty()


class WidgetsTest(DatastoreTestCase):

    def test_url_scan_on_put(self):
        """Should scan for links and store referenced URLNode ids on save"""
        url_node_1 = URLNode(
            url_order=0,
            title='Test URLNode',
            url_fragment='test-url-node-1',
        )
        url_node_1.put()

        url_node_2 = URLNode(
            url_order=0,
            title='Test URLNode 2',
            url_fragment='test-url-node-2',
        )
        url_node_2.put()

        test_widget = DummyWidget(
            name='Dummy Widget',
            html_element='p',
            content=(
                'Content with multiple links: '
                '{% page_url "test-url-node-1" %} '
                '{% page_url "test-url-node-2" %} '
                '{% page_url "test-url-node-1" %} '
            )
        )
        test_widget.put()
        self.assertEqual(2, len(test_widget.linked_url_node_keys))
        expected = set([str(url_node_1.key()), str(url_node_2.key())])
        found = set(test_widget.linked_url_node_keys)
        self.assertEqual(expected, found)

    def test_url_scan_on_put_with_bad_page_ref(self):
        """Should not be saved if referenced URLNodes do not exist"""
        test_widget = DummyWidget(
            name='Dummy Widget',
            html_element='p',
            content=(
                'Content with multiple links: '
                '{% page_url "this-page-does-not-exist" %} '
            )
        )
        self.assertRaises(InvalidURLNodeReference, test_widget.put)
