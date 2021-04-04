import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class FeedService {

  private followed_activity_private_list;
  private followedActivitySubject = new Subject();
  followed_activity_list = this.followedActivitySubject.asObservable();

  constructor(private http: HttpClient) { }

  getFollowedActivity(user_id) {
    return this.http.get('http://localhost:5000/api/v1.0/activity/followedby/' + user_id).subscribe(
        response => {
            this.followed_activity_private_list = response;
            this.followedActivitySubject.next(this.followed_activity_private_list);
        }
    )

}
}
