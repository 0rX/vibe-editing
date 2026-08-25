# MUSIC SELECTION RULES — read before picking any clip's track

> Locked 2026-06-11 from repeated "change the music" notes. Pick the RIGHT track the first time.
> Engine: `finish_clip.py --music <path>` (loudnorm I=-29:TP=-3 under the voice, gentle in/out fades).

1. **VIBE-MATCH THE SPECIFIC CLIP.** Read the clip's emotion + topic and pick a track whose *feeling*
   matches that clip. "It's a good song" is NOT enough — a great track that doesn't fit the clip's
   feeling is the WRONG track. (Repeatedly flagged: "good song, I just don't think it matches.")
   Lanes: reflective/introspective · flirty-playful · uplifting-aspirational · warm-romantic ·
   chill-easygoing · cool-modern-confident · melancholic/heavy. Match the lane to the clip.

2. **ROTATE — don't overuse a track.** Do NOT keep reaching for the same songs across clips/batches.
   Operator notices and calls it out ("good song, I've just used it so much"). Vary your picks; favor
   tracks not used recently. When in doubt, pick something fresh from the folder over an old standby
   (Cornfield Chase, einaudi "experience", etc. have been used a lot — rest them).

3. **EVERY CLIP A DIFFERENT TRACK** within a batch — never the same song twice in one set.

4. **ALWAYS filter through `MUSIC_BLACKLIST.txt`** — including manual picks. A blacklisted song is a
   hard no (it has shipped by mistake before; never again).

5. **Source = TikTok music folder** (`(1) Calm` for aesthetic/reflective/talking-head; `(2) Core` /
   `Trend` for higher energy). Instrumental / vocal-light preferred so it sits under the voice.

Quick gut-check before committing a track: *Does this song's feeling match THIS clip's moment, and have
I used it recently?* If it doesn't match, or I've leaned on it lately — pick another.

6. **WATCH FOR SPOKEN INTROS in TikTok/YT music rips.** Many ripped tracks have a voiceover/sample at the
   start (or throughout) that bleeds under the VO. Before using a bed, transcribe its first ~15s (and the
   clip-length window) — if Groq returns real clustered speech, it's contaminated. Fixes: pick a clean
   alternate, or if the song's instrumental CORE is clean, OFFSET the music start past the spoken intro
   (e.g. øneheart "Snowfall" → start at 24s). Blacklist the contaminated file. (Learned: Speaker DGL, Snowfall.)

7. **USE THE CALIBRATED MATCHER — don't hand-pick.** Run `python ~/.claude/skills/_shared/pick_music.py
   --folder "(1) Calm"` — it ranks tracks by similarity to the centroid of `_APPROVED.txt` (your proven
   taste), excluding `MUSIC_BLACKLIST.txt` + already-used. Hand-picking "good but doesn't match" tracks
   failed ~7× in a row (Speaker PeaceOrPower); the matcher landed once calibrated. When Operator approves a
   track, ADD it to `_APPROVED.txt` so the lane sharpens. Confirm the top pick by EAR before shipping.
