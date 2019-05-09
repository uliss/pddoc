#!/bin/bash

for f in example*.txt
do
    echo "generating image for $f ..."
    pd_ascii2pd -a -f png $f
done

