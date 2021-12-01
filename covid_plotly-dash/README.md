# COVID dashboard on Plotly Dash running on Heroku
The purpose of this application is learning to use Dash, Plotly and website deployment. 

## Dataset
The dataset used for the project is compiled by [Our World in Data](https://github.com/owid/covid-19-data/tree/master/public/data#the-complete-our-world-in-data-covid-19-dataset).

It is an extensive dataset with more than 60 different metrics updated daily from multiple sources.

| Metrics                     | Source                                                    | Updated | Countries |
|-----------------------------|-----------------------------------------------------------|---------|-----------|
| Vaccinations                | Official data collated by the Our World in Data team      | Daily   | 218       |
| Tests & positivity          | Official data collated by the Our World in Data team      | Weekly  | 139       |
| Hospital & ICU              | Official data collated by the Our World in Data team      | Weekly  | 38        |
| Confirmed cases             | JHU CSSE COVID-19 Data                                    | Daily   | 196        |
| Confirmed deaths            | JHU CSSE COVID-19 Data                                    | Daily   | 196       |
| Reproduction rate           | Arroyo-Marioli F, Bullano F, Kucinskas S, Rondón-Moreno C | Daily   | 185        |
| Policy responses            | Oxford COVID-19 Government Response Tracker               | Daily   | 186        |
| Other variables of interest | International organizations (UN, World Bank, OECD, IHME…) | Fixed   | 241       |

## Dashboard
The dashboard allows the user to compare different data in a scatter plot. The user can select one variable for the each of the axis (X and Y).

It also shows the evolution of the variables in time over the right side.

## Use
Please, go to [this site](https://aingelmo.github.io/dash) to use the dashboard.
