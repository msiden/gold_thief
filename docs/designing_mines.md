# Designing mines

Designing mines is easy and does not require any coding skills. All 
you need is the following:

* A basic image editing application such as Microsoft Paint
* A basic text editor
* Basic understanding of the json file format

#### Instructions and guidelines
A mine consists of one or, usually, many rooms. These rooms are 
defined using two types of files. Image files in png-format 
(one for each room) describing the room layouts and a 
json-file (one for each mine) describing the contents of every 
room such as miners, gold sacks, elevators etc.   

[Layout example file](../images/layouts/room1_1.png)   
[Mine contents example file](../mines/mine1.json)

***Creating a room layout***
* Open your image editor
* Create a new image that is 1440x1080 pixels big
* Absolute black (RGB value 0, 0, 0) represents walls, floor and roofs
* Absolute white (RGB value (255, 255, 255) represents areas where the 
player and other sprites can move around.
* No other colors are allowed
* Sprites such as the player, miners etc are 120 pixels high. Keeps this
in mind when designing your room. Sprites will not be able to enter 
tunnels and passages lower than this.
* 
