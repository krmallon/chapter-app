import itertools
import numpy as np
import pandas as pd
import sklearn
import warnings
from scipy.sparse import csr_matrix
from scipy.sparse import save_npz
from sklearn.neighbors import NearestNeighbors

# suppresses potential warning from pandas library as discussed here: https://github.com/pandas-dev/pandas/issues/2841 
warnings.simplefilter(action='ignore', category=FutureWarning)

# initialises two files to be used from the chosen dataset
ratings = None
books = None

def read_data_from_csv():
    global ratings 
    ratings = pd.read_csv('data/ratings.csv')

    global books 
    books = pd.read_csv('data/books.csv')

def get_rating_stats(ratings):
    n_ratings = len(ratings)
    n_books = ratings['book_id'].nunique()
    n_users = ratings['user_id'].nunique()

    print(f"Number of ratings: {n_ratings}")
    print(f"Number of unique book IDs: {n_books}")
    print(f"Number of unique users: {n_users}")
    print(f"Average number of ratings per user: {round(n_ratings/n_users, 2)}")
    print(f"Average number of ratings per book: {round(n_ratings/n_books, 2)}")

def get_user_frequency():
    # creates table showing number of ratings for each user and prints the first five rows
    user_freq = ratings[['user_id', 'book_id']].groupby('user_id').count().reset_index()
    user_freq.columns = ['user_id', 'n_ratings']
    print(user_freq.head())
    print(f"Mean number of ratings for a given user: {user_freq['n_ratings'].mean():.2f}.")

def get_lowest_rated(book_stats):
    # sorts books by bayesian average rating and prints the five lowest rated
    print("The five lowest rated books: ")
    print(book_stats.sort_values('bayesian_avg', ascending=True).head())

def get_highest_rated(book_stats):
    # sorts books by bayesian average rating and prints the five highest rated
    print("The five highest rated books: ")
    print(book_stats.sort_values('bayesian_avg', ascending=False).head())

def bayesian_avg(ratings, C, m):
    # calculates the bayesian average of each book's rating
    bayesian_avg = (C*m+ratings.sum())/(C+ratings.count())
    return bayesian_avg

def books_bayesian_avg():
    # returns books table with bayesian average column added
    # prevents books with few ratings being ranked higher than books with many
    # e.g. a book with 1 rating of 5 compared to a book with 50 ratings with an average of 4.5
    book_stats = ratings.groupby('book_id')[['rating']].agg(['count', 'mean'])
    book_stats.columns = book_stats.columns.droplevel()

    C = book_stats['count'].mean()
    m = book_stats['mean'].mean()
        
    bayesian_avg_ratings = ratings.groupby('book_id')['rating'].agg(bayesian_avg, C, m).reset_index()

    bayesian_avg_ratings.columns = ['book_id', 'bayesian_avg']
    book_stats = book_stats.merge(bayesian_avg_ratings, on='book_id')

    book_stats = book_stats.merge(books[['book_id', 'title']])

    return book_stats

def create_matrix(dataframe):
    """
    Uses the supplied dataframe (ratings) to create a sparse user-item matrix

    Parameters
    --------------
        dataframe: pandas library's primary data structure

    Returns
    --------------
        matrix: user-item matrix (users x books)
        user_mapper: dictionary that maps user_id values to user indices
        book_mapper: dictionary that maps book_id values to book indices
        user_inv_mapper: dictionary that maps user indices to user_id values
        book_inv_mapper: dictionary that maps book indices to book_id values
    """
    N = dataframe['user_id'].nunique()
    M = dataframe['book_id'].nunique()

    user_mapper = dict(zip(np.unique(dataframe["user_id"]), list(range(N))))
    book_mapper = dict(zip(np.unique(dataframe["book_id"]), list(range(M))))
    
    user_inv_mapper = dict(zip(list(range(N)), np.unique(dataframe["user_id"])))
    book_inv_mapper = dict(zip(list(range(M)), np.unique(dataframe["book_id"])))
    
    user_index = [user_mapper[i] for i in dataframe['user_id']]
    book_index = [book_mapper[i] for i in dataframe['book_id']]

    matrix = csr_matrix((dataframe["rating"], (book_index, user_index)), shape=(M, N))
    # saves generated user-item matrix to file
    save_npz('data/user_item_matrix_books.npz', matrix)
    
    return matrix, user_mapper, book_mapper, user_inv_mapper, book_inv_mapper

def matrix_sparsity(matrix):
    # calculates the sparsity of the user-item matrix i.e. percentage of empty cells
    n_total_cells = matrix.shape[0]*matrix.shape[1]
    n_populated_cells = matrix.count_nonzero()
    n_empty_cells = n_total_cells - n_populated_cells
    sparsity = 100 * (n_empty_cells/ n_total_cells)
    sparsity = round(sparsity, 2)

    print("Total cells: " + str(n_total_cells))
    print("Populated cells: " + str(n_populated_cells))
    print("Matrix sparsity: " + str(sparsity))

def find_similar_books(book_id, matrix, book_mapper, book_inv_mapper, k, metric='cosine', show_distance=False):
    """
    Takes supplied book ID and uses k-nearest neighbour algorithm (kNN) to determine k similar books

    Parameters
    --------------
        book_id: ID of the book to base recommendations on
        matrix: user-item matrix of users and book ratings
        book_mapper: book_mapper: dictionary that maps book_id values to book indices
        book_inv_mapper: dictionary that maps book indices to book_id values
        k: number of similar books to retrieve
        metric: distance metric used in calculating kNN

    Returns
    --------------
        neighbour_ids: list of k similar book_id values
    """
    neighbour_ids = []
    
    book_index = book_mapper[book_id]
    book_vector = matrix[book_index]
    k+=1
    kNN = NearestNeighbors(n_neighbors=k, algorithm="brute", metric=metric)
    kNN.fit(matrix)

    if isinstance(book_vector, (np.ndarray)):
        book_vector = book_vector.reshape(1,-1)

    neighbour = kNN.kneighbors(book_vector, return_distance=show_distance)

    for i in range(0,k):
        n = neighbour.item(i)
        neighbour_ids.append(book_inv_mapper[n])

    neighbour_ids.pop(0)
    return neighbour_ids

def show_books(book_titles, n_books):
    # prints a sample of n books for the user
    sample = dict(itertools.islice(book_titles.items(), n_books))
    print("Enter a book ID to generate recommendations: ")
    print("\n".join("{}\t{}".format(k, v) for k, v in sample.items()))

def get_book_id_from_user():
    # allows user to select book_id upon which to base the generated recommendations
    while True:
        try:
            valid_range = range(1,10000)
            book_id = int(input("Enter book_id: "))

            while(book_id not in valid_range):
                book_id = int(input("Invalid input. Enter book_id between 1 and 10000: "))
            break
        except ValueError:
            print("Invalid input. Please enter an integer value between 1 and 10,000.")
    
    return book_id

def make_recommendations(matrix, book_mapper, book_inv_mapper):
    # prints 30 book_id + titles and prompts user to select one
    # prints the k similar books that are determined by the kNN algorithm
    book_titles = dict(zip(books['book_id'], books['title']))

    show_books(book_titles, 30)
    book_id = get_book_id_from_user()

    try:
        similar_ids = find_similar_books(book_id, matrix, book_mapper, book_inv_mapper, k=5)
    except:
        # if the chosen book does not have an adequate number of ratings, the user is prompted to choose another
        print("Insufficient rating data for this book. Please make another choice.")
        make_recommendations(matrix, book_mapper, book_inv_mapper)
    else:
        book_title = book_titles[book_id]

        print(f"Because you read {book_title}:")
        for i in similar_ids:
            print(book_titles[i])

def main():
    read_data_from_csv()
    matrix, user_mapper, book_mapper, user_inv_mapper, book_inv_mapper = create_matrix(ratings)
    make_recommendations(matrix, book_mapper, book_inv_mapper)

if __name__ == "__main__":
    main()

