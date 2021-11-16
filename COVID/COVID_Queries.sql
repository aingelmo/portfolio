-- Get the worst day of the covid total cases
SELECT
	t1.location,
	t1.date,
	t1.new_cases
FROM covid_data AS t1
INNER JOIN (
	SELECT
		location,
		MAX(new_cases) AS new_cases
	FROM covid_data
	WHERE new_cases IS NOT null
	GROUP BY location
) AS t2
	ON t1.location = t2.location AND t1.new_cases = t2.new_cases
WHERE t1.continent IS NOT null
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

--Percentage of people who died and the country life expectancy
SELECT
	location,
	MAX(life_expectancy) AS life_expectancy,
	SUM(new_deaths) / MAX(population) * 100 AS percentage_died
FROM covid_data
WHERE continent IS NOT null	AND life_expectancy IS NOT null AND population IS NOT null AND new_deaths IS NOT null
GROUP BY location
ORDER BY percentage_died DESC

--Top days where new cases were reported (Worldwide)
SELECT
	date,
	SUM(new_cases) AS new_cases
FROM covid_data
WHERE continent IS NOT null AND new_cases IS NOT null
GROUP BY date
ORDER BY new_cases DESC 