import logging
import json
import os

from google.appengine.ext.db import djangoforms
from google.appengine.api import memcache
from django.utils.functional import curry
from django.http import (
    HttpResponse, HttpResponseNotAllowed, Http404, HttpResponseRedirect)
from django.template.loader import get_template
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django.shortcuts import render_to_response

from megacms.basewidgets.widgetmodels import URLNode, Widget, Document
from megacms.common.utils import camel_case_to_underscore
from megacms.frontend.exceptions import (
    NotAllowed, InterruptPageProcessing, ContentTypeUnsupported)
from megacms.frontend.encoders import DjangoJSONEncoder
from megacms.widgets.caching import cache_key_for_node
from megacms.widgets.query import (
    get_direct_element_children, get_match_by_path)
from megacms.widgets.noderesponses import NodeResponseRedirect
from megacms.widgets.register import REGISTER, DEFAULTS


log = logging.getLogger(__name__)


_json_dumps = curry(json.dumps, cls=DjangoJSONEncoder)


def _html_mapper(request, node, node_response, mapped_child_responses):
    """Map a NodeResponse to HTML.

    :param request: HttpRequest
    :param node: the current Node being processed
    :param node_response: the NodeResponse output by the current Node
    :param mapped_child_responses: A list of HTML strings which are the
            mappings of this node's children's responses.
    :return: str

    """
    ctx = node_response.data.copy()
    ctx.update(children=mapped_child_responses)
    prefix = 'pages' if isinstance(node, Document) else 'widgets'
    template_path = os.path.join(
        prefix,
        '%s.html' % camel_case_to_underscore(node.__class__.__name__)
    )
    template = get_template(template_path)
    return mark_safe(template.render(RequestContext(request, ctx)))


def _dict_mapper(request, node, node_response, mapped_child_responses):
    """Map a NodeResponse to a dict.

    :param request: HttpRequest
    :param node: the current Node being processed
    :param node_response: the NodeResponse output by the current Node
    :param mapped_child_responses: A list of dicts which are the
            mappings of this node's children's responses.
    :return: dict

    """
    ctx = node_response.data.copy()
    ctx.update(children=mapped_child_responses)
    return ctx


def _get_node_view(request, node):
    # Only use a node's POST handler when it is identified by id in
    # GET params. Forms on the front end must use the following to
    # target the appropriate Node:
    #
    #    <form action="?key={{ node.key}}" method="POST">

    node_targeted = request.GET.get('key') == str(node.key())
    effective_method = ('POST' if request.method == 'POST'
                        and node_targeted else 'GET')

    if not node.__class__ in REGISTER:
        raise Exception('Attempt to use an unregistered Node')
    else:
        node_view = REGISTER[node.__class__][effective_method]
        if node_view is not None:
            return node_view
        else:
            # Widget doesn't define a specific POST or GET handler.
            log.info('Falling back to default widget view '
                     'for "%s"' % node.__class__.__name__)
            return DEFAULTS[effective_method]


def _should_cache(request, node, content_type, use_cache):
    # TODO: This setup means that all nodes will be re-rendered when an unsafe
    # HTTP method is processed - in many conditions, this is unnecessary, for
    # example, when the node does not respond to a POST it's GET handler is
    # used and could be cached.
    if (node.subtree_cacheable
            and request.method in ["GET", "HEAD"]
            and use_cache):
        return cache_key_for_node(node, content_type)
    else:
        return None


def _check_cache(key):
    mapped_response = memcache.get(key)
    if mapped_response is not None:
        logging.info('Cache hit')
    return mapped_response


def _set_cache(key, item):
    if not memcache.add(key, item, 60):
        logging.error('Memcache set failed for key "%s"' % key)


def _handle_recursive(request, node, mapper, content_type, use_cache):
    logging.info('Handling node: %s' % node)

    cache_key = _should_cache(request, node, content_type, use_cache)
    if cache_key:
        mapped_response = _check_cache(cache_key)
        if mapped_response:
            if content_type == 'text/html':
                # This is a rendered template fragment.
                mapped_response = mark_safe(mapped_response)
            return mapped_response
        else:
            logging.info('Cache miss')

    node_processor = _get_node_view(request, node)

    # Processing happens bottom-up, children first...
    mapped_child_responses = []
    for child in get_direct_element_children(node):
        mapped_child_response = _handle_recursive(
            request, child, mapper, content_type, use_cache)
        mapped_child_responses.append(mapped_child_response)

    # ...then the current node.
    node_response = node_processor(request, node)

    # The node processing step can return a value stops the normal
    # page rendering system, in cases where a Node can handle a POST
    # request, for instance.
    if isinstance(node_response, NodeResponseRedirect):
        raise InterruptPageProcessing(node_response)

    mapped_response = mapper(
        request,
        node,
        node_response,
        mapped_child_responses)

    if cache_key:
        _set_cache(cache_key, mapped_response)

    return mapped_response


CONTENT_TYPE_HANDLERS = {
    'application/json': _dict_mapper,
    'text/html': _html_mapper,
}


def _get_mapper(request):
    # We can handle content-types properly!
    try:
        return CONTENT_TYPE_HANDLERS[request.content_type]
    except KeyError:
        raise ContentTypeUnsupported()


POST_PROCESSORS = {
    'application/json': _json_dumps,
    'text/html': lambda x: x,
}


def _get_post_processor(request):
    try:
        return POST_PROCESSORS[request.content_type], request.content_type
    except KeyError:
        raise ContentTypeUnsupported()


def get_document(request):
    document = get_match_by_path(request.path)
    if document is None:
        raise Http404()
    else:
        return document


def document_view(request):
    """Generic handler for CMS pages.

    """
    # Handler for the page is a composite handler for all of the nodes
    # on a page. These need to be made cacheable, publishable, etc.

    # Pages should be cacheable if all of their child nodes are cacheable.
    return element_node(request, get_document(request))


def get_element(request, element_id):
    element = Widget.get(element_id)
    if element is None:
        raise Http404()
    else:
        return element


def element_view(request, element_id):
    return element_node(request, get_element(request, element_id))


def _find_redirect_url(node_response, element):
    assert isinstance(node_response, NodeResponseRedirect)
    if node_response.redirect_url:
        return node_response.redirect_url
    elif isinstance(element, URLNode):
        return element.denormalized_url
    else:
        raise Exception('Cannot find an appropriate redirect URL')


def element_node(request, element):
    use_cache = False
    try:
        # TODO: This is a cheat!
        request.content_type = 'text/html'
        response_body = _handle_recursive(
            request,
            element,
            _get_mapper(request),
            request.content_type,
            use_cache,
        )

        post_processor, effective_content_type = _get_post_processor(request)
        return HttpResponse(
            post_processor(response_body),
            content_type=effective_content_type)

    except NotAllowed, e:
        return HttpResponseNotAllowed(e.permitted_methods)

    except InterruptPageProcessing, e:
        return HttpResponseRedirect(_find_redirect_url(e.cause, element))


def update_element(request, element_id):
    element = get_element(request, element_id)

    class Form(djangoforms.ModelForm):
        class Meta():
            model = element.__class__

    return render_to_response('form.html', dict(
        form=Form(),
    ), RequestContext(request))

from megacms.common import testdata
keep_this = testdata.ARTICLE
