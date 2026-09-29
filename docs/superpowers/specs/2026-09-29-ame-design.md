# AMe — design spec

**Status:** draft for review · **Date:** 2026-09-29 · **Repo:** `super-rt`

AMe ("A-Me") gives the PC eyes, a face, and a voice: a conversational sparring partner that looks like its user, sounds like them, speaks Brazilian Portuguese, and thinks like them at their best — challenging their reasoning, holding them to their values, and helping them decide and learn.

---

## 1. Intent

### What the user asked for
- **Purpose:** growth through conversation — a sparring partner that thinks like the user at their best.
- **Persona:** starts as a blank slate and **learns who the user is from conversations**.
- **Eyes:** **reads the user** — expression, posture, energy, attention — and adapts.
- **Face:** **looks like the user** — a 3D likeness built from a depth scan.
- **Voice:** **sounds like the user** — a clone of their voice.
- **Language:** AMe speaks **Brazilian Portuguese (pt-BR)**. Code, docs, prompts, and commits are in English.
- **Privacy:** **hybrid** — perception, speech, voice, face, and memory run locally; only text goes to a cloud model.
- **Initiative:** conversations start by wake word **or by AMe itself**.
- **Architecture:** **separate local services**.

### Assumptions (confirmed by the user)
1. "At your best" is learned from what the user *says* they value, kept separate from observed habits; AMe nudges habits toward values.
2. Single user, at their desk, on this PC.
3. Memory is inspectable, editable, and deletable. Raw video and audio are never stored.
4. Unprompted conversations are rare, polite, and easy to decline.
5. AMe is a thinking partner, not a therapist; it redirects crisis or health topics to real help.
6. AMe lives in the `super-rt` repository.

### Success criteria
- After a few weeks of use, AMe's questions and challenges reflect knowledge of the user, not generic advice.
- Conversations leave the user with clearer decisions or new ideas.
- AMe replies at a natural human pace: quick for small talk; a 2–3 s pause before weighty answers is acceptable, and anything slower gets a verbal "thinking" cue.
- The user trusts it enough to leave it running.

---

## 2. Hardware and prerequisites

| Item | Found (2026-09-29) | Required action |
|---|---|---|
| Camera | Intel RealSense D400-series ("Depth Camera 430", USB PID `0AD6`) | **Move to a direct USB 3 port with a USB 3 cable.** It currently enumerates in USB 2 mode behind a USB 2.0 hub; its second video interface (likely colour) has no driver (code 28). Colour is required for the face scan texture. |
| Microphone | None suitable (Bluetooth headset hands-free profile only) | **Acquire a USB speakerphone (hardware echo cancellation) or use a wired headset.** |
| GPU | NVIDIA RTX 5080 (16 GB) | None — sufficient for local STT, TTS/voice cloning, perception, and rendering. |
| CPU / RAM | Intel Core Ultra 7 265KF / 32 GB | None. |
| Python | Windows Store stub only | Install Python (version fixed at kickoff). |
| RealSense SDK | Not installed | Install (confirms exact model, firmware, calibration). |

Every install is a new tool and requires the user's approval (CLAUDE.md rule 5).

---

## 3. Architecture

Four local services and a console, started and supervised by one launcher (`ame start`).

```
          ┌──────────────────── mind ────────────────────┐
 eyes ───►│  hub: WebSocket on 127.0.0.1                 │───► cloud model (text only)
          │  conversation · initiative · memory          │
 voice ◄─►│  HTTP: console page + memory API             │◄──► console (browser)
          └──────────────────────────────────────────────┘
                       ▲
 face ◄────────────────┘  (hub subscriber)
```

| Service | Owns | Publishes | Consumes |
|---|---|---|---|
| **eyes** | RealSense camera; turns frames into signals, then discards frames | `eyes.state`, `eyes.event` | `control.camera` |
| **voice** | Mic and speaker: wake word, STT, TTS (cloned voice), barge-in | `voice.wake`, `voice.user_speaking`, `voice.user_said`, `voice.visemes`, `voice.spoke` | `mind.say`, `mind.stop` |
| **face** | 3D avatar window: lip-sync, expression, gaze, idle motion | `face.status` | `voice.visemes`, `mind.tone`, `eyes.state`, `mind.conversation` |
| **mind** | Hub, conversation, initiative, memory; **sole cloud client** | `mind.say`, `mind.stop`, `mind.tone`, `mind.conversation`, `control.*` relays | everything |
| **console** | Local web page: memory view/edit, camera off, do-not-disturb, status, scan and voice enrollment | `control.*` | status, memory API |

### Principles
- **One hub, one message format.** mind hosts a WebSocket server bound to `127.0.0.1` only. Nothing is reachable off-machine.
- **One privacy boundary.** Only mind makes network calls, and only to the cloud model API. This is testable (§9).
- **Degrade, don't die.** Each service tolerates the absence of any other; the launcher restarts crashed services with backoff.
- **Memory stays inside mind** until another service needs to write it.

### Message envelope
```json
{ "type": "voice.user_said", "ts": 1790722000.123, "source": "voice", "data": { } }
```
`ts` is the sender's wall-clock time in seconds. Time-critical sync (lip-sync) uses `data` fields expressed in the shared monotonic clock of the machine (§5.4).

### Message catalogue
| Type | Data |
|---|---|
| `eyes.state` | `present`, `distance_m`, `attention` (`facing_ame` \| `screen` \| `away`), `expression` (smoothed blendshape summary), `posture` (`upright` \| `slumped` \| `leaning_in` \| `leaning_back`), `energy` (`still` \| `restless` \| `animated`), `head_position` (x, y, z in metres) — sent on change, max 5 Hz |
| `eyes.event` | `kind`: `arrived` \| `left` \| `other_person` \| `other_person_gone` \| `blind` \| `sight_restored` |
| `voice.wake` | `via`: `wake_word` \| `hotkey` |
| `voice.user_speaking` | `state`: `started` \| `stopped` |
| `voice.user_said` | `text`, `language`, `confidence` |
| `voice.visemes` | `utterance_id`, `start_monotonic`, `frames`: list of `{t_ms, viseme}` |
| `voice.spoke` | `utterance_id`, `spoken_text`, `interrupted` |
| `mind.say` | `utterance_id`, `text` (one sentence), `final` |
| `mind.stop` | `utterance_id` |
| `mind.tone` | `tone`: `neutral` \| `thoughtful` \| `amused` \| `concerned` \| `curious` \| `warm` |
| `mind.conversation` | `state`: `started` \| `ended`, `initiator`: `user` \| `ame`, `reason` |
| `control.camera` | `enabled` |
| `control.dnd` | `enabled`, `until` |

---

## 4. Eyes

**Input:** depth and infrared streams (work in low light); colour when available on USB 3.

**Signals**, computed at ~5 Hz and smoothed over a few seconds:

| Signal | Source |
|---|---|
| Presence, distance | Depth (rejects photos and screens) |
| Attention | Head pose and gaze from face landmarks |
| Expression | ~52 standard face blendshape coefficients (the ARKit-compatible set) |
| Posture | Upper-body pose landmarks plus depth |
| Energy | Motion over a rolling window of minutes |

**Output:** `eyes.state` only when a smoothed signal changes; `eyes.event` for discrete transitions. mind converts the latest state into one English observation line per reply, e.g. *"Observed: slumped, low movement, eyes half-closed for ~5 min; mostly looking away while talking."*

**Observations, not emotions.** The prompt labels the line as observation. AMe asks rather than asserts ("você parece cansado — tá?"). The user's answer, not the guess, enters memory.

**Other people.** The nearest face at desk distance is the user. A second face emits `other_person`; AMe avoids personal topics and does not initiate. No face recognition in this design.

**Privacy.** Frames live only in memory and are discarded after analysis; no image is written to disk or sent anywhere. `control.camera: false` stops the camera stream at the device.

**Failure.** Camera missing or failing → `eyes.event: blind`; retry every few seconds; AMe continues without sight.

---

## 5. Voice

### 5.1 Audio hardware
USB speakerphone with hardware echo cancellation (preferred) or a wired headset. The Bluetooth hands-free profile is unsupported. Software echo cancellation is a fallback only.

### 5.2 Modes
- **Asleep:** local wake-word detection for the phrase **"Ei, AMe"** (changeable in the console) plus a hotkey. Audio is processed in a rolling buffer and discarded.
- **In conversation:** open mic; no wake word needed. Ends on an explicit close ("é isso, valeu"), `eyes.event: left`, or ~60 s of silence.
- **AMe-initiated:** soft chime, then speech.

### 5.3 Turn-taking
- End of turn after ~1 s of silence, adjusted by an eyes hint: gaze returning to AMe after a pause shortens the wait; gaze away lengthens it. Both are tunable in the console.
- **Barge-in:** when the user starts speaking while AMe is speaking, playback stops within ~200 ms and `voice.spoke` reports exactly what was said (`interrupted: true`), so transcripts reflect what the user heard.

### 5.4 Speech
- **STT:** local Whisper-family model on the GPU, pt-BR, with tolerance for English terms mid-sentence.
- **TTS:** local voice-cloning model supporting pt-BR, cloned from a one-time recording of the user reading Portuguese text (a few minutes), enrolled via the console. Recording stays local. A stock pt-BR voice is the fallback.
- **Streaming:** synthesises sentence by sentence as `mind.say` arrives.
- **Visemes:** for each utterance, voice publishes `voice.visemes` with `start_monotonic` set to the scheduled playback start, derived from the TTS phoneme timings (or from the audio if the engine lacks them).

**Privacy.** Audio is never written to disk; only text reaches mind.

**Failure.** No mic → console shows it and accepts typed input. Unrecognised speech → "desculpa, não entendi". TTS down → replies appear as text in the console.

---

## 6. Face

### 6.1 Scan (one-time, re-runnable; guided by the console)
1. User sits ~50 cm from the camera and slowly turns their head for ~30 s while depth and colour frames are captured.
2. Frames are fused into a head mesh.
3. The mesh is fitted to a parametric head model with standard expression blendshapes (the same ~52-coefficient set eyes reads) and viseme shapes for lip-sync.
4. Texture is baked from colour frames.
5. Output: a single avatar file in a standard 3D format that supports morph targets.

**Known limit:** hair scans poorly; expect a simplified sculpted hairstyle. Appearance is the scan as-is — no beautification.

### 6.2 Runtime
| Driver | Source | Effect |
|---|---|---|
| Visemes with timing | `voice.visemes` | Lip-sync, scheduled against the shared monotonic clock |
| Tone | `mind.tone` | Expression while speaking |
| User position | `eyes.state.head_position` | AMe looks at the user and follows them |
| Idle | face itself | Blinks, breathing, micro head motion |

**Display:** borderless, always-on-top corner window that fades in on `mind.conversation: started` and out on `ended`. Real-time 3D in a lightweight window that connects to the hub like the console.

**Failure.** Face crash → AMe continues voice-only; launcher restarts face. No scan yet → neutral placeholder head.

---

## 7. Mind — conversation and initiative

### 7.1 Each reply
mind assembles a request to the cloud model:
1. **Role (fixed, cached):** sparring partner that thinks like the user at their best; challenges reasoning, asks rather than assumes, holds the user to *their* stated values; casual spoken pt-BR; short replies, one question at a time; never preachy; not a therapist — redirects crisis or health topics to real help.
2. **Self-model (cached)** and **relevant memories** (§8).
3. **Observation line** from eyes.
4. **Conversation so far.**

Replies stream back, are split into sentences, and each sentence is sent as `mind.say`. A tone tag at the start of each reply sets `mind.tone`. If the first sentence has not arrived within ~3 s, mind sends a short thinking cue ("hmm, deixa eu pensar…").

### 7.2 Models
A fast Claude model serves live conversation; a stronger Claude model runs memory review (§8.2). Exact model IDs and a cost estimate are fixed in the implementation plan. Stable prompt prefixes use prompt caching.

### 7.3 Initiative
| Trigger | Example |
|---|---|
| Follow-up on something said | "Ontem você disse que ia decidir sobre X hoje. Decidiu?" |
| Stuck | Facing the screen for ≥ 45 min with a tense expression (frown or jaw tension) and low energy |
| First arrival of the day | Short greeting only |
| End of day | Reflection prompt (opt-in) |

**Guardrails**
- Daily budget: **3** unprompted starts by default (configurable).
- Never when:
  - `other_person` is present;
  - speech was heard outside a conversation in the last 10 minutes (the user is likely on a call or talking to someone);
  - deep focus — facing the screen with a neutral expression (anything that is not the "stuck" pattern);
  - do-not-disturb is on.
- All thresholds in this section are configurable in the console.
- Opening: chime → face fades in → one short question. "Agora não", or ~10 s without response → fade out and back off for **2 hours**.
- Learning: acceptance rate is tracked per trigger type; triggers with low acceptance fire less often.

---

## 8. Mind — memory

### 8.1 Layers
| Layer | Contents | Written by |
|---|---|---|
| **Conversations** | Full text transcripts in pt-BR, with timestamps and observation lines. No audio. | Live, during conversation |
| **Memories** | Facts and episodes, each with source conversation, creation date, last-confirmed date, and confidence | Post-conversation review |
| **Self-model** | ~1 page: **Values & goals** (stated by the user) · **Patterns** (observed behaviour, including blind spots) · **Style** (how the user talks, jokes, phrases) | Nightly consolidation |

**Values come only from the user.** When review detects a candidate value, it is queued as *pending* in the console for approval, or AMe asks in conversation ("Posso anotar que isso é importante pra você?"). Patterns, memories, and style are written automatically and are fully visible and editable.

### 8.2 Writing
- **After each conversation:** the stronger model reviews the transcript against existing memory — adds, updates, and flags contradictions ("mês passado você disse X, hoje Y").
- **Nightly or when idle:** merges duplicates, decays stale memories, rewrites the self-model.

### 8.3 Reading
Every reply includes the self-model plus the top memories retrieved by semantic similarity to the current conversation, using a local multilingual embedding model.

### 8.4 Storage and control
- Location: `%LOCALAPPDATA%\AMe\` — **outside the repo**, which sits in a OneDrive-synced folder.
- Daily local backups, 7 retained.
- Transcripts are retained until the user deletes them.
- Console: browse, search, edit, delete; "forget this conversation"; "forget everything"; export.
- In conversation, "esquece isso" deletes the last exchange and any memory derived from it.
- **Disclosure:** the self-model and retrieved memories are sent as text to the cloud model with each reply. Video and audio never are.

### 8.5 Cold start
AMe starts blank and curious; early conversations lean toward getting to know the user. An optional guided first session is offered in the console.

---

## 9. Testing

| Unit | Approach |
|---|---|
| Hub protocol | Contract tests per message type; every service tested against a fake hub |
| eyes | Recorded RealSense sessions replayed as fixtures; assertions on emitted signals and events |
| voice | Golden pt-BR audio clips for STT; barge-in timing; viseme timing against audio |
| face | Viseme → morph-target mapping; frame-time budget |
| mind | Cloud client mocked; prompt assembly, sentence splitting, initiative guardrails, "esquece isso" |
| Memory | Scripted transcripts → expected memory and self-model changes; values never auto-approved |
| Privacy boundary | Test that only mind opens network sockets, only to the model API host; that eyes and voice never write media files |
| End to end | Latency harness: end-of-speech → first audio, logged per turn |

---

## 10. Build order

Each slice gets its own implementation plan.

| # | Slice | Delivers | Validates |
|---|---|---|---|
| 0 | **Prerequisites & spikes** | Camera on USB 3, mic, installs (approved). Throwaway spikes: pt-BR voice cloning with viseme timing; head scan → rigged avatar quality; GPU headroom with STT + TTS + render together | The three biggest technical risks, before committing |
| 1 | **Talk** | Launcher, hub, voice (wake word, STT, stock pt-BR TTS, barge-in), mind conversation without memory, console status | Turn-taking feels natural |
| 2 | **Remember** | Transcripts, review, self-model, retrieval, console memory view/edit | AMe knows the user across conversations |
| 3 | **See** | eyes signals, observation line, end-of-turn hint, presence | AMe adapts to how the user seems |
| 4 | **Face** | Scan pipeline, avatar, lip-sync, gaze, fade in/out | AMe looks like the user |
| 5 | **Your voice** | Cloned pt-BR voice replaces stock | AMe sounds like the user |
| 6 | **Initiative** | Triggers, guardrails, acceptance learning | AMe starts conversations welcomely |

Initiative is last because it depends on eyes, face, and a mature memory.

---

## 11. Out of scope (for now)

- Face recognition or multi-user support.
- Languages other than pt-BR (English terms inside Portuguese speech are tolerated).
- Photoreal or stylised avatars.
- Mobile or remote access; anything reachable off-machine.
- Storing raw audio or video.
- Tool use by AMe (calendar, email, web).

## 12. Risks

| Risk | Mitigation |
|---|---|
| pt-BR voice cloning quality or missing phoneme timing | Spike in slice 0; stock voice fallback; audio-derived visemes |
| Scan-to-avatar quality (hair, texture, uncanny look) | Spike in slice 0; re-scan; simplified hair by design |
| GPU contention between STT, TTS, and rendering | Measure in slice 0; STT and TTS run between user turns, not concurrently |
| Initiative feels intrusive | Low budget, easy decline, acceptance learning, do-not-disturb |
| Memory drifts or misrepresents the user | Values need approval; everything visible and editable; contradictions surfaced |
| Personal data sent to the cloud model as text | Disclosed; single audited network boundary; video and audio never sent |
