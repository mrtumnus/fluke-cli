# fluke-cli
Python 2.7 script for getting Fluke 189/289 measurements

Example usages:
Print measurement
`python fluke.py -p COM5`
Print measurement, scaling by 1000 and rounding to nearest integer
(yes, this is a very specific use-case I had :)
`python fluke.py -p COM5 -s 1000 -r 0`

Python module dependencies:
- docopt
- pyserial
