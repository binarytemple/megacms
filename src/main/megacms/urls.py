from django.conf.urls import patterns, url, include

from megacms.widgets.discovery import autodiscover_widgets
import megacms.frontend.urls

autodiscover_widgets()

urlpatterns = patterns(
    '',
    url(r'.*',
        include(megacms.frontend.urls)),
)
