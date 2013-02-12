from megacms.widgets.register import register_widget

from projectwidgets.widgetmodels import NewsletterSignupWidget
from projectwidgets.widgetviews import (
    news_letter_signup_get, news_letter_signup_post)

register_widget(
    NewsletterSignupWidget,
    get=news_letter_signup_get, post=news_letter_signup_post)
