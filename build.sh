#!/usr/bin/env bash

docker build -t python_developer_test_unittests -f Dockerfile.unittests .
docker build -t python_developer_test -f Dockerfile.main .
