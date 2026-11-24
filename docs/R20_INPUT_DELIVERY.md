# R20 Shared Input Delivery Status

Updated 2026-10-30.

R20 reached **INPUT_DELIVERY_PASS**. The input, seal, execution version, and independent readback from a new path on the same machine all passed. The parent supervisor exited with raw code 0. The result covers research input delivery. **R18 remains PARTIAL**, and the R19 recovery outcome and earlier failures remain recorded.

## Input Scope and Counts

| Item | R20 measured result |
| --- | --- |
| Targets / executable targets / stations | 180 / 180 / 10 |
| High / medium / low priority | 60 / 60 / 60 |
| Windows / complete candidates | 6709 / 116223 |
| Targets with zero candidates / target-station pairs with no windows | 0 / 153 |
| H60 subset windows / candidates | 2173 / 39720 |
| Remaining 120 targets' windows / candidates | 4536 / 76503 |
| schedule / native backend / initial / native | 0 / 0 / 0 / 0 |

The model covers all 86400 seconds of 2026-08-05 UTC. It uses the same 10 stations and numeric parameters as R18. H60 is a strict subset of H180 and the identities of all nine raw files match. The input uses windows generated for this run. The R12 Aug03 windows are outside that set. Geometric elevation is 10–85 degrees without refraction, sampled at 30-second coarse and 1-second fine intervals. Task durations are 120 or 240 seconds, with 30 seconds between tasks and up to 12 starts per duration per window. The historical package lacked complete historical byte identities for the dependencies and embedded time auxiliary data. As a result, zero windows were reused and all 1800 target-station pairs were generated from scratch.

The windows were sorted and numbered consistently, with a sidecar mapping retained. The original `make_candidates` generated all candidates, and the deterministic replay matched byte for byte. Raw TLE epochs were checked 10000 times with scalar calculations. Production made 14725 vector propagation backend calls for 20952285 samples. Geometry made 13078 `elevations` calls and another 1647 independent direct geometry calls. Propagation errors totaled zero. The read-only input validator's `propagation_calls=0` describes that validator alone.

## Verification and Interpretation

All 20127 samples covering every window's start, last valid whole second, and midpoint passed. The tolerance was 1e-7 degrees, and the maximum direct versus reference error was 0 degrees. A window's `end_s` is inclusive. The 153 empty pairs establish absence within the frozen grid and the regions that were actually refined. Continuous-time search completeness and full optical observability remain unverified.

Summing the highest candidate score for each target gives 3000 integer points, equivalent to a score of 600. This is a loose upper bound that ignores resource conflicts. The sum measures neither an achieved J nor a jointly feasible optimum, completed score, or method gain.

The source is bound to the complete 99-file tree at `b0e6461`. Production modules match the earlier bound version. Five control and protocol files were frozen before formal production and matched their identities afterward. The positive qualification case completed archiving, sealing, and terminal receipt generation. Wrong IDs, wrong dates or bindings, missing files, tampering, nonzero exits, and short timeouts were rejected as expected. Formal production and sealing each ran once, with zero formal failures. The preflight and final-report failures are reported separately.

## Budget and Delivery

Conservative accounting totaled 530.423 / 600 seconds, comprising 442.438 for preparation below its 480-second limit, 60 for sealing, 7.985 for independent acceptance, and 20 for wrap-up. Preparation includes a conservative 45-second preflight allowance. Complete UTC timing was unavailable for some early tools. The ledger measures the scoped work.

The successful terminal receipt was written after the actual seal exited with code 0. The second new path used the packaged source and tools with the bound external Python environment. The missing-file copy exited with code 1. Dependency identities are in the package, and the runtime environment is external. The result applies to this same-machine dependency boundary.

The research input package contains zero real initial plans. It serves the research workflow, separately from the `no_fault_source` v1 format and product API. The planned R21 use of the frozen input for two initial and four native runs remained pending at this point. R20 produced zero new J values or differences between methods.

Under the [contribution guidelines](../CONTRIBUTING.md), real data, full packages, research tools, and machine receipts are kept locally. The sole local R21 entry point is `RELEASE.json`, with SHA256 `8b8b8a6ff087803a5261961e77740070978003196b8531e891ab1d195bc635e4`. The digest allows verification of the local package.
