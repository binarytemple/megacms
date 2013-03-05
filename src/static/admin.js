var megacms = megacms || {};

megacms.admin = (function () {

    "use strict";

    var module = {};

    module.indent = function (string, amount) {
        var prefix, i;

        prefix = '';

        for (i = 0; i < amount; i++) {
            prefix += '    ';
        }
        return prefix + string;
    };

    module.htmlDocumentOutline = function (documentOutline) {
        function inner(current, depth) {
            var i, node, ret;
            ret = '';

            if (depth === 0) {
                ret += '<ul>';
            }

            ret += module.indent(module.widgetToHTML(current) + '\n', depth);

            if (current.children.length > 0) {
                ret += '<ul>';
                for (i = 0; i < current.children.length; i++) {
                    node = current.children[i];
                    ret += inner(node, depth + 1);
                }
                ret += '</ul>';
            }

            if (depth === 0) {
                ret += '</ul>'
            }
            return ret;
        }
        return inner(documentOutline, 0);
    };

    module.widgetToHTML = function (widget) {
        return '<li><a href="/element/' + widget.key + '/update" data-widget-id="' + widget.key + '">' + widget.class_name + ' (terminal: ' + widget.is_terminal + ')</a></li>';
    };

    module.fetchDocumentOutline = function () {
        $.ajaxSetup({
            dataType: 'json',
            cache: false
        });

        return $.ajax({
            url: window.location
        });
    };

    $(document).ready(function () {
        var promise, documentOutline, htmlOutline, $admin, current;

        $admin = $('#admin');

        $admin.on(
            {
                mouseenter: function(event) {
                    var id;
                    id = $(this).data('widget-id');
                    current = $('#' + id);
                    current.css('outline', '1px solid fuchsia');
                },
                mouseleave: function (event) {
                current.css('outline', 'none');
                current = null;
                }
            },
            'a'
        );

        promise = megacms.admin.fetchDocumentOutline();
        promise.done(
            function(data){
                documentOutline = data;
                htmlOutline = module.htmlDocumentOutline(documentOutline);
                $admin.html(htmlOutline);
            }
        );
    });

    return module;

}());
