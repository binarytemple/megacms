Megacms - The Mega CMS
======================

Setup
-----

This will install the appengine SDK and make scripts available in ./bin.

The appengine application lives in ./src. Application code goes in ./src/main,
the other locations are library locations and are .gitignored.


Development
+++++++++++

  python bootstrap.py
  ./bin/buildout -c development.cfg


Running the thing
+++++++++++++++++

  ./bin/dev_appserver src

Then go to http://localhost:8080/my-awesome-site/page-2/page-2-2 to see a
demo page in your browser.
