dsmptd: A debugger SMTP server for Humans
=========================================

dsmtpd is a small tool to help the developer without an smtp server

Usage
-----

::
    
    $ dsmtpd -p 1025 -i 127.0.0.1
    2013-01-13 14:00:07,346 INFO: Starting SMTP server at 127.0.0.1:1025


Installation
------------

For the installation, we recommend to use a virtualenv, it's the easy way if you want to discover this package::

    virtualenv ~/.envs/dsmtpd
    source ~/.envs/dsmtpd/bin/activate

    pip install dsmtpd

Documentation
-------------

Execute dsmtpd with the --help flag and you will get the usage of this command::

    dsmtpd --help

There are two options:

* -p You specify the port of dsmtpd (default is 1025)
* -i You specify the network interface (default is loopback, 127.0.0.1)
* -d You specify the directory to save the incoming emails

Use it
------

Here is a small example::

    dsmtpd

    swaks --from stephane@wirtel.be --to foo@bar.com  --server localhost --port 1025

Contributing
------------

    git clone git://github.com/matrixise/dsmtpd.git


Copyright 2013 (c) by Stephane Wirtel
