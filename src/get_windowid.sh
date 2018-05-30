#!/bin/bash
window_id=$(wmctrl -lpi | awk '{ if($3==id) print $1}' id=$1)
echo $window_id
