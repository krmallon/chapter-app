import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CommentService {

  private comments_private_list;
  private commentsSubject = new Subject();
  comment_list = this.commentsSubject.asObservable();

  constructor(private http: HttpClient) { }

  getComments(object_id, target_id) {
    return this.http.get('http://localhost:5000/api/v1.0/comments/' + object_id + '/' + target_id)
    .subscribe(response => { 
        this.comments_private_list = response;
        this.commentsSubject.next(this.comments_private_list);
    });
  }
}
