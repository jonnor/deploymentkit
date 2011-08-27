PYTHON=/usr/bin/python2
export PYTHONPATH=./

$PYTHON -tt tests/sanity.py || exit 1
$PYTHON tests/archlinux.py || exit 1
