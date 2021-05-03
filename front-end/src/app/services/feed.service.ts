import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';
import config from '../config';

@Injectable({
  providedIn: 'root'
})
export class FeedService {

  private followed_activity_private_list;
  private followedActivitySubject = new Subject();
  followed_activity_list = this.followedActivitySubject.asObservable();

  constructor(private http: HttpClient) { }

  getFollowedActivity(user_id) {
    return this.http.get(config.app_url + 'activity/followedby/' + user_id).subscribe(
        response => {
            this.followed_activity_private_list = response;
            this.followedActivitySubject.next(this.followed_activity_private_list);
        }
    )

}
}
