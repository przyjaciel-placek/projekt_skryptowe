from abc import ABC, abstractmethod
import sqlite3
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
import random
from datetime import date
import os


"""
    Gra 'Zgadnij co to'
    Autor: Michał Górniak

    Gra polega na wskazywaniu poprawnej odpowiedzi spośród kilku innych odnośnie tego. Program wyświetla losowy obrazek kota, psa lub pokemona, 
    zadaniem gracza jest wskazanie poprawnej odpowiedzi z nazwą rasy psa/kota lub imienia pokemona.
    Po udzieleniu każdej poprawnej odpowiedzi gracz otrzymuje 1 punkt oraz zostaje mu przypisany do konta obrazek, dla którego udzielono poprawnej odpowiedzi.
    Gracz może oglądać swoje obrazki przypisane do konta w 'galerii' Moje obrazki.
    Gra kończy się przy udzieleniu niepoprawnej odpowiedzi. 

    Program wykorzystuje bazę danych, w której przechowuje informacje odnośnie użytkowników, ich zdobytych obrazków, tabelę najwyższych wyników.
    Do rozpoczęcia gry wymagane jest zalogowanie. W celu założenia konta wymagana jest rejestracja nowego użytkownika.

    Gra składa się z kilku okien:
     - okno logowania                   - logowanie i rejestracja
     - okno menu                        - wyświetlenie tablicy najwyższych wyników, ustawienia gry
     - okno 'galerii' obrazków gracza   - dostęp do obrazków przypisanych do konta gracza (na które udzielił wcześniej poprawnej odpowiedzi)
     - okno gry                         - wyświetlenie obrazka wraz z możliwymi odpowiedziami do udzielenia


    Program używa trzech API do pobierania danych:
     - https://dog.ceo/dog-api/
     - https://thecatapi.com/
     - https://pokeapi.co/

    Do przechowywania danych wykorzystana baza danych sqlite3 (plik 'game_database.db').

    Program używa motywu do tkinter (folder 'theme' i plik 'sun-valley.tcl') dostępnego tutaj:
    https://github.com/rdbende/Sun-Valley-ttk-theme

"""







class Creature(ABC):

    # metoda zwraca trzy inne nazwy niż poprawna odpowiedź
    @abstractmethod
    def _get_three_more_names(self):
        pass

    # ustawia wszystkie możliwe nazwy dla typu klasy, przydatna w losowaniu nazw (metoda wyżej)
    @abstractmethod
    def _set_names(self):
        pass

    # metoda ustawia tekst 'name' i obraz 'image_to_show' dla poprawnej odpowiedzi
    @abstractmethod
    def _set_image_and_name(self):
        pass

    

class Dog(Creature):
    
    are_names_set = False

    def __init__(self):
        if not Dog.are_names_set:
            Dog.names = Dog._set_names(self)
            Dog.are_names_set = True
        self._set_image_and_name()
        self.fake_names = self._get_three_more_names()

    
    def _get_three_more_names(self):
        max = len(Dog.names)

        names = []
        while(len(names) < 3):
            dog_name = Dog.names[random.randint(0, max-1)].title()
            if dog_name != self.name and dog_name not in names:                 
                names.append(dog_name)

        return names



    def _set_names(self):
        names = requests.get("https://dog.ceo/api/breeds/list/all")

        list_of_names = []
        if names.status_code == 200 and names.json()["status"] == "success":
            for name in names.json()["message"].keys():
                addition = names.json()["message"][name]
                if addition == []:
                    list_of_names.append(name)
                else:
                    for add in addition:
                        list_of_names.append(str(name) + " " + str(add))
            return list_of_names
        else:
            raise "NIE POBRANO LISTY PSOW, WYSTAPIL BLAD"

    def _set_image_and_name(self):
            # image and name
        answer = requests.get("https://dog.ceo/api/breeds/image/random")

        if answer.status_code == 200 and answer.json()["status"] == "success":
            self._image_url = answer.json()["message"]

            # set name
            self.name = str(self._image_url).split("/")[-2].replace('-', ' ').title()

            #read the image
            self.image_to_show = requests.get(self._image_url).content
        else:
            raise "Blad w pobraniu danych psa"



class Cat(Creature):

    are_names_set = False

    def __init__(self):

        if not Cat.are_names_set:
            Cat.names = Cat._set_names(self)
            Cat.are_names_set = True
        self._set_image_and_name()
        self.fake_names = self._get_three_more_names()
    #    print(Cat.names)


    # wybierz trzy imiona inne niz self.name, każdy człon zaczyna się z wielkiej litery
    def _get_three_more_names(self):
        max = len(Cat.names)

        names = []
        while(len(names) < 3):
            cat_name = Cat.names[random.randint(0, max-1)][0].title()
            if cat_name != self.name and cat_name not in names:                 
                names.append(cat_name)

        return names


    def _set_names(self):
        names = requests.get("https://api.thecatapi.com/v1/breeds")

        list_of_names = []
        if names.status_code == 200:
            for cat_type in names.json():
                list_of_names.append((cat_type["name"], cat_type["id"]))
              
            return list_of_names
        else:
            raise "NIE POBRANO LISTY PSOW, WYSTAPIL BLAD"


    def _set_image_and_name(self):
            # image and name

        which_cat = random.randint(0, len(Cat.names))
 #       print(Cat.names[which_cat])
        self.name = Cat.names[which_cat][0].title()
        cat_id = Cat.names[which_cat][1]

        answer = requests.get("https://api.thecatapi.com/v1/images/search?breed_id={}".format(cat_id))
       # print(cat_id)
        if answer.status_code == 200:
            self._image_url = answer.json()[0]["url"]

        #read the image
            self.image_to_show = requests.get(self._image_url).content
        else:
            raise "Blad w pobieraniu danych kota."



class Pokemon(Creature):
    def __init__(self):
        self._set_image_and_name()
        self.fake_names = self._get_three_more_names()


    
    def _get_three_more_names(self):
        names = []
        while(len(names) < 3):
            pokemon_id = random.randint(1, 650)
            pokemon_data = requests.get("https://pokeapi.co/api/v2/pokemon/{}".format(pokemon_id))
            pokemon_name = pokemon_data.json()["name"].capitalize()
            if pokemon_name != self.name and pokemon_name not in names:
                names.append(pokemon_name)

        return names



    def _set_names(self):
        # pokemony losuje sie z api numerami 1-650, nie ma potrzeby tworzenia listy ich nazw/imion - mozna latwo je wylosowac z api, a tworzenie listy trwaloby bardzo dlugo
        pass


    def _set_image_and_name(self):
        # image and name
        pokemon_id = random.randint(1, 650)         # pokemony w api maja numery od 1 do 649
        
        pokemon_data = requests.get("https://pokeapi.co/api/v2/pokemon/{}".format(pokemon_id))
        self.name = pokemon_data.json()["name"].capitalize()
        self.pokemon_id = pokemon_data.json()["id"]

        self._image_url = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{}.png".format(pokemon_id)
        self.image_to_show = requests.get(self._image_url).content




# _________________________________________________________________________________________________________________________________________________________________________________
# _______________________________________________________________________________   \/ OKNA APLIKACJI \/   ________________________________________________________________________
# _________________________________________________________________________________________________________________________________________________________________________________


class App(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.title("Zgadnij co to")
        self.switch_frame(LoggingScreen)


    def switch_frame(self, frame_class):
        # niszczy aktualną ramkę i zastępuje ją nową
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()

        self._frame = new_frame
        
        self._frame.pack(fill="both", expand=True)
        self.update()
        
        self.resizable(False, False)
        x_cordinate = int((self.winfo_screenwidth() / 2) - (self.winfo_width() / 2))
        y_cordinate = int((self.winfo_screenheight() / 2) - (self.winfo_height() / 2))
        self.geometry("+{}+{}".format(x_cordinate, y_cordinate))
        
        

class LoggingScreen(tk.Frame):

    user_login = ""

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)

        self.im = Image.open("logo.jpg")


        self.img = ImageTk.PhotoImage(self.im)
        self.label_image = tk.Label(self, image=self.img)
        self.label_image.grid(column=0, padx=(20, 10), columnspan=5, row=0)


# _____________________________________________________ logowanie

        # ramka dla logowania
        self.logging_frame = ttk.LabelFrame(self, text="Logowanie", padding=(30, 10))
        self.logging_frame.grid(
            row=1, column=0, padx=(20, 10), pady=(20, 10), sticky="nsew"
        )


        # login Label + Entry
        self.label_logging_login = ttk.Label(self.logging_frame, text="Login:")
        self.label_logging_login.grid(row=0, column=0, padx=5, pady=3, sticky="sw")
        self.entry_logging_login = ttk.Entry(self.logging_frame)
        self.entry_logging_login.grid(row=1, column=0, padx=5, pady=0, sticky="nw")

        # przerwa
        self.label_logging_password = ttk.Label(self.logging_frame, text="")
        self.label_logging_password.grid(row=2, column=0, padx=5, pady=0, sticky="sw")

        # hasło Label + Entry
        self.label_logging_password = ttk.Label(self.logging_frame, text="Hasło:")
        self.label_logging_password.grid(row=3, column=0, padx=5, pady=3, sticky="sw")
        self.entry_logging_password = ttk.Entry(self.logging_frame, show="•")
        self.entry_logging_password.grid(row=4, column=0, padx=5, pady=0, sticky="nsew")

        # przerwa
        self.label_logging_password = ttk.Label(self.logging_frame, text="")
        self.label_logging_password.grid(row=5, column=0, padx=5, pady=0, sticky="sw")

        # Accentbutton logowanie
        self.accentbutton = ttk.Button(
            self.logging_frame, text="Zaloguj", style="Accent.TButton", command=lambda: self.check_logging_login_and_password(
                                                                                                                        parent,
                                                                                                                        self.entry_logging_login.get(),
                                                                                                                        self.entry_logging_password.get()
                                                                                                                     )
        )
        self.accentbutton.grid(row=6, column=0, padx=5, pady=10, sticky="nsew")

# _________________________________________________________________________________________________________


        # Separator
        self.separator = ttk.Separator(self, orient='vertical')
        self.separator.grid(row=1, column=1, padx=(25, 15), pady=(30, 10), sticky="nsew")



        # Label tekst o rejestracji
        self.label_logging_password = ttk.Label(self, text="Nie masz konta?\nZarejestruj się tutaj →")
        self.label_logging_password.grid(row=1, column=2, padx=5, pady=3, sticky="w")


# ______________________________________________ rejestracja

        # ramka dla rejstracji
        self.registration_frame = ttk.LabelFrame(self, text="Rejestracja", padding=(30, 10))
        self.registration_frame.grid(
            row=1, column=3, padx=(20, 10), pady=(20, 10), sticky="nsew"
        )

        # login Label + Entry
        self.label_registration_login = ttk.Label(self.registration_frame, text="Login:")
        self.label_registration_login.grid(row=0, column=0, padx=5, pady=3, sticky="sw")
        self.entry_registration_login = ttk.Entry(self.registration_frame)
        self.entry_registration_login.grid(row=1, column=0, padx=5, pady=0, sticky="nw")

        # przerwa
        self.label_registration_password = ttk.Label(self.registration_frame, text="")
        self.label_registration_password.grid(row=2, column=0, padx=5, pady=0, sticky="sw")

        # hasło Label + Entry
        self.label_registration_password = ttk.Label(self.registration_frame, text="Hasło:")
        self.label_registration_password.grid(row=3, column=0, padx=5, pady=3, sticky="sw")
        self.entry_registration_password = ttk.Entry(self.registration_frame, show="•")
        self.entry_registration_password.grid(row=4, column=0, padx=5, pady=0, sticky="nsew")

        # przerwa
        self.label_registration_password = ttk.Label(self.registration_frame, text="")
        self.label_registration_password.grid(row=5, column=0, padx=5, pady=0, sticky="sw")

        # Button rejestracja
        self.button = ttk.Button(self.registration_frame, text="Zarejestruj", command=lambda: self.check_registration_login_and_password(
                                                                                                                        self.entry_registration_login.get(),
                                                                                                                        self.entry_registration_password.get()
                                                                                                                     ))
        self.button.grid(row=6, column=0, padx=5, pady=10, sticky="nsew")      

        self.label_info_text = ttk.Label(self, foreground = 'red', text="  ")
        self.label_info_text.grid(row=5, column=1, columnspan=4, padx=20, pady=0, sticky="sw")





    def check_logging_login_and_password(self, parent, login, password):
        try:
            self.label_info_text = ttk.Label(self, foreground = 'red', text="                                                                                                ")
            self.label_info_text.grid(row=5, column=1, columnspan=5, padx=20, pady=0, sticky="sw")

            info_text = ''
            if len(login) < 5:
                info_text = 'Login musi mieć co najmniej 5 znaków'
            elif  len(password) < 5:
                info_text = 'Hasło musi mieć co najmniej 5 znaków'

            else:
                if db.login(login, password):
                    LoggingScreen.user_login = login
                    parent.switch_frame(MenuScreen)
                else:
                    info_text = 'Niepoprawne dane logowania'


            self.label_info_text = ttk.Label(self, foreground = 'red', text=info_text)
            self.label_info_text.grid(row=5, column=1, columnspan=5, padx=20, pady=0, sticky="sw")
        except:
            pass

        
    def check_registration_login_and_password(self, login, password):

        self.label_info_text = ttk.Label(self, foreground = 'red', text="                                                                                                ")
        self.label_info_text.grid(row=5, column=1, columnspan=4, padx=20, pady=0, sticky="sw")

        info_text = 'Zarejestrowano użytkownika \'' + login + '\''
        if len(login) < 5:
            info_text = 'Login musi mieć co najmniej 5 znaków'
        elif  len(password) < 5:
            info_text = 'Hasło musi mieć co najmniej 5 znaków'

        elif not db.register(login, password):         # co jak już jest taki w bazie  
            info_text = 'Istnieje już użytkownik o loginie \'' + login + '\''


        self.label_info_text = ttk.Label(self, foreground = 'red', text=info_text)
        self.label_info_text.grid(row=5, column=1, columnspan=4, padx=20, pady=0, sticky="sw")



class MenuScreen(tk.Frame):

    game_type = []

    # przyciski do zapamiętywania wyboru trybu gry użytkownika w sesji
    dogs_button_is_on = True
    cats_button_is_on = True
    pokemons_button_is_on = True


    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)


        # Make the app responsive
        for index in [0, 1, 2]:
            self.columnconfigure(index=index, weight=1)
            self.rowconfigure(index=index, weight=1)

        # Create value lists
        self.option_menu_list = ["", "OptionMenu", "Option 1", "Option 2"]
        self.combo_list = ["Combobox", "Editable item 1", "Editable item 2"]
        self.readonly_combo_list = ["Readonly combobox", "Item 1", "Item 2"]

        # Create control variables
        self.var_0 = tk.BooleanVar()
        self.var_1 = tk.BooleanVar(value=True)
        self.var_2 = tk.BooleanVar()
        self.var_3 = tk.IntVar(value=2)
        self.var_4 = tk.StringVar(value=self.option_menu_list[1])
        self.var_5 = tk.DoubleVar(value=75.0)


# _________________________________________________________________ ramka ustawienia gry

        # ramka na ustawienia gry
        self.settings_frame = ttk.LabelFrame(self, text="Ustawienia gry", padding=(20, 10))
        self.settings_frame.grid(
            row=0, column=0, padx=(20, 10), pady=(20, 10), sticky="nsew"
        )

        # Switch psy
        self.switch_dogs = ttk.Checkbutton(self.settings_frame, text="Psy", style="Switch.TCheckbutton")
        if MenuScreen.dogs_button_is_on:
            self.switch_dogs.state(['selected'])
        self.switch_dogs.grid(row=0, column=0, padx=5, pady=10, sticky="nsew")

        # Switch koty
        self.switch_cats = ttk.Checkbutton(self.settings_frame, text="Koty", style="Switch.TCheckbutton")
        if MenuScreen.cats_button_is_on:
            self.switch_cats.state(['selected'])
        self.switch_cats.grid(row=1, column=0, padx=5, pady=10, sticky="nsew")

        # Switch pokemony
        self.switch_pokemons = ttk.Checkbutton(self.settings_frame, text="Pokemony", style="Switch.TCheckbutton")
        if MenuScreen.pokemons_button_is_on:
            self.switch_pokemons.state(['selected'])
        self.switch_pokemons.grid(row=2, column=0, padx=5, pady=10, sticky="nsew")


        # dodanie większej czcionki do istniejącego stylu
        s = ttk.Style()
        s.configure("Accent.TButton", font=('', 30))


        self.buttonx = ttk.Button(self, text="GRAJ", style="Accent.TButton", command=lambda: self.start_game(parent))
        self.buttonx.grid(row=1, column=0, padx=(20, 10), pady=10, ipady=10, sticky="nsew")
        

        # Separator
        self.separator = ttk.Separator(self)
        self.separator.grid(row=2, column=0, padx=(20, 10), pady=10, sticky="ew")


# _________________________________________________________________ ramka moje konto

        # tworzenie ramki, potem przyciskow
        self.account_frame = ttk.LabelFrame(self, text="Moje konto", padding=(20, 10))
        self.account_frame.grid(row=3, column=0, padx=(20, 10), pady=10, sticky="nsew")

        self.buttonx = ttk.Button(self.account_frame, text="Moje obrazki", command=lambda: parent.switch_frame(UserImagesScreen))
        self.buttonx.grid(row=0, column=0, padx=5, pady=10, sticky="nsew")

        self.buttonx = ttk.Button(self.account_frame, text="Wyloguj", command=lambda: self.logout(parent))
        self.buttonx.grid(row=1, column=0, padx=5, pady=10, sticky="nsew")

    

        self.score_table_title = tk.Label(self, text=" Najwyższe wyniki:", font=("", 20, "bold")).grid(column=2, row=0, sticky='n', pady=(20, 0))

        # Panedwindow
        self.paned = ttk.PanedWindow(self)
        self.paned.grid(row=0, column=2, pady=(53, 5), sticky="nesw", rowspan=5)

        # Pane #1
        self.pane_1 = ttk.Frame(self.paned, padding=5)
        self.paned.add(self.pane_1, weight=1)

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.pane_1)
        self.scrollbar.pack(side="right", fill="y")

        # Treeview
        self.treeview = ttk.Treeview(
            self.pane_1,
            selectmode="browse",
            yscrollcommand=self.scrollbar.set,
            columns=(1, 2),
            height=10,
        )
        self.treeview.pack(expand=True, fill="both")
        self.scrollbar.config(command=self.treeview.yview)

        # Treeview columns
        self.treeview['columns'] = ('Użytkownik', "Punkty", "Typ gry")
        self.treeview.column("#0", anchor="w", width=60, minwidth=60)
        self.treeview.column("Użytkownik", anchor="w", width=170, minwidth=150)
        self.treeview.column("Punkty", anchor="w", width=60, minwidth=60)
        self.treeview.column("Typ gry", anchor="w", width=170, minwidth=150)



        self.treeview.heading("#0",  text="Miejsce")
        self.treeview.heading("Użytkownik", text="Użytkownik")
        self.treeview.heading("Punkty",  text="Punkty")
        self.treeview.heading("Typ gry", text="Typ gry")


        # wartości dla tablicy najlepszych wyników
        highscores_values = db.get_highscores()
      #  print('lista = ', highscores_values)

        place = 1
        counter = 1
        previous_points = 0
        for item in highscores_values:
            # pierwsza iteracja
            if counter == 1:
                previous_points = item[1]
            
            # jeżeli poprzednik nie ma tyle samo punktów (nie stoi na tym samym miejscu)
            if previous_points > item[1]:
                previous_points = item[1]
                place = counter

            template = ("", counter, place, (item[0], item[1], str(item[2])))

            self.treeview.insert(
                parent=template[0], index="end", iid=template[1], text=template[2], values=template[3]
            )
            counter += 1


        # Sizegrip
        self.sizegrip = ttk.Sizegrip(self)
        self.sizegrip.grid(row=100, column=100, padx=(0, 5), pady=(0, 5))



    def logout(self, parent):
        s = ttk.Style()
        s.configure("Accent.TButton", font=('', 10))
        parent.switch_frame(LoggingScreen)


    def start_game(self, parent):
        # przed każdą grą wyzeruj (tablica używana w klasie uruchomionej gry, dlatego jest jako zmienna klasy MenuScreen a nie obiektu)
        MenuScreen.game_type = []
        if self.switch_cats.instate(['selected']):
            MenuScreen.game_type.append('Koty')
            MenuScreen.cats_button_is_on = True
        else:
            MenuScreen.cats_button_is_on = False

        if self.switch_dogs.instate(['selected']):
            MenuScreen.game_type.append('Psy')
            MenuScreen.dogs_button_is_on = True
        else:
            MenuScreen.dogs_button_is_on = False

        if self.switch_pokemons.instate(['selected']):
            MenuScreen.game_type.append('Pokemony')
            MenuScreen.pokemons_button_is_on = True
        else:
            MenuScreen.pokemons_button_is_on = False

        # jeżeli cokolwiek wybrane to odpalaj grę
        if MenuScreen.game_type:
            parent.switch_frame(GameScreen)
        else:
            # wywal info jak niezaznaczona zadna mozliwa gra?? czy właściwie wystarczająco czytelne z tymi switchami
            pass



class UserImagesScreen(tk.Frame):

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)

        # styl przycisku
        s = ttk.Style()
        s.configure("Accent.TButton", font=('', 10))

        
        self.button_back_to_menu = ttk.Button(self, text="Kliknij tutaj aby wrócić do MENU", command=lambda: parent.switch_frame(MenuScreen))
        self.button_back_to_menu.grid(row=1, column=2, padx=5, pady=10, sticky="nsew")



        # ______________________________________________________ tworzenie listy obrazków użytownika

        self.score_table_title = tk.Label(self, text=" Moje obrazki:", font=("", 20, "bold")).grid(column=2, row=2, sticky='n', pady=(20, 0))

        # Panedwindow
        self.paned = ttk.PanedWindow(self)
        self.paned.grid(row=2, column=2, pady=(53, 5), sticky="nesw", rowspan=5)

        # Pane #1
        self.pane_1 = ttk.Frame(self.paned, padding=5)
        self.paned.add(self.pane_1, weight=1)

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.pane_1)
        self.scrollbar.pack(side="right", fill="y")

        # Treeview
        self.treeview = ttk.Treeview(
            self.pane_1,
            selectmode="browse",
            yscrollcommand=self.scrollbar.set,
            columns=(1, 2),
            height=10,
        )
        self.treeview.pack(expand=True, fill="both")
        self.scrollbar.config(command=self.treeview.yview)

        # Treeview columns
        self.treeview['columns'] = ("Nazwa", "Typ", "Data zdobycia")
        self.treeview.column("#0", anchor="w", width=60, minwidth=60)
        self.treeview.column("Nazwa", anchor="w", width=170, minwidth=170)
        self.treeview.column("Typ", anchor="w", width=120, minwidth=120)
        self.treeview.column("Data zdobycia", anchor="w", width=90, minwidth=90)

        self.treeview.heading("#0",  text="L.p.")
        self.treeview.heading("Nazwa", text="Nazwa")
        self.treeview.heading("Typ", text="Typ")
        self.treeview.heading("Data zdobycia",  text="Data zdobycia")

            # template = ("", counter, place, (item[0], item[1], str(item[2])))

            # self.treeview.insert(
            #     parent=template[0], index="end", iid=template[1], text=template[2], values=template[3]
            # )

        # wartości dla tablicy najlepszych wyników
        self.user_images = db.get_users_images(LoggingScreen.user_login)
    #    print('FOTKI = ', self.user_images)

        counter = 1
        for item in self.user_images:
            template = ("", counter, counter, (item[2], item[3], item[4]))

            self.treeview.insert(
                parent=template[0], index="end", iid=template[1], text=template[2], values=template[3]
            )
            counter += 1

        # ______________________________________________________________________________________________ 

                                                                                                                                # przekazywana aktualna pozycja == L.p. w tabeli
        self.button_show_image = ttk.Button(self, text="Wyświetl zaznaczony obrazek", style="Accent.TButton", command=lambda: self.show_image(parent, self.treeview.selection()))
        self.button_show_image.grid(row=0, column=2, padx=5, pady=10, sticky="nsew")






    def show_image(self, parent, index):
        # gdyby nie było internetu
        try:
            # jeżeli coś zaznaczone na liście
            if index:
                # pobieranie z listy adresu url dla odpowiedniego obrazka
            #    print(self.user_images[int(index[0]) - 1][1])
                image_url = self.user_images[int(index[0]) - 1][1]
                self.image_to_show = requests.get(image_url).content

                self.im = Image.open(BytesIO(self.image_to_show))
                # # ustaw wysokosc obrazka zaleznie od wielkosci okna, oblicz szerokosc obrazka tak, aby zachowac oryginalne proporcje
                screen_hight = self.winfo_screenheight()
                image_h = 600
                if screen_hight < 1000:
                    image_h = 400 #int(screen_hight * 0.6)

                image_width, image_height = self.im.size
                new_image_width, new_image_height = int((image_width*image_h)/image_height), image_h

                self.im = self.im.resize((new_image_width, new_image_height), resample=Image.Resampling.LANCZOS)
                self.img = ImageTk.PhotoImage(self.im)
                tk.Label(self,image=self.img).grid(column=0, row=0, rowspan=5)
        except:
            tkinter.messagebox.showinfo('Błąd',"Gra potrzebuje połączenia z internetem.")



class GameScreen(tk.Frame):

    points = 0

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)

        # wylosuj czy pytanie ma dotyczyc psa, kota czy pokemona
        random_creature_type = random.randint(0, len(MenuScreen.game_type) - 1)
        creature_to_show = ...
        question_addition = ...
        try:
            if MenuScreen.game_type[random_creature_type] == 'Psy':
                creature_to_show = Dog()
                question_addition = 'psa'
            elif MenuScreen.game_type[random_creature_type] == 'Koty':
                creature_to_show = Cat()
                question_addition = 'kota'
            elif MenuScreen.game_type[random_creature_type] == 'Pokemony':
                creature_to_show = Pokemon()
                question_addition = 'pokemona'



            self.image_to_show = creature_to_show.image_to_show
            self.im = Image.open(BytesIO(self.image_to_show))
            
        # print(self.winfo_screenheight())
            screen_hight = self.winfo_screenheight()
            image_h = 600
            if screen_hight < 1000:
                image_h = 400 #int(screen_hight * 0.6)

            # ustaw wysokosc obrazka zaleznie od wielkosci okna, oblicz szerokosc obrazka tak, aby zachowac oryginalne proporcje
            image_width, image_height = self.im.size
            new_image_width, new_image_height = int((image_width*image_h)/image_height), image_h
            self.im = self.im.resize((new_image_width, new_image_height), resample=Image.Resampling.LANCZOS)
            self.img = ImageTk.PhotoImage(self.im)

            # wyświetl obrazek
            tk.Label(self,image=self.img).grid(column=0, row=0)
        except:
            tkinter.messagebox.showinfo('Błąd',"Gra potrzebuje połączenia z internetem.")

        # 'gruby' separator
        sep1 = tk.Frame(self, height=2, width=600, bd=1, relief='sunken')
        sep1.grid(row=1, column=0, padx=5, pady=5)

        # stała wielkość przycisków
        x = max(600, new_image_width)
        button_size = int((x - 200)/2)

        tk.Label(self, text="Jakiego {} widzisz:".format(question_addition), font=("", 30, "bold")).grid(column=0, row=2)

    #   separator2 = ttk.Separator(self)
    #   separator2.grid(row=3, column=0, padx=button_size, pady=8, sticky="nsew")
                
        # nazwy pozostałych przycisków (3 niepoprawne odpowiedzi)
        fake_answers = creature_to_show.fake_names

        # umieszczenie nazwy poprawnej odpowiedzi na losowym miejscu (w losowym przycisku)
        right_answer_position = random.randint(0,3)
        fake_answers.insert(right_answer_position, creature_to_show.name)
        #   print(creature_to_show.name)

        # 4 przyciski z odpowiedziami
        togglebutton0 = ttk.Checkbutton(self, text=fake_answers[0], style="Toggle.TButton", command=lambda: check_answer(0))
        togglebutton0.grid(row=4, column=0, padx=button_size, pady=9, sticky="nsew")

        togglebutton1 = ttk.Checkbutton(self, text=fake_answers[1], style="Toggle.TButton", command=lambda: check_answer(1))
        togglebutton1.grid(row=5, column=0, padx=button_size, pady=9, sticky="nsew")

        togglebutton2 = ttk.Checkbutton(self, text=fake_answers[2], style="Toggle.TButton", command=lambda: check_answer(2))
        togglebutton2.grid(row=6, column=0, padx=button_size, pady=9, sticky="nsew")

        togglebutton3 = ttk.Checkbutton(self, text=fake_answers[3], style="Toggle.TButton", command=lambda: check_answer(3))
        togglebutton3.grid(row=7, column=0, padx=button_size, pady=9, sticky="nsew")

        sep3 = tk.Frame(self, height=2, width=600, bd=1, relief='sunken')
        sep3.grid(row=8, column=0, padx=5, pady=5)
        tk.Label(self, text="Twoje punkty: " + str(GameScreen.points), font=("", 20, "bold")).grid(column=0, row=9)


        def check_answer(button_number):
            togglebutton0.state(['disabled'])
            togglebutton1.state(['disabled'])
            togglebutton2.state(['disabled'])
            togglebutton3.state(['disabled'])

            if button_number == right_answer_position:
                GameScreen.points += 1

                creature_type = 'Pokemon'
                if isinstance(creature_to_show, Cat):
                    creature_type = 'Kot'
                elif isinstance(creature_to_show, Dog):
                    creature_type = "Pies"

                db.put_image(LoggingScreen.user_login, str(date.today()), creature_to_show.name, creature_to_show._image_url, creature_type)
                parent.switch_frame(GameScreen)
            else:
                message = ''

                # aby zapisać do bazy tablicę bez nawiasów i apostrofów
                concat_str = ''
                for word in MenuScreen.game_type:
                    concat_str += word + '   '

                images_information = '\n'
                if GameScreen.points == 1:
                    images_information = '\nOdgadnięty obrazek został dodany to Twojej kolekcji.\n'
                elif GameScreen.points > 1:
                    images_information = '\nOdgadnięte obrazki zostały dodane to Twojej kolekcji.\n'

                # czy wynik wystarczający do dodania do tablicy wyników
                if db.put_score(LoggingScreen.user_login, GameScreen.points, concat_str):
                    message = '\nGratulacje!\nTwój wynik znajdzie się na liście najlepszych wyników.'     
                tkinter.messagebox.showinfo('Koniec gry',"Pomyłka, prawidłowa odpowiedź to '" + creature_to_show.name + "'"+ images_information + message)

                parent.switch_frame(MenuScreen)
                GameScreen.points = 0



# _________________________________________________________________________________________________________________________________________________________________________________
# _______________________________________________________________________________   \/ BAZA DANYCH \/   ___________________________________________________________________________
# _________________________________________________________________________________________________________________________________________________________________________________



class Database:

    def __init__(self):
        database_name = 'game_database.db'

        # czy baza istnieje przed połączeniem się do niej (utworzeniem)
        does_database_exist = database_name in os.listdir('.')

        self.conn = sqlite3.connect(database_name)
        self.c = self.conn.cursor()

        # stwórz tabele w bazie jeżeli baza nie istniała przed połączeniem (stworzeniem bazy)
        if not does_database_exist:
            self.create_tables()


    def __del__(self):
        self.conn.commit()
        self.conn.close()


    def create_tables(self):

        self.c.execute('''CREATE TABLE Highscores (
                            login TEXT, 
                            points INTEGER, 
                            game_type TEXT
                            )''')

        self.c.execute('''CREATE TABLE Users (
                            login TEXT, 
                            password TEXT
                            )''')

        # wszystkie 'Stwory' odgadnięte przez wszystkich użytkowników zapisywane są do Creatures
        self.c.execute('''CREATE TABLE Creatures (
                            creature_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            image_url TEXT, 
                            creature_name TEXT,
                            creature_type TEXT
                            )''')

        # łączenie użytkownika ze stworami z Creatures - przypisanie odpowiednich stworów do loginu
        self.c.execute('''CREATE TABLE Possessions (
                            user_login TEXT, 
                            creature_id INTEGER,
                            date_of_addition TEXT
                            )''')

        self.conn.commit()

# _______________________________ users

    def login(self, login:str, password:str):
        # jeżeli jest już w bazie
        self.c.execute("SELECT * FROM Users WHERE Users.login=:log AND Users.password=:pass", {'log':login, 'pass':password})
        if self.c.fetchall():
            return True      # można się zalogować
        else:
            return False     # nie można się zalogować

    

    def register(self, login:str, password:str):
        self.c.execute("SELECT * FROM Users WHERE Users.login=:log", {'log':login})
        if self.c.fetchall():
              return False      # nie można zarejestrować, już jest użytkownik o takim loginie
        else:
            self.c.execute("INSERT INTO Users VALUES (?, ?)", (login, password))
            self.conn.commit()
            return True


# _______________________________ 



# _______________________________ score

    def put_score(self, login:str, points:int, game_type:str):
        # nie ma sensu dodawać wyników = 0, nawet jak jest jeszcze miejsce w tabeli
        if points > 0: 
            self.c.execute("SELECT * FROM Highscores ORDER BY Points DESC")
            highscores = self.c.fetchall()

            # jeżeli w bazie jest >= 30 lepszych rekordów to nie dodawaj, dodaj gdy najgorszy wynik 
            if len(highscores) <= 30 or highscores[-1][1] <= points:
                self.c.execute("INSERT INTO Highscores VALUES (?, ?, ?)", (login, points, game_type))

                # usuwanie słabszych wyników z bazy (jeżeli są słabsze niż wartość pnktów na pozycji 30tej)
                if len(highscores) > 30:
                    self.c.execute("DELETE FROM Highscores WHERE Highscores.points<:poin", {'poin':highscores[30][1]})

                return True # dopisano wynik do bazy

        return False # niedopisano


    def get_highscores(self):
        self.c.execute("SELECT * FROM Highscores ORDER BY Points DESC")
        return self.c.fetchall()

# _______________________________ 



# _______________________________ images

    def put_image(self, user_login:str, date_of_addition:str, creature_name:str, image_url:str, creature_type:str):
        
        self.c.execute("SELECT * FROM Creatures WHERE Creatures.image_url=:img_u", {'img_u': image_url})
        # jeżeli w tabeli Creatures nie ma jeszcze rekordu z takim image_url to dodaj rekord do tabeli
        if not self.c.fetchall():
            self.c.execute("INSERT INTO Creatures VALUES (?, ?, ?, ?)", (None, image_url, creature_name, str(creature_type)))
            self.conn.commit()

        # self.c.execute("SELECT * FROM Creatures")
        # all = self.c.fetchall()
        # for i in all:
        #     print(i)

        # pobieranie id z Creatures tak, aby potem przypisać to id w Possessions
        self.c.execute("SELECT Creatures.creature_id FROM Creatures WHERE Creatures.image_url=:img_u", {'img_u': image_url})
        s = self.c.fetchone()
        if s:
            creature_id = s[0]

        # czy uzytkownik posiada w Possessions
        self.c.execute("SELECT * FROM Possessions INNER JOIN Creatures ON Possessions.creature_id=Creatures.creature_id WHERE Creatures.image_url=:img_u", {'img_u': image_url})
        # użytkownik nie ma danej kreatury w swojej kolekcji, dodaj


        if not self.c.fetchall():
            self.c.execute("INSERT INTO Possessions VALUES (?, ?, ?)", (user_login, str(creature_id), date_of_addition))
            self.conn.commit()



    def get_users_images(self, login):
        
        self.c.execute("SELECT Creatures.creature_id, Creatures.image_url, Creatures.creature_name, Creatures.creature_type, Possessions.date_of_addition FROM Creatures INNER JOIN Possessions ON Creatures.creature_id=Possessions.creature_id WHERE Possessions.user_login=:usr_log", {'usr_log': login})
        return self.c.fetchall()




# _________________________________________________________________________________________________________________________________________________________________________________
# _________________________________________________________________________________________________________________________________________________________________________________
# _________________________________________________________________________________________________________________________________________________________________________________




if __name__ == "__main__":

    app = App()

    # ustaw motyw (używa plik 'sun-valley.tcl' i folderu 'theme')
    app.tk.call("source", "sun-valley.tcl")
    app.tk.call("set_theme", "light")
    global db
    db = Database()

    app.mainloop()
