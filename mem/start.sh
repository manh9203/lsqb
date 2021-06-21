#!/bin/bash

set -eu
set -o pipefail

cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd ..

. mem/vars.sh

docker stop ${MEMGRAPH_CONTAINER} || echo "No container ${MEMGRAPH_CONTAINER} found"

# port changed from 7687 to 27687
docker run \
    --rm \
    --detach \
    --publish 27687:7687 \
    --volume mg_lib:/var/lib/memgraph:z \
    --volume mg_log:/var/log/memgraph:z \
    --volume mg_etc:/etc/memgraph:z \
    --name ${MEMGRAPH_CONTAINER} \
    memgraph/memgraph:${MEMGRAPH_VERSION} \
    --telemetry-enabled=False

sleep 5
