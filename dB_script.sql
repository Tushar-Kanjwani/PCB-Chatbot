CREATE DATABASE IF NOT EXISTS pcb_chatbot;
USE pcb_chatbot;

CREATE TABLE players (
    id INT AUTO_INCREMENT PRIMARY KEY,
    player_name VARCHAR(100),
    starting_year INT,
    ending_year INT,
    matches_played INT,
    innings_batted INT,
    not_outs INT,
    runs_scored INT,
    highest_score INT,
    average_score DECIMAL(5,2),
    centuries INT,
    half_centuries INT,
    ducks INT
);

USE pcb_chatbot;
SELECT * FROM players LIMIT 10;

USE pcb_chatbot;

CREATE TABLE chat_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_query TEXT,
    model_response TEXT,
    total_tokens INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO chat_logs (user_query, model_response, total_tokens)
VALUES (
    'Who scored the most runs for Pakistan?',
    'Inzamam-ul-Haq scored the most with 20498 runs.',
    102
);

SELECT * FROM chat_logs ORDER BY created_at DESC LIMIT 10;
