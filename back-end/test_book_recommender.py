import pandas as pd 
import pytest
from book_recommender import *

# initialises two files to be used from the chosen dataset
testBooks = pd.read_sql_table('BookRecData', con=engine)
testRatings = pd.read_sql_table('Ratings', con=engine)

def test_books_bayesian_avg():
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
        matrix, user_mapper, book_mapper, user_inv_mapper, book_inv_mapper = create_matrix(testRatings)
        
        with pytest.raises(KeyError):
            find_similar_books(book_id, matrix, book_mapper, book_inv_mapper, k=5)

