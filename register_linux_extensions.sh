#!/bin/bash
xdg-icon-resource install --context mimetypes --size 256 ./images/icon/hyperspy256.png x-application-hyperspyui
xdg-icon-resource install --context mimetypes --size 128 ./images/icon/hyperspy128.png x-application-hyperspyui
xdg-icon-resource install --context mimetypes --size 64 ./images/icon/hyperspy64.png x-application-hyperspyui
xdg-icon-resource install --context mimetypes --size 48 ./images/icon/hyperspy48.png x-application-hyperspyui
xdg-icon-resource install --context mimetypes --size 32 ./images/icon/hyperspy32.png x-application-hyperspyui
xdg-icon-resource install --context mimetypes --size 22 ./images/icon/hyperspy22.png x-application-hyperspyui
xdg-icon-resource install --context mimetypes --size 16 ./images/icon/hyperspy16.png x-application-hyperspyui

xdg-mime install hyperspyui-mime.xml