# AnesthesiaCopilot Rules

This document defines the operational rules used by AnesthesiaCopilot.

The objective is to describe the department's scheduling logic independently of the software implementation.

---

# Core Concepts

## Master Availability

Master availability defines each anesthesiologist's normal weekly schedule.

Characteristics:

- One schedule per anesthesiologist.
- Organized by weekday.
- Stable over time.
- Modified only when a staff member joins, leaves, or has a permanent schedule change.

Master availability is the baseline from which daily availability is calculated.

---

## Availability Override

An availability override replaces the master availability for a specific date.

Typical examples:

- Teaching activities.
- Medical appointments.
- Extra working day.
- Early departure.
- Late arrival.
- Vacation.

Overrides are temporary and only affect the specified date.

After that date, the master availability automatically applies again.

---

## Daily Availability

Daily availability is computed by combining:

- Master availability
- Availability overrides

Daily availability is never entered manually.

It is a computed result.

---

# Hard Constraints

## Availability

- An anesthesiologist cannot be assigned to a case whose planned finish time exceeds their daily availability.
- Availability overrides replace the master availability for that date.
- Vacation is treated as an availability override resulting in no availability.

## Scheduling

- An anesthesiologist cannot be assigned to overlapping procedures.
- Every scheduled case requiring anesthesia must have exactly one anesthesiologist assigned.

---

# Soft Constraints

These rules are preferences rather than mandatory requirements.

## Early departure

If an anesthesiologist is scheduled to leave early (e.g. 13:00), they should preferably be assigned to an operating room that has another anesthesiologist scheduled during the afternoon. This allows a seamless handoff if the room runs later than planned.

Future versions of AnesthesiaCopilot may assign scores to soft constraints when generating schedules.