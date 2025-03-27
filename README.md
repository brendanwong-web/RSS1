# RECYCLING SORTING CENTER
THis project is a smart recycling bin

# to update git:
```
git rm -r --cached FolderName
git commit -m "Removed folder from repository"
git push origin main
```

# Setup for RSS1
1. Type ```cd /Documents/rss1```
4. In rss1 venv, type: `source bin/activate `
3. Check venv is enabled
5. In a separate terminal, check mosquito is enabled using `sudo systemctl status mosquitto`
6. If not running, start mosquitto using: `sudo systemctl start mosquitto`
7. Start MQTT subscriber on the raspberry pi using:`python3 RPI-Sub.py`
8. Connect ESP32 to same LAN. Messages should start streaming in.
9. Type ```mosquitto_pub -h 192.168.1.250 -t weight -m 'getWeight' -q 1``` to publish message

# Setup for nicegui
1. ```cd Documents/nicegui```
2. Verify with ```pyenv virtualenvs```
2. ```pyenv activate nicegui```
4. Start with ```python3 main.py```

## If starting on different setup
1. Run ```hostname -I``` in bash to get ip address
2. Change **hostname** in RPI-Sub.py to ip address
3. change **SSID, PASSWORD, and mqtt_server** in ESP32_MQTT.ino
4. Proceed with above steps

## TODO
1. Implement total weight recycled on home page

## NOTES
1. No need for series resistor when using solenoid
2. `tmuxinator start --local rss1`
