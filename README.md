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
    - [ ] Idle with stun gun
    - [ ] Walking with stun gun
    - [ ] Using stun gun 
- [ ] More player abilities
    - [x] Climb
    - [x] Carry sack
    - [x] Die if fall to far
    - [ ] Pull up
    - [x] Push wheelbarrow
    - [ ] Ride cart   
    - [x] Die if caught by miner 
    - [ ] Use stun gun (add bonus points!)
    - [ ] Ride elevator
    - [x] Empty gold in truck and collect points
    - [x] Kill miners if hitting with gold sack
- [ ] Design rooms
- [X] Nicer granite texture
- [ ] More textures
- [ ] Create more sprites
    - [X] Ladder
    - [X] Miner
    - [X] Gold sack
    - [ ] Cart
    - [x] Wheelbarrow
    - [ ] Stun gun
    - [ ] Key
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
- [x] Points system:    
- [x] Game Over screen
- [x] Create a Texts enum!
- [x] Start screen
- [ ] High scores
- [ ] Save game function
- [x] Pause game function
- [x] Player will be in immortal mode for a few seconds after passing out
- [x] Player must get a warning when a miner is close to one of the doors
    and might enter the room        
- [ ] Sound effects
- [ ] Music
- [ ] Make sure there is always at least one miner in the same room as the player
- [ ] Load a new mine
    - total score must be saved between mines
    - rename "total score" > "score". Score is reset per mine and total score is for all mines
    - Update game completed screen
    - Create game finished screen
    
KNOWN ISSUES
- [ ] Passed out timer (and other timers) must pause when in pause mode 

FEATURES FROM ORIGINAL GAME TO BE IMPLEMENTED (?)
* Miners can choose to wait for elevators
* Bonus counts down every second from 3000 but is reset when 
player is passed out 


