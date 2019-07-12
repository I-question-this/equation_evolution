#!/bin/bash
SAVEIFS=$IFS
IFS=$(echo -en "\n\b")
for f in yesterDaysOutput/*
do
  ./corrections.py "$f"
done
IFS=$SAVEIFS
