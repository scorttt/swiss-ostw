# Swiss MVM
An Overwatch workshop mode built on [OSTW](https://github.com/ItsDeltin/Overwatch-Script-To-Workshop) to provide a slew of movie making features for Overwatch content creators

## Planned Features
- [ ] Timeline for easy visualizations of dummy bot playback
    - [x] Cursor navigation
    - [x] Controls
        - [x] Play/Pause/Stop
        - [x] Fast Forward/Rewind
        - [x] Jump to Start/End
        - [x] Scrub frame by frame
        - [x] Keybinds
        - [x] Flags
            - Similar to how osu! handles flags with their editor, flag specific frames with Melee and quickly jump around them in a recording with Shift + A/D
    - [x] Trimming
    - [x] Scrubbing
    - [ ] Events (deaths, kills, objectives, etc)
- [ ] Recording
    - [ ] Dummy bot playback of player actions
    - [ ] Synchronous playback of multiple bots 
    - [ ] Camera pathing with curve options
        - Each path type has their pros and cons, and can be changed at any time
            - [ ] Cubic B-spline
            - [ ] Catmull-Rom
            - [ ] Linear
- [ ] Options
    - [ ] Import / Export recordings
    - [ ] Timescale adjustment
    - [ ] Perspective
    - [ ] Damage scaling (slider)
    - [ ] Recording Accuracy 
        - Record actions every x ticks, from 1-8. Higher values are more prone to movement drifting and/or movement compensation
    - [ ] Flight/Noclip
    - [ ] Aim assist
        - [ ] Strength (slider)
        - [ ] Aim at:
            - [ ] Position (feet/legs)
            - [ ] Center
            - [ ] Eye Position
                - Note: eye position does not always line up with a model's head
    - [ ] End game 
        - Overwatch replays can take up to 5 minutes to appear

## How do I import / export my recordings?
### Exporting
0. Before exporting, ensure that `Enable Workshop Inspector` and `Enable Workshop Inspector Log File` settings are turned **ON** in `Gameplay -> General` 
1. Open the options menu in Swiss, click on the "Export to Inspector" button. Exports are not automatic, and must be done manually.
2. After export, open the Workshop Inspector by pressing Esc -> Open Workshop Inspector -> Click on the `(X)` button at the bottom of the menu and save the copied contents to a file

### Importing 
1. Before loading into Swiss, copy the file contents of an export. Ensure that the map of the export is enabled in the custom game lobby in `Settings -> Maps`, the imported recording will give you a warning in-game if the incorrect map is loaded 
2. In the custom game lobby, click on `Settings -> Workshop`, then click on the orange button at the top right. Ensure that the item prefixed with `[IMPORT]` is at the top of the list! If your import is not at the top of the list, move it up by checking it with the box on the far right and use the arrows on the UI
3. Start the game, your tracks and options should be loaded automatically

## Notes and Limitations
- Menus will only display correctly if the game is running at a 16:9 resolution, FOV is set to 103, and ingame language is not set to Traditional/Simplified Chinese, Japanese, Korean, Thai, or Russian
- Intended for use with only one human player, using multiple human players in a lobby is untested and may not work correctly
- Swiss isn't intended to be used in other custom games, results will vary if you merge Swiss with another custom game
- Viewing an Overwatch replay with Swiss will not playback any Swiss camera pathing, you will need to find a different solution; there are Autohotkey scripts available to get similar results within the viewer
- It is not possible for bots to use skins
- Keybinds are intended to be used with default keybinds for Melee, Primary/Secondary Fire, Ability Buttons, Crouch, and Ultimate. It's not possible for keybinds to be set to an individual key or be setting agnostic

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
