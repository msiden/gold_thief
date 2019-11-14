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
    - [ ] Kill miners if hitting with gold sack
- [ ] Design real levels
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
    - [ ] Doors
- [x] Make miners move
- [ ] Make player able to move between different rooms
    - Only load player once for room 1
    - Same sprite/activity must move between rooms
- [ ] Make carts move
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
- [ ] Re-think room config json layouts.    
    - Miners to be placed randomly or enter through doors
    - Player always starts in same position as truck
    
KNOWN ISSUES
* Wheelbarrow disappears when player hits wall

FEATURES FROM ORIGINAL GAME TO BE IMPLEMENTED (?)
* Player and miners are reset to original position after player is
passed out
* Only two miners who start from a fixed position and move across
all rooms
* Miners can choose to wait for elevators
* Miners keep moving when in another room and not visible
* Bonus counts down every second from 3000 but is reset when 
player is passed out 


