var megacms = megacms || {};

megacms.admin = (function () {

    "use strict";

    var module = {};

    module.WidgetNode = function ($element, children) {
        this.element = $element;
        this.children = children || [];
    };

    module.findWidgets = function ($currentEl, parentNode, topLevelWidgets) {
        var currentNode, $childEls, $childEl, i;

        if ($currentEl.hasClass('widget')) {
            currentNode = new module.WidgetNode($currentEl);

            if (parentNode === null) {
                // If parentNode is null, the currentNode is a top-level widget.
                topLevelWidgets.push(currentNode);
            } else {
                // It is a child of the parent node which was passed in.
                parentNode.children.push(currentNode);
            }
        }

        $childEls = $currentEl.children();
        for (i = 0; i < $childEls.length; i++) {
            $childEl = $($childEls[i]);
            module.findWidgets($childEl, currentNode || parentNode, topLevelWidgets);
        }
    };

    module.buildWidgetTree = function ($body) {
        var topLevelWidgets, $children, i;

        topLevelWidgets = [];
        $children = $body.children();

        for (i = 0; i < $children.length; i++) {
            module.findWidgets($($children[i]), null, topLevelWidgets);
        }
        return topLevelWidgets;
    };

    module.indent = function (string, amount) {
        var prefix, i;

        prefix = '';

        for (i = 0; i < amount; i++) {
            prefix += '    ';
        }
        return prefix + string;
    };

    module.printWidgetTree = function (roots) {
        function inner(nodes, depth) {
            var i, node;
            for (i = 0; i < nodes.length; i++) {
                node = nodes[i];
                console.log(module.indent(node.element.attr('class'), depth));
                inner(node.children, depth + 1);
            }
        }

        inner(roots, 0);
    };

    $(document).ready(function () {
        // Prints a nested outline of all the widgets on the page.
        megacms.admin.printWidgetTree(
            megacms.admin.buildWidgetTree($('body'))
        );
    });

    return module;

}());
