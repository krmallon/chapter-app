import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class StatService {

  private most_read_private_list;
  private mostReadSubject = new Subject();
  most_read_list = this.mostReadSubject.asObservable();

  private total_pages_private_list;
  private totalPagesSubject = new Subject();
  total_pages_list = this.totalPagesSubject.asObservable();
  
  constructor(private http: HttpClient) { }

  getMostRead(user_id) {
    return this.http.get('http://localhost:5000/api/v1.0/' + user_id + '/stats/mostread').subscribe(
      response => {
        this.most_read_private_list = response;
        this.mostReadSubject.next(this.most_read_private_list);
      })
    }

  getTotalPagesRead(user_id) {
    return this.http.get('http://localhost:5000/api/v1.0/' + user_id + '/stats/totalpages').subscribe(
      response => {
        this.total_pages_private_list = response;
        this.totalPagesSubject.next(this.total_pages_private_list);
      })
    }

  }

