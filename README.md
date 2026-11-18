# Overdub
An Overwatch workshop mode built on [OSTW](https://github.com/ItsDeltin/Overwatch-Script-To-Workshop) where you can record every action to be played back together as bots on an editable timeline.

- **Timeline** for easy visualizations of bot playback, with keybinds
    - Hold Interact to open/close
    - Cursor navigation (aim to move the cursor, Primary Fire to click)
    - Controls
        - Record (Hold Reload then Interact x2 to start/stop)
            - On a recorded track, the button becomes a retake button. Click it again to arm a whole track recording instead. Retakes re-records the track from the playhead and keeps everything before it. Stand in the ring and aim at the sphere to start the countdown, you can't move while lined up so keys like sprint can be held beforehand. 
        - Play/Pause (Space)
        - Stop (Ctrl + Space)
        - Fast Forward/Rewind (Shift + Q / Shift + E), press again to go faster
        - Scrub frame by frame (hold Q / E to repeat)
        - Scrub in steps (A / D, each step is 1/20 of the timeline)
        - Loop playback between trim markers
        - Flags
            - Similar to how osu! handles flags with their editor, flag specific frames with Melee (up to 8 per track) and quickly jump around them in a recording with Shift + A/D
            - Click a flag to jump to it, Melee or Secondary Fire on a flag removes it, Shift + Melee on a flag or the flag button removes all flags
        - Change Hero
    - Trimming (drag the handles)
    - Scrubbing (drag the seeker), handles and seeker snap to flags and track ends
    - Teleport to the focused track (Go To Track) or cycle teleport between each objective (Go to Objective)
    - Up to 12 tracks, switched with the track buttons or the Track menu
        - Each track in the menu has a Hide/Show button, team toggle, and a delete button
            - A hidden track has no bot, but stays on the timeline and in exports
        - The Team button sets the focused track's bot to ally or enemy
- **Recording**, with chunking to keep server and client performance at bay
    - Bot playback of player actions, with synchronous playback
- **Export recordings to the inspector to be imported at a later date.** Export/imports have a compression process utilizing [swinging door compression](https://github.com/emrumo/swingingdoor), where only changes are kept, which is far less space compared to saving each frame.

- **Options**
    - Perspective
        - Detached
        - Orbit (the mouse swings the camera around the focused track's bot, Q / E zoom)
        - First Person (take perspective of the bot's recorded actions)
            - Opening the timeline pauses it, Jump/Crouch or Stop detaches you and puts you back where you were
    - Play all tracks simultaneously in editor
        - When off, only the focused track plays and the other tracks stay in place
    - Play all tracks while recording
        - Pre-roll, tracks play during the countdown and reach the recording's start when it ends
    - Recording starts at trim start
        - When off, recording starts at the playhead
    - Recording stops at trim end
    - Stop recording on death
    - Instant respawns while recording
    - Teleport to start of previous take (when re-recording a track)
    - Go to next empty track after recording
    - Keep bots dead
        - Bots that die while recording stay dead instead of respawning
    - Recording health
        - A slider up to the hero's max health, your health is set to it until a recording starts
    - Damage scaling
        - 0-500%
    - Noclip (Interact x2 to toggle, Jump/Crouch to rise/fall, hold Reload to sprint)
        - Toggle to automatically disable when starting a recording
        - Toggle to disable collision
    - Export recording to Inspector (see below)
    - End game, with option to kick you from the lobby
        - Ends the game for Overwatch replays

## How do I import / export my recordings?
Before doing anything, ensure that `Enable Workshop Inspector` and `Enable Workshop Inspector Log File` settings are turned **ON** in `Options > Gameplay > General`, they are turned off by default

### Exporting
1. Open the options menu in Overdub, click on the "Export recording to Inspector" button, then "Export" on the confirmation screen (it lists these steps too). Exports are not automatic, and must be done manually. All tracks are exported (hidden ones too) with their flags, bot teams and trim markers. The timeline and recording are locked until the export finishes, its progress is shown at the top of the screen.
2. After export, open the Workshop Inspector by pressing Esc > `Open Workshop Inspector` > "`Copy to clipboard all log`" button (second button from the left) to copy the generated code to your clipboard 
3. Paste the contents into a text editor
4. Remove the **very first timestamp** (looks like `[01:23:45]`) so that the code is pastable

The inspector can't be cleared by the script and keeps every export since the lobby began. If you exported more than once, new exports will start with a `/* ===== DELETE EVERYTHING RIGHT BEFORE THIS COMMENT ===== */` line, delete everything right before the **very last** one so you get the latest export.

### Importing 
1. Before loading into Overdub, copy the contents of an export with the very first timestamp removed (or everything after the "`DELETE EVERYTHING`" comment). Make sure the export’s map is the only one enabled in `Settings > Maps`. Overdub will give you a warning ingame if the incorrect map is loaded
2. In the custom game lobby, click on `Settings > Workshop`, then click on the orange paste button at the top right. Long recordings are split into multiple rules (`[IMPORT 1234] part 2`, `part 3`, ..., each rule of an export will show the same number) since one rule can't be above 98 KB - they all come from one paste and can be in any order, but each part has to be there. If any part is missing, Overdub shows "Import failed!" and imports nothing.
3. Load the map and wait, your recordings will be loaded in over time. **Delete previous import rules or start a brand new lobby before importing a different recording**.

The number in `[IMPORT 1234]` only identifies the export (the time in game it was exported), it is not a date. If several imports exist in the rule list, the import with the higher number will win the load

### Converting exports from older versions
Newer versions of Overdub use a smaller export format, but still import older exports like normal. An export from 1.0.3 or older is about ~40% larger, so a large import leaves less room under the Workshop's element limit. To convert old exports to the new format, use the export converter with code J3KFX. This is a separate gamemode that does nothing else, and shouldn't be necessary to do unless you are reaching the element cap.
1. Create a lobby on any map with the export converter, paste the old format export rules into it like you would in Overdub, and start the game
2. Wait for "Converted!" at the top of the screen, then copy the Inspector log like you normally would (with the first timestamp removed)
3. Import that into Overdub. The recording plays back the same as the old export within half a millimeter.

## Notes and Limitations
- Menus will only display correctly if the game is running at a 16:9 resolution, FOV is set to 103, and ingame language is not set to Traditional/Simplified Chinese, Japanese, Korean, Thai, or Russian.
- Overdub is designed to be used by only one human player in a lobby, not with multiple human players, results will vary with more than one human player.
- Overdub cannot be used in other custom gamemodes.
- It is not possible for bots to use skins. For this reason, skins are disabled for consistency and to allow for more bots to be spawned.
- Overdub keybinds were set with the intention that the default keybinds are used, such as the keys for movement (WASD), interact (F), melee (V), reload (R), primary/secondary fire (LMB/RMB), ability buttons (LShift, E), crouch (LCtrl), and ultimate (Q). It's not possible for keybinds to be set to an individual key or be setting agnostic.
- Instant ult and 0% cooldown is enabled to get around hero inconsistencies in workshop (see https://workshop.codes/wiki/articles/ow2-workshop-changesbugs). Certain abilities like Tracer recall will always have a cooldown regardless of setting or workshop workaround.
- A track (an individual hero and its recorded actions) can be at most 2 minutes (7500 frames) long, recording will automatically stop when it reaches that limit. Up to 12 tracks can be recorded.
- All tracks together can be at most 10 minutes (37500 frames) to prevent server crashes, recording stops when the total reaches that. Stored tracks cause server load spikes as a recording grows, risking a server crash in extreme cases.
- Exports are utilizing [swinging door compression](https://github.com/emrumo/swingingdoor) to fit within the Workshop’s element limit since Overdub is quite heavy element wise. This makes exports very slightly lossy, positions can be off by up to 1 cm, and facing (aim) by up to 0.015° in the worst case. Height while on the ground is marginally lossy. Inputs and health are not lossy at all. 
    - An important caveat is that re-exporting an import slowly increases the error each time it’s re-exported (~0.01° more facing error per re-export), so be conservative with re-exports if you plan to reuse the same track(s). Newly recorded tracks are not affected by this.
- reading the code in game will probably give you an aneurysm

## Compiling

### Prerequisites
- [OSTW](https://github.com/ItsDeltin/Overwatch-Script-To-Workshop/wiki/Getting-Started) installed and set-up correctly
- [`macros-ostw`](https://github.com/scorttt/macros-ostw) folder right next to the `overdub-ostw` folder

Expected folder structure:

```
scripts/
├── macros-ostw/
│   ├── main.del
│   └── ...
└── overdub-ostw/
    ├── main.del
    └── ...
```
With Overdub's `main.del` open and focused in VSCode, press `Ctrl+Alt+C` to copy the compiled workshop code into your clipboard that can then be pasted into Overwatch.
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
