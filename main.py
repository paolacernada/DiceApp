import random
import sys
import time
import itertools
import os
from colorama import init, Fore, Back, Style
import pygame
import zmq

# Initialize colorama for colored text
init(autoreset=True)

# Initialize pygame mixer for sound effects
pygame.mixer.init()

# Theme settings for different visual styles
themes = {
    'classic': {'header': Fore.CYAN + Style.BRIGHT,
                'option': Fore.YELLOW, 'border': Fore.CYAN + Style.BRIGHT,
                'text': Fore.GREEN, 'highlight': Fore.MAGENTA},
    'dark': {'header': Fore.WHITE + Back.BLACK + Style.BRIGHT,
             'option': Fore.YELLOW + Back.BLACK,
             'border': Fore.WHITE + Back.BLACK + Style.BRIGHT,
             'text': Fore.LIGHTWHITE_EX + Back.BLACK,
             'highlight': Fore.LIGHTMAGENTA_EX + Back.BLACK},
    'retro': {'header': Fore.GREEN + Back.YELLOW + Style.BRIGHT,
              'option': Fore.MAGENTA + Back.YELLOW,
              'border': Fore.GREEN + Back.YELLOW + Style.BRIGHT,
              'text': Fore.BLUE + Back.YELLOW,
              'highlight': Fore.RED + Back.YELLOW}
}

# Default settings for theme and sounds
current_theme = 'classic'
current_dice_sound = 'default'
achievements = []
scores = {}


# Function to request weather data from microservice A
def request_weather_data(city_name):
    # Establish the communication pipeline
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    # Send the city name to microservice A
    socket.send_string(city_name)

    # Receive a JSON object from microservice A and return object
    reply = socket.recv_pyobj()
    return reply


# Apply the current theme settings to global variables
def apply_theme():
    global header_color, option_color, border_color
    global text_color, highlight_color
    header_color = themes[current_theme]['header']
    option_color = themes[current_theme]['option']
    border_color = themes[current_theme]['border']
    text_color = themes[current_theme]['text']
    highlight_color = themes[current_theme]['highlight']


apply_theme()


def magenta_text(text):
    return Fore.MAGENTA + text


def formatted_line(descriptor, value, width):
    descriptor_formatted = f"{descriptor:<{width - len(value) - 1}}"
    return text_color + "| " + descriptor_formatted + magenta_text(value) + text_color + "  |"


# Function to display weather information
def display_weather_info():
    clear_screen()
    print_header("Hey Gamer, Check the Weather!")

    print(text_color + "Enter a city name: ", end="")
    city_name = input(Fore.MAGENTA)

    clear_screen()
    print_header("Hey Gamer, Check the Weather!")

    try:
        weather_data = request_weather_data(city_name)
        if weather_data.get('cod') == 200:
            fixed_width = 42

            print(formatted_line("Location:", weather_data['name'], fixed_width))
            print(formatted_line("Weather Conditions:", weather_data['weather'][0]['description'], fixed_width))
            print(formatted_line("Temperature:", f"{weather_data['main']['temp']}°F", fixed_width))
            print(formatted_line("Low:", f"{weather_data['main']['temp_min']}°F", fixed_width))
            print(formatted_line("High:", f"{weather_data['main']['temp_max']}°F", fixed_width))
            print(formatted_line("Humidity:", f"{weather_data['main']['humidity']}%", fixed_width))
            print(formatted_line("Wind Speed:", f"{weather_data['wind']['speed']} mph", fixed_width))
        else:
            print(Fore.RED + "| Error retrieving weather data. Try again.  |")

    except Exception as e:
        print(Fore.RED + f"Error: {e}")

    print_border()
    print_option(1, "Back to Welcome Page")
    print_option(2, "Exit")
    print_border()
    print(text_color + "Please select an option: ", end="")
    choice = input(Fore.MAGENTA)
    if choice == '1':
        welcome_page()
    elif choice == '2':
        exit_application()
    else:
        print(Fore.RED + "Invalid selection. Please try again.")
        display_weather_info()


# Clear the console screen
def clear_screen():
    _ = os.system('cls' if os.name == 'nt' else 'clear')


# Print header with given title
def print_header(title):
    print(header_color + "\n+" + "-"*44 + "+")
    print(header_color + f"|{title.center(44)}|")
    print(header_color + "+" + "-"*44 + "+")


# Print option with a number and text
def print_option(number, option):
    print(option_color + f"| {number}. {option:<39} |")


# Print border line
def print_border():
    print(border_color + "+" + "-"*44 + "+")


# Play sound with optional looping
def play_sound(filename, loop=False):
    try:
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play(-1 if loop else 0)
    except Exception as e:
        print(Fore.RED + f"Error playing sound: {e}")


# Stop any playing sound
def stop_sound():
    pygame.mixer.music.stop()


# Welcome page with main options
def welcome_page():
    clear_screen()
    print_header("Welcome to the Dice App!")
    print(text_color + "| This app allows you to roll virtual dice   |")
    print(text_color + "| for your board games and RPG sessions.     |")
    print(text_color + "|                                            |")
    print(text_color + "| Rolling a virtual die is free and no       |")
    print(text_color + "| personal data is collected.                |")
    print(text_color + "|                                            |")
    print_option(1, "Start Rolling Dice")
    print_option(2, "Play Dice Duel")
    print_option(3, "Achievements")
    print_option(4, "Check Today's Weather")
    print_option(5, "Help")
    print_option(6, "Exit")
    print_border()
    print(text_color + "Please select an option: ", end="")
    choice = input(Fore.MAGENTA)
    if choice == '1':
        set_rerolls()
    elif choice == '2':
        play_dice_duel()
    elif choice == '3':
        view_achievements()
    elif choice == '4':
        display_weather_info()
    elif choice == '5':
        help_menu()
    elif choice == '6':
        exit_application()
    else:
        print(Fore.RED + "Invalid selection. Please try again.")
        welcome_page()


# View list of achievements
def view_achievements():
    clear_screen()
    print_header("Achievements")
    if achievements:
        for achievement in achievements:
            print(text_color + f"| {achievement:<42} |")
    else:
        print(text_color + "| No achievements yet. Roll the dice to      |")
        print(text_color + "| unlock achievements!                       |")
    print_border()
    print_option(1, "Back to Welcome Page")
    print_border()
    print(text_color + "Please select an option: ", end="")
    choice = input(Fore.MAGENTA)
    if choice == '1':
        welcome_page()
    else:
        print(Fore.RED + "Invalid selection. Please try again.")
        view_achievements()


# Help menu with instructions
def help_menu():
    clear_screen()
    print_header("Help Menu")

    print(text_color + "| " + magenta_text("1. Start Rolling Dice:") + text_color + " Begin rolling dice. |")
    print(text_color + "| " + magenta_text("2. Set Re-rolls:") + text_color + " Set the number of re-rolls|")
    print(text_color + "| " + magenta_text("3. Roll Dice:") + text_color + " Roll up to 6 dice at once.   |")
    print(text_color + "| " + magenta_text("4. Re-roll:") + text_color + " Re-roll specific dice          |")
    print(text_color + "| " + magenta_text("5. Play Dice Duel:") + text_color + " Play the Dice Duel game.|")
    print(text_color + "| " + magenta_text("6. Main Menu:") + text_color + " Return to the main menu.     |")
    print(text_color + "| " + magenta_text("7. Exit:") + text_color + " Close the application.            |")
    print(text_color + "|                                            |")
    print(Fore.YELLOW + "| Press" + Fore.CYAN + " Enter " + Fore.YELLOW + "to return to the Welcome Page. |")

    print_border()
    input()
    welcome_page()


# Set the number of re-rolls
def set_rerolls():
    clear_screen()
    print_header("Set Re-rolls")
    print(text_color + "| Enter the number of re-rolls allowed (0-4) |")
    print_border()

    try:
        print(text_color + "Number of re-rolls: ", end="")
        num_rerolls = int(input(Fore.MAGENTA))

        if 0 <= num_rerolls <= 4:
            main_menu(num_rerolls)
        else:
            print(Fore.RED + "Invalid number of re-rolls. Please try again.")
            set_rerolls()

    except ValueError:
        print(Fore.RED + "Invalid input. Please enter a number between 0 and 4.")
        set_rerolls()


# Main menu after setting re-rolls
def main_menu(num_rerolls):
    clear_screen()
    print_header("Main Menu")
    print_option(1, "Roll Dice - Roll up to 6 dice at once")
    print_option(2, "View Session Summary")
    print_option(3, "Settings")
    print_option(4, "Check Today's Weather")
    print_option(5, "Back to Welcome Page")
    print_option(6, "Exit - Close the application")
    print_border()
    print(text_color + "Please select an option: ", end="")
    choice = input(Fore.MAGENTA)
    if choice == '1':
        roll_dice(num_rerolls)
    elif choice == '2':
        view_session_summary(num_rerolls)
    elif choice == '3':
        settings_menu(num_rerolls)
    elif choice == '4':
        display_weather_info()
    elif choice == '5':
        welcome_page()
    elif choice == '6':
        exit_application()
    else:
        print(Fore.RED + "Invalid selection. Please try again.")
        main_menu(num_rerolls)


# Settings menu for theme and sound
def settings_menu(num_rerolls):
    clear_screen()
    print_header("Settings")
    print(text_color + "| 1. Change Theme                            |")
    print(text_color + "| 2. Change Dice Sound                       |")
    print_option(3, "Back to Main Menu")
    print_border()
    print(text_color + "Please select an option: ", end="")
    choice = input(Fore.MAGENTA)
    if choice == '1':
        change_theme(num_rerolls)
    elif choice == '2':
        change_dice_sound(num_rerolls)
    elif choice == '3':
        main_menu(num_rerolls)
    else:
        print(Fore.RED + "Invalid selection. Please try again.")
        settings_menu(num_rerolls)


# Change the visual theme
def change_theme(num_rerolls):
    clear_screen()
    print_header("Change Theme")
    print(text_color + "| 1. Classic                                 |")
    print(text_color + "| 2. Dark Mode                               |")
    print(text_color + "| 3. Retro                                   |")
    print_option(4, "Back to Settings")
    print_border()
    print(text_color + "Please select an option: ", end="")
    choice = input(Fore.MAGENTA)
    if choice == '1':
        set_theme('classic')
    elif choice == '2':
        set_theme('dark')
    elif choice == '3':
        set_theme('retro')
    elif choice == '4':
        settings_menu(num_rerolls)
    else:
        print(Fore.RED + "Invalid selection. Please try again.")
        change_theme(num_rerolls)
    settings_menu(num_rerolls)


# Change the dice roll sound
def change_dice_sound(num_rerolls):
    clear_screen()
    print_header("Change Dice Sound")
    print(text_color + "| 1. Default Sound                           |")
    print(text_color + "| 2. Dice Roll Sound 1                       |")
    print(text_color + "| 3. Dice Roll Sound 2                       |")
    print_option(4, "Back to Settings")
    print_border()
    print(text_color + "Please select an option: ", end="")
    choice = input(Fore.MAGENTA)
    if choice == '1':
        set_dice_sound('default')
    elif choice == '2':
        set_dice_sound('sound1')
    elif choice == '3':
        set_dice_sound('sound2')
    elif choice == '4':
        settings_menu(num_rerolls)
    else:
        print(Fore.RED + "Invalid selection. Please try again.")
        change_dice_sound(num_rerolls)
    settings_menu(num_rerolls)


# Set the theme and apply it
def set_theme(theme):
    global current_theme
    current_theme = theme
    apply_theme()
    print(text_color + f"Theme changed to {theme}!")
    time.sleep(1)


# Set the dice roll sound
def set_dice_sound(sound):
    global current_dice_sound
    current_dice_sound = sound
    print(text_color + f"Dice sound changed to {sound}!")
    time.sleep(1)


# View the summary of the current session
def view_session_summary(num_rerolls):
    clear_screen()
    print_header("Session Summary")
    print(text_color + "| Here are your rolls so far:                |")
    print(text_color + "|                                            |")
    if session_summary:
        max_len = 34
        for i, summary in enumerate(session_summary):
            roll_text = ', '.join(map(str, summary))
            padded_roll_text = roll_text.ljust(max_len)
            print(text_color + f"| Roll {i + 1}: {padded_roll_text} |")
    else:
        print(Fore.RED + "| No rolls yet.                              |")
    print(text_color + "|                                            |")
    print_option(1, "Back to Main Menu")
    print_border()
    print(text_color + "Please select an option: ", end="")
    choice = input(Fore.MAGENTA)
    if choice == '1':
        main_menu(num_rerolls)
    else:
        print(Fore.RED + "Invalid selection. Please try again.")
        view_session_summary(num_rerolls)


# Roll a specified number of dice
def roll_dice(num_rerolls):
    clear_screen()
    print_header("Roll Dice")
    print(text_color + "| Enter the number of dice to roll (1-6)     |")
    print_border()

    try:
        print(text_color + "Number of dice: ", end="")
        num_dice = int(input(Fore.MAGENTA))

        if 1 <= num_dice <= 6:
            roll_dice_transition(num_dice, num_rerolls, initial_roll=True)
        else:
            print(Fore.RED + "Invalid number of dice. Please try again.")
            roll_dice(num_rerolls)

    except ValueError:
        print(Fore.RED + "Invalid input. Please enter a number between 1 and 6.")
        roll_dice(num_rerolls)


# Transition for dice rolling animation and results
def roll_dice_transition(num_dice, num_rerolls, initial_roll=True, results=None):
    play_sound(current_dice_sound + '.mp3', loop=True)
    dot_cycle = itertools.cycle(['...', '......', '.........'])
    if initial_roll:
        print_header("Rolling Dice...")
        print(highlight_color + "| Your dice roll is being generated.         |")
    else:
        print_header("Re-Rolling Dice...")
        print(highlight_color + "| Your dice re-roll is being generated.      |")
    print(highlight_color + "|                                            |")
    print_border()

    for _ in range(10):  # Loop for rolling animation
        sys.stdout.write('\r' + next(dot_cycle))
        sys.stdout.flush()
        time.sleep(0.5)

    stop_sound()
    if results is None:
        results = [random.randint(1, 6) for _ in range(num_dice)]
    else:
        for i in range(len(results)):
            if results[i] == 0:
                results[i] = random.randint(1, 6)
    session_summary.append(results)
    check_achievements(results)
    dice_result(results, num_rerolls)


# Display the dice roll results and options for re-roll
def dice_result(results, num_rerolls):
    clear_screen()
    print_header("Dice Result")
    for i, result in enumerate(results):
        print(highlight_color + f"| Die {i+1}: {result:<35} |")
    print(highlight_color + "|                                            |")
    if num_rerolls > 0:
        print_option(1, "Re-roll All Dice")
        print_option(2, "Re-roll Specific Dice")
        print_option(3, "Main Menu")
        print_option(4, "Exit")
        print_border()
        print(text_color + "Please select an option: ", end="")
        choice = input(Fore.MAGENTA)
        if choice == '1':
            num_rerolls -= 1
            roll_dice_transition(len(results), num_rerolls, initial_roll=False)
        elif choice == '2':
            reroll_specific_dice(results, num_rerolls)
        elif choice == '3':
            main_menu(num_rerolls)
        elif choice == '4':
            exit_application()
        else:
            print(Fore.RED + "Invalid selection. Please try again.")
            dice_result(results, num_rerolls)
    else:
        print(Fore.RED + "  No more re-rolls left.")
        print_option(1, "Main Menu")
        print_option(2, "Exit")
        print_border()
        print(text_color + "Please select an option: ", end="")
        choice = input(Fore.MAGENTA)
        if choice == '1':
            main_menu(num_rerolls)
        elif choice == '2':
            exit_application()
        else:
            print(Fore.RED + "Invalid selection. Please try again.")
            dice_result(results, num_rerolls)


# Re-roll specific dice chosen by the user
def reroll_specific_dice(results, num_rerolls):
    clear_screen()
    print_header("Re-roll Specific Dice")
    print(text_color + "Enter the die numbers to re-roll (e.g., 1,3,5)")
    print_border()
    print(text_color + "Die numbers: ", end="")
    reroll_indices = input(Fore.MAGENTA)

    try:
        reroll_indices = [int(x)-1 for x in reroll_indices.split(',')
                          if 0 <= int(x)-1 < len(results)]
        new_results = [results[i] if i not in reroll_indices else 0
                       for i in range(len(results))]
        num_rerolls -= 1
        roll_dice_transition(len(results), num_rerolls, initial_roll=False,
                             results=new_results)

    except ValueError:
        print(Fore.RED + "Invalid input. Enter valid die numbers separated by commas.")
        reroll_specific_dice(results, num_rerolls)


# Check for achievements based on dice results
def check_achievements(results):
    if results.count(6) == len(results):
        if "All Sixes" not in achievements:
            achievements.append("All Sixes")
            print(text_color + "Achievement Unlocked: All Sixes!")
    if results.count(1) == len(results):
        if "Snake Eyes" not in achievements:
            achievements.append("Snake Eyes")
            print(text_color + "Achievement Unlocked: Snake Eyes!")
    if len(set(results)) == len(results):
        if "No Duplicates" not in achievements:
            achievements.append("No Duplicates")
            print(text_color + "Achievement Unlocked: No Duplicates!")
    if sum(results) == 20:
        if "Exact Twenty" not in achievements:
            achievements.append("Exact Twenty")
            print(text_color + "Achievement Unlocked: Exact Twenty!")


# Play the dice duel game
def play_dice_duel():
    clear_screen()
    print_header("Dice Duel Game")
    print(text_color + "| Enter number of players (1-2)              |")
    print_border()

    try:
        print(text_color + "Number of players: ", end="")
        num_players = int(input(Fore.MAGENTA))

        if 1 <= num_players <= 2:
            player_names = []
            for i in range(num_players):
                name = input(text_color + f"Enter name for Player {i+1}: ")
                player_names.append(name)
            dice_duel_game(num_players, player_names)
        else:
            print(Fore.RED + "Invalid number of players. Please try again.")
            play_dice_duel()

    except ValueError:
        print(Fore.RED + "Invalid input. Please enter 1 or 2.")
        play_dice_duel()


# Main game logic for dice duel
def dice_duel_game(num_players, player_names):
    slam_number = random.randint(1, 6)
    smap_number = slam_number ** 2
    player_scores = {name: 0 for name in player_names}
    skips = {name: 3 for name in player_names}
    clear_screen()
    print_header(f"Slam Number: {slam_number} | Smap Number: {smap_number}")
    while all(score >= 0 and score < 20 for score in player_scores.values()):
        for name in player_names:
            clear_screen()
            print_header(f"{name}'s Turn")
            print(text_color + f"| Slam Number: {slam_number}                             |")
            print(text_color + f"| Smap Number: {smap_number}                             |")
            print(text_color + f"| Skips Remaining: {skips[name]}                         |")
            print(text_color + "|                                            |")
            for pname, score in player_scores.items():
                print(
                    Fore.MAGENTA + f"  Player's Name: {pname} Score: {score}")
            print_border()
            turn_points = 0
            rolls_this_turn = 0
            while True:
                rolls_this_turn += 1
                print(text_color + "  1. Roll Again \n  2. Skip Turn \n  3. Gamble Points")
                print(text_color + "  4. Buy Re-roll (3 pts) \n  5. Exit Game")
                print(text_color + "  6. Back to Welcome Page")
                choice = input(Fore.MAGENTA + "Your choice: ").strip()
                if choice == '1':
                    roll = [random.randint(1, 6) for _ in range(3)]
                    play_sound(current_dice_sound + '.mp3', loop=False)
                    print(highlight_color + f"- Roll: {roll}")
                    if slam_number in roll:
                        slams = roll.count(slam_number)
                        turn_points += slams * rolls_this_turn
                        print(Fore.MAGENTA + f"- {name} scored {slams * rolls_this_turn} "
                              f"points this roll!")
                        if turn_points >= 20:
                            turn_points = 0
                            print(Fore.MAGENTA + f"- {name} busted by going over 20!")
                            break
                    elif sum(roll) >= smap_number:
                        turn_points -= 5
                        print(Fore.MAGENTA + f"- {name} hit a smap! Lost 5 points.")
                        if turn_points < 0:
                            print(Fore.MAGENTA + f"- {name} is out of the game!")
                            player_scores[name] = -1
                            break
                    else:
                        print(Fore.MAGENTA + f"- {name} rolled no slams. Turn ends.")
                        break
                elif choice == '2':
                    if skips[name] > 0:
                        skips[name] -= 1
                        print(Fore.MAGENTA + f"- {name} skips the turn.")
                        break
                    else:
                        print(Fore.MAGENTA + "- No skips remaining.")
                elif choice == '3':
                    if random.choice([True, False]):
                        turn_points *= 2
                        print(Fore.MAGENTA + "- Gamble successful! Points doubled!")
                    else:
                        turn_points = 0
                        print(Fore.MAGENTA + "- Gamble failed! Lost all turn points!")
                    break
                elif choice == '4':
                    if player_scores[name] >= 3:
                        player_scores[name] -= 3
                        rolls_this_turn -= 1
                        print(Fore.MAGENTA + "- Re-roll purchased. Points deducted.")
                    else:
                        print(Fore.MAGENTA + "- Not enough points to buy re-roll.")
                elif choice == '5':
                    exit_application()
                elif choice == '6':
                    welcome_page()
                else:
                    print(Fore.RED + "Invalid selection. Please try again.")
            player_scores[name] += turn_points
            print(text_color + f"- {name}'s Total Score: {player_scores[name]}")
            print_border()
            if player_scores[name] >= 20:
                player_scores[name] = 20
                print(text_color + f"- {name} has reached 20 points and wins!")
                break
            if player_scores[name] < 0:
                print(text_color + f"- {name} has negative points and is out!")
                break
        if any(score >= 20 for score in player_scores.values()):
            break
    winner = max(player_scores, key=player_scores.get)
    clear_screen()
    print_header(f"{winner} wins the game!")
    print(text_color + "| Final Scores:                              |")
    for pname, score in player_scores.items():
        print(text_color + f"| {pname}: {score}                                    |")
    print_border()
    save_scores(player_scores)
    print_option(1, "Back to Welcome Page")
    print_border()
    print(text_color + "Please select an option: ", end="")
    choice = input(Fore.MAGENTA)
    if choice == '1':
        welcome_page()
    else:
        print(Fore.RED + "Invalid selection. Please try again.")
        welcome_page()


# Save the scores to a file
def save_scores(scores):
    with open("dice_duel_scores.txt", "a") as f:
        for name, score in scores.items():
            f.write(f"{name}: {score}\n")


# Exit the application with a confirmation prompt
def exit_application():
    clear_screen()
    print_header("Exit Application")
    print(Fore.RED + "| Are you sure you want to exit?             |")
    print(Fore.RED + "|                                            |")
    print_option(1, "Yes")
    print_option(2, "No (Return to Main Menu)")
    print_border()
    print(text_color + "Please select an option: ", end="")
    choice = input(Fore.MAGENTA)
    if choice == '1':
        print(Fore.RED + "Exiting the application... Goodbye!")
        sys.exit()
    elif choice == '2':
        main_menu(0)  # Reset the number of re-rolls when returning to the main menu
    else:
        print(Fore.RED + "Invalid selection. Please try again.")
        exit_application()


# Store the session summary
session_summary = []

# Start the application with the welcome page
if __name__ == "__main__":
    welcome_page()
