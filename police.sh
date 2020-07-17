#!/bin/bash Verificacion de estado

if pgrep python3
then
  echo ok
else
  aws sns publish --topic-arn arn:aws:sns:us-east-1:222412207658:Alerta-Lectora --message "Salida Inglaterra"
  sudo reboot
fi

