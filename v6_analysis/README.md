# V6 analysis freeze

This package is a derived, reviewable freeze built from the verified V5 measured tensor, V5 fold-specific selections and the completed reconstruction/dual-endpoint pilot. The source files remain outside this package and are not overwritten.

Scope is 29 main scans (S01-S28 and S30), with S29 excluded. The common-valid target domain is 4,149 EX-EM positions. The structural endpoint is V5 inter-sample distance-ranking preservation (`rho_structure`); reconstruction is supplementary and reports supported-position error plus support fractions.

`src/v6_freeze.py` regenerates the package. `tests/test_v6_freeze.py` checks row counts, site scope, the RE_F/NRMSE internal equivalence, non-redundant public metrics, and required figure-data files.
