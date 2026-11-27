# Arivo — the storage provider decision request (Q12/Q17; the ONE consolidated gate)

**Prepared per the directive's Workstream 8.** This is the single consolidated decision
request for the owner. Nothing provider-specific has been implemented; every frozen
contract stays provider-neutral (RTM §4.4's adapter boundary). The credentials for BOTH
options are already in the secure store — whichever you ratify, implementation proceeds
behind the existing `harness/adapters/blob.py` interface (content-addressed by sha256,
atomic writes, re-hash verification, orphan sweep).

## The recommendation

**Ratify Cloudflare R2 as Arivo's private object store.**

## Why (the measured comparison)

| Criterion | Supabase Storage | Cloudflare R2 (recommended) |
|---|---|---|
| Egress cost | $0.09/GB beyond the 5 GB free tier (Pro $25/mo) | **$0 — zero egress fees, all storage classes** |
| Storage cost | 1 GB free, then Pro $25/mo incl. 100 GB | **10 GB-month free, then $0.015/GB-month** (≈100 GB ≈ $1.50/mo) |
| Class A ops | bundled | 1M/month free, then $4.50/M |
| S3 API | platform SDK only | **native S3-compatible API** (the S3 crash-matrix evidence already landed — RTM's standing proofs) |
| Content identity | object keys can be the digest | same (the S3 PUT/GET by digest — the existing adapter contract) |
| Signed access | platform-native signed URLs | **S3 presigned URLs** (the standard form; the desktop client needs no vendor SDK) |
| Backup story | platform-managed with the project | **the export/restore machine carries the blob copies by digest** (already the case — SYS-10's manifest copies every referenced blob into the archive; the store is rehydratable from any archive) |
| Purge/orphan | the recovery walk over the platform listing | the recovery walk over the S3 listing (the same machine — orphan cleanup is store-neutral) |
| Deployment surface | one platform (D-032-consistent) | a second credential domain — **mitigated: the R2 credentials are already in the store, the account is yours, and the adapter isolates the choice** |
| Durability | platform SLA | 11 9's durability (R2's published SLA), multi-region replication included at no egress cost |

**The deciding factors:** Arivo is a single-owner reading library — the byte volumes are
readable-text documents (megabytes, not gigabytes), so BOTH options cost nearly nothing at
current scale; the costs only diverge on **egress** (every source read, every sync, every
restore) and on **the S3 API shape** (the landed crash-matrix evidence, presigned URLs for
the desktop, no vendor SDK lock). R2 wins both. Supabase Storage's one advantage — the
single operator surface — is real but small for one owner, and D-032's letter ("hosted on
Supabase, cloud + local synced") governs the DATABASE, not the blob store.

**If you prefer one vendor for everything**, Supabase Storage remains fully supported by
the neutral boundary — ratify it and the same implementation lands against its API. The
frozen contracts do not change under either choice.

## What implementation looks like after ratification (either choice)

Behind `harness/adapters/blob.py`, unchanged for every caller: S3-backed `put/get/delete/
residents` with the digest as the object key, staged verify before commit (the import
machine's §3.1 law), the re-hash refusal on every read (ARV-BLOB-003), the orphan sweep
(the recovery walk), the purge's blob erasure (D-011), and the export/restore archive
copies (SYS-10). ~one slice, its own RED-first battery.

## The gate

Reply with **"R2"** or **"Supabase Storage"** (or name another S3-compatible provider).
Until then, Workstreams 9-10 proceed on the neutral boundary — the gate blocks only the
provider-specific adapter slice.
