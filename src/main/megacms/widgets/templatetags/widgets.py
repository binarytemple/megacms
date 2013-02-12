from django import template

from megacms.common.exceptions import InvalidURLNodeReference

register = template.Library()


@register.simple_tag(takes_context=True)
def page_url(context, url_fragment):
    from megacms.basewidgets.widgetmodels import URLNode
    context_key = '_linked_url_nodes'
    if not context_key in context:
        context[context_key] = dict()

    cached_nodes = context[context_key]
    if url_fragment in cached_nodes:
        url_node = cached_nodes[url_fragment]
    else:
        url_nodes = (URLNode.all()
                     .filter('url_fragment =', unicode(url_fragment))
                     .fetch(None))

        count = len(url_nodes)
        if not count == 1:
            raise InvalidURLNodeReference(
                'Expected one match for URLNode "%s". '
                'Found %s.' % (url_fragment, count,)
            )
        else:
            url_node = url_nodes[0]
            cached_nodes[url_fragment] = url_node
    return url_node.denormalized_url


@register.filter
def render_as_template(template_string):
    rendered, ctx = render_as_template_with_ctx(template_string)
    return rendered


# Don't expose this in the templates.
def render_as_template_with_ctx(template_string, reuse_ctx=None):
    from megacms.basewidgets.widgetmodels import FORCED_LOAD_TAG
    t = template.Template('\n'.join([
        FORCED_LOAD_TAG, template_string]))
    ctx = reuse_ctx or template.Context({})
    return t.render(ctx), ctx
