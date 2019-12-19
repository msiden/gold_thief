#TO DO:

#### ADD NEW FEATURES:
- [ ] Mine carts
    - [ ] Draw sprites/animations
        - [ ] For the cart
        - [ ] For the rails the cart rides on
        - [ ] For the handle or hook
        - [ ] Player pulling up with a handle or hook
        - [ ] Player riding cart  
    - [ ] Make the carts move. They should move back and forth left/right. 
    When they reach the end of the rail they should pause a few seconds and 
    then turn around. Carts must be able to move between rooms.
    - [ ] The player and miners are passed out if hit by a moving cart
    - [ ] The player can climb on and ride the carts when they are paused 
    or by pulling himself up by a handle/hook and drop into a moving cart

- [ ] Stun gun (partially replaces the pick axe in the original game)
    - [ ] Sprites and animations  
        - [ ] Player idle with stun gun
        - [ ] Player walking with stun gun
        - [ ] Player using stun gun
        - [ ] Stun gun idle
    - [ ] Miners passes out for a few seconds if hit by stun gun. Player get bonus points.
    
- [ ] Doors and keys 
    - [ ] Sprites and animations
        - [ ] Door
        - [ ] Key
    - [ ] Player can use key to unlock doors


#### Improvements
- [ ] Enable elevators to move between rooms
- [ ] Design lots of mines
- [ ] Design more background textures
- [ ] The entire code could do well with some refactoring
    - [ ] Split into several modules to improve readability
    - [ ] Improve performance
    - [ ] Use the "return_sprite" argument more when calling the "collides" method in Sprite class.
    - [ ] Etc. etc.
- [ ] High scores
- [ ] Save game function
- [ ] Sound effects
- [ ] Music
- [ ] Make sure there is always at least one miner in the same room as the player
    
    
#### KNOWN ISSUES
- [ ] Passed out timer (and other timers) must pause when in pause mode
- [ ] Wheelbarrow temporarily disappears if player falls while pushing wheelbarrow
- [ ] Player can sometimes fall straight through an elevator if it has already started moving down when the player steps on
- [ ] Player can end up inside a wall if falling and passing out with wheelbarrow
