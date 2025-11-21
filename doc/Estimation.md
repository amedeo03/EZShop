# Project Estimation

Date: 13/11/25

Version: 1.0

# Estimation approach

Consider the EZShop project as described in your requirements document, assume that you are going to develop the project INDEPENDENT of the deadlines of the course, and from scratch

# Estimate by size

###

|                                                                                                         | Estimate |
| ------------------------------------------------------------------------------------------------------- | -------- |
| NC = Estimated number of classes to be developed                                                        |     11    |
| A = Estimated average size per class, in LOC                                                            |     550     |
| S = Estimated size of project, in LOC (= NC \* A)                                                       |      6050    |
| E = Estimated effort, in person hours (here use productivity 10 LOC per person hour)                    |    605 ph     |
| C = Estimated cost, in euro (here use 1 person hour cost = 30 euro)                                     |    18,150.00 €    |
| Estimated calendar time, in calendar weeks (Assume team of 5 people, 8 hours per day, 5 days per week ) |    ~3 week     |

# Estimate by product decomposition

###

| component name       | Estimated effort (person hours) |
| -------------------- | ------------------------------- |
| Requirement document |                25                 |
| Design document      |                  25               |
| code                 |                 110                |
| code test            |                   70              |
| api and comunication test |               20                  |
|  write documentation |                    25             |
|   total | 275 |


# Estimate by activity decomposition + Gantt chart

###
step 1: activities (WBS), step 2 Gantt chart
| Activity name | Estimated effort (person hours) |
| ------------- | ------------------------------- |
| Requirement analysis and definition | 15 |
| System, architecture and database desing | 20 |
| Cash register comunication and API Development| 25 |
| Backend Development | 70 |
| Database and query Development| 50 |
| Frontend Development | 30 |
| Testing | 100 |
| Create Documentation | 15 |
| Some Feedback | 20 |
| Total| 345 |


###

## Gantt chart
![Grafico gantt](media/gantt.png)


# Summary

|                                    | Estimated effort (ph) | Estimated duration (calendar time, relative)|
| ---------------------------------- | ---------------- | ------------------ |
| estimate by size                   |          605        |         ~3 weeks           |
| estimate by product decomposition  |          275        |         ~2 weeks           |
| estimate by activity decomposition (Gantt) |    345      |             3 weeks       |

The differences between effort-based estimation and size-based estimation come from the fact that the former assumes the work is done by a single person, 
while the latter considers that tasks are split among multiple team members who can work in parallel.
Overall, however, the total project duration remains similar, since it is assumed that the same number of people are working with the same availability throughout the project.