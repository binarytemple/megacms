from google.appengine.ext import db

from bootstrapwidgets.widgetmodels import (
    ContainerWidget, RowWidget, SpanWidget)
from megacms.basewidgets.widgetmodels import Node, Site, HTMLWidget, Document
from projectwidgets.widgetmodels import NewsletterSignupWidget

SITES_ROOT = Node(
    key_name='sites-root',
    url_order=0,
)
SITES_ROOT.put()

SITE = Site(
    key_name='site',
    title='My Awesome Site',
    url_order=0,
    url_fragment='my-awesome-site',
    url_parent=SITES_ROOT,
)
SITE.put()


DOCUMENT1 = Document(
    key_name='page 1',
    title='Page 1',
    url_fragment='page-1',
    url_order=0,
    url_parent=SITE,
)
DOCUMENT1.put()


DOCUMENT5 = Document(
    key_name='page-1-1',
    title='Page 1 1',
    url_fragment='page-1-1',
    url_order=0,
    url_parent=DOCUMENT1
)
DOCUMENT5.put()

DOCUMENT6 = Document(
    key_name='page-1-2',
    title='Page 1 2',
    url_fragment='page-1-2',
    url_order=1,
    url_parent=DOCUMENT1
)
DOCUMENT6.put()

DOCUMENT2 = Document(
    key_name='page-2',
    title='Page 2',
    url_fragment='page-2',
    url_order=0,
    url_parent=SITE
)
DOCUMENT2.put()

DOCUMENT3 = Document(
    key_name='page-2-1',
    title='Page 2 1',
    url_fragment='page-2-1',
    url_order=1,
    url_parent=DOCUMENT2
)
DOCUMENT3.put()

DOCUMENT4 = Document(
    key_name='page-2-2',
    title='Page 2 2',
    url_fragment='page-2-2',
    url_order=2,
    url_parent=DOCUMENT2
)
DOCUMENT4.put()

DOCUMENT_CONTENT = ContainerWidget(
    key_name='root',
    content='',
    extra_css_classes=['container'],
    url_order=0,
    element_parent=DOCUMENT4,
)
DOCUMENT_CONTENT.put()


HEADER_ROW = RowWidget(
    key_name='header-row',
    html_element='div',
    content='',
    element_order=0,
    element_parent=DOCUMENT_CONTENT,
)

HEADER_SPAN = SpanWidget(
    key_name='header-span',
    content='',
    element_order=0,
    element_parent=HEADER_ROW,
    columns=12,
)
HEADER_SPAN.put()

HEADER = HTMLWidget(
    key_name='header',
    content='<h1>This is a header</h1>',
    html_element='header',
    element_order=0,
    element_parent=HEADER_SPAN,
)

CONTENT_ROW = RowWidget(
    key_name='content-row',
    html_element='div',
    content='',
    element_order=1,
    element_parent=DOCUMENT_CONTENT,
)

ARTICLE = SpanWidget(
    key_name='article',
    content='Article',
    html_element='article',
    element_order=1,
    element_parent=CONTENT_ROW,
    columns=9,
)

SIDEBAR = SpanWidget(
    key_name='aside',
    html_element='aside',
    element_order=2,
    element_parent=CONTENT_ROW,
    columns=3,
)

SIDEBAR_CONTENT = HTMLWidget(
    key_name='sidebar-content',
    element_order=0,
    element_parent=SIDEBAR,
    content='<h2>This is in a sidebar</h2>',
)

FOOTER_ROW = RowWidget(
    key_name='footer-row',
    html_element='div',
    content='',
    element_order=3,
    element_parent=DOCUMENT_CONTENT,
)

FOOTER_SPAN = SpanWidget(
    key_name='footer-span',
    html_element='div',
    element_order=0,
    element_parent=FOOTER_ROW,
    columns=12,
)

FOOTER = NewsletterSignupWidget(
    key_name='footer',
    content='<h3>This is a Footer</h3>',
    html_element='footer',
    element_order=3,
    element_parent=FOOTER_SPAN,
)

db.put([HEADER_ROW, HEADER, CONTENT_ROW, ARTICLE, SIDEBAR,
        SIDEBAR_CONTENT, FOOTER_ROW, FOOTER_SPAN, FOOTER])

LOREM = """Lorem ipsum dolor sit <a href="{% page_url "page-1" %}">amet,
consectetur adipisicing elit, sed do eiusmod</a>
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
"""

db.put([
    HTMLWidget(
        key_name='heading_%s' % i,
        content=LOREM,
        html_element='h%s' % (i+1),
        element_order=i,
        element_parent=ARTICLE,
    )
    for i in xrange(1)
])
