# Swiss MVM
A work in progress Overwatch workshop mode built on [OSTW](https://github.com/ItsDeltin/Overwatch-Script-To-Workshop) to provide a slew of movie making features for Overwatch content creators

## Features
- Timeline for easy visualizations of dummy bot playback and camera pathing **(WIP)**
    - [x] Cursor navigation
    - [x] Controls
        - [x] Play/Pause/Stop
        - [x] Fast Forward/Rewind
        - [x] Jump to Start/End
        - [x] Scrub frame by frame
        - [x] Keybinds
    - [x] Trimming
    - [x] Scrubbing
- [ ] Recording **(NOT IMPLEMENTED)**
    - [ ] Player recording with dummy bot playback 
    - [ ] Camera pathing
- Recording Options **(NOT IMPLEMENTED)**
    - [ ] Timescale adjustment
    - [ ] Add/Remove Bot Track
    - [ ] Add/Remove Camera Track
    - [ ] Recording update rate (62.5, 31.2, 20.8, 15.6, 10.4)
- [ ] Player Options **(NOT IMPLEMENTED)**
    - [ ] Noclip
    - [ ] Aim assist

## Notes and Limitations
- Cursor controlled menus will only display correctly if the game is running at a 16:9 resolution, FOV is set to 103, and game language is not set to Traditional/Simplified Chinese, Japanese, or Korean
- The "framerate" is about 62.5 FPS, with each "frame" lasting 0.016 seconds (1s/0.016s = 62.5)
- Server load is (probably going to be) high while playback and recording is active, because of this it is recommended to only be used by one player. It will work with multiple players; however server crashes are likely

## Compiling
My [`macros`](https://github.com/scorttt/macros-ostw) repo must be placed in a folder named `macros-ostw` above Swiss' parent directory. The folder structure should appear as follows: 
```
macros-ostw
    ├ main.del
    └ other macro files

swiss-ostw
    ├ main.del
    └ other swiss files
```
