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

  constructor(private http: HttpClient) { }

  getRecommendations(user_id) {
    return this.http.get('http://localhost:5000/api/v1.0/' + user_id + '/recommendations').subscribe(
        response => {
            this.books_private_list = response;
            this.BooksSubject.next(this.books_private_list);
          })
  }
}
