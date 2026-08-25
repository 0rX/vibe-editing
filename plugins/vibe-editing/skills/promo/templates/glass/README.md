# templates/glass — Liquid-Glass Premium Demo / Explainer kit

The drop-in design system behind the high-end, brand-native "holy shit" presentation/demo video
(see the playbook + **the gotchas** in `../../SKILL.md` → "PREMIUM LIQUID-GLASS DEMO / EXPLAINER VIDEOS").

**Worked example:** `%USERPROFILE%/Videos/vibe-editing/engine/2026-06-12_WorkflowDemo/10_WORK/engine-workflow-demo` — the
`FlywheelFilm` composition (a content-flywheel demo for Speaker / company.com). 1920×1080 @ 30fps,
bold lower-thirds, no voiceover.

## Use it
1. Scaffold a Remotion project (`npm create video@latest`, blank + Tailwind), `npm i`, then add
   `@remotion/transitions @remotion/google-fonts`.
2. Drop this `src/` in (merge `components/`, `constants.ts`, `audio/`, and the example
   `compositions/FlywheelFilm.tsx` + `Root.tsx`).
3. **Rebrand (the only two steps):**
   - `src/constants.ts` → set `COLORS` (sambucus/indigo/lavender or the brand's) + the font.
   - `public/` → drop the brand's **trimmed** logo PNGs (`logo-trim.png` wordmark, `mark-trim.png`
     glyph) and point `BrandSting`/`GlassOutro` at them. Trim to content; size by WIDTH (gotcha #5).
4. Storyboard beats in a composition with `<TransitionSeries>` and render:
   `npx remotion render <CompId> out/<name>.mp4 --codec=h264 --crf=16`.
5. **QC by extracting frames** (`ffmpeg -ss <t> -i out.mp4 -frames:v 1 f.jpg`) on EVERY beat. Never blind.

## What's generic vs the example
- **Generic kit (reuse as-is):** `constants.ts`, and `components/` — `GlassBG`, `GlassPanel`,
  `GlassBeats` (GlassTitle/GlassFrame/SceneDemo/GlassOutro/PayoffCard), `BrandSting`, `CreateShots`
  (NarratorChip + players), `FXOverlay`, `GlassBrowser`, `ScaleWall`, `Odometer`, `Stopwatch`,
  `BeforeAfter`, `CameraPush`, `ReceiptStrip`, and `audio/`.
- **Signature beats (reuse the pattern, swap the content):** `Flywheel.tsx` — `ContentFlywheel`
  (the compounding loop ring), `FlywheelEscalation` (stacking payoff lines), `AutoPostScheduler`
  (**live terminal + real screen-recording side-by-side**), `HeroClipPlayer`, `RawSessionPlayer`;
  `ChannelScroll` (channel feed), `RealClipShowcase` (clip grid).
- **Example only (rewrite per brand):** `compositions/FlywheelFilm.tsx`, `data/clips.ts`,
  `data/receipts.ts`, and any `Brand*`-prefixed component. These carry Speaker/company.com specifics
  and are the canonical EXAMPLE, not part of the reusable kit.

## Real assets
- Footage/clips → `OffthreadVideo` (muted, `startFrom`, `playbackRate`) inside a glass frame; make 720/1080 proxies.
- Screen recordings → crop to JUST the app UI (`ffmpeg -vf "crop=W:H:0:Y,scale=1600:-2" -an`), speed up so it visibly progresses.
- Real thumbnails → `yt-dlp "https://youtube.com/@CH/videos" --flat-playlist --print "%(id)s|%(duration_string)s|%(title)s"` + `i.ytimg.com/vi/<id>/maxresdefault.jpg`.

Read `../../SKILL.md` for the full playbook and the 9 hard-won gotchas (transition salad, sting
bleed-through, scrim-over-text dimming, invisible logos, audio clipping, zsh word-split, …).
