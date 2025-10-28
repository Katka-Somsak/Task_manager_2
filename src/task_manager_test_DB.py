import mysql.connector

spravce_ukolu = {
    1: "Přidat nový úkol",
    2: "Zobrazit všechny úkoly",
    3: "Aktualizovat úkol",
    4: "Odstranit úkol",
    5: "Konec Programu"
} 

#připojení na testovací databázi
def pripojeni_test_db():
    try:
        conn = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "",  # doplň vlastní heslo
            database = "test_task_manager" # nebo vyplň vlastní testovací DB
        )
        return conn
    except mysql.connector.errors.ProgrammingError as err:
        print(f"CHYBA PŘI PŘIPOJOVÁNÍ K DATABÁZI.")
        return None

# připojení k databázi
def pripojeni_db():
    try:
        conn = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "",  # doplň vlastní heslo
            database = "task_manager" # nebo vyplň vlastní DB
        )
        return conn
    except mysql.connector.errors.ProgrammingError as err:
        print(f"CHYBA PŘI PŘIPOJOVÁNÍ K DATABÁZI.")
        return None

# definované spojení - pokud není parametr vyplněn, připojí se na pracovní databázi
def connection(spojeni=None):
    if spojeni is not None:
        conn = spojeni
        return conn
    else:
        conn = pripojeni_db()
        return conn

# vytvoření tabulky "ukoly", pokud neexistuje. Nově přidáne úkoly mají stav Nezahájeno
def vytvoreni_tabulky(spojeni=None):
        conn = connection(spojeni)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ukoly (
	        UkolID INT PRIMARY KEY auto_increment,
            Nazev VARCHAR(100) NOT NULL,
            Popis VARCHAR(100) NOT NULL,
            Stav VARCHAR(50) NOT NULL DEFAULT "Nezahájeno",
            DatumVytvoreni DATE NOT NULL
            )
        """)

        conn.commit()
        cursor.close()
        # pokud zapisuje přímo do DB, ukončit spojení:
        if spojeni is None:
            conn.close()
        print("Tabulky byly úspěšně vytvořeny, nebo již existují.")


# přidání úkolu do seznamu - oddělená funkce pro zápis do databáze, přijímá parametry název úkolu, popis úkolu, spojení - buď přímo databáze nebo testovací DB
def pridat_ukol_db(nazev,popis,spojeni=None):
    try:
        conn = connection(spojeni)
            
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ukoly (Nazev, Popis, DatumVytvoreni) VALUES (%s, %s, CURDATE())", (nazev, popis))
        conn.commit()
        cursor.close()
        # pokud zapisuje přímo do DB, ukončit spojení:
        if spojeni is None:
            conn.close()
        return f"Úkol '{nazev}' byl přidán.\n"
    except mysql.connector.errors.DataError as err:
        return "Název nebo popis je přílíš dlouhý (max. 100 znaků). Zkus to znovu."

# přidání úkolu do seznamu - oddělená funkce pro příjem vstupů od uživatele (název a popis úkolu)
def pridat_ukol():
    while True:
        nazev_1 = input("\nZadejte název úkolu: ")
        popis_1 = input("Zadejte popis úkolu: ")
        if nazev_1.strip() and popis_1.strip():
            # volání funkce pro zápis do DB:
            return pridat_ukol_db(nazev_1, popis_1)
        else:
            print("Pole název a popis nesmí být prázdné!")

# funkce pouze pro náhled, tedy zobrazení úkolů
def zobrazit_ukoly(spojeni=None):
    conn = connection(spojeni)

    cursor = conn.cursor()
    # zobrazuje pouze úkoly ve stavu Nezahájeno nebo Probíhá
    cursor.execute("SELECT UkolID, Nazev, Popis, Stav, DatumVytvoreni FROM ukoly WHERE (Stav = 'Nezahájeno' OR Stav = 'Probíhá')")
    zobrazit = [{"ID": row[0], "Nazev": row[1], "Popis": row[2], "Stav": row[3], "Datum_vytvoreni": row[4]} for row in cursor.fetchall()]
    cursor.close()
    # pokud zobrazuje z pracovní DB, ukončit spojení:
    if spojeni is None:
        conn.close()

    # pokud je seznam prázdný, zobrazit info !Žádné uložené úkoly". Jinak zobrazit úkoly.    
    if not zobrazit:
        return f"\nSeznam úkolů:\nŽádné uložené úkoly\n"
    else:
        seznam = ""
        for row in zobrazit:
            seznam += f"{row["ID"]}. {row["Nazev"]} - {row["Popis"]}, stav {row["Stav"]}, vytvořeno {row["Datum_vytvoreni"]}\n"
        return f"\nSeznam úkolů:\n{seznam}"

# aktualizace úkolu v seznamu - oddělená funkce pro úpravu dat v databázi, přijímá parametry ID úkolu,
# číslo nového stavu úkolu, název úkolu pro zobrazení v hlášce potvrzující úpravu stavu a spojení - buď přímo databáze nebo testovací DB
def aktualizovat_ukol_db(ukol_ID, cislo_stav, nazev_ukolu, spojeni=None):
    conn = connection(spojeni)
    cursor = conn.cursor()
    # změna stavu na Probíhá po výběru možnosti č. 1
    if int(cislo_stav) == 1:
        cursor.execute("UPDATE ukoly SET Stav = 'Probíhá' WHERE UkolID = %s", (ukol_ID,))
        conn.commit()
        cursor.close()
        # pokud pracuje s pracovní DB, ukončit spojení:
        if spojeni is None:
            conn.close()
        return f"Stav úkolu '{nazev_ukolu}' byl aktualizován."
    # změna stavu na Hotovo po výběru možnosti č. 2
    elif int(cislo_stav) == 2:
        cursor.execute("UPDATE ukoly SET Stav = 'Hotovo' WHERE UkolID = %s", (ukol_ID,))
        conn.commit()
        cursor.close()
        # pokud pracuje s pracovní DB, ukončit spojení:
        if spojeni is None:
            conn.close()
        return f"Stav úkolu '{nazev_ukolu}' byl aktualizován."
    # změna stavu na Zrušeno po výběru možnosti č. 3
    elif int(cislo_stav) == 3:
        cursor.execute("UPDATE ukoly SET stav = 'Zrušeno' WHERE UkolID = %s", (ukol_ID,))
        conn.commit()
        cursor.close()
        # pokud pracuje s pracovní DB, ukončit spojení:
        if spojeni is None:
            conn.close()
        return f"Stav úkolu '{nazev_ukolu}' byl aktualizován."
    else:
        return f"Něco se nepovedlo."

# aktualizace úkolu v seznamu - oddělená funkce pro příjem vstupů od uživatele
def aktualizovat_ukol(spojeni=None):
    # výpis úkolů
    conn = connection(spojeni)
    cursor = conn.cursor()
    cursor.execute("SELECT UkolID, Nazev, Stav FROM ukoly")
    zobrazit = [{"ID": row[0], "Nazev": row[1], "Stav": row[2]} for row in cursor.fetchall()]
    cursor.close()
    # pokud pracuje s pracovní DB, ukončit spojení:
    if spojeni is None:
        conn.close()
    if not zobrazit:
        return f"\nSeznam úkolů:\nŽádné uložené úkoly\n"

    # opakování příjmu vstupu, pokud uživatel nezadá platné ID úkolu
    while True:
        # zobrazení úkolů
        seznam = ""
        for row in zobrazit:
            seznam += f"{row["ID"]}. {row["Nazev"]}, stav {row["Stav"]}\n"
        
        # kontrola, že ID zadané uživatelem je platné, tedy je v seznamu
        # seznam platných ID:
        platne_ID = [str(ukol["ID"]) for ukol in zobrazit]
        # vyžádání ID od uživatele:
        ukol_ID = input(f"\n{seznam}\n\nZadejte číslo úkolu, který chcete aktualizovat: ")
        # kontrola vstupu v seznamu platných ID
        if ukol_ID in platne_ID:
            # opakování příjmu vstupu, pokud není zadaný platný vstup pro číslo stavu
            while True:
                cislo_stav = input("Vyberte jednu z možností:\n\n1. Probíhá\n2. Hotovo\n3. Zrušeno\n\nZadejte číslo stavu: ")
                if cislo_stav.isnumeric() and int(cislo_stav) in range (1, 4):
                    aktualizovany_ukol = ""
                    for radek in zobrazit:
                        if radek["ID"] == int(ukol_ID):
                            aktualizovany_ukol += f"{radek["Nazev"]}"
                    return aktualizovat_ukol_db(ukol_ID, cislo_stav, aktualizovany_ukol)
                else:
                    print("\nNeplatná volba, vyberte znovu.\n")
        else:
            print("\nNeznáme číslo úkolu. Zadejte znovu.")

# odstránění úkolu ze seznamu - oddělená funkce pro odstránění záznamu v databázi, přijímá parametry ID úkolu, název smazaného úkolu a typ spojení (testovací DB nebo pracovní DB)
def odstranit_ukol_db(ukol_ID, smazany_ukol, spojeni=None):
    conn = connection(spojeni)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ukoly WHERE UkolID = %s", (ukol_ID,))
    conn.commit()
    cursor.close()
    if spojeni is None:
        conn.close()
    return f"Úkol '{smazany_ukol}' byl odstraněn.\n"
    
# odstranění úkolu ze seznamu - oddělená funkce pro příjem vstupu ID úkolu od uživatele 
def odstranit_ukol(spojeni=None):
    conn = connection(spojeni)
    cursor = conn.cursor()
    cursor.execute("SELECT UkolID, Nazev, Popis, Stav FROM ukoly")
    zobrazit = [{"ID": row[0], "Nazev": row[1], "Popis": row[2], "Stav": row[3]} for row in cursor.fetchall()]
    cursor.close()
    if spojeni is None:
        conn.close()
    if not zobrazit:
        return f"\nSeznam úkolů:\nŽádné uložené úkoly\n"

    # opakování zadávání vstupů, pokud uživatel vyplňuje neplatné vstupy
    while True:
        seznam = ""
        for row in zobrazit:
            seznam += f"{row["ID"]}. {row["Nazev"]} - {row["Popis"]}, stav {row["Stav"]}\n"    
        platna_ID = [str(ukol["ID"]) for ukol in zobrazit]  
        ukol_ID = input(f"\n{seznam}\n\nZadejte číslo úkolu, který chcete odstranit: ")
        if ukol_ID in platna_ID:
            zmazany_ukol = ""
            for radek in zobrazit:
                if radek["ID"] == int(ukol_ID):
                    zmazany_ukol += f"{radek["Nazev"]}"
            return odstranit_ukol_db(ukol_ID, zmazany_ukol)

        else:
            print("Neplatné ID, zadejte znovu.")

# hlavní menu správce úkolů
def hlavni_menu():
    # smyčka while zabezpečí, že po dokončení akce libovolné volby se znovu spustí hlavní menu
    while True:
        # vytvoření hlavičky menu s dalšími volbami
        hlavicka_menu = ""
        for key, value in spravce_ukolu.items():
            hlavicka_menu += f"{key}. {value}\n" 

        # vyžádání volby v menu od uživatele + kontrola platného vstupu
        dotaz = input(f"Správce úkolů - Hlavní menu\n{hlavicka_menu}Vyberte možnost (1-{len(spravce_ukolu)}): ")
        while not (dotaz.isnumeric() and int(dotaz) in range(1, len(spravce_ukolu)+1)):
            print("ZADEJTE PLATNÝ VSTUP")
            dotaz = input(f"Vyberte možnost (1-{len(spravce_ukolu)}): ")

        dotaz = int(dotaz)
        if dotaz == 1:
            print(pridat_ukol())
            continue
        elif dotaz == 2:
            print(zobrazit_ukoly())
            continue
        elif dotaz == 3:
            print(aktualizovat_ukol())
            continue
        elif dotaz == 4:
            print(odstranit_ukol())
            continue
        else:
            print("\nKonec programu")
            break
    
if __name__ == "__main__":   
    if pripojeni_db():
        vytvoreni_tabulky() 
        hlavni_menu()
