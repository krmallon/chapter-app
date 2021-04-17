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

  private followed_users_private_list;
  private followedSubject = new Subject();
  followed_users_list = this.followedSubject.asObservable();

  currentUser;
  following;

  constructor(private http: HttpClient) {} 

  addUserToDB(user) {
    let userData = new FormData();

    userData.append("name", user.name);
    userData.append("auth0_id", user.sub);
    userData.append("image", user.picture);

    this.http.post('http://localhost:5000/api/v1.0/userprofiletodb', userData).subscribe(
      response => {} );
    

    // let auth0_id = user.sub
    // let name = user.name
    // let email = user.email

    // axios.post('http://localhost:5000/api/v1.0/userprofiletodb/' + auth0_id + '/' + name + '/' + email)
  }

  existingUser(user) {
    // check if user in DB
    console.log(this.http.get('http://localhost:5000/api/v1.0/userinDB/' + user))
    return this.http.get('http://localhost:5000/api/v1.0/userinDB/' + user)

  }

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

  getFollowedUsers(user_id) {
    return this.http.get('http://localhost:5000/api/v1.0/user/' + user_id + '/followed').subscribe(
      response => {
        this.followed_users_private_list = response;
        this.followedSubject.next(this.followed_users_private_list)
        console.log(response)
      }
    )
  }
}
