# COVID-19 SQL project

## Introduction

The purpose of this project is to show my Python and SQL skills analyzing a huge database created by [Our World In Data](https://github.com/owid/covid-19-data).

## Set up

In order to set up the proper SQL environment, I decided to run Postgres SQL on my Raspberry Pi and update the data all nights. You can check the script I wrote for this matter here: [database_connect.py](https://github.com/aingelmo/portfolio/blob/main/COVID/database_connect.py).

### Requirements

To run PostgreSQL on a Raspberry Pi, you can find multiple tutorials on the internet like [this one](https://opensource.com/article/17/10/set-postgres-database-your-raspberry-pi).

We would also need PostgreSQL for Windows. You can download it [here](https://www.postgresql.org/download/).

### Connection

After installing PostgreSQL, we would need to connect to the Raspberry Pi's server. In my case, I have my RP running permanently at `192.168.1.7`. In my case, it looks like this:

![RP PostgreSQL server](https://i.imgur.com/CsYICYb.png)

We are ready now to start writing our queries!