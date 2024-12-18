CREATE TABLE IF NOT EXISTS country (
	country_id CHAR(3) PRIMARY KEY,
	name VARCHAR(64) NOT NULL
);

CREATE TABLE IF NOT EXISTS athlete (
	athlete_id INT PRIMARY KEY,
	name VARCHAR(128) NOT NULL,
	gender VARCHAR(32),
	date_of_birth DATE,
	height DECIMAL(5,2),
	weight DECIMAL(5,2),
	country_id CHAR(3),
	FOREIGN KEY (country_id) REFERENCES country(country_id)
);

CREATE TABLE IF NOT EXISTS game (
	game_id INT PRIMARY KEY,
	title VARCHAR(128) NOT NULL,
	city VARCHAR(128) NOT NULL,
	start_date DATE,
	end_date DATE,
	was_held BOOLEAN,
	country_id CHAR(3),
	FOREIGN KEY (country_id) REFERENCES country(country_id)
);

CREATE TABLE IF NOT EXISTS sport (
	sport_id INT PRIMARY KEY,
	sport_name VARCHAR(128) NOT NULL,
	is_team_sport BOOLEAN
);

CREATE TABLE IF NOT EXISTS "event" (
	event_id INT PRIMARY KEY,
	event_name VARCHAR(128) NOT NULL,
	gender VARCHAR(32),
	sport_id INT,
	FOREIGN KEY (sport_id) REFERENCES sport(sport_id)
);

CREATE TABLE IF NOT EXISTS "result" (
	result_id INT PRIMARY KEY,
	"position" INT,
	athlete_id INT,
	event_id INT,
	game_id INT,
	FOREIGN KEY (athlete_id) REFERENCES athlete(athlete_id),
	FOREIGN KEY (event_id) REFERENCES "event"(event_id),
	FOREIGN KEY (game_id) REFERENCES game(game_id)
);