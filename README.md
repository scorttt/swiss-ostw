# Swiss MVM
A work in progress Overwatch workshop mode built on [OSTW](https://github.com/ItsDeltin/Overwatch-Script-To-Workshop) to provide a slew of movie making features for Overwatch content creators

## Features
- Timeline for easy visualizations of dummy bot playback and camera pathing **(WIP)**
    - Cursor navigation **(DONE)**
    - Controls **(DONE)**
        - Play/Pause/Stop **(DONE)**
        - Fast Forward/Rewind **(DONE)**
        - Jump to Start/End **(DONE)**
        - Scrub frame by frame **(DONE)**
    - Trimming **(DONE)**
    - Scrubbing **(DONE)**
- Recording **(NOT IMPLEMENTED)**
    - Player recording with dummy bot playback **(NOT IMPLEMENTED)**
    - Camera pathing **(NOT IMPLEMENTED)**
- Recording Options
    - Timescale adjustment **(NOT IMPLEMENTED)**
    - Add/Remove Bot Track **(NOT IMPLEMENTED)**
    - Add/Remove Camera Track **(NOT IMPLEMENTED)**
    - Recording framerate (62.5, 31.2, 20.8, 15.6, 10.4) **(NOT IMPLEMENTED)**
- Player Options **(NOT IMPLEMENTED)**
    - Noclip **(NOT IMPLEMENTED)**
    - Aim assist **(NOT IMPLEMENTED)**

## Notes and Limitations
- Cursor controlled menus will only display correctly if the game is running at a 16:9 resolution, FOV is set to 103, and game language is not set to Traditional/Simplified Chinese, Japanese, or Korean
- Framerate is about 62.5 FPS, with each frame lasting 0.016 seconds (1s/0.016s = 62.5)
- Server load is high while playback and recording is active, because of this it is recommended to only be used by one player. It will work with multiple players; however server crashes are likely
