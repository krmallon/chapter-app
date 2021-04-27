import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class RecommendationService {

  private books_private_list;
  private BooksSubject = new Subject()
  books_list = this.BooksSubject.asObservable();

  private inspiration_books_private_list;
  private InspoBooksSubject = new Subject()
  inspiration_books_list = this.InspoBooksSubject.asObservable();

  constructor(private http: HttpClient) { }

  getRecommendations(user_id) {
    return this.http.get('http://localhost:5000/api/v1.0/' + user_id + '/recommendations').subscribe(
        response => {
            this.books_private_list = response;
            this.BooksSubject.next(this.books_private_list);
            // this.recommendationsExist()
          })
  }

  recommendationsExist() {
    // console.log(this.books_private_list.length)
    // console.log(this.books_private_list.length)
    console.log(typeof this.books_private_list)
    return typeof this.books_private_list != 'undefined'
    // this.recommendations
    // return typeof this.books_private_list != "undefined"
    // return this.books_private_list.length != 0
  }

  getRecInspiration() {
    return this.http.get('http://localhost:5000/api/v1.0/recommendations/inspiration').subscribe(
        response => {
            this.inspiration_books_private_list = response;
            this.InspoBooksSubject.next(this.inspiration_books_private_list);
            console.log(response)

  })
}
}
