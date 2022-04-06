# PERFORMANCE

Performance report data web app.

Python 3
Flask
SQLAlchemy

# When delay codes show

DIFF is the number of minutes between estimated and actual times, calculated such that it is always positive. Then, if estimated time is greater than actual time, it is set to negative.

LATE_GT is a configured threshold number of minutes, defaulting to zero.

```mermaid
flowchart TD
    A{DIFF \n> LATE_GT?} -- Yes --> E
    A -- No --> C
    A -- No --> B{Any XLD code?}
    B -- Yes --> E
    B -- No --> C[Do not show]
    E[Show delay codes]
```

# INCIDENTS

* #16585 hide delays from report for config LATE_GT.
* #19499 an incident that became a place to put a flurry of reported errors.
