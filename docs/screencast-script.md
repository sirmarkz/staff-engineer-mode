# 60-Second Screencast — Before / After

Goal: visually prove the before/after the README promises. The README's See-It-Work block is the text version of what this screencast captures live.

The single thing this video has to show: same prompt, same agent, two responses. One ships the diff. One catches the risks.

## Production Notes

- **Length:** 60 seconds, hard cap.
- **Format:** screencap of a terminal or IDE chat pane. No talking head.
- **Audio:** narrator voice-over only. No music. The brand voice is restrained; the audio should be too.
- **Captions:** burned-in, sans-serif, white on translucent black. Captions carry the meaning if the viewer is muted.
- **Tooling:** `asciinema` if a terminal-only capture works; otherwise screen-record the IDE chat pane at 1280×720 minimum.
- **Two takes recommended:** one with the agent's actual responses captured live, one as a backup with edited (but truthful) text.

## Beat Sheet

Total: 60 seconds. Eight beats.

### Beat 1 — Cold open (0:00–0:05)

- **On screen:** black frame, single white line of text fading in.
- **Caption:** "The senior reviewer your AI coding agent is missing."
- **Narrator:** *(silence)*
- **Purpose:** brand-mark in five seconds. No setup.

### Beat 2 — The prompt (0:05–0:13)

- **On screen:** terminal or chat pane. User types a prompt.
- **Caption:** typed text appears live.
- **Prompt:** `Add pagination to the users API.`
- **Narrator:** "One prompt. Same agent. Twice."
- **Purpose:** establish the experiment.

### Beat 3 — Without the pack (0:13–0:25)

- **On screen:** the agent's response without Staff Engineer Mode installed. Diff appears, looks plausible, ships.
- **Caption:** "Without Staff Engineer Mode."
- **Narrator:** "Without it: the agent ships the diff. Looks plausible. Done."
- **Purpose:** establish the failure mode. Do not exaggerate the response — show the real plausible-looking output.

### Beat 4 — The install line (0:25–0:31)

- **On screen:** terminal showing the install command, executing.
- **Caption:** `/plugin install staff-engineer-mode`
- **Narrator:** "Now install the pack."
- **Purpose:** show the install moment is one line. No friction.

### Beat 5 — Same prompt again (0:31–0:35)

- **On screen:** the same prompt typed again into a fresh session.
- **Caption:** `Add pagination to the users API.`
- **Narrator:** "Same prompt."
- **Purpose:** anchor the comparison. The variable is the pack, not the prompt.

### Beat 6 — With the pack, the catches (0:35–0:52)

- **On screen:** the agent's response with Staff Engineer Mode installed. The router selects a specialist; the response lists the flagged risks one by one.
- **Caption:** each flagged risk highlighted as it appears:
  - missing rollback for the new index migration
  - no SLO declared for the new endpoint
  - owner unset
  - no telemetry budget
  - page-size unbounded (DoS risk)
- **Narrator:** "With it: missing rollback. No SLO. Owner unset. No telemetry budget. Unbounded page size. Five risks the agent missed."
- **Purpose:** the proof. This is the load-bearing beat. Do not rush.

### Beat 7 — Proof line (0:52–0:57)

- **On screen:** black frame, single line of text.
- **Caption:** "Same prompt. Same agent. One reviews; one ships."
- **Narrator:** *(silence — let the line land)*
- **Purpose:** name the experiment in the viewer's vocabulary.

### Beat 8 — Closer (0:57–1:00)

- **On screen:** wordmark, sub-line, install URL.
- **Caption:**
  - **Staff Engineer Mode**
  - *Fewer vibes. More engineering.*
  - `github.com/tnilabs/staff-engineer-mode`
- **Narrator:** *(silence)*
- **Purpose:** brand-stamp and install path.

## Shot List Summary

| Beat | Time | What to capture |
| --- | --- | --- |
| 1 | 0:00–0:05 | Black frame + sub-line |
| 2 | 0:05–0:13 | Prompt being typed |
| 3 | 0:13–0:25 | Agent ships the plausible diff |
| 4 | 0:25–0:31 | Install command executing |
| 5 | 0:31–0:35 | Same prompt typed in fresh session |
| 6 | 0:35–0:52 | Agent flags five risks |
| 7 | 0:52–0:57 | Black frame + proof line |
| 8 | 0:57–1:00 | Wordmark, closer line, install URL |

## Recording Pre-flight

1. Capture both responses in real sessions before recording. Do not invent the "with pack" output; it has to be a real run. If the live response differs from the canonical example, update both this script and the README block to match what the pack actually returns.
2. Use a clean shell prompt and a neutral terminal theme. No personal aliases visible.
3. Use a generic example repo (e.g., a fresh checkout of an open-source service that exposes a `users` endpoint). Do not record against a private repo.
4. Mute notifications, hide bookmark bars, close other windows.
5. Record at 60fps minimum so captions stay readable on playback.

## After Recording

- Embed the video at the top of the README, above the See It Work block, alongside the existing text transcript.
- Drop a high-resolution still of Beat 6 (the five flagged risks) into the marketplace listing as the social card image.
- Post the 60-second clip to the maintainer's preferred social channels with the proof line as the post text. Link the README.

## Brand Constraints On The Recording

- No music. The brand voice is restrained.
- No emoji in captions. The kill list applies to video too.
- No "powerful," "comprehensive," or other marketing adjectives in the narrator script.
- No FAANG name-dropping. The video sells the artifact, not the provenance.
- The narrator script above is the maximum allowed voice-over. Cut, do not add.
