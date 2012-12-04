kenya-election-data
===================

This is data useful to election mapping in Kenya.

Shapefiles containing County and Constituency boundaries, and Polling Place locations, can be downloaded from
https://github.com/mikelmaron/kenya-election-data/tree/master/output

Use the _sphericalmercator versions with TileMill, will be much faster. Otherwise, you're probably fine with the unprojected versions.

This data comes from http://vote.iebc.or.ke/. There are simple endpoints for requesting json encoded data. download.py iterates, caches, and builds the output.

More info at http://brainoff.com/