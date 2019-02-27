#!/bin/bash

set -o nounset
set -o errexit
set -o pipefail

cd /var/cyhy/cyhy-mailer || exit 1
docker-compose up -d
