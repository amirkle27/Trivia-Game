
CREATE TABLE questions (
    question_id SERIAL PRIMARY KEY,
    question_text TEXT NOT NULL,
    answer_a TEXT NOT NULL,
    answer_b TEXT NOT NULL,
    answer_c TEXT NOT NULL,
    answer_d TEXT NOT NULL,
    correct_answer CHAR(1) CHECK (correct_answer IN ('a', 'b', 'c', 'd')) NOT NULL
);

CREATE TABLE players (
    player_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,  -- better to encrypt
    email VARCHAR(100) UNIQUE NOT NULL,
    age INTEGER NOT NULL,
    questions_solved INTEGER DEFAULT 0
);

CREATE TABLE player_answers (
    player_id INTEGER REFERENCES players(player_id) ON DELETE CASCADE,
    question_id INTEGER REFERENCES questions(question_id) ON DELETE CASCADE,
    selected_answer CHAR(1) CHECK (selected_answer IN ('a', 'b', 'c', 'd')) NOT NULL,
    is_correct BOOLEAN NOT NULL,
    PRIMARY KEY (player_id, question_id) -- Composite primary key
);

--   drop table high_scores
CREATE TABLE high_scores (
    player_id INTEGER REFERENCES players(player_id) ON DELETE CASCADE,
    score_id  SERIAL PRIMARY KEY, -- representing scores from 1 to 20
    achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE high_scores
ADD COLUMN started_at TIMESTAMP DEFAULT NULL,
ADD COLUMN finished_at TIMESTAMP DEFAULT NULL,
ADD COLUMN total_game_time INTERVAL NULL,
ADD COLUMN score integer DEFAULT 0,
DROP COLUMN achieved_at;
CREATE INDEX ON high_scores (score DESC);


CREATE TABLE new_player_log (
    player_id INTEGER PRIMARY KEY REFERENCES players(player_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO questions (question_text,
                       answer_a,
                       answer_b,
                       answer_c,
                       answer_d,
                       correct_answer
                       ) VALUES
                        ('What is the capital of France?','Rome','Madrid','Berlin','Paris','d'),
                        ('Who wrote "To Kill a Mockingbird"?','Harper Lee','Mark Twain','J.K. Rowling','Ernest Hemingway','a'),
                        ('What is the largest planet in our solar system?','Earth','Jupiter','Mars','Venus','b'),
                        ('In what year did the Titanic sink?','1912','1920','1898','1905','a'),
                        ('Which element has the chemical symbol "O"?','Oxygen','Gold','Hydrogen','Helium','a'),
                        ('Who painted the Mona Lisa?','Vincent van Gogh','Pablo Picasso','Claude Monet','Leonardo da Vinci','d'),
                        ('What is the square root of 64?','6','7','8','9','c'),
                        ('Which country is known as the Land of the Rising Sun?','China','Japan','South Korea','Thailand','b'),
                        ('Who discovered penicillin?','Alexander Fleming','Marie Curie','Albert Einstein','Isaac Newton','a'),
                        ('What is the currency of the United Kingdom?','Dollar','Euro','Pound Sterling','Yen','c'),
                        ('How many continents are there?','5','6','7','8','c'),
                        ('Who was the first person to walk on the moon?','Buzz Aldrin','Michael Collins','Neil Armstrong','Yuri Gagarin','c'),
                        ('Which ocean is the largest?','Atlantic','Indian','Arctic','Pacific','d'),
                        ('What is the chemical symbol for water?','CO2','H2O','O2','H2','b'),
                        ('Who is known as the Father of Computers?','Alan Turing','Charles Babbage','Thomas Edison','Nikola Tesla','b'),
                        ('What is the smallest country in the world?','Monaco','San Marino','Vatican City','Liechtenstein','c'),
                        ('Which planet is closest to the sun?','Earth','Venus','Mars','Mercury','d'),
                        ('How many bones are in the adult human body?','206','205','210','212','a'),
                        ('Who wrote "1984"?','George Orwell','Aldous Huxley','F. Scott Fitzgerald','J.R.R. Tolkien','a'),
                        ('What is the longest river in the world?','Amazon','Nile','Yangtze','Mississippi','b'),
                        ('Which gas do plants absorb from the atmosphere?','Oxygen','Nitrogen','Carbon Dioxide','Helium','c'),
                        ('Who invented the telephone?','Thomas Edison','Alexander Graham Bell','Nikola Tesla','Guglielmo Marconi','b'),
                        ('What is the hardest natural substance on Earth?','Gold','Iron','Diamond','Quartz','c'),
                        ('Which country gifted the Statue of Liberty to the United States?','France','Germany','Spain','Italy','a'),
                        ('What is the chemical symbol for gold?','Au','Ag','Fe','Pb','a'),
                        ('How many planets are in our solar system?','7','8','9','10','b'),
                        ('Who wrote "Pride and Prejudice"?','Jane Austen','Emily Brontë','Charles Dickens','George Eliot','a'),
                        ('What is the tallest mountain in the world?','K2','Mount Everest','Kangchenjunga','Kilimanjaro','b'),
                        ('Which country is the largest by area?','Canada','China','Russia','United States','c'),
                        ('Who painted "Starry Night"?','Pablo Picasso','Vincent van Gogh','Claude Monet','Salvador Dalí','b'),
                        ('What is the main ingredient in guacamole?','Tomato','Avocado','Onion','Pepper','b'),
                        ('Which planet is known as the Red Planet?','Jupiter','Mars','Saturn','Neptune','b'),
                        ('Who is the author of the Harry Potter series?','J.K. Rowling','J.R.R. Tolkien','C.S. Lewis','Suzanne Collins','a'),
                        ('What is the largest mammal?','African Elephant','Blue Whale','Giraffe','Hippopotamus','b'),
                        ('What is the boiling point of water at sea level?','90°C','95°C','100°C','105°C','c'),
                        ('Who developed the theory of relativity?','Isaac Newton','Albert Einstein','Galileo Galilei','Niels Bohr','b'),
                        ('Which organ is responsible for pumping blood throughout the body?','Liver','Kidney','Heart','Lungs','c'),
                        ('What is the capital of Japan?','Beijing','Seoul','Tokyo','Bangkok','c'),
                        ('Who wrote "The Great Gatsby"?','Ernest Hemingway','F. Scott Fitzgerald','Mark Twain','John Steinbeck','b'),
                        ('Which vitamin is produced when a person is exposed to sunlight?','Vitamin A','Vitamin B','Vitamin C','Vitamin D','d'),
                        ('What is the largest desert in the world?','Sahara','Gobi','Kalahari','Arctic','a'),
                        ('Who was the first President of the United States?','Thomas Jefferson','Benjamin Franklin','George Washington','John Adams','c'),
                        ('Which element has the chemical symbol "Fe"?','Lead','Iron','Zinc','Copper','b'),
                        ('What is the currency of Japan?','Yuan','Yen','Won','Dollar','b'),
                        ('What is the largest internal organ in the human body?','Heart','Liver','Kidney','Lungs','b'),
                        ('Who wrote "The Odyssey"?','Homer','Virgil','Sophocles','Plato','a'),
                        ('What is the most widely spoken language in the world?','English','Spanish','Mandarin','Hindi','c'),
                        ('What is the smallest planet in our solar system?','Mars','Mercury','Venus','Neptune','b'),
                        ('Which city hosted the 2016 Summer Olympics?','London','Tokyo','Rio de Janeiro','Beijing','c'),
                        ('Who was the Greek god of the sea?','Zeus','Hades','Poseidon','Apollo','c'),
                        ('What is the freezing point of water?','0°C','32°C','100°C','50°C','a'),
                        ('Which artist cut off his own ear?','Claude Monet','Pablo Picasso','Vincent van Gogh','Salvador Dalí','c'),
                        ('What is the capital of Australia?','Sydney','Melbourne','Canberra','Perth','c'),
                        ('What is the largest island in the world?','Greenland','Australia','New Guinea','Borneo','a'),
                        ('Who discovered America?','Ferdinand Magellan','Christopher Columbus','Leif Erikson','Amerigo Vespucci','b'),
                        ('What is the powerhouse of the cell?','Nucleus','Ribosome','Mitochondria','Golgi apparatus','c'),
                        ('Which language has the most native speakers?','English','Mandarin','Spanish','Hindi','b'),
                        ('Who was the first woman to win a Nobel Prize?','Marie Curie','Rosalind Franklin','Ada Lovelace','Jane Goodall','a'),
                        ('What is the longest bone in the human body?','Fibula','Tibia','Femur','Humerus','c'),
                        ('Which planet is known for its rings?','Mars','Jupiter','Saturn','Uranus','c'),
                        ('What is the largest ocean on Earth?','Atlantic','Indian','Pacific','Arctic','c'),
                        ('Who wrote "Moby-Dick"?','Mark Twain','Herman Melville','Charles Dickens','Nathaniel Hawthorne','b'),
                        ('What is the main gas found in the air we breathe?','Oxygen','Nitrogen','Carbon Dioxide','Hydrogen','b'),
                        ('Who invented the light bulb?','Nikola Tesla','Alexander Graham Bell','Thomas Edison','Guglielmo Marconi','c'),
                        ('What is the capital of Italy?','Rome','Florence','Milan','Naples','a'),
                        ('Which organ is responsible for filtering blood?','Heart','Kidney','Liver','Lungs','b'),
                        ('Who painted "The Last Supper"?','Michelangelo','Raphael','Leonardo da Vinci','Donatello','c'),
                        ('What is the chemical symbol for sodium?','S','Na','K','Cl','b'),
                        ('Which planet is known as the Evening Star?','Mars','Venus','Jupiter','Saturn','b'),
                        ('Who is the author of "The Catcher in the Rye"?','J.D. Salinger','F. Scott Fitzgerald','Ernest Hemingway','John Steinbeck','a'),
                        ('What is the chemical symbol for potassium?','P','K','Po','Pt','b'),
                        ('What is the smallest bone in the human body?','Stapes','Femur','Tibia','Radius','a'),
                        ('Who was the first man to reach the South Pole?','Roald Amundsen','Robert Scott','Ernest Shackleton','Richard Byrd','a'),
                        ('Which country is known for the dance Flamenco?','Portugal','Spain','Italy','Argentina','b'),
                        ('Who developed the polio vaccine?','Alexander Fleming','Jonas Salk','Louis Pasteur','Robert Koch','b'),
                        ('What is the capital of Canada?','Toronto','Vancouver','Ottawa','Montreal','c'),
                        ('Which metal is liquid at room temperature?','Iron','Mercury','Copper','Gold','b'),
                        ('Who was the lead singer of Queen?','Mick Jagger','Freddie Mercury','David Bowie','Elton John','b'),
                        ('What is the largest continent?','Africa','Asia','Europe','South America','b'),
                        ('Who wrote "The Lord of the Rings"?','J.K. Rowling','J.R.R. Tolkien','C.S. Lewis','George R.R. Martin','b'),
                        ('What is the smallest prime number?','0','1','2','3','c'),
                        ('Which gas is most abundant in the atmosphere?','Oxygen','Carbon Dioxide','Nitrogen','Helium','c'),
                        ('Who painted "The Scream"?','Edvard Munch','Pablo Picasso','Claude Monet','Vincent van Gogh','a'),
                        ('What is the chemical symbol for iron?','Ir','Fe','In','I','b'),
                        ('Which planet is known as the Blue Planet?','Mars','Earth','Neptune','Uranus','b'),
                        ('Who discovered gravity when he saw a falling apple?','Albert Einstein','Galileo Galilei','Isaac Newton','Johannes Kepler','c'),
                        ('What is the name of the longest river in South America?','Amazon','Nile','Yangtze','Mississippi','a'),
                        ('Who was the first female Prime Minister of the United Kingdom?','Margaret Thatcher','Theresa May','Angela Merkel','Indira Gandhi','a'),
                        ('What is the main ingredient in hummus?','Chickpeas','Lentils','Beans','Peas','a'),
                        ('Which planet is closest in size to Earth?','Mars','Venus','Jupiter','Mercury','b'),
                        ('Who was known as the Maid of Orléans?','Catherine the Great','Joan of Arc','Marie Antoinette','Queen Elizabeth I','b'),
                        ('What is the largest type of whale?','Humpback Whale','Blue Whale','Beluga Whale','Orca','b'),
                        ('Who is the Greek goddess of wisdom?','Aphrodite','Hera','Athena','Demeter','c'),
                        ('What is the capital of Egypt?','Cairo','Alexandria','Luxor','Giza','a'),
                        ('Which scientist proposed the theory of evolution by natural selection?','Gregor Mendel','Charles Darwin','Louis Pasteur','Isaac Newton','b'),
                        ('What is the longest running Broadway show?','The Phantom of the Opera','Cats','Les Misérables','Chicago','a'),
                        ('Which vitamin is also known as ascorbic acid?','Vitamin A','Vitamin B12','Vitamin C','Vitamin D','c'),
                        ('Who invented the World Wide Web?','Bill Gates','Steve Jobs','Tim Berners-Lee','Mark Zuckerberg','c'),
                        ('Which natural disaster is measured with a Richter scale?','Tornado','Earthquake','Hurricane','Flood','b'),
                        ('What is the capital of Argentina?','Buenos Aires','Lima','Santiago','Montevideo','a'),
                        ('Who wrote "Frankenstein"?','Mary Shelley','Bram Stoker','Edgar Allan Poe','H.G. Wells','a'),
                        ('Which element has the atomic number 1?','Oxygen','Hydrogen','Carbon','Helium','b'),
                        ('What is the largest land animal?','Giraffe','Elephant','Hippopotamus','Rhinoceros','b'),
                        ('Who was the first African American president of the United States?','Barack Obama','George Washington','Abraham Lincoln','Bill Clinton','a'),
                        ('What is the capital city of Thailand?','Hanoi','Bangkok','Manila','Jakarta','b'),
                        ('Which planet is known for having a Great Red Spot?','Mars','Venus','Jupiter','Saturn','c'),
                        ('Who wrote "The Divine Comedy"?','Dante Alighieri','Geoffrey Chaucer','John Milton','Virgil','a'),
                        ('What is the process by which plants make their food?','Respiration','Digestion','Photosynthesis','Fermentation','c'),
                        ('What is the capital of South Korea?','Seoul','Pyongyang','Tokyo','Busan','a'),
                        ('Which is the fastest land animal?','Cheetah','Lion','Horse','Gazelle','a'),
                        ('Who was the last queen of France?','Marie Antoinette','Catherine de Medici','Joan of Arc','Anne of Austria','a')

