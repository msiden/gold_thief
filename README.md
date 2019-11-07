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
    
KNOWN ISSUES
* Incorrect animation when dropping gold in wheelbarrow or truck - check gravity()
* Can't drop empty wheelbarrow when in front of truck
* Animation doesn't update when passed out while climbing
* Miner sometimes get stuck in a route. How random is randomness?