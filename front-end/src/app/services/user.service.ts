import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import axios from 'axios';
import { Subject } from 'rxjs';
import config from '../config';
import { FeedService } from './feed.service';

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

  private followed_activity_private_list;
  private followedActivitySubject = new Subject();
  followed_activity_list = this.followedActivitySubject.asObservable();

  currentUser;
  following;

  constructor(private http: HttpClient, private feedService: FeedService) {} 

  addUserToDB(user) {
    let userData = new FormData();

    userData.append("name", user.name);
    userData.append("auth0_id", user.sub);
    userData.append("image", user.picture);

    this.http.post(config.app_url + 'userprofiletodb', userData).subscribe(
      response => {} );
    

    // let auth0_id = user.sub
    // let name = user.name
    // let email = user.email

    // axios.post(config.app_url + 'userprofiletodb/' + auth0_id + '/' + name + '/' + email)
  }

  existingUser(user) {
    // check if user in DB
    console.log(this.http.get(config.app_url + 'userinDB/' + user))
    return this.http.get(config.app_url + 'userinDB/' + user)

  }

  getCurrentUser(auth0_id) {
      return this.http.get(config.app_url + 'auth0/' + auth0_id).subscribe(
          response => {
              this.currentUser = response;
              sessionStorage.setItem("user_id", this.currentUser)

              console.log(this.currentUser)
              
              this.getFollowedActivity(this.currentUser)
              this.getProfileDetails(this.currentUser)
              this.getFollowedUsers(this.currentUser)
          }
      )
  }

  // getCurrentUserProfile(auth0_id) {
  //   this.getCurrentUser(auth0_id)
  //   this.getFollowedActivity(this.currentUser)
  //   this.getProfileDetails(this.currentUser)
  //   this.getFollowedUsers(this.currentUser)
  // }
    


  // getCurrentUser(auth0_id) {
  //   return this.http.get(config.app_url + 'auth0/' + auth0_id).subscribe(
  //     response => {
  //         this.currentUser = response;
  //         sessionStorage.setItem("user_id", this.currentUser)
  //   })
  // }

  // getUserProfile(auth0_id) {
  //   this.getCurrentUser(auth0_id)
  //   this.getFollowedActivity(this.currentUser)
  //   this.getProfileDetails(this.currentUser)
  //   this.getFollowedUsers(this.currentUser)
  // }

  getProfileDetails(user_id) {
    return this.http.get(config.app_url + 'user/' + user_id).subscribe(
        response => {
            this.profile_details_private_list = response;
            this.profileDetailsSubject.next(this.profile_details_private_list);
    })
  }

  checkFollowing(user_id, follower_id) {
    return this.http.get(config.app_url + 'user/' + user_id + '/followedby/' + follower_id).subscribe(
        response => {
            // console.log(response)
            this.following = [response][0];
            console.log(this.following)
        }
    )
  }
  
  followUser(user_id, follower_id) {
    axios.post(config.app_url + 'user/' + user_id + '/follow/' + follower_id)
  }
  
  unfollowUser(user_id, follower_id) {
    axios.delete(config.app_url + 'user/' + user_id + '/unfollow/' + follower_id)
  }

  getFollowedUsers(user_id) {
    return this.http.get(config.app_url + 'user/' + user_id + '/followed').subscribe(
      response => {
        this.followed_users_private_list = response;
        this.followedSubject.next(this.followed_users_private_list)
        console.log(response)
      }
    )
  }

  getFollowedActivity(user_id) {
    return this.http.get(config.app_url + 'activity/followedby/' + user_id).subscribe(
        response => {
            this.followed_activity_private_list = response;
            this.followedActivitySubject.next(this.followed_activity_private_list);
        }
    )

}
}
