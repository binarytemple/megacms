import logging

from django import forms

from megacms.basewidgets.widgetviews import _node_to_dict
from megacms.common.utils import camel_case_to_hyphenated
from megacms.widgets.noderesponses import NodeResponseRedirect, NodeResponse


log = logging.getLogger(__name__)


class NewsletterSignupForm(forms.Form):
    email = forms.EmailField()
    junk_mail = forms.BooleanField(required=True)


def _get_context(request, node):
    data = _node_to_dict(node)
    css_classes = getattr(node, 'extra_css_classes', [])[:]
    css_classes.append(camel_case_to_hyphenated(node.__class__.__name__))

    data.update(
        css_classes=css_classes,
        key=str(node.key()),
        class_name=node.__class__.__name__,
        is_terminal=node.is_terminal,
    )
    return data


def news_letter_signup_get(request, node):
    ctx = _get_context(request, node)
    ctx.update(form=NewsletterSignupForm())
    return NodeResponse(ctx)


def news_letter_signup_post(request, node):
    form = NewsletterSignupForm(request.POST)
    if form.is_valid():
        log.info(
            'User %s just signed up to the newsletter' %
            form.cleaned_data['email'])
        return NodeResponseRedirect(redirect_url=request.path)
    else:
        ctx = _get_context(request, node)
        ctx.update(form=form)
        return NodeResponse(ctx)
