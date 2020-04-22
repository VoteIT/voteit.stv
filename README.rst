STV Polls for VoteIT
====================

.. image:: https://travis-ci.org/VoteIT/voteit.stv.png?branch=master
    :target: https://travis-ci.org/VoteIT/voteit.stv

This is a plugin package for VoteIT that provides functionality
for Single transferable vote polls.

Currently only Scottish STV is activated.

CPO STV works in most polls, but is deactivated. The reason is that
polls with a huge amount of possible combination of winners takes
too long to calculate. It needs a limit. However, current VoteIT
voting process is not built to filter out voting methods.
