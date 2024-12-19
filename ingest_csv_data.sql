COPY country(country_id, name)
FROM '/Users/mischa/Library/Mobile Documents/com~apple~CloudDocs/University of Waterloo/Classes/3B/Databases/Assignments/Group Project/databases_group_k/dataset/country.csv'
WITH (FORMAT csv, DELIMITER ',', HEADER true);

COPY athlete(athlete_id, name, gender, date_of_birth, height, weight, country_id)
FROM '/Users/mischa/Library/Mobile Documents/com~apple~CloudDocs/University of Waterloo/Classes/3B/Databases/Assignments/Group Project/databases_group_k/dataset/athlete.csv'
WITH (FORMAT csv, DELIMITER ',', HEADER true);

COPY game(game_id, title, city, start_date, end_date, was_held, country_id)
FROM '/Users/mischa/Library/Mobile Documents/com~apple~CloudDocs/University of Waterloo/Classes/3B/Databases/Assignments/Group Project/databases_group_k/dataset/game.csv'
WITH (FORMAT csv, DELIMITER ',', HEADER true);

COPY sport(sport_id, name)
FROM '/Users/mischa/Library/Mobile Documents/com~apple~CloudDocs/University of Waterloo/Classes/3B/Databases/Assignments/Group Project/databases_group_k/dataset/sport.csv'
WITH (FORMAT csv, DELIMITER ',', HEADER true);

COPY "event"(event_id, name, gender, is_team_event, sport_id)
FROM '/Users/mischa/Library/Mobile Documents/com~apple~CloudDocs/University of Waterloo/Classes/3B/Databases/Assignments/Group Project/databases_group_k/dataset/event.csv'
WITH (FORMAT csv, DELIMITER ',', HEADER true);

COPY "result"(result_id, "position", game_id, event_id, athlete_id)
FROM '/Users/mischa/Library/Mobile Documents/com~apple~CloudDocs/University of Waterloo/Classes/3B/Databases/Assignments/Group Project/databases_group_k/dataset/result.csv'
WITH (FORMAT csv, DELIMITER ',', HEADER true);
