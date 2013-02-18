import json
import datetime

from django import forms


class DjangoJSONEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, datetime.datetime):
            return obj.isoformat()

        # TODO: Decide on how to usefully serialize a Django form.
        if isinstance(obj, forms.Form):
            return str(obj)

        return super(DjangoJSONEncoder, self).default(obj)
