#!/bin/sh

if [ -d "/datasets" ]; then
  for DATASET in $(find /datasets -maxdepth 1); do
    ln -sf "$DATASET" "$HOME"
  done
  rm "$HOME/datasets"
else
  echo "/datasets directory does not exist."
fi