from src.task_manager_test_DB import pripojeni_test_db, vytvoreni_tabulky, pridat_ukol_db, zobrazit_ukoly, aktualizovat_ukol, aktualizovat_ukol_db, odstranit_ukol, odstranit_ukol_db
import pytest
from mysql.connector.errors import IntegrityError
from datetime import date
    

@pytest.fixture
def test_db():
    conn = pripojeni_test_db()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS ukoly")
    conn.commit()
    vytvoreni_tabulky(spojeni=conn)
    yield conn
    cursor.execute("DELETE FROM ukoly")
    conn.commit()
    cursor.close()
    conn.close()


@pytest.fixture
def create_items(test_db):
    items = [
        ("test 1", "popis 1"),
        ("test 2", "popis 2"),
        ("test 3", "popis 3"),  
        ("test 4", "popis 4"),
        ("test 5", "popis 5")
    ]
    for nazev, popis in items:
        pridat_ukol_db(nazev, popis, spojeni=test_db)
    return test_db

@pytest.fixture
def create_1_item(test_db):
    nazev = "Přidání záznamu"
    popis = "K zobrazení uloženého úkolu"
    pridat_ukol_db(nazev, popis, spojeni=test_db)
    return test_db


@pytest.mark.empty
def test_zobrazit_ukoly(test_db):
    result = zobrazit_ukoly(test_db)
    assert "\nSeznam úkolů:\nŽádné uložené úkoly\n" in result


@pytest.mark.empty
def test_aktualizovat_ukol(test_db):
    result = aktualizovat_ukol(test_db)
    assert "\nSeznam úkolů:\nŽádné uložené úkoly\n" in result


@pytest.mark.empty
def test_odstranit_ukol(test_db):
    result = odstranit_ukol(test_db)
    assert "\nSeznam úkolů:\nŽádné uložené úkoly\n" in result
  

@pytest.mark.positive
@pytest.mark.parametrize(
    "nazev, popis", 
    [
        ("test 1", "popis 1"),
        ("test 2", "popis 2"),
        ("test 3", "popis 3")
    ]
)
def test_pridat_ukol_db_poz(nazev, popis, test_db):
    result = pridat_ukol_db(nazev, popis, spojeni=test_db)
    #assert result == f"Úkol '{nazev}' byl přidán.\n"
    assert f"Úkol '{nazev}' byl přidán" in result


@pytest.mark.positive
def test_zobrazit_ukoly_poz(create_1_item):
    result = zobrazit_ukoly(create_1_item)
    datum = date.today()
    assert f"\nSeznam úkolů:\n1. Přidání záznamu - K zobrazení uloženého úkolu, stav Nezahájeno, vytvořeno {datum}\n" in result


@pytest.mark.negative
@pytest.mark.parametrize(
        "nazev, popis",
    [
        ("test 1", "Prilis_dlouhy_text_Prilis_dlouhy_text_Prilis_dlouhy_text_Prilis_dlouhy_text_Prilis_dlouhy_text_Prilis_dlouhy_text"),
        ("Prilis_dlouhy_text_Prilis_dlouhy_text_Prilis_dlouhy_text_Prilis_dlouhy_text_Prilis_dlouhy_text_Prilis_dlouhy_text", "popis 2")
    ]
)
def test_pridat_ukol_db_neg(nazev, popis, test_db):
    result = pridat_ukol_db(nazev, popis, spojeni=test_db)
    assert "Název nebo popis je přílíš dlouhý (max. 100 znaků). Zkus to znovu." in result


@pytest.mark.negative
@pytest.mark.parametrize(
        "nazev, popis, expected_exception",
        [
            (None, None, IntegrityError),
            (None, "popis 1 negativ", IntegrityError),
            ("test 2 negativ", None, IntegrityError)
        ]
)
def test_pridat_ukol_db_neg_2(nazev, popis, expected_exception, test_db):
    with pytest.raises(expected_exception):
        pridat_ukol_db(nazev, popis, spojeni=test_db)



@pytest.mark.positive
@pytest.mark.parametrize(
        "ukol_ID, cislo_stav, nazev_ukolu",
        [
            (1, 1, "test 1"),
            (3, 2, "test 3"),
            (4, 3, "test 4")
        ]
)
def test_aktualizovat_ukol_db_poz(ukol_ID, cislo_stav, nazev_ukolu, create_items):
    result = aktualizovat_ukol_db(ukol_ID, cislo_stav, nazev_ukolu, spojeni=create_items)
    assert f"Stav úkolu '{nazev_ukolu}' byl aktualizován." in result


@pytest.mark.negative
@pytest.mark.parametrize("ukol_ID, cislo_stav, nazev_ukolu", [(3, 5, "test 3")])
def test_aktualizovat_ukol_db_neg(ukol_ID, cislo_stav, nazev_ukolu, create_items):
    result = aktualizovat_ukol_db(ukol_ID, cislo_stav, nazev_ukolu, spojeni=create_items)
    assert "Něco se nepovedlo." in result



@pytest.mark.positive
@pytest.mark.parametrize(
        "ukol_ID, zmazany_ukol", 
        [
         (1, "test 1"),
         (2, "test 2")
        ]
)
def test_odstranit_ukol_DB_poz(ukol_ID, zmazany_ukol, create_items):
    result = odstranit_ukol_db(ukol_ID, zmazany_ukol, spojeni=create_items)
    assert f"Úkol '{zmazany_ukol}' byl odstraněn.\n" in result



@pytest.mark.negative
def test_odstranit_ukol_neg(monkeypatch, create_1_item):
    input = iter(["jedna"])
    monkeypatch.setattr("builtins.input", lambda _:next(input))
    with pytest.raises(StopIteration):
        odstranit_ukol(create_1_item)
