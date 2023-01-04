# Swiss MVM
A work in progress Overwatch workshop mode built on [OSTW](https://github.com/ItsDeltin/Overwatch-Script-To-Workshop) to provide a slew of movie making features for Overwatch content creators

## Features
- Timeline for easy visualizations of dummy bot playback and camera pathing **(WIP)**
    - Cursor navigation **(DONE)**
    - Controls **(DONE)**
        - Play **(DONE)**
        - Pause **(DONE)**
        - Stop **(DONE)**
        - Fast Forward/Rewind **(DONE)**
        - Jump to Start/End **(DONE)**
        - Scrub frame by frame **(DONE)**
    - Trimming **(DONE)**
    - Scrubbing **(DONE)**
- Recording **(Not Implemented)**
    - Player recording with dummy bot playback **(Not Implemented)**
    - Camera pathing **(Not Implemented)**
- Recording Options
    - Timescale adjustment **(Not Implemented)**
    - Add/Remove Bot Track **(Not Implemented)**
    - Add/Remove Camera Track **(Not Implemented)**
- Player Options **(Not Implemented)**
    - Noclip **(Not Implemented)**
    - Aim assist **(Not Implemented)**

## Notes and Limitations
- Cursor controlled menus will only display correctly if the game is running at a 16:9 resolution, FOV is set to 103, and game language is not set to Traditional/Simplified Chinese, Japanese, or Korean
- Each frame is 0.016s (about 62.5 fps), 60s recording = 3,750 frames, 30s recording = 1,875 frames, etc. Because of this, it is not possible to have a recording in seconds end as a whole odd number
- Server load is high while playback and recording is active, because of this it is recommended to only be used by one player. It will work with multiple players; however server crashes are likely
