# krang
A fool's approach to writing an HTTP request fuzzer using a genetic algorithm

![krang_pic](https://raw.githubusercontent.com/whoismissing/krang/master/Krang_80s.png)

Inspired by boofuzz, krang was written to gain insight behind the process of fuzzing and to bridge the gap between dumb and smart fuzzing. The goal of using a genetic algorithm is to provide guided randomness while otherwise maintaining the protocol's format as close as possible.

Configuration of target IP address, port, and process name can be set in krang.py.

Usage
------------
::

    python3 krang.py
