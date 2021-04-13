import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import axios from 'axios';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class LikeService {

  likeCount;

  private likes_private_list;
  private likesSubject = new Subject();
  likes_list = this.likesSubject.asObservable();

  constructor(private http: HttpClient) { }

  addLike(objectID, targetID) {
    axios.post('http://localhost:5000/api/v1.0/' + sessionStorage.user_id + '/likes' + '?objectID=' + objectID + '&targetID=' + targetID)
  }

  getLikes(objectID, targetID) {
    return this.http.get('http://localhost:5000/api/v1.0/likes' +  '?objectID=' + objectID + '&targetID=' + targetID).subscribe(
      response => {
        this.likes_private_list = response;
        this.likesSubject.next(this.likes_private_list);
      })
  }
}
