C:\Users\123\PycharmProjects\trivia_game\.venv\Scripts\python.exe C:\Users\123\PycharmProjects\trivia_game\trivia_game.py 
                                                      Hello, and welcome to:                                                      
                                                         The Trivia Game!                                                          

Please choose one of the options below:

    1. New Player Sign-in [Press N]
    2. Existing Player Log-in [Press E]
    3. Show Statistics [Press S]
    4. Quit the Game [Press Q]

n
Please enter a username: 
saba
Please enter a password: 
avta
Please re-enter your Password: 
savta
Please enter your E-mail address: 
sav@e.com
Please enter your age: 
99
Passwords mismatch. Please try again or press [q] to go back to main menuavta
Please enter a username: 
saba
Please enter a password: 
savta
Please re-enter your Password: 
savta
Please enter your E-mail address: 
saba@saba.com
Please enter your age: 
99
Fetch result: [17]
Player saba created successfully with ID:
17 
Questions stored in MongoDB for player_id: 17
                                                   GET READY, STARTING THE QUIZ!                                                   

                                                  Who is the author of the Harry Potter series?

                                        a.J.K. Rowling                             b.J.R.R. Tolkien

                                        c. C.S. Lewis                              d.Suzanne Collins

Please enter your answer:
Is it (a), (b), (c), or (d)? 
a
Correct Answer!


                                                  Who was the last queen of France?

                                        a.Marie Antoinette                         b.Catherine de Medici

                                        c. Joan of Arc                             d.Anne of Austria

Please enter your answer:
Is it (a), (b), (c), or (d)? 
Traceback (most recent call last):
  File "C:\Users\123\PycharmProjects\trivia_game\trivia_game.py", line 267, in <module>
    main_menu()
  File "C:\Users\123\PycharmProjects\trivia_game\trivia_game.py", line 248, in main_menu
    start_quiz(player_id)
  File "C:\Users\123\PycharmProjects\trivia_game\trivia_game.py", line 138, in start_quiz
    answer = input(
             ^^^^^^
  File "<frozen codecs>", line 319, in decode
KeyboardInterrupt

Process finished with exit code -1073741510 (0xC000013A: interrupted by Ctrl+C)
