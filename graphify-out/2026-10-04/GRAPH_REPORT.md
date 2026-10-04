# Graph Report - webscraper  (2026-10-04)

## Corpus Check
- 5 files · ~4,572 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: .csv 3, (none) 2)

## Summary
- 83 nodes · 121 edges · 8 communities (3 shown, 5 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Direct Contract Outreach Plan
- outreach.py
- CollectorTests
- .scrape
- ContactPage
- Direct Contract Outreach
- PublicRedirect

## God Nodes (most connected - your core abstractions)
1. `CollectorTests` - 11 edges
2. `PageError` - 9 edges
3. `ContactPage` - 9 edges
4. `Direct Contract Outreach Plan` - 9 edges
5. `public_url()` - 7 edges
6. `Collector` - 7 edges
7. `response()` - 6 edges
8. `check_public_host()` - 5 edges
9. `Direct Contract Outreach` - 5 edges
10. `Blocked` - 4 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `PageError`  [EXTRACTED]
  outreach.py → outreach.py  _Bridges community 3 → community 1_

## Import Cycles
- None detected.

## Communities (8 total, 5 thin omitted)

### Community 0 - "Direct Contract Outreach Plan"
Cohesion: 0.12
Nodes (14): Completion Criteria, Contact Collector, Contact Handling, Direct Contract Outreach Plan, Evidence and Portfolio Readiness, Launch Checklist, Messages, Target and Offer (+6 more)

### Community 2 - "CollectorTests"
Cohesion: 0.22
Nodes (3): CollectorTests, http_error(), response()

### Community 3 - ".scrape"
Cohesion: 0.36
Nodes (6): Blocked, check_public_host(), Collector, FatalError, PageError, public_url()

## Knowledge Gaps
- **13 isolated node(s):** `Language`, `Start the manual pilot`, `Use the optional collector`, `Tracking`, `Verify offline` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 44 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CollectorTests` connect `CollectorTests` to `test_outreach.py`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Why does `ContactPage` connect `ContactPage` to `outreach.py`, `.scrape`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **Why does `response()` connect `CollectorTests` to `.scrape`, `test_outreach.py`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **What connects `Language`, `Start the manual pilot`, `Use the optional collector` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Direct Contract Outreach Plan` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._
- **Should `outreach.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._