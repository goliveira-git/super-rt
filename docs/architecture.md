# AMe architecture

The full design is `docs/superpowers/specs/2026-09-29-ame-design.md`. This page is the one-screen map.

AMe is four local services and a console, started by one launcher:

| Service | Role |
|---|---|
| eyes | RealSense camera → signals about the user (presence, attention, expression, posture, energy). Frames never leave memory. |
| voice | Wake word, speech-to-text, cloned-voice text-to-speech, barge-in, viseme timing. Audio never leaves memory. |
| face | 3D avatar scanned from the user; lip-sync, expression, gaze. |
| mind | Hub (WebSocket on 127.0.0.1), conversation, initiative, memory. The only service that uses the network. |
| console | Local web page: memory, camera off, do-not-disturb, status, enrollment. |

Services exchange JSON envelopes `{type, ts, source, data}` (spec §3), implemented in `src/ame/hub/messages.py`.

Build order: spec §10. Slice 0 answers the technical risks; slice 1 makes AMe talk.
