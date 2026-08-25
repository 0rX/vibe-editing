---
name: promo
description: THE branded video-promo skill (run as /promo). Makes premium branded videos with Remotion + Claude Code, picking ONE OF TWO MODES at the start. MODE A — ANIMATED EXPLAINER / DEMO — fully animated, brand-tokenized motion graphics (the LIQUID-GLASS kit in templates/glass: brand sting, hook cards, content-flywheel ring, terminal+screen-recording side-by-side, channel feeds, clip grids, escalation, payoff outro; or the SaaS-animation kit in templates/saas) for deck demos, feature launches, flywheel videos, branded explainers. MODE B — ARCHIVE / ORIGIN-STORY FILM — take a long ASSEMBLY CUT whose chapters are separated by black frames, auto-map the chapters, add branded era/chapter CARDS between them, a scene-matched music bed per chapter, flash transitions, and a climactic exponential GROWTH-CURVE payoff, then assemble + loudness-normalize via assemble.py. Renders to MP4. Use when user says make a promo video, /promo, create a SaaS demo, make a premium demo video, liquid glass video, presentation video for the deck, flywheel video, branded explainer, make a history film, origin story video, company timeline video, "X years in Y minutes", era cards, chapter cards, growth curve payoff, turn my assembly cut into a film, or hands over a deck / URL / brand / assembly-cut asking for a polished branded video.
---

# /promo — branded video generator (Remotion + Claude Code)

Makes two kinds of premium branded video. Powered by Remotion (React-based video) + Claude Code + the `remotion-best-practices` skill.

## 🎬 PICK THE MODE FIRST (ask the user if it's not obvious)

- **MODE A — ANIMATED EXPLAINER / DEMO.** Fully animated, no real long-form footage as the spine. Deck demos, feature launches, the content-flywheel video, SaaS promos, branded explainers. → built from `templates/glass/` (premium liquid-glass) or `templates/saas/`. See the **glass** section below. *Worked example: `%USERPROFILE%/Videos/vibe-editing/engine/2026-06-12_WorkflowDemo` (the FlywheelFilm composition).*
- **MODE B — ARCHIVE / ORIGIN-STORY FILM.** The user hands you a long **assembly cut** (their own edit — real footage, chapters separated by black frames) and wants it turned into a branded film: chapter cards between sections, scene-matched music per chapter, flash transitions, and a growth-curve payoff. → era cards + `assemble.py`. See the **MODE B** section below. *Worked example: `%USERPROFILE%/Videos/vibe-editing/engine/2026-06-14_BrandHistory` (a "4.5 years in ~5 minutes" origin film).*

Both modes share the same brand-tokenized glass kit (sting, `GlassBG`, era cards, growth curve, brand `constants.ts`), so they look like one family. **Rebrand per brand in `constants.ts` + `public/` logos — never hard-code a brand name into a component.**

## When to use this (vs other video skills)

- ✅ **Use this**: standalone promo videos, SaaS demos, course teasers, feature launch videos, animated explainers from a URL
- ❌ **Don't use this**: talking-head clips, face-tracked reframing, filler-word surgery, captioning existing video (use `shortform` / `caption-clips` instead)

## Ready-made SaaS animation templates

Three production-ready Remotion components for the "SaaS animation style" (the $1-2k/video style dominating tech-brand Instagram/TikTok in 2026). Drop them into any Remotion project:

- `templates/saas/SaasTextPopup.tsx` — 4s branded intro with pop-in text + logo reveal
- `templates/saas/SaasGlassReveal.tsx` — 6s glass-UI feature cards with backdrop-blur
- `templates/saas/SaasDashboardTour.tsx` — 8s 3D dashboard tour with animated cursor

Full technique reference at [`editing-styles/saas-animation-style.md`](../editing-styles/saas-animation-style.md). Chained orchestrator at [`saas-animation-video`](../saas-animation-video/SKILL.md) — trigger with "make a saas animation video".

See [`templates/saas/README.md`](templates/saas/README.md) for wiring + brand customization.

---

## 🟣 PREMIUM LIQUID-GLASS DEMO / EXPLAINER VIDEOS — `templates/glass/`

The system behind the high-end, brand-native "holy shit" presentation video (the kind that drops into a slide deck as a live demo). Use this — not the saas templates — when the brief is **a polished, deck- or concept-driven explainer/demo** with real footage, real product UI, and bold on-screen text instead of a voiceover. Worked example: `%USERPROFILE%/Videos/vibe-editing/engine/2026-06-12_WorkflowDemo` (the `FlywheelFilm` composition — a content-flywheel demo). **1920×1080 @ 30fps, bold lower-thirds, no VO.**

> **BRAND-AGNOSTIC.** The kit is brand-tokenized. Set the brand in `src/constants.ts` (`COLORS` + font) and drop the brand's logo PNGs in `public/`. The example uses **Speaker / company.com** (Sambucus `#131628`, Electric Indigo `#6f00ff`, Lavender `#a08bec`, Poppins) — swap those tokens per brand; never hard-code a brand name into a component.

### What's in the kit (`templates/glass/src/`)
- **`constants.ts`** — brand tokens (COLORS, FPS, WIDTH, HEIGHT, spring presets). THE one place to rebrand.
- **`components/GlassBG.tsx`** — persistent drifting-orb gradient background (the continuous-flow base; sits behind every beat).
- **`components/GlassPanel.tsx`** — the frosted "liquid glass" panel (backdrop-filter blur + sheen + depth). `dark` variant for text legibility. **backdrop-filter DOES render in Remotion's headless Chrome.**
- **`components/GlassBeats.tsx`** — the beat primitives: `GlassTitle` (hook card), `GlassFrame`/`SceneDemo` (UI-in-a-glass-window + narration), `GlassOutro` (payoff card + logo), `PayoffCard`.
- **`components/BrandSting.tsx`** — ~1.5s logo sting (streaks → flash → mark bloom → wordmark).
- **`components/CreateShots.tsx`** — `NarratorChip` (the bold lower-third caption = the "bold text, no VO" layer) + media-player shots.
- **`components/Flywheel.tsx`** — signature beats: `ContentFlywheel` (the compounding loop RING), `FlywheelEscalation` (stacking deck-line payoff), `AutoPostScheduler` (**live terminal + real screen-recording, side by side**), `RawSessionPlayer`, `HeroClipPlayer` (clip in a phone frame), `Tier1Prompt`/`Tier1Pipeline` (command + steps).
- **`components/ChannelScroll.tsx`** — a real channel feed scrolling (thumbnails + durations). **`RealClipShowcase.tsx`** — a grid of real vertical clips playing. **`GlassBrowser.tsx`** — app UI in a browser frame. `ScaleWall`/`Odometer`/`Stopwatch` — volume + number drama. `FXOverlay` — grain/vignette.
- **`audio/index.tsx`** — `AudioBed` (music, low) + `Sfx` (whoosh/braam/riser/tick…) with a MASTER gain map.
- **`compositions/FlywheelFilm.tsx`** — the worked example: sting → hook → raw-proof → command → pipeline → (mids: channel + auto-post terminal/recording) → (shorts: hero + grid) → flywheel ring → escalation → outro.

### The production playbook (the order that works)
1. **Read the source material FIRST** (the deck / brief). Extract the concept AND the brand's **own language** — pull verbatim lines for the beats so the video feels native to their talk. (Don't invent generic copy.)
2. **Set brand tokens** in `constants.ts`; drop logos in `public/` (see gotcha #5 on logo PNGs).
3. **Storyboard the beats** with `TransitionSeries` (sting → hook → demo beats → payoff loop → escalation → outro). Keep it **tight (~38–45s)** — fast beats, bold lower-thirds. ("Too slow" is the #1 note.)
4. **Wire real assets** (see patterns below) — real footage/UI > mockups, every time.
5. **Render:** `npx remotion render <CompId> out/<name>.mp4 --codec=h264 --crf=16` (append *"use Remotion best practices"* when prompting edits).
6. **QC BY EXTRACTING FRAMES — never trust it blind** (gotcha #1).
7. **Deliver** to the project's `20_DELIVER/` (Brand-named). Local only unless told otherwise.

### Real-asset patterns
- **Footage** → `<OffthreadVideo muted startFrom={..} playbackRate={..} />` inside a glass player/phone/browser frame. Make proxies (720×1280 / 1080) so the studio + render stay fast.
- **Screen recordings** → crop to JUST the app UI (kill the browser tab/address bar/banner): `ffmpeg -ss A -t B -i rec.mov -vf "crop=W:H:0:Y,scale=1600:-2" -an out.mp4`. Speed up (`playbackRate` 2–3.5×) so it visibly *progresses* through steps, not dwells.
- **Terminal + recording side-by-side** (the killer beat): a styled terminal whose log **mirrors the REAL script's stdout** (read the actual skill/script to get authentic lines) next to the actual screen recording — the two reading the same names sells it as one system. See `AutoPostScheduler`.
- **Real data/thumbnails** → pull live: `yt-dlp "https://youtube.com/@CHANNEL/videos" --flat-playlist --print "%(id)s|%(duration_string)s|%(title)s"`, then thumbnails from `https://i.ytimg.com/vi/<id>/maxresdefault.jpg` (fallback `mqdefault.jpg`). For Speaker clip data, the `your analytics` MCP.

### 🛑 THE GOTCHAS — every one is a real fix from building this; read before you render
1. **QC by frames, never blind.** After every render, `ffmpeg -ss <t> -i out.mp4 -frames:v 1 f.jpg` across EVERY beat and actually look. Render the first half early with `--frames=0-540` while assets finish.
2. **Transition text-salad.** Two text beats that crossfade overlap into unreadable garbage. FIX: fade each text beat's content OUT over its last ~14 frames (an `exit = interpolate(f,[dur-16,dur],[1,0])` multiplied into opacity) so it's gone before the next crossfades in. (Or hard-cut text beats.)
3. **Sting/logo bleed-through.** A sting (or any beat) that ends on a bright logo bleeds THROUGH the next translucent glass card during the crossfade. FIX: fade the sting's logo out at its OWN end so it hands off on a clean dark frame.
4. **Scrim-over-text dimming (subtle!).** An `<AbsoluteFill>` scrim is a *positioned* sibling, so it paints ABOVE static text and dims it — bright white survives, lavender/secondary text gets crushed and looks faint. FIX: put the scrim at `zIndex:0` and wrap the text in a `position:relative; zIndex:1` container. (Then a high-opacity scrim kills the drifting-orb "glow-then-unglow" pulse without dimming the text.)
5. **Invisible logos.** A square logo PNG with transparent padding renders the actual mark tiny/invisible. FIX: trim the PNG to its content first, then size by **WIDTH** (`<Img style={{ width: 600, height: 'auto' }} />`).
6. **Audio clipping.** Unmapped SFX play at 1.0 → full-scale clip. FIX: a MASTER gain (~0.5) + a full per-SFX VOL map + music ~0.2 under the voice; loudnorm `I=-14:TP=-1.5` on the final deliverable. Verify `volumedetect` max ≤ ~−3 dB.
7. **zsh word-split.** `for x in $VAR` does NOT split in zsh (one iteration with the whole string). Use a literal list or `${=VAR}`. (Bit me batch-downloading thumbnails.)
8. **Keep the last frame live** (not black) — outros end on the logo card; verify last-frame luma > ~10.
9. **Fonts** via `@remotion/google-fonts` (Poppins, JetBrainsMono). **Numbers/keywords** glow with a constant `textShadow` (don't rely on the bg for glow — see #4).

---

## 🧊 3D + 2.5D PARALLAX + ☁️ CLOUD SCALE (MODE A power-ups)

Worked example: `%USERPROFILE%/Videos/vibe-editing/_PROJECTS/2026-06-15_3DSaasDemo` (a a sample SaaS demo — parallax hero, floating glass dashboard cards, 3D bar chart + a true-WebGL variant).

### 3D — two paths
- **CSS 3D (default, no deps, renders anywhere).** Wrap a scene in `perspective` + `transformStyle:'preserve-3d'`; place layers at different `translateZ` and animate the world's Z with `useCurrentFrame()` = a camera dolly where near layers move more than far (real 2.5D parallax). Floating glass cards, extruded bar charts (front/side/top faces), receding grid floors all come from CSS transforms. **Reach for this first** — it's bulletproof in headless Chrome.
- **True WebGL — `@remotion/three` + React Three Fiber.** Real meshes, lighting, shadows, materials. Use only when CSS-3D can't (true geometry/lighting/DOF). Install `@remotion/three` + `@react-three/fiber@^9` + `three` (**R3F v9 is required for React 19**; v8 is React 18). Drive animation with Remotion's `useCurrentFrame()`, NOT R3F's `useFrame` (Remotion renders frame-by-frame). Wrap in `<ThreeCanvas width={width} height={height} camera={...}>`.
  - 🔑 **GOTCHA — headless WebGL needs a GL backend.** A plain `npx remotion render` of a Three scene fails: *"Could not create a WebGL context"* (SwiftShader). FIX: render with **`--gl=angle`** (uses the GPU on a real Mac; works on Lambda). Without it the frame errors/blanks. CSS-3D has no such requirement.

### ☁️ Scale — Remotion Lambda
For "lots of these" / 4K / batches: render on AWS Lambda (frames fan out massively parallel). `@remotion/lambda` install + deploy/render npm scripts are templated; the only missing piece is an AWS account + IAM keys. Full steps in the demo project's `LAMBDA.md`. Local render needs zero AWS — Lambda is purely the throughput lever.

---

## 🎞️ MODE B — ARCHIVE / ORIGIN-STORY FILM (`assemble.py` + era cards + growth-curve payoff)

The user hands over a long **assembly cut** (their own edit — real archive footage, chapters separated by BLACK frames) and wants it turned into a branded, deck-ready film: chapter CARDS between the sections, a different scene-matched music bed per chapter, flash transitions, and a climactic exponential GROWTH-CURVE payoff. 1920×1080 @ 30fps, no VO. *Worked example: `%USERPROFILE%/Videos/vibe-editing/engine/2026-06-14_BrandHistory` ("4.5 years in ~5 minutes").*

> **BRAND-AGNOSTIC.** Cards + curve carry the brand via Remotion `constants.ts` (COLORS + font) + `public/` logos — swap per brand; never hard-code a name into a component. Per-film specifics (chapter titles, years, milestones, which sections get music) live in the PROJECT (`assemble.py` CONFIG + `Root.tsx` + `GrowthCurve.tsx` data), never in the skill.

### The pieces (all in `templates/glass/`)
- **`src/components/EraCard.tsx`** — branded chapter card (chapter index + YEAR + title + sub); doubles as the section→section transition. Props `{chapter, year, title, sub}`. Register one per chapter in `Root.tsx` (78f each).
- **`src/components/GrowthCurve.tsx`** — THE payoff: a compounding exponential curve that draws on, milestones popping as the comet draw-head passes, climaxing on a big stat (e.g. `3 → 200`) + logo (glowing area-fill reveal, ring-pulse milestones, climax flash, rising sparks, breathing glow). Edit `MILES` (label+year per milestone; x is decorative even-spacing), the stat, and the axis `TICKS` per film. ~190f.
- **`assemble.py`** — the stitch engine (copy into the film's `10_WORK/`): card→section→…→payoff, per-section grade + music bed, card SFX, final-section flash into the payoff, concat + loudnorm. Driven by its CONFIG block.
- **`scripts/detect_sections.py`** — blackdetect → the content spans between chapters → paste into `SECTIONS`.
- **`scripts/wait_valid.py`** — wait for a still-uploading cut to finish writing before you touch it.

### The process (the order that works)
1. **`new_project.py <brand> <slug>`** (default brand `speaker`) → `00_SOURCE/ 10_WORK/ 20_DELIVER/`. Copy the cut into `00_SOURCE/` — if it's mid-upload, `wait_valid.py` it first (a partial mp4 reads as "moov atom not found").
2. **Scaffold the Remotion project** in `10_WORK/` (copy `templates/glass/`; symlink `node_modules` from a sibling promo project to skip install). Set brand in `constants.ts`, logos in `public/`.
3. **`detect_sections.py <cut>`** → chapter spans. Sample a frame from the middle of each span and identify each chapter.
4. **🛑 CONFIRM chapter TITLES + YEARS with the user — dates are factual + Brand-facing, NEVER guess.** Wire the confirmed `{chapter, year, title, sub}` into `Root.tsx` (one EraCard per chapter) and the matching `{label, year}` into `GrowthCurve.tsx` `MILES`. Era-card year MUST equal the curve milestone year.
5. **Pick music per chapter** with the calibrated matcher: `python ${CLAUDE_PLUGIN_ROOT}/lib/_shared/pick_music.py --folder "(1) Calm" --used "<picks so far>"` (ranks by the user's `_APPROVED.txt` centroid, excludes `MUSIC_BLACKLIST.txt`). DISTINCT track per chapter, mood-matched, in the emotional/calm lane. Some chapters may want NO music or a barely-there bed (vol 0.05) — per-section call, ASK if unsure. Blacklist anything the user rejects (append to `MUSIC_BLACKLIST.txt` with their reason).
6. **Render** the cards + curve: `npx remotion render Card0N out/Card0N.mp4 --codec=h264 --crf=18` (+ `GrowthCurve`).
7. **`python assemble.py all`** → sections (graded + music) · cards (SFX) · payoff (flash-in) · concat + loudnorm → `10_WORK/build/film_assembled.mp4`.
8. **QC by frames + measurement:** every chapter boundary lands on real content (no black bleed); each card shows the right title + YEAR; the curve milestone years are right (zoom in and READ them); snap + flash transitions intact; loudnorm OK / no clip; A/V durations match.
9. **Deliver** to `20_DELIVER/` (local). NEVER push to Frame/Monday without explicit per-file permission.

### 🛑 MODE B GOTCHAS — every one is a real fix from building the origin film
1. **`-ss`/`-t` are INPUT options** — both BEFORE `-i CUT`, else they bind to the next input (the music) and the section comes out the wrong length. (Baked into `assemble.py`.)
2. **Cards: NO `-shortest`** — the SFX is shorter than the 2.6s card and `-shortest` truncates it. Use `apad` + a hard `-t 2.6`. (Baked in.)
3. **Blackdetect boundaries are estimates** — start ~+0.13s after `black_end`, end ~−0.10s before `black_start`, then VERIFY a frame at each edge. A "dark" open (night exterior, dim event) is real content, not black bleed — eyeball it, don't trust a luma threshold alone.
4. **Keep in-chapter "snap to black" beats INSIDE the span** — a short black mid-chapter is usually an intentional snap transition (with its own SFX in the source). Don't split on it; `detect_sections.py` only splits on long blacks.
5. **Flash into the payoff** = last section fades to white over its last ~0.17s + payoff fades FROM white over its first ~0.27s; whoosh swishes up into the cut, soft impact lands as the curve appears. (Baked in via `flash_out=True` on the last SECTION + the payoff filter.)
6. **DATES ARE FACTUAL** — the single most important review note on the origin film was a wrong chapter year. Confirm every year; if the user flags one, fix it in BOTH the era card AND the curve milestone, then re-verify by reading it off the rendered frame.
7. **Music: calibrated matcher, never hand-pick by title; never ElevenLabs artist-name prompts.** Bespoke "bombastic" payoff music got rejected — the approved lane is emotional/calm cinematic, turned DOWN under the visual (payoff bed ~0.30, braam carries the punch). ElevenLabs `compose_music` rejects artist-name references (use its `prompt_suggestion`).
8. **Loudnorm once, at the end** (`I=-15:TP=-1.5:LRA=11` on the concatenated film), not per section. A dialogue-only (no-music) section gets brought up to match — fine.
9. **A/V duration:** a ~50–110ms audio-longer-than-video delta is trailing AAC padding from the concat, not progressive drift (each piece is built A/V-locked) — not a sync problem.

---

## What Remotion can do well

- **Multi-scene animated promos** — hook / feature / CTA scenes with CSS animations
- **3D text effects** — perspective rotations, parallax
- **Code blocks & terminal UIs** — typewriter effects, syntax highlighting
- **Fake browser views** — realistic app screenshots with animated highlights
- **Reuse existing React components** — if the brand has a web app, drop its components into the video
- **Audio via 11 Labs MCP** — optional voiceover from a generated script

## Typical prompts

```
Use remotion to create a short promo video for https://bytegrad.com/courses/react-nextjs
  → 5 scenes, animated hero + key benefits + price + CTA, ~30s

Use remotion to create a 20s promo for my SaaS. URL: https://myapp.com
Use the brand colors from the homepage. Show 3 key features with a fake browser view.
  → Scraped URL, extracts colors + copy, builds scenes

Create an instructor intro scene for [course name]. Use image at public/instructor.jpg.
Give it a 3D parallax effect.
  → Single-scene insert, drops into an existing Remotion project
```

## Setup (one-time per brand / project)

```bash
# Create a Remotion project
npm create video@latest my-promo   # pick "blank" template, enable Tailwind

cd my-promo
npm install

# Install Remotion agent skills globally (one-time)
npx skills add @remotion/skills    # adds remotion-best-practices + cloud-code agents
```

The `remotion-best-practices` skill is already installed globally. Claude picks it up automatically when you run `claude` from inside a Remotion project.

## Golden rule — ALWAYS append this to every Remotion prompt

> **"use Remotion best practices"**

Without this, output quality drops hard (layout breaks, non-idiomatic Remotion, slow renders). Remotion's own team recommends it on every prompt. Bake it into your prompt template.

## Zod schema controls (do this in every project)

After the first render, prompt:

```
Add a Zod schema with controls for every composition and every clip/sequence.
Expose: animation speeds, positions, scales, opacities, text content, colors.
```

This gives you live-customizable sliders in the Remotion Studio preview panel (no re-prompting for small tweaks). Save this prompt — run it on every new Remotion project.

## Speed — Opus 4.6 Fast mode for 3D / complex scenes

For 3D SVG, 3D text, metallic materials, or any composition with heavy math: `/fast` (Opus 4.6 fast mode) is ~3× quicker than Sonnet. Costs more ($30/$150 per M tokens) but worth it when iterating on expensive scenes.

## Multi-composition generation via Playwright MCP

For product-page promos (SaaS feature grids, e-commerce catalogs), install Playwright MCP first:

```bash
claude mcp add playwright
```

Then a single prompt like *"use playwright mcp to scrape https://apple.com/iphone, collect name + starting price + key specs + image for each product, then create a Remotion composition per product"* produces one video per product — handoff-ready deliverable in one shot.

## Lottie assets (free motion graphics library)

```bash
npx remotion lottie
```

Browse tens of thousands of free Lottie animations, download, drop into `public/`, then prompt: *"use smooth-triple-dot-loader.lottie from assets and add to a new composition called motion-styles-showcase"*.

## Output location

Final MP4 lands in `out/<project-name>.mp4`. Use `npm run build` or click "Render video" in the Remotion Studio.

## Iteration pattern (from the tutorial)

1. **First prompt**: generic ("make a promo video") — get V1 in ~30s
2. **Review**: scroll scenes, note what's off (text too small, wrong colors, missing images)
3. **Iterate**: prompt specific fixes ("make text significantly bigger for all scenes", "use #00FF88 as accent")
4. **Add assets**: drop images into `public/`, then prompt to use them
5. **Render**: click "Render video" → MP4 in `out/`

## VPS option (for heavier renders)

For long promos or render farms, run Remotion + Claude Code on a VPS (Hostinger has a Claude Code VPS template). Frees local machine, renders faster, shareable preview via `IP:3000`.

## Integration with other agency skills

- **`repurpose-youtube`** — use this skill to render the Instagram carousel slides and LinkedIn hero card as Remotion React components instead of static Pillow images
- **`shortform`** — pre-render intro title cards with Remotion (3D text, brand colors), then concat with the talking-head clip via ffmpeg
- **`agency-pipeline`** — when Brand asks for "one promo video for the landing page" — that's this skill, not shortform
- **`remotion-best-practices`** — referenced automatically by Claude Code when editing Remotion projects

## Limits

- **Audio sync** — Remotion handles but 11 Labs MCP must be configured separately
- **Render time** — not free. A 30s promo with animations is ~30-60s render time local, faster on VPS
- **Re-encoding hit** — rendering through React + Chrome → ffmpeg means more CPU than a straight ffmpeg pipe. Don't use for tasks ffmpeg alone can do.
