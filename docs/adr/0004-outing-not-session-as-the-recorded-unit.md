# Outing, not Session, is the unit of time on track

In FIA and FIM usage a Session is an officially scheduled period (free practice, qualifying, race), and the trade calls one continuous run on track an outing. TRACE uses the words the same way: an **Outing** is one Vehicle's continuous period on track on one Course, a **Session** is the scheduled period it happened in, an **Event** groups Sessions, and a **Log** is the recorded unit brought into TRACE, holding one or more Outings. Using "session" for the recorded unit would clash with the word engineers already use.

## Consequences

- Session and Event are metadata when the Source supplies them; a Log from a phone lap timer may have neither.
- Out-laps and in-laps are named parts of an Outing, not Laps: only a lap started and completed by crossing the Control line on the track counts.
