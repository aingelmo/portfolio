-- Get the worst day of the covid total cases
SELECT
	t1.location AS location,
	MAX(t1.date) AS date,
	MAX(t1.new_cases) AS new_cases
FROM covid_data AS t1
INNER JOIN (
	SELECT
		location,
		MAX(new_cases) AS new_cases
	FROM covid_data
	WHERE new_cases IS NOT null AND continent IS NOT null
	GROUP BY location
) AS t2
	ON t1.location = t2.location AND t1.new_cases = t2.new_cases
WHERE t1.continent IS NOT null
GROUP BY t1.location
ORDER BY new_cases DESC

-- Get the worst day of the covid total cases with CTE
--- Define the CTE expression name and column list
WITH newCases_country (location, date, new_cases) 
AS
--- Define the CTE query
(
	SELECT
		t1.location AS location,
		MAX(t1.date) AS date,
		MAX(t1.new_cases) AS new_cases
	FROM covid_data AS t1
	INNER JOIN (
		SELECT
			location,
			MAX(new_cases) AS new_cases
		FROM covid_data
		WHERE new_cases IS NOT null AND continent IS NOT null
		GROUP BY location
	) AS t2
		ON t1.location = t2.location AND t1.new_cases = t2.new_cases
	WHERE t1.continent IS NOT null
	GROUP BY t1.location
)
--- Define the outer query referencing the CTE name
SELECT *
FROM newCases_country

-- Get the worst day of the covid new cases measured by new cases per million
SELECT
	t1.location AS location,
	MAX(t1.date) AS date,
	MAX(ROUND(t1.new_cases / population * 1000000)) AS new_cases
FROM covid_data AS t1
INNER JOIN (
	SELECT
		location,
		MAX(ROUND(new_cases / population * 1000000)) AS new_cases
	FROM covid_data
	WHERE new_cases IS NOT null AND continent IS NOT null
	GROUP BY location
) AS t2
	ON t1.location = t2.location AND t1.new_cases = t2.new_cases
WHERE t1.continent IS NOT null
GROUP BY t1.location
ORDER BY new_cases DESC

-- Get the worst day of the covid in deaths
SELECT
	t1.location,
	t1.date,
	t1.new_deaths
FROM covid_data AS t1
INNER JOIN (
	SELECT
		location,
		MAX(new_deaths) AS new_deaths
	FROM covid_data
	WHERE new_deaths IS NOT null
	GROUP BY location
) AS t2
	ON t1.location = t2.location AND t1.new_deaths = t2.new_deaths
WHERE t1.continent IS NOT null
ORDER BY new_deaths DESC

-- Ranking of countries by percentage of population vaccinated
SELECT
	location,
	MAX(people_fully_vaccinated) AS people_fully_vaccinated,
	MAX(people_fully_vaccinated) / MAX(population) * 100 AS percentage_fully_vaccinated
FROM covid_data
WHERE continent IS NOT null	AND people_fully_vaccinated IS NOT null
	AND population IS NOT null
GROUP BY location
ORDER BY percentage_fully_vaccinated DESC

-- Percentage of people who died and the country life expectancy
SELECT
	location,
	MAX(life_expectancy) AS life_expectancy,
	SUM(new_deaths) / MAX(population) * 100 AS percentage_died
FROM covid_data
WHERE continent IS NOT null	AND life_expectancy IS NOT null AND population IS NOT null AND new_deaths IS NOT null
GROUP BY location
ORDER BY percentage_died DESC

-- Create a view of the last query to use in future analysis
CREATE VIEW mortalityRate_lifeExpectancy AS
SELECT
	location,
	MAX(life_expectancy) AS life_expectancy,
	SUM(new_deaths) / MAX(population) * 100 AS percentage_died
FROM covid_data
WHERE continent IS NOT null	AND life_expectancy IS NOT null AND population IS NOT null AND new_deaths IS NOT null
GROUP BY location
ORDER BY percentage_died DESC

-- Top days where new cases were reported (Worldwide)
SELECT
	date,
	SUM(new_cases) AS new_cases
FROM covid_data
WHERE continent IS NOT null AND new_cases IS NOT null
GROUP BY date
ORDER BY new_cases DESC 

-- Get correlation coefficient between percentage of smoking population and deaths
SELECT CORR(smokers, deaths_per_100000)
FROM
	(SELECT
		location,
		(MAX(female_smokers) + MAX(male_smokers))/2 AS smokers,
		MAX(total_deaths) / MAX(population) * 100000 AS deaths_per_100000
	FROM covid_data
	WHERE male_smokers IS NOT null AND continent IS NOT null AND total_deaths IS NOT null
	GROUP BY location) AS t

-- Get correlation coefficient between percentage of smoking population and deaths without a builtin function
SELECT
	((tot_sum - (smokers_sum * deaths_per_100000_sum / _count)) / SQRT((smokers_sum_sq - pow(smokers_sum, 2.0) / _count) * (deaths_per_100000_sum_sq - pow(deaths_per_100000_sum, 2.0) / _count))) AS pearson_corr
FROM(
	SELECT
		SUM(smokers) AS smokers_sum,
		SUM(deaths_per_100000) AS deaths_per_100000_sum,
		SUM(smokers * smokers) AS smokers_sum_sq,
		SUM(deaths_per_100000 * deaths_per_100000) AS deaths_per_100000_sum_sq,
		SUM(smokers * deaths_per_100000) AS tot_sum,
		COUNT(*) AS _count
	FROM
		(SELECT
			location,
			(MAX(female_smokers) + MAX(male_smokers))/2 AS smokers,
			MAX(total_deaths) / MAX(population) * 100000 AS deaths_per_100000
		FROM covid_data
		WHERE male_smokers IS NOT null AND continent IS NOT null AND total_deaths IS NOT null
		GROUP BY location) AS t1
	) AS t2