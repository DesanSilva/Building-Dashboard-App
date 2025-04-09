#!/bin/bash

cd ~/flask-app

source venv/bin/activate

sudo cp flask-app.service /etc/systemd/system/

sudo systemctl daemon-reload

sudo systemctl enable flask-app

sudo systemctl start flask-app

sudo systemctl status flask-app
