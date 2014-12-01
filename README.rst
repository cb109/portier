portier
=======

A small tool to check a host address for open ports using multple threads.


Installation
------------

    pip install portier


Usage
-----

Default address is localhost. Use like:

    portier <portrange>

    portier <portrange> --address my/host/address

with portrange being a single port like '435' or a range like: '50-200'.
