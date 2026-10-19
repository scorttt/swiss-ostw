# Swiss MVM
An Overwatch workshop mode built on [OSTW](https://github.com/ItsDeltin/Overwatch-Script-To-Workshop) to provide a slew of movie making features for Overwatch content creators. Whether it's frag movies, skits, or showcasing balance changes, this tool is designed to assist in the creation of all sorts of Overwatch content  

## Planned Features
- [ ] Timeline for easy visualizations of dummy bot playback
    - [x] Cursor navigation
    - [x] Controls
        - [x] Play/Pause/Stop
        - [x] Fast Forward/Rewind
        - [x] Scrub frame by frame
        - [x] Scrub by the second
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
        - [ ] Toggle to automatically disable when starting a recording
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

Before doing anything, ensure that `Enable Workshop Inspector` and `Enable Workshop Inspector Log File` settings are turned **ON** in `Options -> Gameplay -> General`. They are turned off by default

### Exporting
1. Open the options menu in Swiss, click on the "Export to Inspector" button. Exports are not automatic, and must be done manually.
2. After export, open the Workshop Inspector by pressing Esc -> Open Workshop Inspector -> Click on the `(X)` button at the bottom of the menu to save your recording to your clipboard that can then be saved to a file or whichever medium you choose

### Importing 
1. Before loading into Swiss, copy the file contents of an export. Ensure that the map of the export is enabled in the custom game lobby in `Settings -> Maps`, the imported recording will give you a warning in-game if the incorrect map is loaded 
2. In the custom game lobby, click on `Settings -> Workshop`, then click on the orange button at the top right. Ensure that the item prefixed with `[IMPORT]` is at the top of the list! If your import is not at the top of the list, move it up by checking it with the box on the far right and use the arrows on the UI
3. Start the game, your tracks and options should be loaded automatically

## Notes and Limitations
- Menus will only display correctly if the game is running at a 16:9 resolution, FOV is set to 103, and ingame language is not set to Traditional/Simplified Chinese, Japanese, Korean, Thai, or Russian
- Swiss is designed to be used by only one human player in a lobby, not with multiple human players, results will vary with more than one human player
- Swiss isn't intended to be used in other custom games, results will vary if you merge Swiss with another custom game
- Viewing an Overwatch replay with Swiss will not playback any Swiss camera pathing, you will need to find a different solution; there are Autohotkey scripts available to get similar results within the viewer
- It is not possible for bots to use skins. For this reason, skins are disabled for consistency and allows for more bots to be spawned.
- Swiss keybinds were set with the intention that the default keybinds are used, such as the keys for movement (WASD), interact (F), melee (V), reload (R), primary/secondary fire (LMB/RMB), ability buttons (LShift, E), crouch (LCtrl), and ultimate (Q). It's not possible for keybinds to be set to an individual key or be setting agnostic
- Instant ult and 0% cooldown is enabled to get around hero inconsistencies in workshop (see https://workshop.codes/wiki/articles/ow2-workshop-changesbugs). Certain abilities like Tracer recall will always have a cooldown.

## Compiling

### Prerequisites
- [OSTW](https://github.com/ItsDeltin/Overwatch-Script-To-Workshop/wiki/Getting-Started) installed and set-up correctly
- [`macros-ostw`](https://github.com/scorttt/macros-ostw) repository cloned adjacent to Swiss' parent directory

Expected folder structure:

```
scripts/
├── macros-ostw/
│   ├── main.del
│   └── ...
└── swiss-ostw/
    ├── main.del
    └── ...
```
With Swiss' `main.del` open and focused in VSCode, press `Ctrl+Alt+C` to copy the compiled workshop code into your clipboard that can then be pasted into Overwatch.
Please note that Flatpak/Snap builds of VSCode do not share the clipboard with other applications, use VSCode's output window instead; otherwise you'll have to figure something else out for a workaround.

### Linux

If you're using a VSCode fork such as VSCodium or Code OSS, you'll have to install the extension manually since OSTW is not listed on the Open VSX registry, you can download the VSIX from the [Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=Deltin.overwatch-script-to-workshop) directly and install it manually.

You may also need to set execute permissions on the language server binary:

```bash
# adjust the path and version number to match your install
chmod 755 ~/.config/Code\ -\ OSS/User/globalStorage/deltin.overwatch-script-to-workshop/Server/v3.2.3-linux-x64/Deltinteger
```

In the OSTW extension settings, set the Deltinteger path with quotes:

```
"/home/user/.config/Code - OSS/User/globalStorage/deltin.overwatch-script-to-workshop/Server/v3.2.3-linux-x64/Deltinteger"
```
