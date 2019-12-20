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
json-database file (one for each mine) describing the contents of every 
room such as miners, gold sacks, elevators etc.   

[Layout example](../images/layouts/room1_1.png)   
[Mine database example](../mines/mine1.json)

***Creating a room layout***
* Open your image editor
* Create a new image that measures 1440x1080 pixels
* Absolute black (RGB value 0, 0, 0) represents walls, floor and roofs
* Absolute white (RGB value (255, 255, 255) represents areas where the 
player and other sprites can move around.
* No other colors are allowed
* Sprites such as the player, miners etc are 120 pixels high maximum. Keeps this
in mind when designing your room. Sprites will not be able to enter 
tunnels and passages lower than this. It's probably a good idea to have 
a bit of margin too.
* Draw your room layout(s) and save it in the project folder under 
images/layouts/. You can give it any name you want but I recommend using 
the current nomenclature roomX_Y.png (X=mine, Y=room number)

***Creating a mine database***
* Open your text editor and create a new json-file. Or, better still, use
the example above as a template.
* The following keys are available. Items marked with astrix (*) are mandatory:
    * **"texture"** * - This refers to an image file that will be used to give 
    the mine it's 'look'. Texture images must also measure 1440x1080 pixels.
    * **"time_limit_mins"** * - An integer value. The number of minutes the player 
    has got to complete the mine.
    * **"rooms"** * - Holds a sub-level of keys one for each room in the mine.    
        * **"1"** * - Obviously a mine must contain at least one room. This will 
        also hold a sub-level of keys.
            * **"layout"** * - The name of the image file created in the previous 
            section.
            * **"sprites"** * - Contains a sub-level of keys describing the start 
            position of the sprites in the room. The following sprites are 
            available:
                * **"player"** * - Must always be defined in room 1 of each mine! 
                Must not be defined in any other room.
                * **"truck"** * - Must be defined in one of the rooms in the mine
                but there can only be one per mine
                * **"wheelbarrow"**
                * **"miner"**
                * **"gold"** * - You will need at least one obviously
                * **"ladder"** - Always define the "height" value of the ladder
                * **"exit"** - These are invisible doors leading to another room. 
                Always define "exit_dir" (the direction the player or miner 
                must face to go through the door) and "leads_to" (the room 
                and coordinate the door leads to).
                * **"elevator_shaft"** - Must always be placed along the path of 
                an elevator. Always define "height".
                * **"elevator"** - Always define "stops" (the position along the 
                y coordinate where the elevator pauses). "stop_direction" is 
                optional. If provided the elevator will only pause at stops 
                when going in this direction.
* Save the json-file as "mineX.json" (X = mine number) in the folder "mines".
* Technically a mine can contain an unlimited number of sprites and rooms but 
bear in mind that too many sprites or rooms will have a negative effect on 
performance. The fewer stuff the smoother the game will run.

***General guidelines and tips***  
* It is recommended not to make tunnels too high from ceiling to floor. 
About 130 pixels is recommended. Having large rooms where the ceiling is higher than 
this should work as long as tunnels leading into the room are not too high.
* Ladders can be tricky. They need to have walls on both sides else miners will get 
confused and constantly fall off. Try to keep exits points, where sprites can exit 
the ladder, in 90 degree angles to the ladder itself.
                