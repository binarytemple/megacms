var megacms = megacms || {};

megacms.admin = (function () {

    "use strict";

    var module = {};

    module.templates = {};

    module.init = function () {
        module.initTemplates();
    };

    module.initTemplates = function () {
        var ids = ['widget-list-item'],
            i,
            $el;

        for(i=0; i < ids.length; i++) {
            $el = $('#' + ids[i]);
            module.templates[ids[i]] = Handlebars.compile($el.html());
        }
    };

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

            ret += module.indent(module.templates['widget-list-item'](current) + '\n', depth);

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
            'li'
        );

        megacms.admin.init();
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
