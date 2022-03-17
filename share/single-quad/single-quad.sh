#!/bin/sh
gpt -o result.gdf single-quad.in GPTLICENSE=$GPTLICENSE gamma=1.23
pbpl-gpt-gdf2hdf result.gdf avg std
pbpl-gpt-plot-phase-space plot-phase-space.toml result.h5
