

class NodeResponse(object):
    def __init__(self, data):
        self.data = data


class NodeResponseRedirect(NodeResponse):
    """If a Node returns NodeResponseRedirect it will cause
    page processing to be interrupted and a HttpResponse to be
    generated for the user immediately.

    """
    def __init__(self, data=None, redirect_url=None):
        """
        :param redirect_url: Used in cases where Nodes need to
        override the default behavior which is to redirect to the
        page of which the node is a child.

        """
        super(NodeResponseRedirect, self).__init__(data)
        self.redirect_url = redirect_url
