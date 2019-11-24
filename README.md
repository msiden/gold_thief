# Gold Thief
A platform puzzle game made with PyGame based on the C64 classic Gilligan's Gold

TODO:  
- [x] Set screen size (1440 * 1080)
- [ ] Player animations  
    - [x] Idle
    - [x] Walking
    - [x] Climbing
    - [x] Idle while climbing
    - [ ] Pulling up
    - [x] Passed out
    - [x] Idle carrying sack
    - [x] Walking carrying sack
    - [x] Climbing carrying sack
    - [x] Pushing empty wheelbarrow
    - [x] Pushing loaded 01 wheelbarrow
    - [x] Pushing loaded 02 wheelbarrow
    - [x] Pushing loaded 03 wheelbarrow
    - [x] Idle with empty wheelbarrow
    - [x] Idle with loaded 01 wheelbarrow
    - [x] Idle with loaded 02 wheelbarrow
    - [x] Idle with loaded 03 wheelbarrow
    - [ ] Riding cart
    - [ ] Idle with axe
    - [ ] Walking with axe
    - [ ] Using axe
- [ ] More player abilities
    - [x] Climb
    - [x] Carry sack
    - [x] Die if fall to far
    - [ ] Pull up
    - [x] Push wheelbarrow
    - [ ] Ride cart   
    - [x] Die if caught by miner 
    - [ ] Use axe
    - [ ] Ride elevator
    - [x] Empty gold in truck and collect points
    - [x] Kill miners if hitting with gold sack
- [ ] Design levels
- [X] Nicer granite texture
- [ ] More textures
- [ ] Create more sprites
    - [X] Ladder
    - [X] Miner
    - [X] Gold sack
    - [ ] Cart
    - [x] Wheelbarrow
    - [ ] Axe
    - [ ] Elevator
    - [ ] Handle
    - [x] Truck
    - [ ] Door
- [x] Make miners move
- [x] Make player able to move between different rooms
- [x] Make other sprites (miners/carts) able to move between rooms)  
- [ ] Make carts move
- [x] Miners (and carts) must keep moving when in another room    
- [x] Print number of lives etc to the top of the screen
- [x] Game over if no lives left
- [x] Player should not be able to move while falling
- [x] Player should not be able to move outside screen
- [ ] Points system:    
    - Player has limited amount of time in each mine before Game Over
    - Keep track of number of collected gold sacks
    - More points if sacks are collected quickly
    - Bonus for time left when mine is completed
    - Print collected sacks, time left, bonus and total score on screen
- [ ] Start screen
- [ ] High scores
- [ ] Save game function
- [ ] Pause game function
- [ ] Player will be in immortal mode for a few seconds after passing out
    - [ ] Set self.image.set_alpha(x) in sprite.update 

    
KNOWN ISSUES
- [ ] Miners should not walk all the way to the edge of the screen to 
avoid player from being caught directly when entering another room or 
when miner enters the same room as player 

FEATURES FROM ORIGINAL GAME TO BE IMPLEMENTED (?)
* Miners can choose to wait for elevators
* Miners keep moving when in another room and not visible
* Bonus counts down every second from 3000 but is reset when 
player is passed out 


