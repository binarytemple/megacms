from django.conf.urls import patterns, url

import megacms.frontend.views

urlpatterns = patterns(
    '',
    url(r'element/(?P<element_id>[\w|-]+)/update',
        megacms.frontend.views.update_element),

    url(r'element/(?P<element_id>[\w|-]+)',
        megacms.frontend.views.element_view),

    url(r'.*',
        megacms.frontend.views.document_view),
)
