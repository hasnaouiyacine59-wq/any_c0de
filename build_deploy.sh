#!/bin/bash
set -euo pipefail
git pull
REGISTRY="quay.io/mylastres0rt05_redhat"
docker login -u='mylastres0rt05_redhat' -p='FblabXC4LK1oW8SekCVMi+98cxukLiBephztGlutNdxQSoLVacTSvDbxZi9/qrbf' quay.io


echo "==> Building nova_dromidia-proxy"
docker build -t "${REGISTRY}/nova_dromidia-proxy:latest" tor-proxy/
docker push "${REGISTRY}/nova_dromidia-proxy:latest"

# 1. pull latest


# 2. build & tag for quay.io
docker build -t "${REGISTRY}/nova_dromidia:latest" .
docker push "${REGISTRY}/nova_dromidia:latest"



echo "==> Done"
