#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSS 458: Fundamentals of Computer Simulation
Class Final Project
Author: Joshua Medvinsky and Daniel Penkov
"""

import numpy as np
import player as p
import random
import copy

# Global variables
turns = 0
deck_count = 1
player_types = ["m", "r", "p","d", "m+", "m++"]
#player_types = ["m", "r", "p"]
player_count = 3
rules = ["pair", "sandwich", "top_bottom", "joker", "marriage",
         "divorce", "3_in_a_row"]
players = []
memorization_range = [2, 5]
reaction_range = [7,9]
placing_range = [2,10]
memorization_value = 5.6
reaction_value = 2
placing_value = 2
miss_slap_value = 2
# tracking slap sizes by game and level
# graph of turns vs amount of decks over 10000 games

def main():
    create_players()
    sim_one_game(players)


def create_players():
    for player in len(player_types):
        players.append(player(player_types[player]), memorization_value,
                                reaction_value, placing_value, miss_slap_value)
    
    
def is_valid_slap(table_deck, rules):
    if rules.count("pair") > 0:
        if len(table_deck) >= 2 and table_deck[-1][0] == table_deck[-2][0]:
            # Slap is a pair
            return True
    if rules.count("sandwich") > 0:
        if len(table_deck) >= 3 and table_deck[-1][0] == table_deck[-3][0]:
            # Slap is a sandwich
            return True
    if rules.count("top_bottom") > 0:
        if len(table_deck) >= 2 and table_deck[-1][0] == table_deck[0][0]:
            # Slap is top/bottom
            return True
    if rules.count("joker") > 0:
        if table_deck[-1][0] == "Joker":
            # Slap is a joker
            return True
    if rules.count("marriage") > 0:
        if len(table_deck) >= 2 and ((table_deck[-1][0] == "Queen" and table_deck[-2][0] == "King")
                                     or (table_deck[-1][0] == "King" and table_deck[-2][0] == "Queen")):
            # Slap is marriage
            return True
    if rules.count("divorce") > 0:
        if len(table_deck) >= 3 and ((table_deck[-1][0] == "Queen" and table_deck[-3][0] == "King")
                                     or (table_deck[-1][0] == "King" and table_deck[-3][0] == "Queen")):
            # Slap is divorce
            return True
    if rules.count("3_in_a_row") > 0:
        if len(table_deck) >= 3:  
            face_cards = {
                    #makes joker untouchable 
                    "Joker": -5,
                    "Jack": 11,
                    "Queen": 12,
                    "King": 13,
                    "Ace": 14
            }
            first = ""
            second = ""
            third = ""
            try:
                first = float(table_deck[-1][0])
            except ValueError:
                first = float(face_cards.get(table_deck[-1][0]))
                
            try:
                second = float(table_deck[-2][0])
            except ValueError:
                second = float(face_cards.get(table_deck[-2][0]))
                
            try:
                third = float(table_deck[-3][0])
            except ValueError:
                third = float(face_cards.get(table_deck[-3][0]))
    
            if are_decreasing(first, second, third) or are_increasing(first, second, third):
                # Slap is 3 in a row
                return True        
    return False
    
def are_decreasing(first, second, third):
    return first + 1 == second and second + 1 == third
    
def are_increasing(first, second, third):
    return third + 1 == second and second + 1 == first

def create_shuffled_game_deck():
    
    table_deck = []
    #Jokers
    table_deck.append(("Joker","Black"))
    table_deck.append(("Joker","Red"))
    #card values list
    card_values = ["Ace","2","3","4","5","6","7","8","9","10","Jack","Queen","King"]
    #suits list
    suits = ["Spades","Diamonds","Clubs","Hearts"]
    for suit in suits:
        for card in card_values:
            table_deck.append(tuple((card,suit)))
            
    random.shuffle(table_deck)
    #uncomment to see deck
    #print(table_deck)
    return table_deck
    
def sim_one_game(players):
    global turns
    players_left = copy.copy(players)
    game_deck = create_shuffled_game_deck()
    faceplacer = -1
    current_player_index = 0
    #face card counter
    face_count = -1
    #table deck
    table_deck = []
    #shuffling cards
    for deck_no in range(deck_count):
        for card in game_deck:
            players_left[current_player_index].deck.append(card)
            current_player_index = get_next_player_index(current_player_index, players_left)
    
    current_player_index = 0
    #prints everyones cards
    for player in players_left:
        print(player.deck)

    #runs while there are more than 1 players left in the game
    while np.size(players_left) > 1:
        for player in players_left:
            print(player.name + ": " + (str)(player.deck))
            print()
        print()
        print("Table deck: " + (str)(table_deck))
        
        #print("CURRENT SIZE--------------- : " +(str)(len(players_left)))
        #print("CURRENT PLAYER INDEX--------------- : " +(str)(current_player_index))
      
        #take card from top of current player
        placed_card = players_left[current_player_index].deck.pop(len(players_left[current_player_index].deck)-1)
        #add card to table deck
        table_deck.append(placed_card)
        #add turn to the game
        turns+=1
        print()
        print(players_left[current_player_index].name + \
              " places a card: " + (str)(placed_card))
        place_time_quicker = False
        
        i = 0
        #index of the fastest player
        fast_index = 0 
        #fast_time = players_left[0].get_reaction_time()
        fast_time = 10000000
        for player in players_left:
            reaction_time = player.get_reaction_time()
            #print(player.name + "'s reaction time: " + (str)(reaction_time))
            if reaction_time < fast_time:
                fast_index = i
                fast_time = reaction_time
            i+=1
        #index of the next placer
        next_player = get_next_player_index(current_player_index, players_left)
        #time of the next place
        place_time = players_left[next_player].get_placing_time()
        #if reaction time is faster than place time
        if(place_time<fast_time):  place_time_quicker = True
        #checks if the current slap is valid
        if is_valid_slap(table_deck, rules):
            
            #print("INSIDE SLAP METHOD")           
            # ---------- Utilizing memorized cards logic ----------
            for player in players_left:
                # Joker is remembered
                if len(table_deck) >= 1 and len(player.memorized_deck) >= 1 and \
                    table_deck[-1][0] == "Joker" and \
                    player.memorized_deck.count(table_deck[-1]) == 1:
                    print(player.name + " memorized the joker and slapped!")
                    # TODO: calculate if they slap
                    player.memorized_deck = []
                    # TODO: remove cards from memorization deck
                # Pair is remembered
                elif len(table_deck) >= 2 and len(player.memorized_deck) >= 2 and \
                    table_deck[-1][0] == table_deck[-2][0] and \
                    player.memorized_deck.count(table_deck[-1]) == 1:
                    pair_card = table_deck[-1]
                    card_value = pair_card[0]
                    card_index = player.memorized_deck.index(pair_card)
                    if card_index < len(player.memorized_deck) - 1 and \
                        card_value == player.memorized_deck[card_index + 1][0]:
                        print(player.name + " memorized the pair of " + (str)(card_value) + "'s and slapped!") 
                        # TODO: calculate if they slap
                        player.memorized_deck = []
                        # TODO: remove cards from memorization deck
                # Top/Bottom is remembered
                elif len(table_deck) >= 2 and len(player.memorized_deck) >= 1 and \
                    table_deck[-1][0] == table_deck[0][0]:
                    target_card = (table_deck[0][0], "top/bottom")
                    card_value = target_card[0]
                    if player.memorized_deck.count(target_card) == 1:
                        print(player.name + " memorized the top/bottom " + (str)(card_value) + "'s and slapped!")
                        # TODO: calculate if they slap
                        player.memorized_deck = []
                        # TODO: remove cards from memorization deck

            
            if place_time > fast_time:
                
                #What happens when a player gets a slap
                print(players_left[fast_index].name + " SLAPPED") 
                print("Table Deck: " + (str)(table_deck))
                #players_left[fast_index].deck.insert(0, table_deck.reverse())
                players_left[fast_index].slaps += 1
                for card in table_deck:
                    players_left[fast_index].deck.insert(0,card)
                    
                players_left[fast_index].slap_cards_gained += len(table_deck)
                players_left[fast_index].slaps += 1
                print(players_left[fast_index].name + " deck after slap:" + (str)(players_left[fast_index].deck))
                
        # -------------------- Memorization logic --------------------
                cards_to_memorize = []
                # Slap is pair or joker
                if len(table_deck) >= 2 and (table_deck[-1][0] == table_deck[-2][0] or \
                    table_deck[-1][0] == "Joker"):
                    cards_to_memorize.append(table_deck[-1])
                    cards_to_memorize.append(table_deck[-2])
                # Slap is top/bottom
                if len(table_deck) >= 2 and table_deck[-1][0] == table_deck[0][0]:
                    card = table_deck[0]
                    new_card = (card[0], "top/bottom")
                    cards_to_memorize.append(new_card)
                #Every player has the chance to memorize the slap cards
                for player in players_left:
                    #Checks if player has enough memorization capacity
                    if (player.memorization_limit - \
                        len(player.memorized_deck)) >= len(cards_to_memorize):
                        if (float)(np.random.randint(0,100)) >= player.memorization_chance:
                            #print("Slap has been memorized!")
                            for card in cards_to_memorize:
                                player.memorized_deck.insert(0, card)
                            #print(player.name + "'s memorization deck: " + (str)(player.memorized_deck))
                                
        # --------------------------------------------------------------
                                
                table_deck = []
                
        # ---------- Updating index logic if player is eliminated ---------
                #if the current players deck is 0
                if np.size(players_left[current_player_index].deck) == 0:
                    print()
                    print("Eliminated Player: " + \
                          (str)(players_left[current_player_index].name))
                    if faceplacer > current_player_index:
                        faceplacer -= 1
                    #current player is eliminated
                    players_left.pop(current_player_index)
                    #if you are the last player do not subtract
                    if current_player_index > fast_index:                            
                        current_player_index = fast_index
                    else:
                        current_player_index = fast_index - 1 
                    
                face_count = -1
                faceplacer = -1
                continue
            else:
                place_time_quicker = True
                #misslap cannot occur on a empty deck
                #if np.size(table_deck)==0:
                 #   continue
        if place_time_quicker == True:    
        # -------------------- Misslap logic --------------------
                #check if any players have empty decks before burn
            i = 0  
            elimination_index = 0
            for player in players_left:
                if np.size(player.deck) == 0:
                    elimination_index = i
                i += 1
                print(players_left[elimination_index].name)
                print("face placer: " + players_left[faceplacer].name)
                #checks if the player has 0 cards and placed a face card last
            if np.size(players_left[elimination_index].deck) == 0 and faceplacer != elimination_index:
                print("Eliminated Player: " + (str)(players_left[elimination_index].name))
                if faceplacer > current_player_index:
                    faceplacer-=1
                players_left.pop(elimination_index)
                if current_player_index == len(players_left):
                    current_player_index = 0
                elimination_index=0
                               
                                                        
                
                #return_to_start=False
                #Scenario in where the placing time is faster than the slap time
                
                # have an outer if statement checking every reaction
            temp_list = []
            reaction_time = 0
            #large constant
            fast_time = 10000000
            bool_list = []
            for player_i in players_left:
                miss_slap_bool = player_i.miss_slap_occured()
                bool_list.append(miss_slap_bool)
                
                        
                reaction_time = player_i.get_reaction_time()
                #print(player.name + "'s reaction time: " + (str)(reaction_time))
                if reaction_time < fast_time:
                    fast_index = i
                    fast_time = reaction_time
                    i+=1
                if miss_slap_bool:
                    temp_list.append(tuple((player_i,fast_time)))
                    miss_slapper = player_i
            fast_time=1000000
                
            for player_i in temp_list:
                if player_i[1]> fast_time:
                    miss_slapper = player_i
                
            print(not is_valid_slap(table_deck, rules))         
            print(any(bool_list))
                     
            #checks if this was a valid slap and someone miss-slaps   
            if is_valid_slap(table_deck, rules) and any(bool_list):   
                print(miss_slapper.name + " SLAPPED") 
                print("Table Deck: " + (str)(table_deck))
                miss_slapper.slaps += 1
                for card in table_deck:
                    miss_slapper.deck.insert(0,card)
                print("IN 1--------------------------------------------------")
                miss_slapper.slap_cards_gained += len(table_deck)
                miss_slapper.slaps += 1
                face_count = -1
                faceplacer = -1
                table_deck = []
                                
                continue
                     
            #ignore a miss slap on a face placer with 0 cards  
            if np.size(players_left[elimination_index].deck) == 0 and faceplacer == elimination_index:
                break
            if (is_valid_slap(table_deck, rules)) ==False and any(bool_list):
                miss_slapper.miss_slaps+=1
                print("IN 2--------------------------------------------------")
                #dont pop if at 0
                if(miss_slapper==0 and faceplacer!= elimination_index):
                    print("Josh's special check")
                    players_left.pop(miss_slapper)
                if(miss_slapper.deck!=0):
                    
                    burn_card = miss_slapper.deck.pop(len(miss_slapper.deck)-1)
                    table_deck.insert(0, burn_card)
                print(miss_slapper.name + " miss-slapped")
                print("Card burned: " + (str)(burn_card))        
            """
                    return_to_start=False
                    miss_slap_bool = player_i.miss_slap_occured()
                    if(miss_slap_bool==True):
                        if is_valid_slap(table_deck, rules):
                            
                            print(player_i.name + " SLAPPED") 
                            print("Table Deck: " + (str)(table_deck))
                            player_i.slaps += 1
                            for card in table_deck:
                                player_i.deck.insert(0,card)
                            print("IN 1--------------------------------------------------")
                            player_i.slap_cards_gained += len(table_deck)
                            player_i.slaps += 1
                            face_count = -1
                            faceplacer = -1
                            
                            return_to_start = True
                            if is_valid_slap(table_deck, rules):
                                table_deck = []
                                
                            continue
                        player_i.miss_slaps+=1
                        print("IN 2--------------------------------------------------")
                        burn_card = player_i.deck.pop(len(player_i.deck)-1)
                        table_deck.insert(0, burn_card)
                        print(player_i.name + " miss-slapped")
                        print("Card burned: " + (str)(burn_card))
                        return_to_start =False    
                        break 
                        if(return_to_start==True):
                            print("returning to start")
                            return_to_start=False
                            """
                    
                        
                
        # -------------------- Face card logic --------------------
        
        if face_count > 0:
             face_count -= 1
        
        # Checks if current placed card is a face card
        #print("Face count: " + (str)(face_count))
        #print("placed card: " + placed_card[0])
        if is_face_card(placed_card):
            faceplacer = current_player_index
            face_count = ["Jack", "Queen", "King", "Ace"].index(placed_card[0]) + 1
            current_player_index = get_next_player_index(current_player_index, players_left)
        
       
        if face_count == -1:
            #go to next player
            current_player_index= get_next_player_index(current_player_index, players_left)
       
        if face_count == 0:
            
            #player who placed face card recieves cards if count is 0
            for card in table_deck:
                    players_left[faceplacer].deck.insert(0,card)
            players_left[faceplacer].face_cards_gained+=len(table_deck)
            table_deck = []
            current_player_index = faceplacer
            face_count = -1
            faceplacer = -1
            print(players_left[current_player_index].name + " won off of face cards")
        
        i = 0  
        elimination_index = 0
        for player in players_left:
            if np.size(player.deck) == 0:
                elimination_index = i
            i += 1
        
        #removes player from the game if they run out of cards and the last card they placed was a number
        if np.size(players_left[elimination_index].deck) == 0 and faceplacer != elimination_index:
            print("Eliminated Player: " + (str)(elimination_index))
            if faceplacer > current_player_index:
                        faceplacer-=1
            players_left.pop(elimination_index)
            if current_player_index == len(players_left):
                current_player_index = 0
        print()
    #inserts the cards to winner once the game ends    
    for card in table_deck:
        players_left[faceplacer].deck.insert(0,card)
    #victory message and adds to win count
    print(players_left[0].name + " wins!")
    players_left[0].wins += 1

        
#helper methods            
#runs one game a given amount of times with new players each game
def hundomundo():
    for x in range(10):
        sim_one_game(dummy_players())
        
#gets next player index
def get_next_player_index(current_index, players):
    if current_index == np.size(players) - 1:
        return 0
    else:
        return current_index + 1
#gets the last player index
def get_last_player_index(current_index, players):
    if current_index == 0:
        return np.size(players) - 1
    else:
        return current_index - 1
#method which checks if the card is a face card
def is_face_card(placed_card):
    face_cards = ["Jack", "Queen", "King", "Ace"]
    return face_cards.count(placed_card[0]) == 1
# empty decks
def empty_deck(player_list):
    for player in player_list:
        player.deck = []
#creates 3 dummy players for testing
def dummy_players():
    
    playerOne = p.player("Player 1", "water",5,3,5,5)
    playerTwo = p.player("Player 2", "fire",5,5,5,5)
    playerThree = p.player("Player 3", "earth",5,7,5,5)
    
    playerList = [playerOne,playerTwo,playerThree]
    return playerList        
  

def sim_x_games(number_of_games,x_game_players):
    #x_game_players =dummy_players()
    reset=x_game_players[:]
    #run games x times
    for x in range(number_of_games):
        #resets the list at the start of forloop
        x_game_players = reset
        sim_one_game(x_game_players)
        #empty deck
        empty_deck(x_game_players)
     
    #print out stats
    for player in x_game_players:
        print(player.name + ":") 
        print("    Wins: " + (str)(player.wins))
        print("    Slaps: "+ (str)(player.slaps))
        print("    Slap Cards gained: " + (str)(player.slap_cards_gained))
        print("    Face cards gained: " + (str)(player.face_cards_gained))
        print("    Misslaps: " + (str)(player.miss_slaps))
    return reset