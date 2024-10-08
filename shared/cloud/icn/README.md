# ICN ELO penalties processing

## Prerequisites

- we need to have the quarterly belgian Elo list (csv format)
- we need to have the monthly FIDE Elo list (csv format)

Both files are stored in this directory.   Be aware that the FIDE list must be processed
in the month it is used, as the fide table in the database is overwritten every month

## Penalties

One csv file is created per round checking 
- check forfaits
- check signatures
- check_order_players
- check_average_elo
- check_titular_ok
- check_reserves_in_single_series

## Elo processing

3 TRF reports are generated per round

- first part of Belgian elo (Division 1 to 4)
- second part of Belgian elo (Division 5)
- FIDE report