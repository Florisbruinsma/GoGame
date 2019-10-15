# go_game
Api for the game go
# instructions
Create and object to initialise the game.

you can use **takeTurn** to take the turn of a player.

The game structure is not forced, so you can take multiple turns with the same player.

This can also be used to set up a handicap.

The **takeTurn** function also returns the updated board, the score and if the game is finished by both players passing

To revert back to a previous turn use the **revertBoard** function which resets everything back to that turn

and the **restartGame** function can be used to reset all variables and reset the whole game.

you can also use the **printBoard** function to print the current or given game board with player 1 as x and player 2 as o