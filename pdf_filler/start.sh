#!/bin/bash

sudo docker build -t waeez/pdf_filler_con:backend .

sudo docker run -d --env-file .env --name pdf_filler_con -p 82:82 waeez/pdf_filler_con:backend 

sudo docker system prune -f

