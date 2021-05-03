import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';
import config from '../config';

@Injectable({
  providedIn: 'root'
})
export class SearchService {

  private book_results_private_list;
  private bookResultsSubject = new Subject();
  book_results_list = this.bookResultsSubject.asObservable();

  private user_results_private_list;
  private userResultsSubject = new Subject();
  user_results_list = this.userResultsSubject.asObservable();

  constructor(private http: HttpClient) { }

  searchBooks(query, startIndex, lang, order) {
    return this.http.get(config.app_url + 'search/books/' + query + 
    '?lang=' + lang + '&order=' + order + '&startIndex=' + startIndex).subscribe(
      response => {
        this.book_results_private_list = response;
        this.bookResultsSubject.next(this.book_results_private_list);
      })
  }

  searchUsers(query) {
    return this.http.get(config.app_url + 'search/users/' + query).subscribe(
      response => {
        this.user_results_private_list = response;
        this.userResultsSubject.next(this.user_results_private_list);
      })
    }
  }
