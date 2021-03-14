import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Subject } from 'rxjs';
import axios from 'axios';

@Injectable({
  providedIn: 'root'
})
export class BookService {

  private book_private;
  private bookSubject = new Subject();
  book = this.bookSubject.asObservable();

  bookID;

  constructor(private http: HttpClient) { }

  getBookID(isbn) {
    return this.http.get('http://localhost:5000/api/v1.0/book_id/'+ isbn)
    .subscribe(response => {
        this.bookID = Number(response)
    }); 
}

getBook(isbn) {
    return this.http.get('http://localhost:5000/api/v1.0/books/' + isbn)
    .subscribe(response => { 
        this.book_private = [response];
        this.bookSubject.next(this.book_private)
        this.getBookID(isbn)
    });
}

 addToWantToRead(book, user_id) {
   axios.post('http://localhost:5000/api/v1.0/books/'+ book + '/' + user_id + '/wanttoread')
}

 addToCurrentlyReading(book, user_id) {
   axios.post('http://localhost:5000/api/v1.0/books/' + book + '/' + user_id + '/currentlyreading')
 }

 addToHasRead(book, user_id) {
   axios.post('http://localhost:5000/api/v1.0/books/'+ book + '/' + user_id + '/hasread')
 }
}
