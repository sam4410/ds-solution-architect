---
title: Converter Smoke Test — Data Science Solution Plan
client: Example Client
industry: Retail
prepared_by: DS Solution Architect toolkit
date: 2026-01-01
version: 0.1 (draft)
depth: Standard
classification: Confidential
---

# Converter Smoke Test — Data Science Solution Plan

## 1. Executive Summary
This fixture exercises the **Markdown subset** used by the *solution plan template*, including `inline code`
and a [link](https://example.org).

- Bullet one with **bold** text
  - Nested bullet
- Bullet two [Confirmed] and [Assumed] and [To investigate]

1. First numbered
2. Second numbered

> **Assumption:** Stock-out flags exist in the POS extract.

> **Risk:** Promotion calendar may be revised after forecast origin.

### Scope of this plan
Section 14 omitted: no causal question.

## 5. Data Inventory
| Source | Grain | Point-in-time? | Status |
|---|---|---|---|
| POS sales | SKU×store×day | Yes | [Confirmed] |
| Stock-out log | SKU×store×day | Unknown | [To investigate] |
| Promo calendar | Promo×week | Lock date unknown | [Assumed] |

## 12. Train / Validation / Test Design
```
|== train ========|-gap-|.. test h1..h4 ..|
|== train ============|-gap-|.. test ..|
```
