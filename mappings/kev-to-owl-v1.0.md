# KEV to OWL Mapping v1.0

CISA Known Exploited Vulnerabilities catalog → `kev:KevEntry`, adhered to
`kgcs:Vulnerability` by `HAS_KEV_ENTRY` (ADR-0003, decision extension).

## Source

- `https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json`
  (the JSON feed; a CSV twin exists and is not used)
- Schema: `https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities_schema.json`
  (title "CISA Catalog of Known Exploited Vulnerabilities")
- Verified 2026-09-27 against the schema and the live catalog
  (`catalogVersion` `2026.09.25`, `dateReleased` `2026-09-25T18:58:16.5029Z`,
  `count` 1726). Field names below are the schema's, verbatim.

File structure:

```json
{ "title": "CISA Catalog of Known Exploited Vulnerabilities",
  "catalogVersion": "2026.09.25",
  "dateReleased": "2026-09-25T18:58:16.5029Z",
  "count": 1726,
  "vulnerabilities": [ { "cveID": "CVE-2026-67279", "vendorProject": "MikroTik",
      "product": "RouterOS", "vulnerabilityName": "...", "dateAdded": "2026-09-25",
      "shortDescription": "...", "requiredAction": "Apply vendor mitigations per BOD 26-04 guidance",
      "dueDate": "2026-09-28", "knownRansomwareCampaignUse": "Unknown",
      "forensicTriage": "No", "cwes": ["CWE-841"], "notes": "https://... ; https://..." } ] }
```

Schema constraints (verbatim): root `required` = `catalogVersion`,
`dateReleased`, `count`, `vulnerabilities`; entry `required` = `cveID`,
`vendorProject`, `product`, `vulnerabilityName`, `dateAdded`,
`shortDescription`, `requiredAction`, `dueDate`; `cveID` pattern
`^CVE-[0-9]{4}-[0-9]{4,19}$`; `cwes[]` items pattern `^CWE-([0-9])+$`;
`dateAdded` / `dueDate` `format: date` (YYYY-MM-DD); `dateReleased`
`format: date-time`; `knownRansomwareCampaignUse` "'Known' … 'Unknown'";
`forensicTriage` "'Yes' if this vulnerability requires forensic triage per
BOD 26-04; 'No' …".

## Target Ontology

- `ontology/extensions/decision-extension-v1.0.owl` (namespace `kev:`,
  `docs/namespace-policy-v1.2.md`)
- Class: `kev:KevEntry`. Frozen class referenced: `kgcs:Vulnerability`.
- Graph: label `KevEntry`; edge `HAS_KEV_ENTRY`.

## Entity Mapping

| Source Record | Target Class | Primary ID |
| --- | --- | --- |
| `vulnerabilities[]` entry | `kev:KevEntry` | `kev:cve_id` = `cveID` (graph `cveId`, unique on the label; exactly one entry per CVE) |

## Field Mapping

| Source Field | OWL property | Neo4j property | Cardinality | Notes |
| --- | --- | --- | --- | --- |
| `cveID` | `kev:cve_id` | `cveId` | 1..1 | verbatim; key; CISA pattern enforced (`sh:Violation`) |
| `vendorProject` | `kev:vendor_project` | `vendorProject` | 1..1 | verbatim |
| `product` | `kev:product` | `product` | 1..1 | verbatim |
| `vulnerabilityName` | `kev:vulnerability_name` | `vulnerabilityName` | 1..1 | verbatim |
| `dateAdded` | `kev:date_added` | `dateAdded` | 1..1 | `xsd:date`; graph stores the `YYYY-MM-DD` string verbatim |
| `shortDescription` | `kev:short_description` | `shortDescription` | 1..1 | verbatim |
| `requiredAction` | `kev:required_action` | `requiredAction` | 1..1 | verbatim |
| `dueDate` | `kev:due_date` | `dueDate` | 1..1 | `xsd:date`; string verbatim in the graph |
| `knownRansomwareCampaignUse` | `kev:known_ransomware_campaign_use` | `knownRansomwareCampaignUse` | 0..1 | `Known` \| `Unknown` (`sh:in`, Violation); absence is a Warning (optional in the schema, present on every current entry) |
| `forensicTriage` | `kev:forensic_triage` | `forensicTriage` | 0..1 | `Yes` \| `No` (BOD 26-04; field added by CISA in 2026) |
| `notes` | `kev:notes` | `notes` | 0..1 | verbatim; semicolon-separated URLs in current entries, not parsed |
| `cwes[]` | `kev:cwes` | `cwes` | 0..n | one string per entry, verbatim, CISA pattern; **strings only, never an edge** (see rule 3) |
| file `catalogVersion` | `kev:catalog_version` | `catalogVersion` | 1..1 | copied onto every entry loaded from that file; provenance of the refresh; pattern `YYYY.MM.DD` is a Warning |
| file `dateReleased` | `kev:date_released` | `dateReleased` | 0..1 | `xsd:dateTime`, verbatim |
| file `title`, `count` | — | — | — | not stored (`count` is a loader check: `count` = number of entries) |

## Relationship Mapping

| Source Structure | Ontology Edge | Graph Edge |
| --- | --- | --- |
| `cveID` join to the Vulnerability with the same `cveId` | `kev:has_kev_entry` (`Vulnerability` → `KevEntry`) | `HAS_KEV_ENTRY`, at most one per Vulnerability |
| `cwes[]` | **none** | **none** — the values stay on the entry (ADR-0003 D1, alternative A4 rejected) |

## Transformation Rules

1. **Key and refresh.** `MERGE (k:KevEntry {cveId})` then `SET` every field
   from the current catalog, including `catalogVersion` and
   `dateReleased`. CISA never removes entries and edits them in place
   (due dates, ransomware flag), so the load is a full refresh, idempotent
   on the same file. Entries whose `cveID` has no `Vulnerability` node
   (rejected or reserved CVEs, or CVEs newer than the CVE snapshot) are
   dropped and counted, never created.
2. **Adherence.** The only edge is `HAS_KEV_ENTRY` from the Vulnerability
   whose `cveId` equals the entry's `cveId`. `kev:KevEntryShape` is closed
   and `kev:KevEntryAdherenceShape` rejects any other incoming edge.
3. **`cwes[]` is not `CAUSED_BY`.** CISA's CWE list is a decision-source
   statement, not an NVD `weaknesses[]` entry: no `type`, no place in the
   ADR-0002 provenance lists, and it would change the `CAUSED_BY` count.
   It is stored verbatim as a string list; a future `sourceRoles` value
   `kev` is ADR-0003 Open question 2.
4. **Dates stay strings in the graph**, as `Vulnerability.published` does
   (`contracts/agent-consumable-schema.md`); compare string to string. An
   RDF export types them as `xsd:date` for the shapes to hold.
5. **Build metadata:** `sourceSnapshots` gains `KEV=<catalogVersion>`
   (`shapes/build.shacl.ttl` v1.2).

## Post-load invariants (pipeline, session Q18)

| Check | Shape |
| --- | --- |
| `count(KevEntry)` = entries with a matching Vulnerability; dropped count reported | — (loader report) |
| every `KevEntry` has exactly one incoming edge, `HAS_KEV_ENTRY`, from a `Vulnerability` with the same `cveId` | `kev:KevEntryAdherenceShape`, `kev:KevEntryShape` (SPARQL) |
| at most one `HAS_KEV_ENTRY` per Vulnerability | `decision:VulnerabilityDecisionEdgesShape` (`sh:maxCount 1`) |
| unique `KevEntry.cveId` | `kev:KevEntryShape` (SPARQL) + graph unique constraint |
| no edge leaves a `KevEntry` | `kev:KevEntryShape` (`sh:closed`) |

## Provenance Notes

- Publisher: CISA. Every node carries the `catalogVersion` and
  `dateReleased` of the file it came from.
- Field names, required lists, patterns and the two enumerations were
  read from the published schema and the live catalog on 2026-09-27; the
  raw file is not stored in this repo.
