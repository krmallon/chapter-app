import { Component, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { AuthService } from '../auth.service';
import { FeedService } from '../services/feed.service';
import { GoalService } from '../services/goal.service';
import { LikeService } from '../services/like.service';
import { UserService } from '../services/user.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

  goalForm;
  feedObjectID = 7

  public sessionStorage = sessionStorage;

  constructor(public feedService: FeedService, public authService: AuthService, public likeService: LikeService, public userService: UserService, private formBuilder: FormBuilder, public goalService: GoalService) { }

  ngOnInit(): void {
    // this.userService.getCurrentUser(sessionStorage.getItem("user"))
    if (this.authService.loggedIn) {
      this.feedService.getFollowedActivity(sessionStorage.user_id)
      this.userService.getProfileDetails(sessionStorage.user_id)
      this.userService.getFollowedUsers(sessionStorage.user_id)

    }
    // this.feedService.getFollowedActivity(sessionStorage.user_id)
    // this.userService.getProfileDetails(sessionStorage.user_id)

    this.goalForm = this.formBuilder.group({
      goalFormControl: ['', Validators.required]
    });
  }

  // maybe move these methods to feedService
  actionType(activity) {
    return activity.action
  }

  objectType(activity) {
    return activity.object_id
  }

  likeUpdate(activity) {
    this.likeService.addLike(this.feedObjectID, activity.activity_id); 
    this.likeService.getLikes(this.feedObjectID, activity.activity_id)
  }


}
