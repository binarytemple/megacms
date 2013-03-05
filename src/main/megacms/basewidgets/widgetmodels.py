from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from django.template import Context

from megacms.widgets.db import TemplateStringProperty
from megacms.widgets.caching import invalidate_caches_for_node
from megacms.widgets.query import (get_direct_url_node_children,
                                   get_direct_element_children)
from megacms.widgets.templatetags.widgets import render_as_template_with_ctx


FORCED_LOAD_TAG = '{% load widgets %}'


class Node(polymodel.PolyModel):
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)

    def property_changed(self, property_name):
        # TODO: Surely there is a way we can do this properly.
        assert not isinstance(
            self.properties()[property_name],
            db.ReferenceProperty), (
                'Property "%s" is a ReferenceProperty which '
                'is unsupported by "property_changed"')

        if self._entity is None:
            return True
        else:
            return (not getattr(self, property_name)
                    == self._entity[property_name])


class URLNode(Node):
    url_parent = db.ReferenceProperty(required=False)
    url_order = db.IntegerProperty()
    title = db.StringProperty()
    url_fragment = db.StringProperty()
    denormalized_url = db.StringProperty()

    def put(self, **kwargs):
        this_is_root = not isinstance(self.url_parent, URLNode)
        parent_is_root = (
            not this_is_root and not isinstance(
                self.url_parent.url_parent, URLNode))

        if this_is_root:
            prefix = ''
        else:
            prefix = self.url_parent.denormalized_url

        if parent_is_root and not self.url_parent.url_fragment:
            self.denormalized_url = prefix + self.url_fragment
        else:
            self.denormalized_url = '%s/%s' % (prefix, self.url_fragment)

        # Need to compare the underlying value which was last retrieved
        # from the datastore before put().

        url_changed = self.property_changed('denormalized_url')

        super(URLNode, self).put(**kwargs)

        if url_changed:
            # TODO: Requires test
            # Re-put all children, in order to update their URLs, causing
            # the entire subtree to be updated.
            for child in get_direct_url_node_children(self):
                child.put()

            # TODO: Requires test
            widgets = (
                Widget.all()
                .filter('linked_url_node_keys =', str(self.key())).fetch(None)
            )
            for widget in widgets:
                invalidate_caches_for_node(widget)


class Site(URLNode):
    pass


class Widget(Node):
    """Handling links in content:

    1) Every string stored by the user is a Django template.
    2) Provide a template tag which allows the user to generate
       a URL based on a short name, eg {% page_url 'my-page' %}.
    3) On save, scan all strings on the content object and work out:
      - Whether the links are valid.
      - Which URLNodes this element links to.
    4) Store the ids of the linked URLNodes in a list field on this
       model which is maintained on save. This will be used to maintain
       links when URLs change or to check if it is safe to delete a page
       without breaking any links on the site.
    5) Provide a mechanism for ElementNodes to rescan any template strings
       they have in order to refresh URLs which have changed.
    6) When URLs for a page change, we must find all ElementNodes which
       reference that page, rescan URLs and invalidate caches for this Node and
       all ancestor nodes in the content tree, for every content type
       supported.

    """
    cacheable = True
    is_terminal = False

    subtree_cacheable = db.BooleanProperty(default=True)
    element_parent = db.ReferenceProperty(required=False)
    element_order = db.IntegerProperty()

    linked_url_node_keys = db.StringListProperty()

    def _get_linked_url_nodes(self):
        """Sweeps through all TemplateStringProperties on this instances and
        returns a list of all URLNodes that to which this Widget has links.

        :return: list of URLNodes

        """
        ctx = Context({})
        property_names = (
            name for name, prop in self.properties().iteritems()
            if isinstance(prop, TemplateStringProperty))
        for property_name in property_names:
            render_as_template_with_ctx(
                getattr(self, property_name), reuse_ctx=ctx
            )
        try:
            return ctx['_linked_url_nodes'].values()
        except KeyError:
            # The tag was never run, the Widget content doesn't link to any
            # URLNodes
            return []

    def update_subtree_cacheable(self):
        if self.cacheable:
            subtree_cacheable = all(
                child.subtree_cacheable
                for child in get_direct_element_children(self))

            if not self.subtree_cacheable == subtree_cacheable:
                self.subtree_cacheable = subtree_cacheable
                self.put()

    def put(self, *args, **kwargs):
        create = not self.is_saved()
        if create:
            self.subtree_cacheable = self.cacheable

        self.linked_url_node_keys = [
            str(node.key()) for node in self._get_linked_url_nodes()]

        super(Widget, self).put(**kwargs)

        if not self.cacheable:
            assert not self.subtree_cacheable, (
                '"%s" is uncacheable, therefore its subtree must '
                'also be uncacheable.' % self.__class__.__name__)

        if self.element_parent:

            if (not self.subtree_cacheable
                    and self.element_parent.subtree_cacheable):
                self.element_parent.subtree_cacheable = False
                self.element_parent.put()

            if (self.subtree_cacheable
                    and not self.element_parent.subtree_cacheable):
                self.element_parent.update_subtree_cacheable()

        invalidate_caches_for_node(self)

    def delete(self, **kwargs):
        parent_should_update = False
        if self.element_parent:
            parent = self.element_parent
            parent_should_update = not self.subtree_cacheable

        invalidate_caches_for_node(self)
        super(Widget, self).delete(**kwargs)

        if parent_should_update:
            parent.update_subtree_cacheable()


class ResourceBase(URLNode):
    meta_description = db.StringProperty()
    meta_keywords = db.StringListProperty()
    tags = db.StringListProperty()


class Document(ResourceBase, Widget):
    layout = db.StringProperty()


class ViewResource(ResourceBase):
    cacheable = False
    is_terminal = True


class HTMLWidget(Widget):
    is_terminal = True
    content = TemplateStringProperty()
