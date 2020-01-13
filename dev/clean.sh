#!/bin/bash

echo Removing all .c, .so and .html files...

find vita -type f -name '*.c' -exec rm {} +
find vita -type f -name '*.so' -exec rm {} +
find vita -type f -name '*.html' -exec rm {} +
rm build -rf
