#!/bin/bash
set -euo pipefail
git pull
REGISTRY="quay.io/mylastres0rt05_redhat"
docker login -u='mylastres0rt05_redhat' -p='FblabXC4LK1oW8SekCVMi+98cxukLiBephztGlutNdxQSoLVacTSvDbxZi9/qrbf' quay.io

VERSIONS=(
  "v1.44.0-jammy v1.44.0 v1.44 124"
  # "v1.43.0-jammy v1.43.0 v1.43 123"
  # "v1.42.0-jammy v1.42.0 v1.42 122"
  # "v1.41.0-jammy v1.41.0 v1.41 121"
  # "v1.40.0-jammy v1.40.0 v1.40 120"
)

echo "==> Building nova_dromidia-proxy"
docker build -t "${REGISTRY}/nova_dromidia-proxy:latest" tor-proxy/
docker push "${REGISTRY}/nova_dromidia-proxy:latest"

# 1. pull latest


# 2. build & tag for quay.io
docker build -t "${REGISTRY}/nova_dromidia:latest" .
docker push "${REGISTRY}/nova_dromidia:latest"



echo "==> Done"
