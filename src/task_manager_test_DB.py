import mysql.connector

spravce_ukolu = {
    1: "Přidat nový úkol",
    2: "Zobrazit všechny úkoly",
    3: "Aktualizovat úkol",
    4: "Odstranit úkol",
    5: "Konec Programu"
} 

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


def vytvoreni_tabulky(spojeni=None):
        if spojeni is not None:
            conn = spojeni
        else:
            conn = pripojeni_db()
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
        if spojeni is None:
            conn.close()
        print("Tabulky byly úspěšně vytvořeny, nebo již existují.")

def pridat_ukol_db(nazev,popis,spojeni=None):
    try:
        if spojeni is not None:
            conn = spojeni
        else:
            conn = pripojeni_db()
            
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ukoly (Nazev, Popis, DatumVytvoreni) VALUES (%s, %s, CURDATE())", (nazev, popis))
        conn.commit()
        cursor.close()
        if spojeni is None:
            conn.close()
        return f"Úkol '{nazev}' byl přidán.\n"
    except mysql.connector.errors.DataError as err:
        return "Název nebo popis je přílíš dlouhý (max. 100 znaků). Zkus to znovu."

def pridat_ukol():
    while True:
        nazev_1 = input("\nZadejte název úkolu: ")
        popis_1 = input("Zadejte popis úkolu: ")
        if nazev_1.strip() and popis_1.strip():
            return pridat_ukol_db(nazev_1, popis_1)
        else:
            print("Pole název a popis nesmí být prázdné!")

def zobrazit_ukoly(spojeni=None):
    if spojeni is not None:
        conn = spojeni
    else:
        conn = pripojeni_db()
    cursor = conn.cursor()
    cursor.execute("SELECT UkolID, Nazev, Popis, Stav, DatumVytvoreni FROM ukoly WHERE (Stav = 'Nezahájeno' OR Stav = 'Probíhá')")
    zobrazit = [{"ID": row[0], "Nazev": row[1], "Popis": row[2], "Stav": row[3], "Datum_vytvoreni": row[4]} for row in cursor.fetchall()]
    cursor.close()
    if spojeni is None:
        conn.close()
    if not zobrazit:
        return f"\nSeznam úkolů:\nŽádné uložené úkoly\n"
    else:
        seznam = ""
        for row in zobrazit:
            seznam += f"{row["ID"]}. {row["Nazev"]} - {row["Popis"]}, stav {row["Stav"]}, vytvořeno {row["Datum_vytvoreni"]}\n"
        return f"\nSeznam úkolů:\n{seznam}"

def aktualizovat_ukol_db(ukol_ID, cislo_stav, nazev_ukolu, spojeni=None):
    if spojeni is not None:
        conn = spojeni
    else:
        conn = pripojeni_db()
    cursor = conn.cursor()
    if int(cislo_stav) == 1:
        cursor.execute("UPDATE ukoly SET Stav = 'Probíhá' WHERE UkolID = %s", (ukol_ID,))
        conn.commit()
        cursor.close()
        if spojeni is None:
            conn.close()
        return f"Stav úkolu '{nazev_ukolu}' byl aktualizován."
    elif int(cislo_stav) == 2:
        cursor.execute("UPDATE ukoly SET Stav = 'Hotovo' WHERE UkolID = %s", (ukol_ID,))
        conn.commit()
        cursor.close()
        if spojeni is None:
            conn.close()
        return f"Stav úkolu '{nazev_ukolu}' byl aktualizován."
    elif int(cislo_stav) == 3:
        cursor.execute("UPDATE ukoly SET stav = 'Zrušeno' WHERE UkolID = %s", (ukol_ID,))
        conn.commit()
        cursor.close()
        if spojeni is None:
            conn.close()
        return f"Stav úkolu '{nazev_ukolu}' byl aktualizován."
    else:
        return f"Něco se nepovedlo."

def aktualizovat_ukol(spojeni=None):
    if spojeni is not None:
        conn = spojeni
    else:
        conn = pripojeni_db()
    cursor = conn.cursor()
    cursor.execute("SELECT UkolID, Nazev, Stav FROM ukoly")
    zobrazit = [{"ID": row[0], "Nazev": row[1], "Stav": row[2]} for row in cursor.fetchall()]
    cursor.close()
    if spojeni is None:
        conn.close()
    if not zobrazit:
        return f"\nSeznam úkolů:\nŽádné uložené úkoly\n"

    while True:
        seznam = ""
        for row in zobrazit:
            seznam += f"{row["ID"]}. {row["Nazev"]}, stav {row["Stav"]}\n"

        platne_ID = [str(ukol["ID"]) for ukol in zobrazit]
        ukol_ID = input(f"\n{seznam}\n\nZadejte číslo úkolu, který chcete aktualizovat: ")
        if ukol_ID in platne_ID:
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

def odstranit_ukol_db(ukol_ID, zmazany_ukol, spojeni=None):
    if spojeni is not None:
        conn = spojeni
    else:
        conn = pripojeni_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ukoly WHERE UkolID = %s", (ukol_ID,))
    conn.commit()
    cursor.close()
    if spojeni is None:
        conn.close()
    return f"Úkol '{zmazany_ukol}' byl odstraněn.\n"
    

def odstranit_ukol(spojeni=None):
    if spojeni is not None:
        conn = spojeni
    else:
        conn = pripojeni_db()
    cursor = conn.cursor()
    cursor.execute("SELECT UkolID, Nazev, Popis, Stav FROM ukoly")
    zobrazit = [{"ID": row[0], "Nazev": row[1], "Popis": row[2], "Stav": row[3]} for row in cursor.fetchall()]
    cursor.close()
    if spojeni is None:
        conn.close()
    if not zobrazit:
        return f"\nSeznam úkolů:\nŽádné uložené úkoly\n"

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


def hlavni_menu():
    while True:
        hlavicka_menu = ""
        for key, value in spravce_ukolu.items():
            hlavicka_menu += f"{key}. {value}\n" 
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
