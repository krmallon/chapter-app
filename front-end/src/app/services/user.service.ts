import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import axios from 'axios';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  private profile_details_private_list;
  private profileDetailsSubject = new Subject();
  profile_details_list = this.profileDetailsSubject.asObservable();

  currentUser;
  following;

  constructor(private http: HttpClient) {} 

  getCurrentUser(auth0_id) {
      return this.http.get('http://localhost:5000/api/v1.0/auth0/' + auth0_id).subscribe(
          response => {
              this.currentUser = response;
              sessionStorage.setItem("user_id", this.currentUser)
              console.log(this.currentUser)
          }
      )
  }

  getProfileDetails(user_id) {
    return this.http.get('http://localhost:5000/api/v1.0/user/' + user_id).subscribe(
        response => {
            this.profile_details_private_list = response;
            this.profileDetailsSubject.next(this.profile_details_private_list);
    })
  }

  checkFollowing(user_id, follower_id) {
    return this.http.get('http://localhost:5000/api/v1.0/user/' + user_id + '/followedby/' + follower_id).subscribe(
        response => {
            // console.log(response)
            this.following = [response][0];
            console.log(this.following)
        }
    )
  }
  
  followUser(user_id, follower_id) {
    axios.post('http://localhost:5000/api/v1.0/user/' + user_id + '/follow/' + follower_id)
  }
  
  unfollowUser(user_id, follower_id) {
    axios.get('http://localhost:5000/api/v1.0/user/' + user_id + '/unfollow/' + follower_id)
  }
}
