#!/bin/bash
git fetch --all;
git reset --hard origin/master;
sudo svc -t /etc/service/lib/
