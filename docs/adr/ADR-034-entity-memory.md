# ADR-034: Entity Memory: the Agent Keeps the Names, the Skills Receive Them Through the Inputs They Already Have

Status: Accepted (decision D49)

## Context

Conference and corporate event video repeats the same speakers, company and product names, venues and technical terms
across many clips and many jobs. Each job learned them again: the recogniser misheard the same surname, the subtitles
repeated the misspelling, and a lower third was typed by hand each time.

What already exists, read on `origin/main` on 2026-11-22:

- **transcription-skill 0.13.0+** `transcribe` takes `domain_vocabulary` (`speakers`, `terms`, `programme`, `slides`,
  `max_terms`, `japanese`) and `corrections` (`[{from, to, match: word | substring}]`, applied after recognition, each
  replacement recorded). Its ADR-047.
- **subtitle-skill 1.1.0** `render` takes `emphasis` with a `words` mode (burn only; an entry is one drawn token). Its ADR-013.
- **motion-graphics-skill** `lower_third` takes `name` and `title`.
- **dubbing-skill 1.1.0** `dub` / `narrate` take `--pronunciation <dubbing/pronunciation@1>` (EXPERIMENTAL). Its ADR-015.
- **diarization-skill 1.0.1** `enroll` writes a consented `diarization-skill/voiceprint@1`.
- **video-production-agent** keeps per-channel preferences of `--set` rules (its ADR-111), not records of people.

## Decision

1. **The agent owns the store.** video-production-agent keeps the entity memory (schema `video-agent/entity-store@1`):
   per entity a canonical spelling, aliases and mis-hearings, a type (person, organization, product, place, term), an
   optional title, readings per language and an optional link to a diarization speaker id or an enrolled voiceprint.
   One store per workspace and one per project (an event, a series). It is a JSON file the user may edit, with CSV
   import and export. No Skill stores names.
2. **No Skill contract changes.** Each use goes through an input the Skill already has: transcription `domain_vocabulary`
   + `corrections`; subtitle `emphasis` words (when the request asks for emphasis on a burn-in); the lower third's `name`
   and `title`; dubbing `--pronunciation`. The subtitles follow the corrected transcript, so subtitle-skill needs nothing
   else.
3. **Names stay on the machine.** A plan sends names only to local Skills: to transcription only when every engine the
   request can reach runs locally, and never to an AI provider.
4. **Nothing is learned without a person.** The agent may suggest candidates from a transcript; a person adds each one.
5. **Every use is visible.** The plan summary counts what was applied to each use; an empty store changes nothing.

## Consequences

- video-production-agent implements it (its ADR-128) in one pull request; no Skill needs a release and no pin moves.
- A Skill that later adds a better input (for example, phrase emphasis in subtitle-skill) is an additive change in that
  Skill, followed by the agent's repin.
- The speaker link is stored but not used until the agent calls diarization-skill `name` with a roster.
