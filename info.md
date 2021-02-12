## Usage:
Add to configuration.yaml:

```
switch:
  - platform: denkovi
    resource: http://192.168.1.200
    password: !secret denkovi_password
    relays:
      1:
        name: Living light
        pins: 1
      2:
        name: Kitchen light 1
        pins: 2
      3:
        name: Kitchen light 2
        pins: 3
      4:
        name: Basement light 1
        pins: 4
      5:
        name: Basement light 2
        pins: 5
      6:
        name: Basement light 3
        pins: 6
      7:
        name: Basement light 4
        pins: 7
```

```
      16:
        name: Garage lights
        pins: 16

      17:
        name: Kitchen lights
        pins: 2 3
      18:
        name: Basement lights
        pins: 4 5 6 7
```


Here the important configuration variables are:
- resource: the url to your denkovi relay module, including http://
- password: the password to connect to the relay module (default=admin)

- relays:   the relay number is just an index. You should be able to use any number as long as they are unique.
- name:     the name of the relay / relay group show in Home Assistant
- pins:     the physical relay(s) in this group. Valid numbers are 1-16 seperated by space.
