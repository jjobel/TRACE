# Outing, not Session, is the unit of time on track

The project brief speaks of recording and saving "sessions", but in FIA and FIM usage a Session is an officially scheduled period (free practice, qualifying, race), and professional logging tools call one continuous run on track an "outing" (Cosworth Pi Toolbox, Bosch WinDARAB, MoTeC i2). We follow that usage: an **Outing** is one Vehicle's continuous period on track on one Course, a **Session** is the scheduled period it happened in, an **Event** groups Sessions, and a **Log** is the recorded unit brought into TRACE, holding one or more Outings. Using "session" for the recorded unit would clash with the word engineers already use.

## Consequences

- The brief's "common session format" is a common Log format, and "save each session" means saving each Log.
- Session and Event are metadata when the Source supplies them; a Log from a phone lap timer may have neither.
- Out-laps and in-laps are named parts of an Outing, not Laps, matching F1's rule that only lap times started and completed by crossing the Control line on the track count.
