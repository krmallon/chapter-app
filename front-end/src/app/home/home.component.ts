import { Component, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { AuthService } from '../auth.service';
import { FeedService } from '../services/feed.service';
import { UserService } from '../services/user.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

  constructor(public feedService: FeedService, public authService: AuthService, public userService: UserService) { }

  ngOnInit(): void {
    // this.userService.getCurrentUser(sessionStorage.getItem("user"))
    this.feedService.getFollowedActivity(sessionStorage.user_id)
    this.userService.getProfileDetails(sessionStorage.user_id)
  }

  // maybe move these methods to feedService
  actionType(activity) {
    return activity.action
  }

  objectType(activity) {
    return activity.object_id
}
}
