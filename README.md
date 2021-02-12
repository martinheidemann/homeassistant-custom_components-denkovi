Fork comments and notes:
==========

This is a fork from the main project made by Ronald Dehuysser (rdehuyss).
Thank you so much for creating this great addon.

https://github.com/rdehuyss/homeassistant-custom_components-denkovi

The main change in this fork is the possibility to toggle multiple relays in one command to the Denkovi module.
I have many light groups and when turning the light on or off, it would happen one relay at a time, with a small delay between each relay.
As it is possible to change state of multiple relays in one command i have implementet this.

Use case example:
My basement lights consist of 4 relays each operating a bulb. I would like to operate each relay individually and as a group.
I have defined each relay in the configuration file (id 4-7) and the group (id 18).
The group switch will be shown as ON if at least one of the relays (4-7) is ON. Otherwise it is OFF.

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


      18:
        name: Basement lights
        pins: 4 5 6 7

Quirks:
If you toggle a relay in a group it can take up to 10 seconds for the group to update state in Home Assistant.
The same is also the case, if you toggle a group. Here it can take up to 10 seconds before the individual relays update state.
It is only the visual update in Home Asssistant that is slow, the relays change state immidiatly.

# HomeAssistant - Denkovi
Custom component for - switch platform - for [Denkovi](http://denkovi.com) relay modules in HomeAssistant

Currently tested with [
smartDEN IoT Internet / Ethernet 16 Relay Module - DIN Rail BOX](http://denkovi.com/smartden-lan-ethernet-16-relay-module-din-rail-box)

## Installation
Copy the folder denkovi and all it's contents in your custom_components folder.
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
