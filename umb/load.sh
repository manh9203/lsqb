#!/bin/bash

set -e
set -o pipefail

cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd ..

IMPORT_DATA_DIR=`pwd`/data/social-network-preprocessed

. umb/vars.sh

sed "s|PATHVAR|${IMPORT_DATA_DIR}|" sql/snb-load.sql > umb-scratch/snb-load.sql

cd umb-scratch
rm -rf ldbc.db*
./bin/sql --createdb ldbc.db ../sql/schema.sql  ../sql/schema-constraints.sql snb-load.sql
