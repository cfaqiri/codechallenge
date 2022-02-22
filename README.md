# Introduction
This project is an API inspired by the requirements of the Payroll code challenge written by Wave Financial for their Full-Stack Engineer applicants. See [Wave Software Development Challenge](https://github.com/wvchallenges/se-challenge-payroll) for more details. 

# Features
This API has two endpoints:
- One endpoint to **upload** a csv file containing timekeeping data for employees
- Another endpoint to **retrieve** a report containing payroll information based on a bi-monthly pay cycle

# Prerequisites
PostgreSQL is required to accommodate the DecimalFields used in this project. 

# Assumptions
Beyond the assumptions already outlined in requirements in the link above, the API assumes that job groups have been created in advance of uploading a csv file that contains timekeeping information. 

# Installation
1. Clone the repository
   ```git clone https://github.com/cfaqiri/codechallenge.git```
3. Install the requirements
4. Configure a PostgreSQL server in settings.py
5. Make the migrations
6. Create a superuser
7. Add job groups in the admin


