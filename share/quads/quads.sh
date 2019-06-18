#!/bin/sh
gpt -o result.gdf quads.in GPTLICENSE=$GPTLICENSE gamma=1.23
pbpl-gpt-gdf2hdf result.gdf
