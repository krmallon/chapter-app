import pandas as pd 
import pytest
from book_recommender import books_bayesian_avg
from book_recommender import create_matrix
from book_recommender import find_similar_books
from book_recommender import get_rating_stats
from book_recommender import make_recommendations
from book_recommender import matrix_sparsity
from book_recommender import read_data_from_csv
from book_recommender import show_books

testRatings = None
testBooks = None

def test_csv_import_ratings():
    global testRatings
    testRatings = pd.read_csv('back-end/data/ratings.csv')
    assert testRatings is not None

def test_csv_import_books():
    global testBooks
    testBooks = pd.read_csv('back-end/data/books.csv')
    assert testBooks is not None

def test_books_bayesian_avg():
    read_data_from_csv()
    books = books_bayesian_avg()

    if 'bayesian_avg' in books.columns:
        assert True
    else:
        assert False

def test_create_matrix():
    matrix, user_mapper, book_mapper, user_inv_mapper, book_inv_mapper = create_matrix(testRatings)
    assert matrix is not None
    assert user_mapper is not None
    assert book_mapper is not None
    assert user_inv_mapper is not None
    assert book_inv_mapper is not None

def test_matrix_sparsity(capfd):
    total_cells = "12232254"
    populated_cells = "132914"
    expected_sparsity = "98.91"

    matrix, user_mapper, book_mapper, user_inv_mapper, book_inv_mapper = create_matrix(testRatings)
    matrix_sparsity(matrix)
    captured = capfd.readouterr()

    assert captured.out == "Total cells: " + total_cells + "\n" + "Populated cells: " + populated_cells + "\n" + "Matrix sparsity: " + expected_sparsity + "\n"

def test_find_similar_books():
    book_id = 2
    matrix, user_mapper, book_mapper, user_inv_mapper, book_inv_mapper = create_matrix(testRatings)
    similar_ids = find_similar_books(book_id, matrix, book_mapper, book_inv_mapper, k=3)

    assert similar_ids[0] is not None
    assert similar_ids[1] is not None
    assert similar_ids[2] is not None

def test_find_similar_books_insufficient_rating_data():
        book_id = 1
        testRatings = pd.read_csv('back-end/data/ratings.csv')
        matrix, user_mapper, book_mapper, user_inv_mapper, book_inv_mapper = create_matrix(testRatings)
        
        with pytest.raises(KeyError):
            find_similar_books(book_id, matrix, book_mapper, book_inv_mapper, k=5)

